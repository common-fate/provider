import importlib
import json
import pkgutil
from commonfate_provider import access, resources, target
from commonfate_provider.loader import load_provider
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
@click.option("--dir", default=".", help="Directory to the load the provider from")
def schema(dir):
    Provider = load_provider(dir)
    schema = {}

    # in future we'll handle multiple kinds of targets,
    # but for now, just get the first one
    target_kind = next(iter(access._ALL_TARGETS))
    target_class = access._ALL_TARGETS[target_kind]

    schema["target"] = target.export_schema(target_kind, target_class)

    schema["config"] = Provider.export_schema()
    schema["audit"] = resources.audit_schema()
    print(json.dumps(schema))


@click.group()
def cli():
    pass


cli.add_command(schema)

if __name__ == "__main__":
    cli()
