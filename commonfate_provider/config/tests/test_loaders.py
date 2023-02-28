import os
from commonfate_provider.config import loaders


def test_env_loader_works():
    loader = loaders.EnvLoader()
    os.environ["PROVIDER_CONFIG_MY_VALUE"] = "something"
    got = loader.load_string("my_value")

    assert got == "something"


def test_dev_env_secret_loader_works():
    loader = loaders.DevEnvSecretLoader()
    os.environ["PROVIDER_SECRET_MY_VALUE"] = "something"
    got = loader.load_string("my_value")

    assert got == "something"


def test_dict_loader_works():
    loader = loaders.DictLoader({"value": "something"})
    got = loader.load_string("value")

    assert got == "something"
