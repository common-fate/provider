from dataclasses import dataclass
from enum import Enum
import typing
from abc import ABC, abstractmethod
from commonfate_provider import provider
from commonfate_provider.dataclass import ModelMeta
from commonfate_provider import resources


class ParseError(Exception):
    """Raised if Provider arguments cannot be parsed"""


@dataclass
class Option:
    value: str
    label: str
    description: typing.Optional[str] = None


class Target(metaclass=ModelMeta):
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
    def export_schema(cls) -> dict:
        """
        Exports the target schema defined in an Target class
        to a dictionary.

        For example, if Target is defined as:
        ```
        class Target(target.Target):
            group = target.String(title="Group", description="group to grant access to")
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
                    "resourceName": None,
                }
                if val.description is not None:
                    schema["description"] = val.description
                if val.request_element is not None:
                    schema["requestFormElement"] = val.request_element
                if val.rule_element is not None:
                    schema["ruleFormElement"] = val.rule_element

                target_schema[k] = schema
            if type(v) == Resource:
                val: Resource = v
                schema = {
                    "id": k,
                    "type": "string",
                    "title": val.title,
                    "resourceName": val.resource.__name__,
                }

                if val.resource is not None:
                    properties = {}
                    all_vars = [(k2, v) for (k2, v) in vars(val.resource).items() if not k2.startswith("__")]
                    for k3, v in all_vars:
                        properties[k3] = {"type": "string"}
                    schema["resource"] = val.resource.schema()
                
                if val.description is not None:
                    schema["description"] = val.description

                target_schema[k] = schema
        # Default is a placeholder for future support of multimode providers
        return {"Default": {"schema": target_schema}}




@dataclass
class Field:
    title: typing.Optional[str] = None
    description: typing.Optional[str] = None


class String(Field):
    pass


@dataclass
class Resource(Field):
    resource: typing.Optional[resources.Resource] = None


@dataclass
class Output:
    resource: typing.Optional[typing.Any] = None
