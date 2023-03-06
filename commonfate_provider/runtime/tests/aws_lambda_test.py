import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from commonfate_provider.runtime import AWSLambdaRuntime
from commonfate_provider import namespace, provider, access, target, resources
from commonfate_provider.tests import helper


@pytest.fixture
def snapshot_json(snapshot):
    """use JSON, rather than AmberSnapshotExtension as our schema is serialized as JSON"""
    return snapshot.use_extension(JSONSnapshotExtension)


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

    runtime = AWSLambdaRuntime(provider=basic_provider)
    return runtime


def test_lambda_handler_works(runtime_fixture: AWSLambdaRuntime):
    event = {
        "type": "grant",
        "data": {
            "subject": "testuser",
            "target": {"arguments": {"group": "test"}, "kind": "Default"},
        },
    }
    runtime_fixture.handle(event=event, context=None)


def test_provider_describe(runtime_fixture: AWSLambdaRuntime, snapshot_json):
    event = {"type": "describe"}
    actual = runtime_fixture.handle(event=event, context=None)
    assert actual == snapshot_json


def test_provider_describe_with_config(snapshot_json):
    class Provider(provider.Provider):
        api_url = provider.String(description="API URL")
        api_key = provider.String(description="API key", secret=True)

    p = helper.initialise_test_provider(
        {"api_url": "https://example.com", "api_key": "abcdef"}
    )
    runtime = AWSLambdaRuntime(
        provider=p, publisher="acmecorp", name="test", version="v0.1.0"
    )

    event = {"type": "describe"}
    actual = runtime.handle(event=event, context=None)
    assert actual == snapshot_json


def test_provider_describe_with_errors(snapshot_json):
    class Provider(provider.Provider):
        api_url = provider.String(description="API URL")
        api_key = provider.String(description="API key", secret=True)

    p = helper.initialise_test_provider(
        {"api_url": "https://example.com", "api_key": "abcdef"}
    )
    runtime = AWSLambdaRuntime(
        provider=p, publisher="acmecorp", name="test", version="v0.1.0"
    )
    p.diagnostics.error("some error happened!")

    event = {"type": "describe"}
    actual = runtime.handle(event=event, context=None)
    assert actual == snapshot_json


def test_load_works(snapshot_json):
    class Provider(provider.Provider):
        pass

    class MyResource(resources.Resource):
        val: str

    @resources.loader
    def example_loader(p: Provider):
        resources.register(MyResource(id="123", name="name", val="first"))
        resources.register(MyResource(id="456", val="second", name="resource name"))

    p = Provider()

    runtime = AWSLambdaRuntime(
        provider=p,
    )

    event = {"type": "load", "data": {"task": "example_loader"}}
    actual = runtime.handle(event=event, context=None)
    assert actual == snapshot_json
