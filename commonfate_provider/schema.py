from commonfate_provider import access, namespace, resources, target, loader


def export_schema() -> dict:
    """
    Export a Provider schema, ready to be serialized in JSON format.
    """

    schema = {}

    Provider = namespace.get_provider()

    schema["target"] = target.export_schema()
    schema["config"] = Provider.export_schema()
    schema["audit"] = resources.audit_schema()

    return schema
