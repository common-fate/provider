from provider import provider, access, target


class MyProvider(provider.Provider):
    pass


@access.target()
class Target:
    pass
