import typing
import boto3
from botocore.exceptions import ClientError
from dataclasses import dataclass
from commonfate_provider.config import loaders
from commonfate_provider import provider


class ConfigError(Exception):
    """
    Raised if the provider is incorrectly configured.
    """

    pass


@dataclass
class Configurer:
    """
    Configures a provider with the `configure()` method.
    """

    string_loader: loaders.StringLoader
    secret_string_loader: loaders.SecretStringLoader

    def configure(self, p: provider.Provider):
        """
        Configure a provider. This method looks at the defined fields in the provider class
        and tries to resolve them to actual values. Depending on whether the value
        is a secret or not, `string_loader` or `secret_string_loader` is used.
        These are defined when the Configurer is initialised.

        Example:
        ```
        class MyProvider(provider.Provider):
            api_url = provider.String()

        c = Configurer(string_loader=..., secret_string_loader=...)

        p = MyProvider()
        c.configure(p)

        # p.api_url will now be set, and can be used in the provider with
        # p.api_url.get()
        ```
        """
        all_vars = [
            (k, v) for (k, v) in vars(p.__class__).items() if not k.startswith("__")
        ]
        for k, v in all_vars:
            if isinstance(v, provider.String):
                self.resolve_string(p=p, key=k, val=v)

    def resolve_string(self, p: provider.Provider, key: str, val: provider.String):
        try:
            if val.secret is True:
                # the value is a secret
                resolved_secret = self.secret_string_loader.load_secret_string(key)
                val.set(resolved_secret.value)
                setattr(p, key, val)

                # set the value in the safe config dict to the ref,
                # as the value is sensitive.
                p._safe_config[key] = resolved_secret.ref
                return

            else:
                # the value is not a secret
                resolved_value = self.string_loader.load_string(key)
                val.set(resolved_value)
                setattr(p, key, val)

                # the value is not sensitive, so it can be shown to users.
                p._safe_config[key] = resolved_value
                return

        except loaders.NotFoundError as e:
            # if we get here, we didn't find a value for the config variable
            # this is fine if the variable is optional, but otherwise we raise an exception
            if val.optional is False:
                p.diagnostics.error(f"config {key} is required: {e}")


DEV_LOADER = Configurer(
    string_loader=loaders.EnvLoader(),
    secret_string_loader=loaders.DevEnvSecretLoader(),
)
"""
used only for local provider development.
"""

AWS_LAMBDA_LOADER = Configurer(
    string_loader=loaders.EnvLoader(),
    secret_string_loader=loaders.SSMSecretLoader(),
)
"""
used in the AWS Lambda runtime.
"""
