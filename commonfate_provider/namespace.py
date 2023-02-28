"""
Module namespace as an internal module which contains logic to manage the registered
Provider and decorated functions, like Targets and grant/revoke
methods.

For testing purposes, namespace.clear() can be used to remove
all entries from the namespace between different tests.
"""

import typing

if typing.TYPE_CHECKING:
    from commonfate_provider.provider import Provider
    from commonfate_provider.resources import Resource


_PROVIDER: typing.Optional[typing.Type["Provider"]] = None


_ALL_RESOURCES: typing.List["Resource"] = []
"""instances of particular resources. Updated when resources.register() is called."""

_RESOURCE_CLASSES: typing.List[typing.Type["Resource"]] = []
"""the resource classes themselves. Updated when a class subclasses resources.Resource"""

_TARGET_CLASSES: typing.Dict[str, typing.Any] = {}

LoaderFunc = typing.Callable[[typing.Any], None]


_RESOURCE_LOADERS: typing.Dict[str, LoaderFunc] = {}


def register_provider(provider_class: typing.Type["Provider"]):
    """
    Register a provider class.
    """
    global _PROVIDER
    if _PROVIDER is not None:
        raise Exception(
            f"Tried to register a Provider class {provider_class.__name__} but an existing class has already been registered ({_PROVIDER.__name__})"
        )

    _PROVIDER = provider_class


def register_target_class(kind: str, target_class: typing.Type[typing.Any]):
    _TARGET_CLASSES[kind] = target_class


def register_resource_class(resource_class: typing.Type["Resource"]):
    _RESOURCE_CLASSES.append(resource_class)


def register_resource_loader(func: LoaderFunc):
    _RESOURCE_LOADERS[func.__name__] = func


def get_provider() -> typing.Type["Provider"]:
    """
    Loads the registered Provider class.
    """
    global _PROVIDER
    if _PROVIDER is None:
        raise Exception(
            "a Provider has not been registered. Make sure that you add a provider class which subclasses provider.Provider."
        )
    return _PROVIDER


def get_resource_classes() -> typing.List[typing.Type["Resource"]]:
    return _RESOURCE_CLASSES


def get_resource_loaders() -> typing.Dict[str, LoaderFunc]:
    return _RESOURCE_LOADERS


def get_target_classes() -> typing.Dict[str, typing.Type[typing.Any]]:
    return _TARGET_CLASSES


def clear():
    """
    Removes all registered classes and functions.

    Used for testing only.
    """
    global _PROVIDER, _ALL_RESOURCES, _RESOURCE_CLASSES, _RESOURCE_LOADERS, _TARGET_CLASSES
    _PROVIDER = None
    _ALL_RESOURCES = []
    _RESOURCE_CLASSES = []
    _RESOURCE_LOADERS = {}
    _TARGET_CLASSES = {}
