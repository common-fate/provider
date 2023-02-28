import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from commonfate_provider import access, namespace, provider, resources, schema, target


@pytest.fixture(autouse=True)
def fresh_namespace():
    """clear the registered provider, targets etc between test runs"""
    yield
    namespace.clear()


@pytest.fixture
def snapshot_json(snapshot):
    """use JSON, rather than AmberSnapshotExtension as our schema is serialized as JSON"""
    return snapshot.use_extension(JSONSnapshotExtension)


def test_simple_schema(snapshot_json):
    class Provider(provider.Provider):
        pass

    @access.target()
    class MyTarget:
        pass

    actual = schema.export_schema()
    assert actual == snapshot_json


def test_schema_with_config(snapshot_json):
    class ConfigResource(resources.Resource):
        some_val: str

    class Provider(provider.Provider):
        some_config = provider.String(usage="Some config usage")
        api_token = provider.String(usage="API Token", secret=True)

    @access.target()
    class MyTarget:
        first = target.String(description="first var", title="First")
        my_resource = target.Resource(
            description="first var", title="First", resource=ConfigResource
        )

    actual = schema.export_schema()
    assert actual == snapshot_json


def test_multiple_targets(snapshot_json):
    class Provider(provider.Provider):
        pass

    @access.target()
    class MyTarget:
        first = target.String(description="first var", title="First")

    @access.target()
    class SecondTarget:
        second = target.String(description="second var", title="Second")

    actual = schema.export_schema()
    assert actual == snapshot_json
