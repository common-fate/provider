from commonfate_provider import namespace, provider


def validate_config(p: provider.Provider):
    all_validators = namespace.get_config_validators()
    for id, validator in all_validators.items():
        try:
            validator.func(p)
        except Exception as e:
            p.diagnostics.error(f"config validation {id} failed: {e}")
