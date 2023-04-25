import typing

import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from provider import namespace, resources


@pytest.fixture(autouse=True)
def fresh_namespace():
    """clear the registered provider, targets etc between test runs"""
    yield
    namespace.clear()


@pytest.fixture
def snapshot_json(snapshot):
    """use JSON, rather than AmberSnapshotExtension as our schema is serialized as JSON"""
    return snapshot.use_extension(JSONSnapshotExtension)


def test_resource_schema_works(snapshot_json):
    class FirstResource(resources.Resource):
        """
        An example resource
        """

        value: str
        related_field: typing.Optional[str] = resources.Related("FirstResource")

    class SecondResource(resources.Resource):
        value: str
        related_field: typing.Optional[str] = resources.Related(FirstResource)

    @resources.loader
    def load_resources():
        pass

    got = resources.export_schema()
    assert got.dict() == snapshot_json


def test_resource_schema_works_with_unnamed_resources(snapshot_json):
    class NoName(resources.BaseResource):
        """
        An example resource
        """

        value: str

    got = resources.export_schema()
    assert got.dict() == snapshot_json
