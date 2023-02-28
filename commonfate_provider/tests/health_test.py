import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from commonfate_provider import diagnostics, namespace, provider, health


@pytest.fixture(autouse=True)
def fresh_namespace():
    yield
    namespace.clear()


@pytest.fixture
def snapshot_json(snapshot):
    """use JSON, rather than AmberSnapshotExtension as our schema is serialized as JSON"""
    return snapshot.use_extension(JSONSnapshotExtension)


@pytest.fixture
def provider_with_config_validators():
    class ExampleProvider(provider.Provider):
        pass

    @provider.config_validator(name="List Users")
    def can_list_users(provider: ExampleProvider) -> None:
        provider.diagnostics.info("some message here")

    @provider.config_validator(name="Fails")
    def fails(provider: ExampleProvider) -> None:
        raise Exception("something bad happened")

    return ExampleProvider


def test_provider_config_validation_works(
    provider_with_config_validators, snapshot_json
):
    ExampleProvider = provider_with_config_validators
    prov = ExampleProvider()
    health.validate_config(prov)
    actual = prov.diagnostics.export_logs()
    assert actual == snapshot_json

    healthy = prov.healthy()
    assert healthy == False
