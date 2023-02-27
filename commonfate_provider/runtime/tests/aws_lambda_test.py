import typing
from commonfate_provider.runtime import AWSLambdaRuntime
from commonfate_provider import provider, target


class BasicProvider(provider.Provider):
    pass


def fetch_groups(provider: BasicProvider) -> typing.List[target.Option]:
    return [
        target.Option(value="one", label="one"),
        target.Option(value="two", label="two"),
        target.Option(value="three", label="three"),
    ]


class Args(target.Target):
    group = target.String(fetch_options=fetch_groups)
    pass


@provider.grant()
def grant(p: BasicProvider, subject, args):
    pass


basic_provider = BasicProvider()
basic_provider._cf_load_config(config_loader=provider.NoopLoader())

runtime = AWSLambdaRuntime(provider=basic_provider, args_cls=Args)


def test_lambda_handler_works():
    event = {
        "type": "grant",
        "data": {
            "subject": "testuser",
            "target": {"arguments": {"group": "test"}, "mode": "Default"},
        },
    }
    runtime.handle(event=event, context=None)


def test_provider_describe():
    event = {"type": "describe"}
    runtime.handle(event=event, context=None)


def test_lambda_runtime_calls_provider_setup():
    class MyProvider(provider.Provider):
        def setup(self):
            self.is_setup = True

    runtime = AWSLambdaRuntime(provider=MyProvider(), args_cls=Args)
    assert runtime.provider.is_setup == True
