from dataclasses import dataclass
from commonfate_provider import (
    provider,
    target,
    resources,
    tasks,
    namespace,
    schema,
)
import typing

from pydantic import BaseModel, Field


class GrantData(BaseModel):
    class Target(BaseModel):
        arguments: typing.Dict[str, str]
        kind: str

    subject: str
    target: Target


class Grant(BaseModel):
    type: typing.Literal["grant"]
    data: GrantData


class Revoke(BaseModel):
    type: typing.Literal["revoke"]
    data: GrantData


class Describe(BaseModel):
    type: typing.Literal["describe"]


class LoadResources(BaseModel):
    class Data(BaseModel):
        name: str
        """the resource loader function ID to run"""
        ctx: dict = {}
        """context information for the task"""

    type: typing.Literal["loadResources"]
    data: Data


class Event(BaseModel):
    __root__: typing.Union[Grant, Revoke, LoadResources, Describe] = Field(
        ..., discriminator="type"
    )


_T = typing.TypeVar("_T")


@dataclass
class AWSLambdaRuntime:
    provider: provider.Provider
    name: typing.Optional[str] = None
    version: typing.Optional[str] = None
    publisher: typing.Optional[str] = None

    def handle(self, event, context):
        parsed = Event.parse_obj(event)
        event = parsed.__root__

        if isinstance(event, Grant):
            try:
                registered_targets = namespace.get_target_classes()
                registered_target = registered_targets[event.data.target.kind]
                args_cls = registered_target.cls
            except KeyError:
                all_keys = ",".join(registered_targets.keys())
                raise KeyError(
                    f"unhandled target kind {event.data.target.kind}, supported kinds are [{all_keys}]"
                )

            args = target._initialise(args_cls, event.data.target.arguments)
            grant = registered_target.get_grant_func()
            grant(self.provider, event.data.subject, args)
            return {"message": "granting access"}

        elif isinstance(event, Revoke):
            try:
                registered_targets = namespace.get_target_classes()
                registered_target = registered_targets[event.data.target.kind]
                args_cls = registered_target.cls
            except KeyError:
                all_keys = ",".join(registered_targets.keys())
                raise KeyError(
                    f"unhandled target kind {event.data.target.kind}, supported kinds are [{all_keys}]"
                )

            args = target._initialise(args_cls, event.data.target.arguments)

            revoke = registered_target.get_revoke_func()
            revoke(self.provider, event.data.subject, args)
            return {"message": "revoking access"}
        if isinstance(event, Describe):
            # Describe returns the configuration of the provider including the current status.
            result = {}
            result["provider"] = {
                "publisher": self.publisher,
                "name": self.name,
                "version": self.version,
            }
            result["config"] = self.provider._safe_config
            result["diagnostics"] = self.provider.diagnostics.export_logs()
            result["healthy"] = self.provider.diagnostics.has_no_errors()
            result["schema"] = schema.export_schema()

            return {"body": result}

        elif isinstance(event, LoadResources):
            resources._reset()
            tasks._reset()
            tasks._execute(
                provider=self.provider, name=event.data.name, ctx=event.data.ctx
            )
            # find the resources and pending tasks, and return them
            found = resources.get()
            pending_tasks = tasks.get()
            print(found)
            response = {
                "resources": [r.export_json() for r in found],
                "pendingTasks": [t.json() for t in pending_tasks],
            }
            print(response)
            return {"body": response}

        else:
            raise Exception(f"unhandled event type")
