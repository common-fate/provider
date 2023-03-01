import typing
from commonfate_provider import config, namespace, provider


def initialise_provider(
    configurer: typing.Optional[config.Configurer] = None,
) -> provider.Provider:
    """
    Used in the Provider runtimes to load and initialise a provider class.
    """
    # load the provider from the provider.Provider subclass
    Provider = namespace.get_provider()

    # initialise the provider class
    provider = Provider()

    # configure the provider
    if configurer is not None:
        configurer.configure(provider)

    # run the setup method to call any provider developer-defined
    # setup operations, like configuring API clients.
    provider.setup()

    return provider
