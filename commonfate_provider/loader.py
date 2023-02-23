import typing
from commonfate_provider.provider import Provider
from commonfate_provider.args import Args


def load_provider() -> typing.Tuple[typing.Type[Provider], typing.Type[Args]]:
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
