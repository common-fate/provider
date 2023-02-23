import json
from commonfate_provider import resources
from commonfate_provider.loader import load_provider
import click


@click.command()
@click.option("--dir", default=".", help="Directory to the load the provider from")
def schema(dir):
    Provider, Args = load_provider(dir)
    schema = {}

    schema["config"] = Provider.export_schema()
    schema["audit"] = resources.audit_schema()
    schema["target"] = Args.export_schema()
    print(json.dumps(schema))


@click.group()
def cli():
    pass


cli.add_command(schema)

if __name__ == "__main__":
    cli()
