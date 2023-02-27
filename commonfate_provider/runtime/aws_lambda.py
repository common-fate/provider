from commonfate_provider import provider, access, target, resources, tasks
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


class AWSLambdaRuntime:
    def __init__(
        self,
        provider: provider.Provider,
        config_loader: provider.ConfigLoader,
        name: str = "",
        version: str = "",
        publisher: str = "",
    ) -> None:
        self.provider = provider
        self.name = name
        self.version = version
        self.publisher = publisher

        # load the provider config
        provider._cf_load_config(config_loader=config_loader)

        # call the setup method on the provider to initialise any API clients etc.
        provider.setup()

    def handle(self, event, context):
        parsed = Event.parse_obj(event)
        event = parsed.__root__

        if isinstance(event, Grant):
            try:
                args_cls = access._ALL_TARGETS[event.data.target.kind]
            except KeyError:
                all_keys = ",".join(access._ALL_TARGETS.keys())
                raise KeyError(
                    f"unhandled target kind {event.data.target.kind}, supported kinds are [{all_keys}]"
                )

            args = target._initialise(args_cls, event.data.target.arguments)
            grant = access._get_grant_func()
            grant(self.provider, event.data.subject, args)
            return {"message": "granting access"}

        elif isinstance(event, Revoke):
            try:
                args_cls = access._ALL_TARGETS[event.data.target.kind]
            except KeyError:
                all_keys = ",".join(access._ALL_TARGETS.keys())
                raise KeyError(
                    f"unhandled target kind {event.data.target.kind}, supported kinds are [{all_keys}]"
                )

            args = target._initialise(args_cls, event.data.target.arguments)

            revoke = access._get_revoke_func()
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
            result["config"] = self.provider.config_dict
            result["configValidation"] = self.provider._cf_validate_config()
            result["schema"] = {}

            # in future we'll handle multiple kinds of targets,
            # but for now, just get the first one
            target_kind = next(iter(access._ALL_TARGETS))
            target_class = access._ALL_TARGETS[target_kind]

            result["schema"]["target"] = target.export_schema(target_kind, target_class)
            result["schema"]["audit"] = resources.audit_schema()
            result["schema"]["config"] = self.provider.export_schema()

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
