import pytest


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

    return container

def test_container_resource_has_crud_methods(MockResource, MockContainer):
    assert callable(MockContainer.create_mock)
    assert callable(MockContainer.get_mock_by_id)
    assert callable(MockContainer.modify_mock_by_id)
    assert callable(MockContainer.destroy_mock_by_id)

def test_embedded_resources_can_be_created(container_with_resources):
    new_mock = container_with_resources.create_mock(name='new_mock')
    assert new_mock.id
    assert new_mock.name == 'new_mock'

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

def test_embedded_resources_can_be_destroyed_by_id(container_with_resources):
    mock_id = container_with_resources.mocks[4].id

    assert container_with_resources.destroy_mock_by_id(mock_id)

    mock = container_with_resources.get_mock_by_id(mock_id)
    assert not mock
