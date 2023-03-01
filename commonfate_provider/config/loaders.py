import os
import boto3
from botocore.exceptions import ClientError
from dataclasses import dataclass
from abc import ABC, abstractmethod


class NotFoundError(Exception):
    """
    Raised if a config value is not found.
    """

    pass


class StringLoader(ABC):
    @abstractmethod
    def load_string(self, field_name: str) -> str:
        """
        Load the config string value.

        If the config value is not found, this method
        should return NotFoundError with a descriptive
        error message indicating where the loader looked
        for the value.
        """
        pass


@dataclass
class Secret:
    ref: str
    """a reference to where the secret can be found"""

    value: str
    """the actual contents of the secret"""


class SecretStringLoader(ABC):
    @abstractmethod
    def load_secret_string(self, field_name: str) -> Secret:
        """
        Load the config secret string value.

        If the config value is not found, this method
        should return NotFoundError with a descriptive
        error message indicating where the loader looked
        for the value.
        """
        pass


class EnvLoader(StringLoader):
    def load_string(self, field_name: str) -> str:
        """
        The field name is transformed to an env var in the following
        format - `PROVIDER_CONFIG_FIELD_NAME`

        For example, if the field is `api_url`, the env var will be
        `PROVIDER_CONFIG_API_URL`
        """
        env_var = f"PROVIDER_CONFIG_{field_name.upper()}"
        value = os.getenv(env_var)
        if value is None:
            raise NotFoundError(f"{env_var} environment variable is not set")

        return value


class DevEnvSecretLoader(SecretStringLoader):
    """
    For local development only. Not supported in any deployed provider runtimes.
    """

    def load_secret_string(self, field_name: str) -> Secret:
        """
        The field name is transformed to an env var in the following
        format - `PROVIDER_SECRET_FIELD_NAME`

        For example, if the field is `api_token`, the env var will be
        `PROVIDER_SECRET_API_TOKEN`
        """
        env_var = f"PROVIDER_SECRET_{field_name.upper()}"

        value = os.getenv(env_var)
        if value is None:
            raise NotFoundError(f"{env_var} environment variable is not set")

        return Secret(ref=f"env://{env_var}", value=value)


class DictLoader(StringLoader, SecretStringLoader):
    """
    Used only for writing unit tests which require loaded config.
    """

    def __init__(self, config_dict: dict) -> None:
        self.config = config_dict

    def load_string(self, field_name: str) -> str:
        value = self.config.get(field_name, None)
        if value is None:
            raise NotFoundError(f"{field_name} is not set in config_dict")

        return value

    def load_secret_string(self, field_name: str) -> Secret:
        val = self.config.get(field_name, None)
        if val is None:
            raise NotFoundError(f"secret {field_name} is not set in config_dict")

        return Secret(ref=f"dict://{field_name}", value=val)


class SSMSecretLoader(SecretStringLoader):
    """
    Secret Loader for AWS SSM
    """

    def load_secret_string(self, field_name: str) -> Secret:
        """
        The field name is transformed to an env var in the following
        format - `PROVIDER_SECRET_FIELD_NAME`

        For example, if the field is `api_token`, the env var will be
        `PROVIDER_SECRET_API_TOKEN`
        """
        env_var = f"PROVIDER_SECRET_{field_name.upper()}"

        secret_path = os.getenv(env_var)
        if secret_path is None:
            raise NotFoundError(f"{env_var} environment variable is not set")

        client = boto3.client("ssm")
        try:
            res = client.get_parameter(Name=secret_path, WithDecryption=True)

            return Secret(ref=f"{secret_path}", value=res["Parameter"]["Value"])

        except ClientError as e:
            if e.response["Error"]["Code"] == "ParameterNotFound":
                raise NotFoundError(
                    f"The AWS SSM parameter '{secret_path}' was not found"
                )
            else:
                raise e
