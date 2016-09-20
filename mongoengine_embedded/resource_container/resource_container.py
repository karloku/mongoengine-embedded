from six import add_metaclass
from mongoengine import Document
from .container_metaclass import ContainerMetaclass


@add_metaclass(ContainerMetaclass)
class ResourceContainer(object):
    meta = {
        'abstract': True}
