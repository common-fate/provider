"""
Module namespace as an internal module which contains logic to manage the registered
Provider and decorated functions, like Targets and grant/revoke
methods.

For testing purposes, namespace.clear() can be used to remove
all entries from the namespace between different tests.
"""

from dataclasses import dataclass
import inspect
import typing

if typing.TYPE_CHECKING:
    from commonfate_provider.provider import Provider, ConfigValidator
    from commonfate_provider.resources import Resource
    from commonfate_provider.access import (
        GrantFunc,
        RevokeFunc,
        GrantValidator,
    )


_PROVIDER: typing.Optional[typing.Type["Provider"]] = None


_ALL_RESOURCES: typing.List["Resource"] = []
"""instances of particular resources. Updated when resources.register() is called."""

_RESOURCE_CLASSES: typing.List[typing.Type["Resource"]] = []
"""the resource classes themselves. Updated when a class subclasses resources.Resource"""

_ALL_GRANT_VALIDATORS: typing.Dict[str, typing.Dict[str, "GrantValidator"]] = {}

_ALL_CONFIG_VALIDATORS: typing.Dict[str, "ConfigValidator"] = {}


@dataclass
class Target:
    cls: typing.Any
    grant_func: typing.Optional["GrantFunc"] = None
    revoke_func: typing.Optional["RevokeFunc"] = None

    def get_revoke_func(self) -> "RevokeFunc":
        if self.revoke_func is None:
            raise Exception("revoke function is not defined for this target")
        return self.revoke_func

    def get_grant_func(self) -> "GrantFunc":
        if self.grant_func is None:
            raise Exception("grant function is not defined for this target")
        return self.grant_func


_TARGET_CLASSES: typing.Dict[str, Target] = {}


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
    _TARGET_CLASSES[kind] = Target(cls=target_class)


_T = typing.TypeVar("_T")

KindType = typing.Optional[typing.Union[typing.Type[_T], str]]


def register_grant_func(kind: KindType, func: "GrantFunc"):
    kind_str = _lookup_kind(kind=kind, function_type="grant function")
    _TARGET_CLASSES[kind_str].grant_func = func


def register_revoke_func(kind: KindType, func: "RevokeFunc"):
    kind_str = _lookup_kind(kind=kind, function_type="revoke function")
    _TARGET_CLASSES[kind_str].revoke_func = func


def _lookup_kind(kind: KindType, function_type: str) -> str:
    """
    Looks up the `kind` parameter to match it with a target kind.

    The `kind` parameter is optional in our decorator methods,
    so if it isn't provided, we try and look up the registered target class.
    """
    if len(_TARGET_CLASSES) == 0:
        raise Exception(
            f"A target class must be defined with @access.target() before registering a {function_type}"
        )
    if kind is None and len(_TARGET_CLASSES) > 1:
        raise Exception(
            f'This provider grants access to multiple targets. You must specify the kind of target that this {function_type} refers to. For example: @decorator_method(kind="MyTarget")'
        )

    if kind is None:
        kind = next(iter(_TARGET_CLASSES))

    if inspect.isclass(kind):
        kind = kind.__name__

    return kind


def register_resource_class(resource_class: typing.Type["Resource"]):
    _RESOURCE_CLASSES.append(resource_class)


def register_resource_loader(func: LoaderFunc):
    _RESOURCE_LOADERS[func.__name__] = func


def register_grant_validator(
    kind: KindType, id: str, grant_validator: "GrantValidator"
):
    kind_str = _lookup_kind(kind=kind, function_type="grant validator")
    _ALL_GRANT_VALIDATORS.setdefault(kind_str, {})
    _ALL_GRANT_VALIDATORS[kind_str][id] = grant_validator


def register_config_validator(id: str, config_validator: "ConfigValidator"):
    _ALL_CONFIG_VALIDATORS[id] = config_validator


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


def get_target_classes() -> typing.Dict[str, typing.Type[Target]]:
    return _TARGET_CLASSES


def get_config_validators():
    return _ALL_CONFIG_VALIDATORS


def clear():
    """
    Removes all registered classes and functions.

    Used for testing only.
    """
    global _PROVIDER, _ALL_RESOURCES, _RESOURCE_CLASSES, _RESOURCE_LOADERS, _TARGET_CLASSES, _ALL_GRANT_VALIDATORS
    _PROVIDER = None
    _ALL_RESOURCES = []
    _RESOURCE_CLASSES = []
    _RESOURCE_LOADERS = {}
    _TARGET_CLASSES = {}
    _ALL_GRANT_VALIDATORS = {}
