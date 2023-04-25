import typing

from pydantic import BaseModel, Field


class AccessRequest(BaseModel):
    id: str


class GrantData(BaseModel):
    class Target(BaseModel):
        arguments: typing.Dict[str, str]
        kind: str

    subject: str
    target: Target
    state: typing.Optional[dict] = None
    request: typing.Optional[AccessRequest] = None


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


class DescribeResponse(BaseModel):
    provider: dict
    config: dict
    diagnostics: typing.List[dict]
    healthy: bool
    provider_schema: dict = Field(alias="schema")


class LoadResponse(BaseModel):
    resources: typing.List[dict]
    tasks: typing.List[dict]


class GrantResponse(BaseModel):
    access_instructions: typing.Optional[str] = None
    state: typing.Optional[dict] = None


class Result(BaseModel):
    response: typing.Union[DescribeResponse, LoadResponse, GrantResponse]
