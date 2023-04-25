import typing
from provider import namespace, tasks
from pydantic import BaseModel, Field
import inspect
from common_fate_schema.provider import v1alpha1


def composite_id(fields: typing.List[str]):
    return "/".join(fields)


class BaseResource(BaseModel):
    #  A resource with no name. Usually you'll want to subclass resources.Resource instead.

    id: str = Field(title="ID")

    def __init_subclass__(cls) -> None:
        namespace.register_resource_class(cls)
        return super().__init_subclass__()

    def export_json(self) -> dict:
        data = dict(self)
        id = data.pop("id")
        output = {"type": self.__class__.__name__, "id": id, "data": data}
        return output

    class Config:
        @staticmethod
        def schema_extra(
            schema: typing.Dict[str, typing.Any], model: typing.Type["BaseResource"]
        ) -> None:
            """
            shift all of the properties that aren't 'id' or 'name' into a 'data'
            field in the schema to match the export_json() method
            """

            data_keys = [
                key
                for key in schema.get("properties", {}).keys()
                if key != "id" and key != "name"
            ]

            if len(data_keys) == 0:
                return

            schema["properties"]["data"] = {}

            for key in data_keys:
                subschema = schema["properties"].pop(key)
                schema["properties"]["data"][key] = subschema


class Resource(BaseResource):
    name: str

    def export_json(self) -> dict:
        data = dict(self)
        id = data.pop("id")
        name = data.pop("name")
        output = {"type": self.__class__.__name__, "id": id, "name": name, "data": data}
        return output


T = typing.TypeVar("T", bound=BaseResource)


def Related(
    to: typing.Union[typing.Type[T], str], title: str = None, description: str = None
) -> str:
    if inspect.isclass(to):
        to = to.__name__
    return Field(relation=to, title=title, description=description)


def loader(func: tasks.LoaderFunc):
    namespace.register_resource_loader(func)
    return func


def export_schema() -> v1alpha1.Resources:
    """
    Returns the schema for the 'resources' section in a provider schema as a dict.
    This section defines the resources the provider can read, along with the
    fetching methods which can be called to fetch them.
    """
    loaders: typing.Dict[str, v1alpha1.Loader] = {}
    for k in namespace.get_resource_loaders().keys():
        loaders[k] = v1alpha1.Loader(title=k)

    resources = v1alpha1.Resources(loaders=loaders, types={})
    for Klass in namespace.get_resource_classes():
        properties = {}
        all_vars = [(k, v) for (k, v) in vars(Klass).items() if not k.startswith("__")]
        for k, v in all_vars:
            properties[k] = {"type": "string"}
        resources.types[Klass.__name__] = Klass.schema()

    return resources


def register(resource: BaseResource):
    namespace._ALL_RESOURCES.append(resource)


def get() -> typing.List[BaseResource]:
    return namespace._ALL_RESOURCES


def _reset():
    namespace._ALL_RESOURCES = []


def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}
