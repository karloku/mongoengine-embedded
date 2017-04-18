import pytest
import mongomock

from datetime import datetime

@pytest.fixture(scope='session')
def db_connection():
    from mongoengine import connect
    connect(
        alias='test',
        db='mongoenginetest',
        host='mongomock://localhost')


@pytest.fixture(scope='session')
def MockResource(db_connection):
    from mongoengine import EmbeddedDocument, StringField, BooleanField, DateTimeField
    from mongoengine_embedded import EmbeddedResource

    class MockResource(EmbeddedDocument, EmbeddedResource):
        name = StringField()
        is_removed = BooleanField(default=False)

    return MockResource

@pytest.fixture(scope='session')
def MockCommonResource(db_connection):
    """
    @brief : not inherit EmbeddedResource
    """
    from mongoengine import EmbeddedDocument, StringField, BooleanField

    class MockCommonResource(EmbeddedDocument):
        name = StringField()
        is_removed = BooleanField(default=False)


    return MockCommonResource


@pytest.fixture(scope='session')
def MockContainer(db_connection, MockResource, MockCommonResource):
    from mongoengine import Document, DateTimeField, EmbeddedDocumentListField, EmbeddedDocumentField
    from mongoengine_embedded import ResourceContainer

    @ResourceContainer
    class MockContainer(Document):
        mocks = EmbeddedDocumentListField(
            MockResource,
            element_name='mock',
            soft_deletion_key='is_removed')

        mock = EmbeddedDocumentField(MockResource, element_name='fmt_mock')

        common_mocks = EmbeddedDocumentListField(MockCommonResource, match_key='name')
        common_mock = EmbeddedDocumentField(MockCommonResource)
        modify_at = DateTimeField(default=None, trigger_modify=True)

        meta = {
            'db_alias': 'test',
            'collection': 'mocks'
        }

    return MockContainer
