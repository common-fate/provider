import typing

import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from commonfate_provider import resources


@pytest.fixture
def snapshot_json(snapshot):
    """use JSON, rather than AmberSnapshotExtension as our schema is serialized as JSON"""
    return snapshot.use_extension(JSONSnapshotExtension)


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


def test_resource_schema_works(snapshot_json):
    got = resources.audit_schema()
    assert got == snapshot_json
