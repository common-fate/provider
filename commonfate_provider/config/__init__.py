import typing
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

    string_loaders: typing.Set[loaders.StringLoader]
    secret_string_loaders: typing.Set[loaders.SecretStringLoader]

    def configure(self, p: provider.Provider):
        """
        Configure a provider. This method looks at the defined fields in the provider class
        and tries to resolve them to actual values. Depending on whether the value
        is a secret or not, `string_loaders` or `secret_string_loaders` are used.
        These are defined when the Configurer is initialised.

        Example:
        ```
        class MyProvider(provider.Provider):
            api_url = provider.String()

        c = Configurer(string_loaders=..., secret_string_loaders=...)

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
        if val.secret is True:
            # the value is a secret
            for s in self.secret_string_loaders:
                resolved_secret = s.load_secret_string(key)
                if resolved_secret is not None:
                    val.set(resolved_secret.value)
                    setattr(p, key, val)

                    # set the value in the safe config dict to the ref,
                    # as the value is sensitive.
                    p._safe_config[key] = resolved_secret.ref

                    return
        else:
            # the value is not a secret
            for s in self.string_loaders:
                resolved_value = s.load_string(key)
                if resolved_value is not None:
                    val.set(resolved_value)
                    setattr(p, key, val)

                    # the value is not sensitive, so it can be shown to users.
                    p._safe_config[key] = resolved_value

                    return

        # if we get here, we didn't find a value for the config variable
        # this is fine if the variable is optional, but otherwise we raise an exception
        if val.optional is False:
            raise ConfigError(f"config value {key} is required but was not provided")


DEV_LOADER = Configurer(
    string_loaders=(loaders.EnvLoader(),),
    secret_string_loaders=(loaders.DevEnvSecretLoader(),),
)
"""
used only for local provider development.
"""

AWS_LAMBDA_LOADER = Configurer(
    string_loaders=(loaders.EnvLoader(),),
    secret_string_loaders=(),  # TODO: add SSM secret loader here
)
"""
used in the AWS Lambda runtime.
"""
