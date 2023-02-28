import os
import typing
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod
from commonfate_provider import diagnostics, namespace


class StringLoader(ABC):
    @abstractmethod
    def load_string(self, field_name: str) -> typing.Optional[str]:
        pass


class EnvLoader(StringLoader):
    def load_secret_string(self, field_name: str) -> typing.Optional[str]:
        """
        The field name is transformed to an env var in the following
        format - `PROVIDER_CONFIG_FIELD_NAME`

        For example, if the field is `api_url`, the env var will be
        `PROVIDER_CONFIG_API_URL`
        """
        env_var = f"PROVIDER_CONFIG_{field_name.upper()}"
        return os.getenv(env_var)


class DevEnvSecretLoader(StringLoader):
    """
    For local development only. Not supported in any deployed provider runtimes.
    """

    def load_string(self, field_name: str) -> typing.Optional[str]:
        """
        The field name is transformed to an env var in the following
        format - `PROVIDER_SECRET_FIELD_NAME`

        For example, if the field is `api_token`, the env var will be
        `PROVIDER_SECRET_API_TOKEN`
        """
        env_var = f"PROVIDER_SECRET_{field_name.upper()}"
        return os.getenv(env_var)


class DictLoader(StringLoader):
    """
    Used only for writing unit tests which require loaded config.
    """

    def __init__(self, config_dict: dict) -> None:
        self.config = config_dict

    def load_string(self, field_name: str) -> typing.Optional[str]:
        return self.config.get(field_name, None)
