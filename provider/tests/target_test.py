import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from provider import access, namespace, resources, target


@pytest.fixture(autouse=True)
def fresh_namespace():
    """clear the registered provider, targets etc between test runs"""
    yield
    namespace.clear()


@pytest.fixture
def snapshot_json(snapshot):
    """use JSON, rather than AmberSnapshotExtension as our schema is serialized as JSON"""
    return snapshot.use_extension(JSONSnapshotExtension)


@access.target()
class ExampleArgs:
    group = target.String()


def test_parse_args():
    got_target = target._initialise(ExampleArgs, {"group": "test"})
    assert got_target.group == "test"


def test_parse_args_missing_required():
    with pytest.raises(target.ParseError):
        target._initialise(ExampleArgs, {})


def test_export_target_schema(snapshot_json):
    @access.target()
    class ExampleTarget:
        my_property = target.String(title="MyProperty")

    got = target.export_schema()
    got_dict = {k: v.dict() for k, v in got.items()}

    assert got_dict == snapshot_json


def test_export_target_resource_schema(snapshot_json):
    class MyResource(resources.Resource):
        pass

    @access.target()
    class ExampleTarget:
        my_property = target.String(title="MyProperty", description="some description")
        my_resource = target.Resource(title="MyResourceField", resource=MyResource)

    got = target.export_schema()
    got_dict = {k: v.dict() for k, v in got.items()}

    assert got_dict == snapshot_json
