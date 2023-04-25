import sys
from os import path

import pytest

from provider import namespace


@pytest.fixture(autouse=True)
def fresh_namespace():
    yield
    namespace.clear()


def test_entrypoint_works():
    sys.path.append(path.join(path.dirname(__file__)))
    from provider.runtime import aws_lambda_entrypoint
