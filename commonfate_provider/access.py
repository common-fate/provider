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
