import typing

from commonfate_provider import config, provider
from commonfate_provider.config import loaders
from commonfate_provider.runtime import initialise


def initialise_test_provider(config_dict: typing.Dict[str, str]) -> provider.Provider:
    """
    A wrapper around commonfate_provider.runtime.initialise
    which uses a dictionary for all config values.

    For use in tests only.
    """
    loader = loaders.DictLoader(config_dict=config_dict)
    configurer = config.Configurer(string_loader=loader, secret_string_loader=loader)

    return initialise.initialise_provider(configurer=configurer)
