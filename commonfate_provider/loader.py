import importlib
import os
import typing
from commonfate_provider.provider import Provider
from commonfate_provider.args import Args
import toml


def load_provider(
    cwd: str = "",
) -> typing.Tuple[typing.Type[Provider], typing.Type[Args]]:
    """
    Loads the Common Fate Provider by reading the provider.toml file.
    This method dynamically instantiates the provider class.
    """
    l = os.path.join(cwd, "provider.toml")
    config = toml.load(l)

    language = config["language"]

    if language != "python3.9":
        # this wrapping code is written in Python, so we can only handle
        # Providers written in Python.
        raise Exception(f"invalid language: {language}")

    provider_class = load_class(cwd, config["python"]["class"])
    arg_class = load_class(cwd, config["python"]["arg_schema"])
    return (provider_class, arg_class)


def load_class(cwd: str, path: str):
    """
    Dynamically loads a class. The path argument is the path
    to the class in the format 'module.ClassName'
    """
    components = path.split(".")  # [module, ClassName]
    modulePathWithinProviderFolder = "/".join(components[:-1]) + ".py"

    # Import the module using an absolute path to the python file containing the Provider class
    spec = importlib.util.spec_from_file_location(
        "provider", os.path.join(cwd, modulePathWithinProviderFolder)
    )
    # Loading the module

    if spec is None or spec.loader is None:
        raise Exception("expected spec and spec.loader not to be None")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class_name = components[-1]  # ClassName
    my_class = getattr(module, class_name)
    return my_class


def load_provider_from_subclass() -> (
    typing.Tuple[typing.Type[Provider], typing.Type[Args]]
):
    """
    Loads the Common Fate Provider.
    This method dynamically instantiates the provider class.
    """
    classes = Provider.__subclasses__()

    if len(classes) == 0:
        raise Exception(
            f"could not find a Provider class. Usually this means that the Provider has been incorrectly packaged. Please report this issue to the provider developer."
        )

    if len(classes) > 1:
        raise Exception(
            f"only 1 Provider class is supported but found {len(classes)}: {[cl.__name__ for cl in classes]}"
        )

    ProviderClass = classes[0]

    arg_classes = Args.__subclasses__()

    if len(arg_classes) == 0:
        raise Exception(
            f"could not find a Provider class. Usually this means that the Provider has been incorrectly packaged. Please report this issue to the provider developer."
        )

    if len(arg_classes) > 1:
        raise Exception(
            f"only 1 Arg class is supported but found {len(arg_classes)}: {[cl.__name__ for cl in arg_classes]}"
        )

    ArgClass = arg_classes[0]

    return (ProviderClass, ArgClass)
