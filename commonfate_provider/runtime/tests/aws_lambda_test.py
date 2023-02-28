import pytest
from commonfate_provider.runtime import AWSLambdaRuntime
from commonfate_provider import namespace, provider, access, target


@pytest.fixture(autouse=True)
def fresh_namespace():
    yield
    namespace.clear()


@pytest.fixture
def runtime_fixture():
    class BasicProvider(provider.Provider):
        pass

    @access.target(kind="Default")
    class Args:
        group = target.String()
        pass

    @access.grant(kind="Default")
    def grant(p: BasicProvider, subject, args):
        pass

    basic_provider = BasicProvider()

    runtime = AWSLambdaRuntime(
        provider=basic_provider, config_loader=provider.NoopLoader()
    )
    return runtime


def test_lambda_handler_works(runtime_fixture):
    event = {
        "type": "grant",
        "data": {
            "subject": "testuser",
            "target": {"arguments": {"group": "test"}, "kind": "Default"},
        },
    }
    runtime_fixture.handle(event=event, context=None)


def test_provider_describe(runtime_fixture):
    event = {"type": "describe"}
    runtime_fixture.handle(event=event, context=None)


def test_lambda_runtime_calls_provider_setup():
    class MyProvider(provider.Provider):
        def setup(self):
            self.is_setup = True

    runtime = AWSLambdaRuntime(
        provider=MyProvider(), config_loader=provider.NoopLoader()
    )
    assert runtime.provider.is_setup == True
