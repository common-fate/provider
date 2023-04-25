from pydantic import BaseModel
import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from provider.runtime import AWSLambdaRuntime
from provider import namespace, access, target, resources, tasks
import provider
from provider.tests import helper


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
    def grant(p: BasicProvider, subject: str, target: Args):
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
        provider=p,
        publisher="acmecorp",
        name="test",
        version="v0.1.0",
        schema_version="v1",
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
        provider=p,
        publisher="acmecorp",
        name="test",
        version="v0.1.0",
        schema_version="v1",
    )
    p.diagnostics.error("some error happened!")

    event = {"type": "describe"}
    actual = runtime.handle(event=event, context=None)
    assert actual == snapshot_json


def test_provider_describe_with_resources(snapshot_json):
    class Provider(provider.Provider):
        pass

    class MyResource(resources.Resource):
        val: str

    class OtherResource(resources.BaseResource):
        other_val: str

    p = Provider()
    runtime = AWSLambdaRuntime(provider=p)

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


def test_load_works_with_subtasks(snapshot_json):
    class Provider(provider.Provider):
        pass

    class MyResource(resources.Resource):
        val: str

    class MyTask(tasks.Task):
        val: str

        def run(self, p: Provider):
            pass

    @resources.loader
    def example_loader(p: Provider):
        tasks.call(MyTask(val="test"))

    p = Provider()

    runtime = AWSLambdaRuntime(
        provider=p,
    )

    event = {"type": "load", "data": {"task": "example_loader"}}
    actual = runtime.handle(event=event, context=None)
    assert actual == snapshot_json


def test_grant_works(snapshot_json):
    class Provider(provider.Provider):
        pass

    @access.target()
    class Target:
        pass

    class State(BaseModel):
        something: str

    @access.grant()
    def grant(p: Provider, subject: str, target: Target) -> access.GrantResult:
        return access.GrantResult(
            access_instructions="test", state=State(something="something")
        )

    p = Provider()

    runtime = AWSLambdaRuntime(
        provider=p,
    )

    event = {
        "type": "grant",
        "data": {"subject": "testuser", "target": {"kind": "Target", "arguments": {}}},
    }
    actual = runtime.handle(event=event, context=None)
    assert actual == snapshot_json


def test_revoke_works_with_state():
    class Provider(provider.Provider):
        pass

    @access.target()
    class Target:
        pass

    class State(BaseModel):
        something: str

    got_var = None

    @access.revoke()
    def revoke(
        p: Provider, subject: str, target: Target, state: State
    ) -> access.GrantResult:
        nonlocal got_var
        got_var = state.something

    p = Provider()

    runtime = AWSLambdaRuntime(
        provider=p,
    )

    event = {
        "type": "revoke",
        "data": {
            "state": {"something": "test"},
            "subject": "testuser",
            "target": {"kind": "Target", "arguments": {}},
        },
    }
    actual = runtime.handle(event=event, context=None)

    # this should be set if the revoke function was
    # called with the correct state.
    assert got_var == "test"
