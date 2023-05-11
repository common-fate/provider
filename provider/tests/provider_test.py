import pytest
from provider import namespace
import provider


@pytest.fixture(autouse=True)
def fresh_namespace():
    yield
    namespace.clear()


@pytest.fixture
def example_provider():
    class ExampleProvider(provider.Provider):
        value = provider.String()

    return ExampleProvider


def test_export_schema_works(example_provider):
    ExampleProvider = example_provider
    got = ExampleProvider.export_config_schema()
    want = {"value": {"type": "string", "description": None, "secret": False}}
    assert got == want


def test_config_value_missing(example_provider):
    ExampleProvider = example_provider
    p = ExampleProvider()
    with pytest.raises(Exception) as exc_info:
        p.value.get()
    assert str(exc_info.value) == "A required config value is not set"
