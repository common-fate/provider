import pytest
from commonfate_provider import namespace, provider, config


@pytest.fixture(autouse=True)
def fresh_namespace():
    """clear the registered provider, targets etc between test runs"""
    yield
    namespace.clear()


def test_configurer_works():
    class ExampleProvider(provider.Provider):
        value = provider.String()

    configurer = config.Configurer()
