import typing
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod
from commonfate_provider import diagnostics
from commonfate_provider.dataclass import ModelMeta


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


@dataclass
class GrantResult:
    access_instructions: typing.Optional[str] = None
    """
    Instructions on how to access the entitlements.
    Common Fate will display these to the user upon a successful Access Request.
    """


class Provider(ABC):
    def __init__(
        self,
        config_loader: ConfigLoader,
    ) -> None:
        self._internal_key = "default"
        self.config_dict = config_loader.load()
        config_dict = config_loader.load()
        all_vars = [
            (k, v) for (k, v) in vars(self.__class__).items() if not k.startswith("__")
        ]
        for k, v in all_vars:
            if isinstance(v, String):
                val = config_dict[k]
                v.set(val=val)
                setattr(self, k, v)

    def validate_config(self) -> dict:
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
                val:String = v
                
                config_vars[k] = {"type": "string", "usage": val.usage, "secret":val.secret}
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


GrantValidatorFunc = typing.Callable[[typing.Any, str, typing.Any], None]


@dataclass
class GrantValidator:
    name: str
    id: str
    func: GrantValidatorFunc


_ALL_GRANT_VALIDATORS: typing.Dict[str, typing.Dict[str, GrantValidator]] = {}


def grant_validator(
    name: str,
    _internal_key: str = "default",
) -> typing.Callable[[GrantValidatorFunc], GrantValidatorFunc]:
    def actual_decorator(func: GrantValidatorFunc):
        id = func.__name__
        cv = GrantValidator(id=id, name=name, func=func)
        _ALL_GRANT_VALIDATORS.setdefault(_internal_key, {})
        _ALL_GRANT_VALIDATORS[_internal_key][id] = cv
        return func

    return actual_decorator


GrantFunc = typing.Callable[[typing.Any, str, typing.Any], typing.Optional[GrantResult]]
_GRANT: typing.Dict[str, GrantFunc] = {}


def _get_grant_func(_internal_key: str = "default"):
    return _GRANT[_internal_key]


def grant(
    _internal_key: str = "default",
) -> typing.Callable[[GrantFunc], GrantFunc]:
    # _internal_key is used for testing purposes, and allows
    # multiple independent decorators to be registered in a single test file
    def actual_decorator(func: GrantFunc):
        _GRANT[_internal_key] = func
        return func

    return actual_decorator


RevokeFunc = typing.Callable[[typing.Any, str, typing.Any], None]


_REVOKE: typing.Dict[str, RevokeFunc] = {}


def revoke(
    _internal_key: str = "default",
) -> typing.Callable[[RevokeFunc], RevokeFunc]:
    # _internal_key is used for testing purposes, and allows
    # multiple independent decorators to be registered in a single test file
    def actual_decorator(func: RevokeFunc):
        _REVOKE[_internal_key] = func
        return func

    return actual_decorator


def _get_revoke_func(_internal_key: str = "default"):
    return _REVOKE[_internal_key]
