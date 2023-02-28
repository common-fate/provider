import importlib
import json
import os
import pkgutil
import sys
from commonfate_provider import config, loader
from commonfate_provider.runtime.aws_lambda import AWSLambdaRuntime
from commonfate_provider.schema import export_schema
import click


def import_submodules(package, recursive=True):
    """Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + "." + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


@click.command()
def schema():
    schema = export_schema()
    print(json.dumps(schema))


@click.command()
@click.argument("event")
def run(event):
    """
    Execute a provider.
    """
    cwd = os.getcwd()

    dirname = os.path.basename(cwd)
    parent_folder = os.path.abspath(os.path.join(dirname, "..", ".."))

    sys.path.append(parent_folder)
    import_submodules(dirname)

    Provider = loader.load_provider_from_subclass()
    provider = Provider()

    runtime = AWSLambdaRuntime(
        provider=provider,
        configurer=config.DEV_LOADER,
        name="",
        version="",
        publisher="",
    )
    event_json = json.loads(event)
    result = runtime.handle(event_json)
    print(result)


@click.group()
def cli():
    pass


cli.add_command(schema)
cli.add_command(run)

if __name__ == "__main__":
    cli()
