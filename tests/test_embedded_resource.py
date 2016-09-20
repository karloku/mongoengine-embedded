from bson.objectid import ObjectId


def test_embedded_resource_has_id(MockResource):
    model = MockResource()

    assert isinstance(model._id, ObjectId)
    assert model._id == model.id
