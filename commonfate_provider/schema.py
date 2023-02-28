from commonfate_provider import access, namespace, resources, target, loader


def export_schema() -> dict:
    """
    Export a Provider schema, ready to be serialized in JSON format.
    """

    schema = {}

    # in future we'll handle multiple kinds of targets,
    # but for now, just get the first one
    target_kind = next(iter(access._ALL_TARGETS))
    target_class = access._ALL_TARGETS[target_kind]

    Provider = namespace.get_provider()

    schema["target"] = target.export_schema(target_kind, target_class)
    schema["config"] = Provider.export_schema()
    schema["audit"] = resources.audit_schema()

    return schema
