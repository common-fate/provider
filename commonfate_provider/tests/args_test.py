import typing
import pytest
from commonfate_provider import args
from commonfate_provider import provider


def fetch_groups(_) -> typing.List[args.Option]:
    return [
        args.Option(value="one", label="one"),
        args.Option(value="two", label="two"),
        args.Option(value="three", label="three"),
    ]


class ExampleArgs(args.Args):
    group = args.String(fetch_options=fetch_groups)


class BasicProvider(provider.Provider):
    pass


def test_parse_args():
    got_args = ExampleArgs({"group": "test"})
    assert got_args.group == "test"


def test_parse_args_missing_required():
    with pytest.raises(args.ParseError):
        ExampleArgs({})
