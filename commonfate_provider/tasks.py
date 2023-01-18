import typing
from commonfate_provider import provider
from dataclasses import dataclass
from typing import Dict, Protocol
from inspect import signature
import abc

from commonfate_provider.dataclass import ModelMeta


class DataClass(Protocol):
    # https://stackoverflow.com/questions/54668000/type-hint-for-an-instance-of-a-non-specific-dataclass
    __dataclass_fields__: Dict


DC = typing.TypeVar("DC", bound=DataClass)

LoaderFunc = typing.Callable[[typing.Any], None]


_RESOURCE_LOADERS: typing.Dict[str, LoaderFunc] = {}

P = typing.TypeVar("P", bound=provider.Provider)


class Task(metaclass=ModelMeta):
    def __init__(self, **data: typing.Any) -> None:
        setattr(self, "__dict__", data)

    def json(self) -> dict:
        return {"name": self.__class__.__name__, "ctx": self.__dict__}

    def run(self, p) -> None:
        """
        Runs the task to fetch resources.
        """
        raise Exception("the run method must be implemented")


_PENDING_TASKS: typing.List[Task] = []


def _reset():
    global _PENDING_TASKS
    _PENDING_TASKS = []


def call(task: Task):
    """
    Registers the intent to call an async task. The task will be deferred
    and executed in the future.
    """
    _PENDING_TASKS.append(task)


def _execute(provider: provider.Provider, name: str, ctx: dict):
    """
    Actually execute a task.

    The task can either be a top-level resource loader, defined with the
    `@resources.fetcher` decorator, or a subtask class
    (e.g. `class MyTask(tasks.Task)`).

    Top-level resource loaders do not accept any context values.
    """
    # check if we have a top-level resource loader registered under the name
    resource_loader = _RESOURCE_LOADERS.get(name)
    if resource_loader is not None:
        return resource_loader(provider)

    for Klass in Task.__subclasses__():
        # todo: handle ambiguity in task class naming
        if Klass.__name__ == name:
            task = Klass(**ctx)
            return task.run(provider)

    # if we get here, we couldn't find the task.
    raise Exception(f"could not find task {name}")


def get() -> typing.List[Task]:
    return _PENDING_TASKS
