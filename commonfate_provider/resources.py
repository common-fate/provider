import typing
from commonfate_provider.dataclass import ModelMeta
from commonfate_provider import tasks
from pydantic import BaseModel, Field
import inspect


def composite_id(fields: typing.List[str]):
    return "/".join(fields)


class Resource(BaseModel):
    id: str

    # def __init__(self, **data: typing.Any) -> None:
    #     setattr(self, "__dict__", data)

    def export_json(self) -> dict:
        return {"type": self.__class__.__name__, "data": dict(self)}

    # def __eq__(self, other: typing.Any) -> bool:
    #     if self.__class__ != other.__class__:
    #         return False
    #     return all(self.__dict__[k] == other.__dict__[k] for k in self.__dict__)

    # def __repr__(self) -> str:
    #     vals = [f"{k}={v}" for (k, v) in self.__dict__.items()]
    #     return self.__class__.__name__ + "(" + ", ".join(vals) + ")"


T = typing.TypeVar("T", bound=Resource)


class Query(typing.Generic[T]):
    def __init__(self, cls: typing.Type[T]) -> None:
        self.cls = cls

    def all(self) -> typing.List[T]:
        return DEFAULT_STORAGE.all(cls=self.cls)


def query(cls: typing.Type[T]) -> Query[T]:
    return Query(cls)


def Related(to: typing.Union[typing.Type[T], str]) -> str:
    if inspect.isclass(to):
        to = to.__name__
    return Field(relatedTo=to)


def Name() -> str:  # type: ignore
    pass


def UserEmail() -> str:  # type: ignore
    pass


class Context(metaclass=ModelMeta):
    def __init__(self, **data: typing.Any) -> None:
        setattr(self, "__dict__", data)


_ALL_RESOURCES: typing.List[Resource] = []


def _reset():
    global _ALL_RESOURCES
    _ALL_RESOURCES = []


def get() -> typing.List[Resource]:
    return _ALL_RESOURCES


def set_fixture(resources: typing.List[Resource]):
    global DEFAULT_STORAGE
    DEFAULT_STORAGE.resources = [r.export_json() for r in resources]


def fetcher(func: tasks.LoaderFunc):
    tasks._RESOURCE_LOADERS[func.__name__] = func
    return func


def audit_schema():
    """
    Returns the schema for the 'audit' section in a provider schema as a dict.
    This section defines the resources the provider can read, along with the
    fetching methods which can be called to fetch them.
    """
    loaders = {}
    for k in tasks._RESOURCE_LOADERS.keys():
        loaders[k] = {"title": k}

    resources = {}
    for Klass in Resource.__subclasses__():
        properties = {}
        all_vars = [(k, v) for (k, v) in vars(Klass).items() if not k.startswith("__")]
        for k, v in all_vars:
            properties[k] = {"type": "string"}
        resources[Klass.__name__] = Klass.schema()

    return {"resourceLoaders": loaders, "resources": resources}


def register(resource: Resource):
    _ALL_RESOURCES.append(resource)


def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}


class JSONStorage:
    def __init__(self, resources: typing.List[dict]) -> None:
        self.resources = resources

    def all(self, cls: typing.Type[T]) -> typing.List[T]:
        resources: typing.List[T] = []
        class_name = cls.__name__
        for r in self.resources:
            if r["type"] == class_name:
                values = without_keys(r, ["type"])
                resource = cls(**values["data"])
                resources.append(resource)

        return resources


DEFAULT_STORAGE = JSONStorage(resources=[])
