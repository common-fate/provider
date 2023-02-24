from dataclasses import dataclass
from enum import Enum
import typing
from abc import ABC, abstractmethod
from commonfate_provider import provider
from commonfate_provider.dataclass import ModelMeta


class ParseError(Exception):
    """Raised if Provider arguments cannot be parsed"""


@dataclass
class Option:
    value: str
    label: str
    description: typing.Optional[str] = None


@dataclass
class GroupOption:
    children: typing.List[str]
    value: str
    label: str
    label_prefix: typing.Optional[str] = None
    description: typing.Optional[str] = None


class Targets(metaclass=ModelMeta):
    def __init__(self, raw_targets: dict) -> None:
        """
        initialise Target based on a provided dictionary.
        """
        all_vars = [k for k in vars(self.__class__).keys() if not k.startswith("__")]
        for k in all_vars:
            if k not in raw_targets:
                raise ParseError(f"{k} argument is required")
            val = raw_targets[k]
            setattr(self, k, val)

    @classmethod
    def options(cls, provider: provider.Provider, target: str) -> typing.List[Option]:
        val = getattr(cls, target)
        if not isinstance(val, Field):
            raise Exception(f"invalid target: {target}")
        if val.fetch_options is None:
            raise Exception(f"target {target} does not provide options")
        return val.fetch_options(provider)

    @classmethod
    def export_schema(cls) -> dict:
        """
        Exports the target schema defined in an Target class
        to a dictionary.

        For example, if Targets is defined as:
        ```
        class Target(target.Target):
            group = args.String(title="Group", description="group to grant access to")
        ```

        this method will produce a dictionary in the form:
        ```json
        {
            "group": {
                "id": "group",
                "description": "group to grant access to",
                "title": "Group",
                "type": "string"
            }
        }
        ```
        """
        target_schema = {}
        all_vars = [(k, v) for (k, v) in vars(cls).items() if not k.startswith("__")]
        for k, v in all_vars:
            if type(v) == String:
                val: String = v
                schema = {
                    "id": k,
                    "type": "string",
                    "title": val.title,
                    "options": val.fetch_options is not None,
                    "groups": None,
                    "ruleFormElement": FormElement.INPUT,
                    "resourceName": None,
                }
                if val.description is not None:
                    schema["description"] = val.description
                if val.request_element is not None:
                    schema["requestFormElement"] = val.request_element
                if val.rule_element is not None:
                    schema["ruleFormElement"] = val.rule_element

                if val.groups is not None:
                    group_schema = {}
                    for g in val.groups:
                        group_schema[g.__name__] = g.__dict__

                target_schema[k] = schema
            if type(v) == Resource:
                val: Resource = v
                schema = {
                    "id": k,
                    "type": "string",
                    "title": val.title,
                    "options": val.fetch_options is not None,
                    "groups": None,
                    "ruleFormElement": FormElement.INPUT,
                    "resourceName": val.resource.__name__,
                }
                if val.description is not None:
                    schema["description"] = val.description
                if val.request_element is not None:
                    schema["requestFormElement"] = val.request_element
                if val.rule_element is not None:
                    schema["ruleFormElement"] = val.rule_element

                if val.groups is not None:
                    group_schema = {}
                    for g in val.groups:
                        group_schema[g.__name__] = g.__dict__

                target_schema[k] = schema
        # Default is a placeholder for future support of multimode providers
        return {"Default": {"schema": target_schema}}


class FormElement(str, Enum):
    SELECT = "SELECT"
    INPUT = "INPUT"
    MULTISELECT = "MULTISELECT"


FormElementValue = typing.Literal["SELECT", "INPUT", "MULTISELECT"]


@dataclass
class Group(ABC):
    description: typing.Optional[str] = None
    title: typing.Optional[str] = None
    resource: typing.Optional[typing.Any] = None

    @abstractmethod
    def match(self, key: str) -> typing.List[str]:
        pass


OptionsFetcher = typing.Callable[[typing.Any], typing.List[Option]]


@dataclass
class Field:
    title: typing.Optional[str] = None
    allow_multiple: bool = True
    description: typing.Optional[str] = None
    groups: typing.Optional[typing.Tuple[typing.Type[Group], ...]] = None
    fetch_options: typing.Optional[OptionsFetcher] = None
    request_element: typing.Optional[FormElementValue] = None
    rule_element: typing.Optional[FormElementValue] = None


class String(Field):
    pass


@dataclass
class Resource(Field):
    resource: typing.Optional[typing.Any] = None


@dataclass
class Output:
    resource: typing.Optional[typing.Any] = None
