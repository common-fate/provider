import typing
from commonfate_provider import namespace, tasks
from pydantic import BaseModel, Field
import inspect


def composite_id(fields: typing.List[str]):
    return "/".join(fields)


class Resource(BaseModel):
    id: str

    def __init_subclass__(cls) -> None:
        namespace.register_resource_class(cls)
        return super().__init_subclass__()

    def export_json(self) -> dict:
        return {"type": self.__class__.__name__, "data": dict(self)}


T = typing.TypeVar("T", bound=Resource)


def Related(
    to: typing.Union[typing.Type[T], str], title: str = None, description: str = None
) -> str:
    if inspect.isclass(to):
        to = to.__name__
    return Field(relatedTo=to, title=title, description=description)


def fetcher(func: tasks.LoaderFunc):
    namespace.register_resource_loader(func)
    return func


def audit_schema():
    """
    Returns the schema for the 'audit' section in a provider schema as a dict.
    This section defines the resources the provider can read, along with the
    fetching methods which can be called to fetch them.
    """
    loaders = {}
    for k in namespace.get_resource_loaders().keys():
        loaders[k] = {"title": k}

    resources = {}
    for Klass in namespace.get_resource_classes():
        properties = {}
        all_vars = [(k, v) for (k, v) in vars(Klass).items() if not k.startswith("__")]
        for k, v in all_vars:
            properties[k] = {"type": "string"}
        resources[Klass.__name__] = Klass.schema()

    return {"resourceLoaders": loaders, "resources": resources}


def register(resource: Resource):
    namespace._ALL_RESOURCES.append(resource)

def get()->typing.List[Resource]:
    return namespace._ALL_RESOURCES

def _reset():
    namespace._ALL_RESOURCES = []

def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}
