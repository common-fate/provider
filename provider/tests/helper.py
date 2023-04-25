import typing

import provider
from provider import config
from provider.config import loaders
from provider.runtime import initialise


def initialise_test_provider(config_dict: typing.Dict[str, str]) -> provider.Provider:
    """
    A wrapper around commonfate_provider.runtime.initialise
    which uses a dictionary for all config values.

    For use in tests only.
    """
    loader = loaders.DictLoader(config_dict=config_dict)
    configurer = config.Configurer(string_loader=loader, secret_string_loader=loader)

    return initialise.initialise_provider(configurer=configurer)
