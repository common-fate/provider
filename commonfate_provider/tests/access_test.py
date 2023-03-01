import pytest
from commonfate_provider import access, namespace


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
