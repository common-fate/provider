import typing
import toml
from commonfate_provider.provider import Provider
from commonfate_provider.args import Args
import importlib


def load_provider() -> typing.Tuple[typing.Type[Provider], typing.Type[Args]]:
    """
    Loads the Common Fate Provider by reading the provider.toml file.
    This method dynamically instantiates the provider class.
    """
    config = toml.load("provider/provider.toml")

    language = config["language"]

    if language != "python3.9":
        # this wrapping code is written in Python, so we can only handle
        # Providers written in Python.
        raise Exception(f"invalid language: {language}")

    provider_class = load_class(config["python"]["class"])
    arg_class = load_class(config["python"]["arg_schema"])
    return (provider_class, arg_class)


def load_class(path: str):
    """
    Dynamically loads a class. The path argument is the path
    to the class in the format 'module.ClassName'
    """
    components = path.split(".")  # [module, ClassName]

    module_path = "provider." + ".".join(components[:-1])  # provider.module
    module = importlib.import_module(module_path)
    class_name = components[-1]  # ClassName
    my_class = getattr(module, class_name)
    return my_class
