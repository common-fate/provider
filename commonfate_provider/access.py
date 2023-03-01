from dataclasses import dataclass
import typing_extensions
import typing

from commonfate_provider import namespace


_T = typing.TypeVar("_T")


@typing_extensions.dataclass_transform()
def target(
    kind: typing.Optional[str] = None,
) -> typing.Callable[[type[_T]], type[_T]]:
    """
    Define a target for access.

    Example:
    ```
    @access.target()
    class Target:
        target_property = target.String()
    ```
    """

    def actual_decorator(cls: type[_T]) -> type[_T]:
        nonlocal kind
        if kind is None:
            kind = cls.__name__

        namespace.register_target_class(kind, cls)

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
    func: GrantValidatorFunc


def grant_validator(
    name: str,
    kind: namespace.KindType = None,
) -> typing.Callable[[GrantValidatorFunc], GrantValidatorFunc]:
    def actual_decorator(func: GrantValidatorFunc):
        id = func.__name__
        gv = GrantValidator(id=id, name=name, func=func)
        namespace.register_grant_validator(kind=kind, grant_validator=gv)
        return func

    return actual_decorator


GrantFunc = typing.Callable[[typing.Any, str, typing.Any], typing.Optional[GrantResult]]

_T = typing.TypeVar("_T")


def grant(
    kind: namespace.KindType = None,
) -> typing.Callable[[GrantFunc], GrantFunc]:
    """
    Register a function as an access granter.

    For example:
    ```
    @access.grant()
    def grant(p: Provider, subject: str, target: MyTargetClass):
        ...
    ```

    The `kind` parameter may be specified to indicate a particular target kind
    that this function grants access to.

    For example:
    ```
    @access.target(kind="MyTargetKind")
    class Target:
        ...

    @access.grant(kind="MyTargetKind")
    def grant(p: Provider, subject: str, target: MyTargetClass):
        ...
    ```
    """

    def actual_decorator(func: GrantFunc):
        namespace.register_grant_func(kind=kind, func=func)
        return func

    return actual_decorator


RevokeFunc = typing.Callable[[typing.Any, str, typing.Any], None]


def revoke(
    kind: typing.Optional[typing.Union[typing.Type[_T], str]] = None,
) -> typing.Callable[[RevokeFunc], RevokeFunc]:
    """
    Register a function as an access revoker.

    For example:
    ```
    @access.revoke()
    def revoke(p: Provider, subject: str, target: MyTargetClass):
        ...
    ```

    The `kind` parameter may be specified to indicate a particular target kind
    that this function revokes access to.

    For example:
    ```
    @access.target(kind="MyTargetKind")
    class Target:
        ...

    @access.revoke(kind="MyTargetKind")
    def revoke(p: Provider, subject: str, target: MyTargetClass):
        ...
    ```
    """

    def actual_decorator(func: RevokeFunc):
        namespace.register_revoke_func(kind=kind, func=func)
        return func

    return actual_decorator
