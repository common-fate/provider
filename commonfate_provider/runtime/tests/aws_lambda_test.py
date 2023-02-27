from commonfate_provider.runtime import AWSLambdaRuntime
from commonfate_provider import provider, access, target


class BasicProvider(provider.Provider):
    pass


@access.target(kind="Default")
class Args:
    group = target.String()
    pass


@access.grant()
def grant(p: BasicProvider, subject, args):
    pass


basic_provider = BasicProvider()

runtime = AWSLambdaRuntime(provider=basic_provider, config_loader=provider.NoopLoader())


def test_lambda_handler_works():
    event = {
        "type": "grant",
        "data": {
            "subject": "testuser",
            "target": {"arguments": {"group": "test"}, "kind": "Default"},
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

    runtime = AWSLambdaRuntime(
        provider=MyProvider(), config_loader=provider.NoopLoader()
    )
    assert runtime.provider.is_setup == True
