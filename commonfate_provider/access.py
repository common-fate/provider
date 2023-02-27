from dataclasses import dataclass
import typing_extensions
import typing

_ALL_TARGETS: typing.Dict[str, typing.Any] = {}


_T = typing.TypeVar("_T")


@typing_extensions.dataclass_transform()
def target(
    kind: typing.Optional[str] = None,
) -> typing.Callable[[type[_T]], type[_T]]:
    def actual_decorator(cls: type[_T]) -> type[_T]:
        nonlocal kind
        if kind is None:
            kind = cls.__name__
        _ALL_TARGETS[kind] = cls

        return cls

    return actual_decorator


@dataclass
class GrantResult:
    access_instructions: typing.Optional[str] = None
    """
    Instructions on how to access the entitlements.
    Common Fate will display these to the user upon a successful Access Request.
    """


GrantValidatorFunc = typing.Callable[[typing.Any, str, typing.Any], None]


@dataclass
class GrantValidator:
    name: str
    id: str
    func: GrantValidatorFunc


_ALL_GRANT_VALIDATORS: typing.Dict[str, typing.Dict[str, GrantValidator]] = {}


def grant_validator(
    name: str,
    _internal_key: str = "default",
) -> typing.Callable[[GrantValidatorFunc], GrantValidatorFunc]:
    def actual_decorator(func: GrantValidatorFunc):
        id = func.__name__
        cv = GrantValidator(id=id, name=name, func=func)
        _ALL_GRANT_VALIDATORS.setdefault(_internal_key, {})
        _ALL_GRANT_VALIDATORS[_internal_key][id] = cv
        return func

    return actual_decorator


GrantFunc = typing.Callable[[typing.Any, str, typing.Any], typing.Optional[GrantResult]]
_GRANT: typing.Dict[str, GrantFunc] = {}


def _get_grant_func(_internal_key: str = "default"):
    return _GRANT[_internal_key]


def grant(
    _internal_key: str = "default",
) -> typing.Callable[[GrantFunc], GrantFunc]:
    # _internal_key is used for testing purposes, and allows
    # multiple independent decorators to be registered in a single test file
    def actual_decorator(func: GrantFunc):
        _GRANT[_internal_key] = func
        return func

    return actual_decorator


RevokeFunc = typing.Callable[[typing.Any, str, typing.Any], None]


_REVOKE: typing.Dict[str, RevokeFunc] = {}


def revoke(
    _internal_key: str = "default",
) -> typing.Callable[[RevokeFunc], RevokeFunc]:
    # _internal_key is used for testing purposes, and allows
    # multiple independent decorators to be registered in a single test file
    def actual_decorator(func: RevokeFunc):
        _REVOKE[_internal_key] = func
        return func

    return actual_decorator


def _get_revoke_func(_internal_key: str = "default"):
    return _REVOKE[_internal_key]
