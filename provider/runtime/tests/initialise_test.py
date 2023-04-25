import provider
from provider.runtime import initialise


def test_lambda_runtime_calls_provider_setup():
    class MyProvider(provider.Provider):
        def setup(self):
            self.is_setup = True

    p = initialise.initialise_provider()
    assert p.is_setup == True
