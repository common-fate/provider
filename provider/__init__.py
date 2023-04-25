import typing
from dataclasses import dataclass
from abc import ABC
from provider import diagnostics, namespace
from common_fate_schema.provider import v1alpha1


@dataclass
class Field:
    description: typing.Optional[str] = None
    secret: bool = False
    optional: bool = False


class String(Field):
    def set(self, val: str) -> None:
        self._value = val

    def get(self) -> str:
        return self._value


class Provider(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._safe_config = {}
        """
        Used internally by the provider library
        to represent a 'safe' configuration with
        any secrets censored out and replaced
        with references.
        """

        self.diagnostics = diagnostics.Logs()
        """
        User-facing log messages associated with
        a provider.

        If any error messages are logged,
        the provider will be marked as unhealthy.
        """

    def __init_subclass__(cls) -> None:
        namespace.register_provider(cls)
        return super().__init_subclass__()

    def healthy(self) -> bool:
        """
        Built-in method to determine whether the provider is
        healthy and able to receive requests.
        """
        return self.diagnostics.has_no_errors()

    def setup(self):
        """
        Provider-specific setup logic can be called here, such as creating API clients.
        """
        pass

    @classmethod
    def export_config_schema(cls) -> typing.Dict[str, v1alpha1.Config]:
        """
        Exports config variables defined in a Provider class
        to a dictionary.

        For example, if a Provider is defined as:
        ```
        class Provider(provider.Provider):
            url = provider.String()
        ```

        this method will produce a dictionary in the form:
        ```
        {"url": {"type": "string"}}
        ```
        """
        config_vars = {}
        all_vars = [(k, v) for (k, v) in vars(cls).items() if not k.startswith("__")]
        for k, v in all_vars:
            if type(v) == String:
                val: String = v

                config_vars[k] = v1alpha1.Config(
                    type="string", description=val.description, secret=val.secret
                )
        return config_vars


ConfigValidatorFunc = typing.Callable[[Provider], None]


@dataclass
class ConfigValidator:
    name: str
    func: ConfigValidatorFunc


def config_validator(
    name: str,
) -> typing.Callable[[ConfigValidatorFunc], ConfigValidatorFunc]:
    def actual_decorator(func: ConfigValidatorFunc):
        id = func.__name__
        cv = ConfigValidator(name=name, func=func)
        namespace.register_config_validator(id=id, config_validator=cv)
        return func

    return actual_decorator
