import pytest


@pytest.fixture(scope='session')
def db_connection():
    from mongoengine import connect
    connect('mongoenginetest', host='mongomock://localhost')


@pytest.fixture(scope='session')
def MockResource(db_connection):
    from mongoengine import EmbeddedDocument, StringField, BooleanField
    from mongoengine_embedded import EmbeddedResource

    class MockResource(EmbeddedDocument, EmbeddedResource):
        name = StringField()
        is_removed = BooleanField(default=False)

    return MockResource


@pytest.fixture(scope='session')
def MockContainer(db_connection, MockResource):
    from mongoengine import Document, StringField, EmbeddedDocumentListField
    from mongoengine_embedded import ResourceContainer

    class MockContainer(Document, ResourceContainer):
        mocks = EmbeddedDocumentListField(
            MockResource,
            element_name='mock',
            soft_deletion_key='is_removed')

    return MockContainer
