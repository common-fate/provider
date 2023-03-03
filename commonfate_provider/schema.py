from pkg_resources import get_distribution
from commonfate_provider import namespace, resources, target


def export_schema() -> dict:
    """
    Export a Provider schema, ready to be serialized in JSON format.
    """

    schema = {}

    Provider = namespace.get_provider()

    commonfateProviderCoreVerison = None
    try:
        commonfateProviderCoreVerison = get_distribution("commonfate_provider").version
    except:
        print("unable to determine the commonfate_provider package version")

    schema["target"] = target.export_schema()
    schema["config"] = Provider.export_schema()
    schema["audit"] = resources.audit_schema()
    schema["meta"] = {
        "schemaVersion": 1,
        "commonfateProviderCoreVersion": commonfateProviderCoreVerison,
    }

    return schema
