from dataclasses import dataclass
import typing
import provider
from provider import (
    resources,
    tasks,
    schema,
    access,
    rpc,
)
from common_fate_schema.provider import v1alpha1


@dataclass
class AWSLambdaRuntime:
    provider: provider.Provider
    name: typing.Optional[str] = None
    version: typing.Optional[str] = None
    publisher: typing.Optional[str] = None
    schema_version: typing.Optional[str] = None

    def handle(self, event, context):
        result = self._do_handle(event=event, context=context)
        if result is not None:
            return result.dict(by_alias=True)

    def _do_handle(self, event, context) -> typing.Optional[rpc.Result]:
        parsed = rpc.Event.parse_obj(event)
        event = parsed.__root__

        if isinstance(event, rpc.Grant):
            grant_result = access.call_access_func(
                type="grant",
                p=self.provider,
                data=event.data,
            )

            if grant_result is None:
                return rpc.Result(response=rpc.GrantResponse())  # empty response

            response = rpc.GrantResponse(
                access_instructions=grant_result.access_instructions,
                state=grant_result.state,
            )

            return rpc.Result(response=response)

        elif isinstance(event, rpc.Revoke):
            return access.call_access_func(
                type="revoke",
                p=self.provider,
                data=event.data,
            )

        if isinstance(event, rpc.Describe):
            # Describe returns the configuration of the provider including the current status.
            provider = {
                "publisher": self.publisher,
                "name": self.name,
                "version": self.version,
            }
            config = self.provider._safe_config
            diagnostics = self.provider.diagnostics.export_logs()
            healthy = self.provider.diagnostics.has_no_errors()

            id = None
            if self.name is not None:
                id = v1alpha1.ID(
                    name=self.name,
                    publisher=self.publisher,
                    schema_version=self.schema_version,
                )

            provider_schema = schema.export_schema(id=id).dict(
                exclude_none=True, by_alias=True
            )

            response = rpc.DescribeResponse(
                config=config,
                diagnostics=diagnostics,
                healthy=healthy,
                provider=provider,
                schema=provider_schema,
            )

            return rpc.Result(response=response)

        elif isinstance(event, rpc.Load):
            resources._reset()
            tasks._reset()
            tasks._execute(
                provider=self.provider, task=event.data.task, ctx=event.data.ctx
            )
            # find the resources and pending tasks, and return them
            found = resources.get()
            pending_tasks = tasks.get()

            response = rpc.LoadResponse(
                resources=[r.export_json() for r in found],
                tasks=[t.json() for t in pending_tasks],
            )

            return rpc.Result(response=response)

        else:
            raise Exception(f"unhandled event type")
