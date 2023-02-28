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


def test_export_schema_works(example_provider):
    ExampleProvider = example_provider
    got = ExampleProvider.export_schema()
    want = {"value": {"type": "string", "usage": None, "secret": False}}
    assert got == want
