import pytest
from datetime import datetime, timedelta

@pytest.fixture
def container(MockContainer, request):
    container = MockContainer()
    container.save()
    def fin():
        container.delete()

    request.addfinalizer(fin)
    return container

@pytest.fixture
def container_with_resources(MockResource, container):
    for i in xrange(10):
        container.create_mock(name='new_mock_%s' % i)

    for i in xrange(10):
        container.create_common_mocks(name='new_mock_%s' % i)

    container.create_common_mock(name='one_instance_new_mock')
    container.create_fmt_mock(name='one_instance_new_mock')

    return container

def test_container_resource_does_not_break_subclass_meta(MockResource, MockContainer):
    mock_resource_meta = MockContainer._meta
    assert mock_resource_meta.get('collection') == 'mocks'
    assert mock_resource_meta.get('db_alias') == 'test'

def test_container_resource_has_crud_methods(MockResource, MockContainer):
    assert callable(MockContainer.create_mock)
    assert callable(MockContainer.get_mock_by_id)
    assert callable(MockContainer.modify_mock_by_id)
    assert callable(MockContainer.destroy_mock_by_id)
    assert callable(MockContainer.create_fmt_mock)
    assert callable(MockContainer.get_fmt_mock)
    assert callable(MockContainer.modify_fmt_mock)
    assert callable(MockContainer.destroy_fmt_mock)
    assert callable(MockContainer.create_common_mocks)
    assert callable(MockContainer.get_common_mocks_by_name)
    assert callable(MockContainer.modify_common_mocks_by_name)
    assert callable(MockContainer.destroy_common_mocks_by_name)
    assert callable(MockContainer.create_common_mock)
    assert callable(MockContainer.get_common_mock)
    assert callable(MockContainer.modify_common_mock)
    assert callable(MockContainer.destroy_common_mock)

def test_embedded_resources_can_be_created(container_with_resources):
    new_mock = container_with_resources.create_mock(name='new_mock')
    assert new_mock.id
    assert new_mock.name == 'new_mock'
    # modify test
    new_time = datetime.now()
    old_time = container_with_resources.modify_at
    diff_time = (new_time - old_time).total_seconds()
    assert diff_time < 0.1


def test_embedded_resources_can_be_got_by_id(container_with_resources):
    mock_id = container_with_resources.mocks[4].id

    mock = container_with_resources.get_mock_by_id(mock_id)
    assert str(mock.id) == str(mock_id)

def test_embedded_resources_can_be_modified_by_id(container_with_resources):
    mock_id = container_with_resources.mocks[4].id

    new_name = 'Choson Awesome Mock'
    assert container_with_resources.modify_mock_by_id(mock_id, set__name=new_name)
    mock = container_with_resources.get_mock_by_id(mock_id)
    assert mock.name == new_name

    #modify test
    new_time = datetime.now()
    old_time = container_with_resources.modify_at
    print old_time
    diff_time = (new_time - old_time).total_seconds()
    assert diff_time < 0.1



def test_embedded_resources_can_be_destroyed_by_id(container_with_resources):
    mock_id = container_with_resources.mocks[4].id

    assert container_with_resources.destroy_mock_by_id(mock_id)

    mock = container_with_resources.get_mock_by_id(mock_id)
    assert mock.is_removed

    # modify test
    new_time = datetime.now()
    old_time = container_with_resources.modify_at
    diff_time = (new_time - old_time).total_seconds()
    assert diff_time < 0.1


def test_embedded_resources_can_be_modified_by_match_key(container_with_resources):
    mock_name = container_with_resources.common_mocks[3].name
    new_name = 'Choson Awesome Mock'
    assert container_with_resources.modify_common_mocks_by_name(mock_name, set__name=new_name)
    mock = container_with_resources.get_common_mocks_by_name(new_name)
    assert mock.name == new_name


def test_embedded_resources_can_be_destroyed_by_match_key(container_with_resources):
    mock_name = container_with_resources.common_mocks[4].name
    assert container_with_resources.destroy_common_mocks_by_name(mock_name)
    mock = container_with_resources.get_common_mocks_by_name(mock_name)
    assert not mock


def test_embedded_res_can_be_modified(container_with_resources):
    old_mock_name = container_with_resources.common_mock.name

    new_name = 'Choson Awesome Mock'
    assert container_with_resources.modify_common_mock(set__name=new_name)
    mock = container_with_resources.get_common_mock()
    assert mock.name == new_name
    # modify test
    new_time = datetime.now()
    old_time = container_with_resources.modify_at
    diff_time = (new_time - old_time).total_seconds()
    assert diff_time < 0.1

def test_embedded_res_can_be_destroyed(container_with_resources):
    new_name = 'Choson Awesome Mock'
    ret = container_with_resources.destroy_common_mock()
    assert ret
    mock = container_with_resources.get_common_mock()
    assert not mock
    # modify test
    new_time = datetime.now()
    old_time = container_with_resources.modify_at
    diff_time = (new_time - old_time).total_seconds()
    assert diff_time < 0.1
