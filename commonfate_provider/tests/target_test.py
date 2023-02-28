import pytest
from commonfate_provider import namespace, target, access, resources
from commonfate_provider import provider


@pytest.fixture(autouse=True)
def fresh_namespace():
    """clear the registered provider, targets etc between test runs"""
    yield
    namespace.clear()


@access.target()
class ExampleArgs:
    group = target.String()


def test_parse_args():
    got_target = target._initialise(ExampleArgs, {"group": "test"})
    assert got_target.group == "test"


def test_parse_args_missing_required():
    with pytest.raises(target.ParseError):
        target._initialise(ExampleArgs, {})


def test_export_target_schema():
    @access.target()
    class ExampleTarget:
        my_property = target.String(title="MyProperty")

    got = target.export_schema()

    want = {
        "ExampleTarget": {
            "schema": {
                "my_property": {
                    "id": "my_property",
                    "resourceName": None,
                    "title": "MyProperty",
                    "type": "string",
                }
            }
        }
    }

    assert want == got


def test_export_target_resource_schema():
    class MyResource(resources.Resource):
        pass

    @access.target()
    class ExampleTarget:
        my_property = target.String(title="MyProperty")
        my_resource = target.Resource(title="MyResource", resource=MyResource)

    got = target.export_schema()

    want = {
        "ExampleTarget": {
            "schema": {
                "my_property": {
                    "id": "my_property",
                    "resourceName": None,
                    "title": "MyProperty",
                    "type": "string",
                },
                "my_resource": {
                    "id": "my_resource",
                    "resource": {
                        "properties": {"id": {"title": "Id", "type": "string"}},
                        "required": ["id"],
                        "type": "object",
                        "title": "MyResource",
                    },
                    "title": "MyResource",
                    "resourceName": "MyResource",
                    "type": "string",
                },
            }
        }
    }

    assert want == got
