from commonfate_provider import resources


class ExampleResource(resources.Resource):
    value: str


def test_resource_equality():
    first = ExampleResource(id="test", value="test")
    second = ExampleResource(id="test", value="test")
    assert first.__eq__ is not None
    assert first == second


def test_json_storage_works():
    js = resources.JSONStorage(
        resources=[{"type": "ExampleResource", "id": "test", "value": "test"}]
    )

    want = [ExampleResource(id="test", value="test")]
    got = js.all(ExampleResource)
    assert want == got
