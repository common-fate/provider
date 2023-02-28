import importlib
import json
import pkgutil
from commonfate_provider.schema import export_schema
import click


def import_submodules(package, rel_name=None, recursive=True):
    """Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package, rel_name)
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


@click.group()
def cli():
    pass


cli.add_command(schema)

if __name__ == "__main__":
    cli()
