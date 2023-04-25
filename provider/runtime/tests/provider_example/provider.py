import provider
from provider import access, target


class MyProvider(provider.Provider):
    pass


@access.target()
class Target:
    pass
