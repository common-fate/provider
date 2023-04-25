from dataclasses import dataclass
import inspect
import typing_extensions
import typing

from pydantic import BaseModel

import provider
from provider import namespace, rpc
from provider import target as cf_target

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


class GrantResult(BaseModel):
    access_instructions: typing.Optional[str] = None
    """
    Instructions on how to access the entitlements.
    Common Fate will display these to the user upon a successful Access Request.
    """
    state: typing.Optional[BaseModel] = None
    """
    State which will be stored and provided to the corresponding revoke function.
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


def call_access_func(
    type: typing.Union[typing.Literal["grant"], typing.Literal["revoke"]],
    p: provider.Provider,
    data: rpc.GrantData,
):
    """
    Calls the actual @access.grant() or @access.revoke function.

    The PDK supports optional 'state', and "request" which is passed between grant() and revoke().

    For a stateful revoke function, the signature looks like:
    ```
    def revoke(p: Provider, subject: str, target: Target, state: State):
        ...
    ```

    For a stateless revoke function, the signature looks like:
    ```
    def revoke(p: Provider, subject: str, target: Target):
        ...
    ```

    This method inspects the signature of the revoke function, and passes
    state through if the signature supports it.
    """
    try:
        registered_targets = namespace.get_target_classes()
        registered_target = registered_targets[data.target.kind]
        args_cls = registered_target.cls
    except KeyError:
        all_keys = ",".join(registered_targets.keys())
        raise KeyError(
            f"unhandled target kind {data.target.kind}, supported kinds are [{all_keys}]"
        )

    t = cf_target._initialise(args_cls, data.target.arguments)

    if type == "grant":
        func = registered_target.get_grant_func()
    else:
        func = registered_target.get_revoke_func()

    # initialise the arguments that the revoke() function
    # will be called by
    kwargs = {
        "p": p,
        "subject": data.subject,
        "target": t,
        "state": data.state,
        "request": data.request,
    }

    spec = inspect.getfullargspec(func)

    # check if the function uses state
    state_anno = spec.annotations.get("state", None)

    # if it doesn't, remove it from the arguments
    # the function is called with
    if state_anno is None:
        del kwargs["state"]

    elif issubclass(state_anno, BaseModel):
        kwargs["state"] = state_anno.parse_obj(data.state)

    # check if the function uses the request
    request_anno = spec.annotations.get("request", None)

    # if it doesn't, remove it from the arguments
    # the function is called with
    if request_anno is None:
        del kwargs["request"]

    return func(**kwargs)
