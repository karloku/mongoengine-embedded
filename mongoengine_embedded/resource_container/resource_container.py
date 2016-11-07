from six import add_metaclass
from .container_metaclass import ContainerMetaclass


@add_metaclass(ContainerMetaclass)
class ResourceContainer(object):
    meta = {
        'abstract': True}
