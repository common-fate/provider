from commonfate_provider import provider, args, resources, tasks
import typing

from pydantic import BaseModel, Field


class GrantData(BaseModel):
    class Target(BaseModel):
        arguments: typing.Dict[str, str]
        mode: str

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


class AWSLambdaRuntime:
    def __init__(
        self,
        provider: provider.Provider,
        args_cls: typing.Type[args.Args],
        name: str = "",
        version: str = "",
        publisher: str = "",
    ) -> None:
        self.provider = provider
        self.args_cls = args_cls
        self.name = name
        self.version = version
        self.publisher = publisher

    def handle(self, event, context):
        parsed = Event.parse_obj(event)
        event = parsed.__root__

        if isinstance(event, Grant):
            if event.data.target.mode != "Default":
                raise Exception(f"unhandled target mode, supported modes are [Default]")
            args = self.args_cls(event.data.target.arguments)
            grant = provider._get_grant_func()
            grant(self.provider, event.data.subject, args)
            return {"message": "granting access"}

        elif isinstance(event, Revoke):
            if event.data.target.mode != "Default":
                raise Exception(f"unhandled target mode, supported modes are [Default]")
            args = self.args_cls(event.data.target.arguments)
            revoke = provider._get_revoke_func()
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
            result["configValidation"] = self.provider.validate_config()
            result["schema"] = {}
            result["schema"]["target"] = self.args_cls.export_schema()
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
