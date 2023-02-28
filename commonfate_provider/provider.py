import typing
from dataclasses import dataclass
from abc import ABC
from commonfate_provider import diagnostics, namespace


@dataclass
class Field:
    usage: typing.Optional[str] = None
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

    def __init_subclass__(cls) -> None:
        namespace.register_provider(cls)
        return super().__init_subclass__()

    def _cf_validate_config(self) -> dict:
        """
        Built-in Provider method to validate config.
        """
        results = {}
        all_validators = namespace.get_config_validators()
        for id, validator in all_validators.items():
            diags = diagnostics.Logs()
            try:
                validator.func(self, diags)
            except Exception as e:
                diags.error(str(e))

            results[id] = {
                "logs": [l.__dict__ for l in diags.logs],
                "success": diags.succeeded(),
            }
        return results

    def setup(self):
        """
        Provider-specific setup logic can be called here, such as creating API clients.
        """
        pass

    @classmethod
    def export_schema(cls) -> dict:
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

                config_vars[k] = {
                    "type": "string",
                    "usage": val.usage,
                    "secret": val.secret,
                }
        return config_vars


ConfigValidatorFunc = typing.Callable[[typing.Any, diagnostics.Logs], None]


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
