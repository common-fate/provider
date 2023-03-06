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


class Load(BaseModel):
    class Data(BaseModel):
        task: str
        """the resource loader function ID to run"""
        ctx: typing.Optional[dict] = {}
        """context information for the task"""

    type: typing.Literal["load"]
    data: Data


class Event(BaseModel):
    __root__: typing.Union[Grant, Revoke, Load, Describe] = Field(
        ..., discriminator="type"
    )


_T = typing.TypeVar("_T")


class DescribeResponse(BaseModel):
    provider: dict
    config: dict
    diagnostics: typing.List[dict]
    healthy: bool
    provider_schema: dict = Field(alias="schema")


class LoadResponse(BaseModel):
    resources: typing.List[dict]
    tasks: typing.List[dict]


class Result(BaseModel):
    response: typing.Union[DescribeResponse, LoadResponse]


@dataclass
class AWSLambdaRuntime:
    provider: provider.Provider
    name: typing.Optional[str] = None
    version: typing.Optional[str] = None
    publisher: typing.Optional[str] = None

    def handle(self, event, context):
        result = self._do_handle(event=event, context=context)
        if result is not None:
            return result.dict(by_alias=True)

    def _do_handle(self, event, context) -> typing.Optional[Result]:
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
            return None

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
            return None

        if isinstance(event, Describe):
            # Describe returns the configuration of the provider including the current status.
            provider = {
                "publisher": self.publisher,
                "name": self.name,
                "version": self.version,
            }
            config = self.provider._safe_config
            diagnostics = self.provider.diagnostics.export_logs()
            healthy = self.provider.diagnostics.has_no_errors()
            provider_schema = schema.export_schema().dict(exclude_none=True)

            response = DescribeResponse(
                config=config,
                diagnostics=diagnostics,
                healthy=healthy,
                provider=provider,
                schema=provider_schema,
            )

            return Result(response=response)

        elif isinstance(event, Load):
            resources._reset()
            tasks._reset()
            tasks._execute(
                provider=self.provider, task=event.data.task, ctx=event.data.ctx
            )
            # find the resources and pending tasks, and return them
            found = resources.get()
            pending_tasks = tasks.get()

            response = LoadResponse(
                resources=[r.export_json() for r in found],
                tasks=[t.json() for t in pending_tasks],
            )

            return Result(response=response)

        else:
            raise Exception(f"unhandled event type")
