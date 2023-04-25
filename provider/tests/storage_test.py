import pytest
from provider import resources, namespace


@pytest.fixture(autouse=True)
def fresh_namespace():
    yield
    namespace.clear()


class ExampleResource(resources.Resource):
    value: str


def test_resource_equality():
    first = ExampleResource(id="test", name="test", value="test")
    second = ExampleResource(id="test", name="test", value="test")
    assert first.__eq__ is not None
    assert first == second
