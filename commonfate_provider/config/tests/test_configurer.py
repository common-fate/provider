import pytest
from commonfate_provider import namespace, provider, config
from commonfate_provider.config import loaders


@pytest.fixture(autouse=True)
def fresh_namespace():
    """clear the registered provider, targets etc between test runs"""
    yield
    namespace.clear()


def test_configurer_works():
    class ExampleProvider(provider.Provider):
        value = provider.String()

    loader = loaders.DictLoader({"value": "something"})
    configurer = config.Configurer(string_loader=loader, secret_string_loader=loader)

    p = ExampleProvider()
    configurer.configure(p)

    assert p.value.get() == "something"


def test_configurer_works_with_secrets():
    class ExampleProvider(provider.Provider):
        value = provider.String(secret=True)

    loader = loaders.DictLoader({"value": "something"})
    secret_loader = loaders.DictLoader({"value": "something_secret"})
    configurer = config.Configurer(
        string_loader=loader, secret_string_loader=secret_loader
    )

    p = ExampleProvider()
    configurer.configure(p)

    # should be loaded through the secret loader
    assert p.value.get() == "something_secret"
