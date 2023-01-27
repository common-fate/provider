from commonfate_provider import provider, args, resources, tasks
import typing
import boto3

from pydantic import BaseModel, Field


class GrantData(BaseModel):
    subject: str
    args: typing.Dict[str, str]


class Grant(BaseModel):
    type: typing.Literal["grant"]
    data: GrantData


class Revoke(BaseModel):
    type: typing.Literal["revoke"]
    data: GrantData


class Schema(BaseModel):
    type: typing.Literal["schema"]


class Options(BaseModel):
    class Data(BaseModel):
        arg: str
        """the argument to fetch options for"""

    type: typing.Literal["options"]
    data: Data


class LoadResources(BaseModel):
    class Data(BaseModel):
        name: str
        """the resource loader function ID to run"""
        ctx: dict = {}
        """context information for the task"""

    type: typing.Literal["loadResources"]
    data: Data


class Event(BaseModel):
    __root__: typing.Union[Grant, Revoke, Options, LoadResources, Schema] = Field(
        ..., discriminator="type"
    )


class SSMSecretLoader(provider.SecretLoader):
    def load(self,  secret_path: str):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.get_secret_value
        client = boto3.client("ssm")
        value = client.get_secret_value(
            SecretId='string',
            VersionId='string',
            VersionStage='string'
        )
        return value["SecretString"]


class AWSLambdaRuntime:
    def __init__(
        self, provider: provider.Provider, args_cls: typing.Type[args.Args]
    ) -> None:
        self.provider = provider
        self.args_cls = args_cls

    def handle(self, event, context):
        parsed = Event.parse_obj(event)
        event = parsed.__root__

        if isinstance(event, Grant):
            args = self.args_cls(event.data.args)
            grant = provider._get_grant_func()
            grant(self.provider, event.data.subject, args)
            return {"message": "granting access"}

        elif isinstance(event, Revoke):
            args = self.args_cls(event.data.args)
            revoke = provider._get_revoke_func()
            revoke(self.provider, event.data.subject, args)
            return {"message": "revoking access"}

        if isinstance(event, Options):
            self.args_cls.options(self.provider, event.data.arg)

        if isinstance(event, Schema):
            print("starting to get schema")
            return {"target": self.args_cls.export_schema()}

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
            return response

        else:
            raise Exception(f"unhandled event type")
