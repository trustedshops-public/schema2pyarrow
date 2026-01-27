def get_value_by_path(d: dict, async_path: str) -> dict:
    """Retrieves a nested value from a dictionary using a path string.

    The path string should be in the format "#/key1/key2/..." and will be split into keys to traverse the dictionary.
    If any key in the path is not found, a ValueError is raised.
    """
    keys = async_path.lstrip("#/").split("/")

    for part in keys:
        if part:
            d = d.get(part)
            if d is None:
                raise ValueError(f"Path {'/'.join(keys)} not found.")

    return d


def resolve_internal_refs(data: dict | list, root: dict) -> dict | list[dict]:
    """
    Resolve ref-references. This only works if the references are resolved in the same file.
    """
    if isinstance(data, dict):
        if "$ref" in data:
            ref_path = data["$ref"]
            return get_value_by_path(root, ref_path)

        return {key: resolve_internal_refs(value, root) for key, value in data.items()}

    elif isinstance(data, list):
        return [resolve_internal_refs(item, root) for item in data]

    return data


def recursive_resolve_refs(schema: dict) -> dict | list[dict]:
    """
    Recursively resolves the schema until no $refs are present.
    This is when the schema stabilizes and no changes happen anymore.
    """
    origin_schema = schema

    previous_schema = None
    while previous_schema != schema:
        previous_schema = schema
        schema = resolve_internal_refs(schema, origin_schema)
    return schema
