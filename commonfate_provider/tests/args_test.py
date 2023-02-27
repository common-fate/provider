import typing
import pytest
from commonfate_provider import target
from commonfate_provider import provider


def fetch_groups(_) -> typing.List[target.Option]:
    return [
        target.Option(value="one", label="one"),
        target.Option(value="two", label="two"),
        target.Option(value="three", label="three"),
    ]


class ExampleArgs(target.Target):
    group = target.String(fetch_options=fetch_groups)


class BasicProvider(provider.Provider):
    pass


def test_parse_args():
    got_target = ExampleArgs({"group": "test"})
    assert got_target.group == "test"


def test_parse_args_missing_required():
    with pytest.raises(target.ParseError):
        ExampleArgs({})
