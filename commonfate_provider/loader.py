import typing
from commonfate_provider.provider import Provider


def load_provider_from_subclass() -> typing.Type[Provider]:
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

    return ProviderClass
