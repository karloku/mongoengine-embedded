from itertools import ifilter
from mongoengine import ListField, EmbeddedDocumentField
from mongoengine.base import TopLevelDocumentMetaclass
from bson.objectid import ObjectId
from mongoengine_embedded.embedded_resource import EmbeddedResource


def is_embedded_document_list_field(field):
    if not isinstance(field, ListField):
        return False
    if not isinstance(field.field, EmbeddedDocumentField):
        return False
    if not issubclass(field.field.document_type, EmbeddedResource):
        return False
    return True


def embedded_crud(base, field, element_name, klass,
                  soft_deletion_key):
    def is_deactive(e):
        return getattr(e, soft_deletion_key, False)

    def create(self, *args, **kwargs):
        # validate the creation params first
        ele = klass(*args, **kwargs)
        ele.validate()

        creation = {'push__%s' % field: ele}
        if self.modify(**creation):
            return getattr(self, field)[-1]

    def show(self, ele_id):
        for e in getattr(self, field):
            if str(ele_id) == str(e.id) and not is_deactive(e):
                return e
        return None

    def modify(self, ele_id, **updates):
        raw_query = {'%s._id' % field: ObjectId(ele_id), '_id': self.id}
        absolute_updates = {}
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
            if hasattr(ele, soft_deletion_key):
                return modify(self, ele_id,
                              **{'set__%s' % soft_deletion_key: True})
            else:
                removal = {'pull__%s' % field: ele}
                return self.modify(**removal)

        return False

    setattr(base, 'create_%s' % element_name, create)
    setattr(base, 'get_%s_by_id' % element_name, show)
    setattr(base, 'modify_%s_by_id' % element_name, modify)
    setattr(base, 'destroy_%s_by_id' % element_name, destroy)


class ContainerMetaclass(TopLevelDocumentMetaclass):
    def __init__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.iteritems():
            if not is_embedded_document_list_field(attr_value):
                continue

            element_name = getattr(attr_value, 'element_name', attr_name)
            soft_deletion_key = getattr(
                attr_value, 'soft_deletion_key', 'is_deactive')
            klass = attr_value.field.document_type

            embedded_crud(
                base=cls,
                field=attr_name,
                element_name=element_name,
                klass=klass,
                soft_deletion_key=soft_deletion_key)
