import pytest
from commonfate_provider import namespace, provider, diagnostics


@pytest.fixture(autouse=True)
def fresh_namespace():
    yield
    namespace.clear()


@pytest.fixture
def example_provider():
    class ExampleProvider(provider.Provider):
        value = provider.String()

    return ExampleProvider


@pytest.fixture
def provider_with_config_validators():
    class ExampleProvider(provider.Provider):
        pass

    @provider.config_validator(name="List Users")
    def can_list_users(
        provider: ExampleProvider, diagnostics: diagnostics.Logs
    ) -> None:
        diagnostics.info("some message here")

    @provider.config_validator(name="Fails")
    def fails(provider: ExampleProvider, diagnostics: diagnostics.Logs) -> None:
        raise Exception("something bad happened")

    return ExampleProvider


def test_export_schema_works(example_provider):
    ExampleProvider = example_provider
    got = ExampleProvider.export_schema()
    want = {"value": {"type": "string", "usage": None, "secret": False}}
    assert got == want


def test_provider_config_validation_works(provider_with_config_validators):
    ExampleProvider = provider_with_config_validators
    prov = ExampleProvider()
    got = prov._cf_validate_config()
    want = {
        "can_list_users": {
            "logs": [{"level": "info", "msg": "some message here"}],
            "success": True,
        },
        "fails": {
            "logs": [{"level": "error", "msg": "something bad happened"}],
            "success": False,
        },
    }
    assert got == want
