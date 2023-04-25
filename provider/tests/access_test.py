from dataclasses import dataclass
from pydantic import BaseModel
import pytest

from provider import access, namespace, rpc
import provider


@pytest.fixture(autouse=True)
def fresh_namespace():
    """clear the registered provider, targets etc between test runs"""
    yield
    namespace.clear()


def test_target():
    @access.target()
    class ExampleTarget:
        pass

    targets = namespace.get_target_classes()

    assert targets["ExampleTarget"].cls == ExampleTarget


def test_target_with_kind():
    @access.target(kind="SomethingElse")
    class ExampleTarget:
        pass

    targets = namespace.get_target_classes()

    assert targets["SomethingElse"].cls == ExampleTarget


def test_call_revoke_works():
    class Provider(provider.Provider):
        pass

    @access.target()
    class ExampleTarget:
        pass

    class State(BaseModel):
        my_val: str

    got_var = None

    @access.revoke()
    def revoke(p: Provider, subject: str, target: ExampleTarget, state: State):
        nonlocal got_var
        got_var = state.my_val

    access.call_access_func(
        type="revoke",
        p=Provider(),
        data=rpc.GrantData(
            subject="test",
            target=rpc.GrantData.Target(
                kind="ExampleTarget",
                arguments={},
            ),
            state={"my_val": "test"},
        ),
    )

    # this should be set if the revoke function
    # was called with the correct state variable.
    assert got_var == "test"


def test_call_revoke_works_with_no_context():
    class Provider(provider.Provider):
        pass

    @access.target()
    class ExampleTarget:
        pass

    @access.revoke()
    def revoke(p: Provider, subject: str, target: ExampleTarget):
        pass

    access.call_access_func(
        type="revoke",
        p=Provider(),
        data=rpc.GrantData(
            subject="test",
            target=rpc.GrantData.Target(
                kind="ExampleTarget",
                arguments={},
            ),
            state=None,
        ),
    )


def test_call_revoke_works_with_dict():
    class Provider(provider.Provider):
        pass

    @access.target()
    class ExampleTarget:
        pass

    got_var = None

    @access.revoke()
    def revoke(p: Provider, subject: str, target: ExampleTarget, state: dict):
        nonlocal got_var
        got_var = state["test"]

    access.call_access_func(
        type="revoke",
        p=Provider(),
        data=rpc.GrantData(
            subject="test",
            target=rpc.GrantData.Target(
                kind="ExampleTarget",
                arguments={},
            ),
            state={"test": "example"},
        ),
    )

    assert got_var == "example"


def test_call_revoke_passes_request_id():
    class Provider(provider.Provider):
        pass

    @access.target()
    class ExampleTarget:
        pass

    got_var = None

    @access.revoke()
    def revoke(
        p: Provider, subject: str, target: ExampleTarget, request: rpc.AccessRequest
    ):
        nonlocal got_var
        got_var = request.id

    access.call_access_func(
        type="revoke",
        p=Provider(),
        data=rpc.GrantData(
            subject="test",
            target=rpc.GrantData.Target(
                kind="ExampleTarget",
                arguments={},
            ),
            request=rpc.AccessRequest(id="req_123"),
        ),
    )

    assert got_var == "req_123"
