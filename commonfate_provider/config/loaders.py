from dataclasses import dataclass
import os
import typing
from abc import ABC, abstractmethod


class StringLoader(ABC):
    @abstractmethod
    def load_string(self, field_name: str) -> typing.Optional[str]:
        pass


@dataclass
class Secret:
    ref: str
    """a reference to where the secret can be found"""

    value: str
    """the actual contents of the secret"""


class SecretStringLoader(ABC):
    @abstractmethod
    def load_secret_string(self, field_name: str) -> typing.Optional[Secret]:
        pass


class EnvLoader(StringLoader):
    def load_string(self, field_name: str) -> typing.Optional[str]:
        """
        The field name is transformed to an env var in the following
        format - `PROVIDER_CONFIG_FIELD_NAME`

        For example, if the field is `api_url`, the env var will be
        `PROVIDER_CONFIG_API_URL`
        """
        env_var = f"PROVIDER_CONFIG_{field_name.upper()}"
        return os.getenv(env_var)


class DevEnvSecretLoader(SecretStringLoader):
    """
    For local development only. Not supported in any deployed provider runtimes.
    """

    def load_secret_string(self, field_name: str) -> typing.Optional[Secret]:
        """
        The field name is transformed to an env var in the following
        format - `PROVIDER_SECRET_FIELD_NAME`

        For example, if the field is `api_token`, the env var will be
        `PROVIDER_SECRET_API_TOKEN`
        """
        env_var = f"PROVIDER_SECRET_{field_name.upper()}"

        val = os.getenv(env_var)
        if val is None:
            return None

        return Secret(ref=f"env://{env_var}", value=val)


class DictLoader(StringLoader, SecretStringLoader):
    """
    Used only for writing unit tests which require loaded config.
    """

    def __init__(self, config_dict: dict) -> None:
        self.config = config_dict

    def load_string(self, field_name: str) -> typing.Optional[str]:
        return self.config.get(field_name, None)

    def load_secret_string(self, field_name: str) -> typing.Optional[Secret]:
        val = self.config.get(field_name, None)
        if val is None:
            return None

        return Secret(ref=f"dict://{field_name}", value=val)
