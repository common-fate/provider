import typing
from pkg_resources import get_distribution
from provider import namespace, resources, target
from common_fate_schema.provider import v1alpha1


def export_schema(id: typing.Optional[v1alpha1.ID] = None) -> v1alpha1.Schema:
    """
    Export a Provider schema, ready to be serialized in JSON format.
    """

    Provider = namespace.get_provider()

    framework_version = None
    try:
        framework_version = get_distribution("provider").version
    except Exception:
        pass

    config_schema = Provider.export_config_schema()
    resources_schema = resources.export_schema()

    targets = target.export_schema()

    schema = v1alpha1.Schema(
        id=id,
        targets=targets,
        config=config_schema,
        resources=resources_schema,
        meta=v1alpha1.Meta(framework=framework_version),
    )

    return schema
