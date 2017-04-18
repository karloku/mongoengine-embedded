from itertools import ifilter
from mongoengine import ListField, EmbeddedDocumentField, DateTimeField
from mongoengine.base import TopLevelDocumentMetaclass
from bson.objectid import ObjectId
from mongoengine_embedded.embedded_resource import EmbeddedResource
from datetime import datetime


def is_embedded_document_list_field(field):
    if not isinstance(field, ListField):
        return False
    if not isinstance(field.field, EmbeddedDocumentField):
        return False

    return True


def is_embedded_document_field(field):
    if not isinstance(field, EmbeddedDocumentField):
        return False
    return True


def is_modify_time_record_field(field):

    if isinstance(field, DateTimeField) and getattr(field, 'trigger_modify', None):
        return True
    return False


def _bind_modify_records(modify_dict, trigger_modify_records):
    if not trigger_modify_records:
        return modify_dict
    time_now = datetime.now()
    for modify_record in trigger_modify_records:
        modify_dict['set__%s' % modify_record] = time_now
    return modify_dict

def embedded_crud_list(base, field, element_name, klass,
                  soft_deletion_key, match_key, trigger_modify_records):

    def is_deactive(e):
        return getattr(e, soft_deletion_key, False)

    def compare_key(field, ele_id):
        fmt_match_key = str(getattr(field, match_key)) if getattr(field, match_key, None) else None
        if str(ele_id) == fmt_match_key:
            return True
        return False

    def create(self, *args, **kwargs):
        # validate the creation params first
        ele = klass(*args, **kwargs)
        ele.validate()

        creation = {'push__%s' % field: ele}
        _bind_modify_records(creation, trigger_modify_records)
        if self.modify(**creation):
            return getattr(self, field)[-1]

    def show(self, ele_id, fetch_type=0):
        """
        :param self:
        :param ele_id:
        :param fetch_type: -1: all  0: active  1:deactive
        :return:
        """
        for e in getattr(self, field):
            if compare_key(e, ele_id):
                if fetch_type == 0 and not is_deactive(e):
                    return e
                elif fetch_type == 1 and is_deactive(e):
                    return e
                return e
        return None

    def modify(self, ele_id, **updates):
        fmt_ele_id = ObjectId(ele_id) if match_key == '_id' else ele_id
        raw_query = {'%s.%s' % (field, match_key): fmt_ele_id, '_id': self.id}
        absolute_updates = {}
        _bind_modify_records(absolute_updates, trigger_modify_records)
        for key in updates.keys():
            key_path = key.split('__')
            key_path.insert(1, '%s__$' % field)
            absolute_updates['__'.join(key_path)] = updates[key]
        updated = self.__class__.objects(__raw__=raw_query).update_one(**absolute_updates)
        if updated:
            self.reload()
        return updated

    def destroy(self, ele_id):
        ele = show(self, ele_id)
        if ele:
            removal = dict()
            if hasattr(ele, soft_deletion_key):
                removal['set__%s' % soft_deletion_key] = True
                return modify(self, ele_id,
                              **removal)
            else:
                removal['pull__%s' % field] = ele
                _bind_modify_records(removal, trigger_modify_records)
                return self.modify(**removal)

        return False

    id_name = 'id' if match_key == '_id' else match_key
    setattr(base, 'create_%s' % element_name, create)
    setattr(base, 'get_%s_by_%s' % (element_name, id_name),  show)
    setattr(base, 'modify_%s_by_%s' %(element_name, id_name), modify)
    setattr(base, 'destroy_%s_by_%s' %(element_name, id_name), destroy)


def embedded_crud(base, field, element_name, klass,
                  soft_deletion_key, trigger_modify_records):

    def create(self, *args, **kwargs):
        # validate the creation params first
        ele = klass(*args, **kwargs)
        ele.validate()

        creation = {'set__%s' % field: ele}
        _bind_modify_records(creation, trigger_modify_records)
        if self.modify(**creation):
            return getattr(self, field)

    def show(self):
        ele = getattr(self, field, None)
        return ele

    def modify(self, **updates):
        raw_query = {'_id': self.id}
        absolute_updates = {}
        _bind_modify_records(absolute_updates, trigger_modify_records)
        for key in updates.keys():
            key_path = key.split('__')
            key_path.insert(1, '%s' % field)
            print key_path
            absolute_updates['__'.join(key_path)] = updates[key]
        updated = self.__class__.objects(__raw__=raw_query).update_one(**absolute_updates)
        if updated:
            self.reload()
        return updated

    def destroy(self):
        ele = show(self)
        if ele:
            removal = dict()
            if hasattr(ele, soft_deletion_key):
                removal['set__%s' % soft_deletion_key] = True
                return modify(self, **removal)
            else:
                _bind_modify_records(removal, trigger_modify_records)
                removal['unset__%s' % field] = True
                return self.modify(**removal)
        return False

    setattr(base, 'create_%s' % element_name, create)
    setattr(base, 'get_%s' % element_name, show)
    setattr(base, 'modify_%s' % element_name, modify)
    setattr(base, 'destroy_%s' % element_name, destroy)


def _bind_crud_list(cls, name, field, trigger_modify_records):
    element_name, soft_deletion_key = _get_embedded_resource_config(name, field)

    match_key = getattr(field, 'match_key', '')
    if not match_key and issubclass(field.field.document_type, EmbeddedResource):
        match_key = '_id'

    klass = field.field.document_type
    embedded_crud_list(
        base=cls,
        field=name,
        element_name=element_name,
        klass=klass,
        soft_deletion_key=soft_deletion_key,
        match_key=match_key,
        trigger_modify_records=trigger_modify_records)


def _bind_crud(cls, name, field, trigger_modify_records):
    element_name, soft_deletion_key = _get_embedded_resource_config(name, field)
    klass = field.document_type
    embedded_crud(
        base=cls,
        field=name,
        element_name=element_name,
        klass=klass,
        soft_deletion_key=soft_deletion_key,
        trigger_modify_records=trigger_modify_records)

def _get_embedded_resource_config(name, field):
    element_name = getattr(field, 'element_name', name)
    soft_deletion_key = getattr(
        field, 'soft_deletion_key', 'is_deactive')
    return element_name, soft_deletion_key


def ResourceContainer(document_klass):
    iter_fields = document_klass._fields.iteritems
    trigger_modify_records = [
        n for (n, f) in iter_fields() if is_modify_time_record_field(f)
    ]

    for name, field in iter_fields():
        if is_embedded_document_list_field(field):
            _bind_crud_list(document_klass, name, field, trigger_modify_records)
        elif is_embedded_document_field(field):
            _bind_crud(document_klass, name, field, trigger_modify_records)

    return document_klass
