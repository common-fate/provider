import typing
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod
from commonfate_provider import diagnostics


@dataclass
class Field:
    usage: typing.Optional[str] = None
    secret: bool = False


class String(Field):
    def set(self, val: str) -> None:
        self._value = val

    def get(self) -> str:
        return self._value


class ConfigLoader(ABC):
    @abstractmethod
    def load(self) -> dict:
        pass


class StringLoader(ConfigLoader):
    def __init__(self, config_json: str) -> None:
        self.config = config_json

    def load(self):
        return json.loads(self.config)


class DictLoader(ConfigLoader):
    def __init__(self, config_dict: dict) -> None:
        self.config = config_dict

    def load(self):
        return self.config


class NoopLoader(ConfigLoader):
    def load(self):
        return {}


class MethodNotImplemented(Exception):
    pass


class Provider(ABC):
    def __init__(self) -> None:
        self._internal_key = "default"

    def _cf_load_config(self, config_loader: ConfigLoader):
        """
        Built-in Provider method to load config from a ConfigLoader.
        """
        self.config_dict = config_loader.load()
        config_dict = config_loader.load()
        all_vars = [
            (k, v) for (k, v) in vars(self.__class__).items() if not k.startswith("__")
        ]
        for k, v in all_vars:
            if isinstance(v, String):
                val = config_dict.get(k, "")
                v.set(val=val)
                setattr(self, k, v)

    def _cf_validate_config(self) -> dict:
        """
        Built-in Provider method to validate config.
        """
        results = {}
        all_validators = _ALL_CONFIG_VALIDATORS.get(self._internal_key, {})
        for validator in all_validators.values():
            diags = diagnostics.Logs()
            try:
                validator.func(self, diags)
            except Exception as e:
                diags.error(str(e))

            results[validator.id] = {
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


def capabilities(_internal_key: str = "default") -> dict:
    return {"builtin": {}}


ConfigValidatorFunc = typing.Callable[[typing.Any, diagnostics.Logs], None]


@dataclass
class ConfigValidator:
    name: str
    id: str
    func: ConfigValidatorFunc


_ALL_CONFIG_VALIDATORS: typing.Dict[str, typing.Dict[str, ConfigValidator]] = {}
"""dict in the format {'default': {'id': {...}}"""


def config_validator(
    name: str,
    _internal_key: str = "default",
) -> typing.Callable[[ConfigValidatorFunc], ConfigValidatorFunc]:
    def actual_decorator(func: ConfigValidatorFunc):
        id = func.__name__
        cv = ConfigValidator(id=id, name=name, func=func)
        _ALL_CONFIG_VALIDATORS.setdefault(_internal_key, {})
        _ALL_CONFIG_VALIDATORS[_internal_key][id] = cv
        return func

    return actual_decorator
