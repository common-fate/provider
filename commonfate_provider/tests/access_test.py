from commonfate_provider import access


def test_target():
    # reset the registered targets
    access._ALL_TARGETS = {}

    @access.target()
    class ExampleTarget:
        pass

    assert access._ALL_TARGETS == {"ExampleTarget": ExampleTarget}


def test_target_with_kind():
    # reset the registered targets
    access._ALL_TARGETS = {}

    @access.target(kind="SomethingElse")
    class ExampleTarget:
        pass

    assert access._ALL_TARGETS == {"SomethingElse": ExampleTarget}
