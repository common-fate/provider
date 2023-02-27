import typing
import pytest
from commonfate_provider import target
from commonfate_provider import provider


class ExampleArgs(target.Target):
    group = target.String()


class BasicProvider(provider.Provider):
    pass


def test_parse_args():
    got_target = ExampleArgs({"group": "test"})
    assert got_target.group == "test"


def test_parse_args_missing_required():
    with pytest.raises(target.ParseError):
        ExampleArgs({})
