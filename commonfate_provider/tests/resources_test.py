import typing
from commonfate_provider import resources


class FirstResource(resources.Resource):
    """
    An example resource
    """

    value: str
    related_field: typing.Optional[str] = resources.Related("FirstResource")


class SecondResource(resources.Resource):
    value: str
    related_field: typing.Optional[str] = resources.Related(FirstResource)


@resources.fetcher
def load_resources():
    pass


def test_audit_schema_works():
    got = resources.audit_schema()

    want = {
        "resourceLoaders": {"load_resources": {"title": "load_resources"}},
        "resources": {
            "FirstResource": {
                "description": "An example resource",
                "properties": {
                    "id": {"title": "Id", "type": "string"},
                    "related_field": {
                        "relatedTo": "FirstResource",
                        "title": "Related Field",
                        "type": "string",
                    },
                    "value": {"title": "Value", "type": "string"},
                },
                "required": ["id", "value", "related_field"],
                "title": "FirstResource",
                "type": "object",
            },
            "SecondResource": {
                "properties": {
                    "id": {"title": "Id", "type": "string"},
                    "related_field": {
                        "relatedTo": "FirstResource",
                        "title": "Related Field",
                        "type": "string",
                    },
                    "value": {"title": "Value", "type": "string"},
                },
                "required": ["id", "value", "related_field"],
                "title": "SecondResource",
                "type": "object",
            },
        },
    }
    assert got == want


def test_build_resource_graph_works():
    pass
    # resources.set_fixture(
    #     [
    #         FirstResource(id="1", value="test"),
    #         SecondResource(id="2", related_field="1", value="test"),
    #     ]
    # )
    # got = resources.graph()
    # want = ["FirstResource:1", "SecondResource:2"]

    # assert got.vs()["name"] == want

    # edges = [e.vertex_tuple for e in got.es()]
    # edge_names = [(source["name"], target["name"]) for (source, target) in edges]

    # assert edge_names == [("FirstResource:1", "SecondResource:2")]
