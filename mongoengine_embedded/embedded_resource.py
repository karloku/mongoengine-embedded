import mongoengine
from bson.objectid import ObjectId


class EmbeddedResource(object):
    _id = mongoengine.ObjectIdField(required=True,
                                    default=lambda: ObjectId())

    @property
    def id(self):
        return self._id
