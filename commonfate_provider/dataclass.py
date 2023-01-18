import abc
from typing_extensions import dataclass_transform
from dataclasses import dataclass


@dataclass_transform()
class ModelMeta(type):
    def __init_subclass__(
        cls,
        *,
        init: bool = True,
        frozen: bool = False,
        eq: bool = True,
        order: bool = True,
    ):
        return dataclass(cls)


class AbstractModelMeta(ModelMeta, abc.ABCMeta):
    pass
