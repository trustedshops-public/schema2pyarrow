import pyarrow as pa
from pyarrow import Field
from schema2pyarrow.exceptions import (
    SchemaValidationError,
    UnsupportedTypeError,
    UnsupportedFormatError,
)


def map_format(field_format: str, line_nr: int) -> pa.Field:
    if field_format == "int32":
        return pa.int32()
    elif field_format == "int64":
        return pa.int64()
    elif field_format == "float":
        return pa.float32()
    elif field_format == "double":
        return pa.float64()
    elif (
        field_format == "byte" or field_format == "binary" or field_format == "password"
    ):
        return pa.string()
    elif field_format == "date":
        return pa.string()
    elif field_format == "uuid" or field_format == "UUID":
        # currently pyarrow does not natively support UUID
        return pa.string()
    elif field_format == "datetime" or field_format == "date-time":
        return pa.timestamp("ms")
    elif field_format == "datetime[us]" or field_format == "date-time[us]":
        return pa.timestamp("us")
    elif field_format == "datetime[s]" or field_format == "date-time[s]":
        return pa.timestamp("s")
    elif field_format == "datetime[ms]" or field_format == "date-time[ms]":
        return pa.timestamp("ms")
    elif field_format == "datetime[ns]" or field_format == "date-time[ns]":
        return pa.timestamp("ns")
    elif field_format == "time":
        return pa.time32("s")
    elif field_format == "^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]Z$":
        # time data is only allowed as seconds
        return pa.string()
    else:
        raise UnsupportedTypeError(
            {"message": f"Unsupported format: {field_format}", "line_nr": line_nr}
        )


def map_datatypes(
    field_type: str, field_format: str, field_example: str, line_nr: int
) -> pa.Field:
    if field_format:
        return map_format(field_format, line_nr)

    if field_type == "string":
        return pa.string()
    elif field_type == "float":
        return pa.float64()
    elif field_type == "integer":
        return pa.int64()
    elif field_type == "number":
        if isinstance(field_example, int):
            return pa.int64()
        if isinstance(field_example, float):
            return pa.float64()
    elif field_type == "boolean":
        return pa.bool_()
    elif field_type is None:
        return pa.null()
    else:
        raise UnsupportedFormatError(
            {"message": f"Unsupported type: {field_type}", "line_nr": line_nr}
        )


def extract_field_properties(field_properties: dict) -> tuple:
    field_type = field_properties.get("type")
    if isinstance(field_type, list):
        # airbyte schema creates types of this structure: ['string', 'null']
        for subtype in field_type:
            if subtype != "null":
                field_type = subtype

    return (
        field_type,
        field_properties.get("format"),
        field_properties.get("example"),
        field_properties.get("__line__"),
    )


def find_event(schema: dict) -> list:
    messages = []

    for channel_name, channel_data in schema.get("channels", {}).items():
        if channel_name == "__line__":
            continue

        # support the publish.message.0 syntax with multiple messages
        if "messages" in channel_data:
            for publish_name, message_def in channel_data["messages"].items():
                if publish_name == "__line__":
                    continue
                messages.append(message_def)
            continue

        message = channel_data["publish"]["message"]

        if not message:
            continue

        # oneOf is used to provide lists of message-schemas
        # this is a fallback if the oneOf syntax is not used
        if "oneOf" in message:
            messages.extend(message["oneOf"])
        else:
            messages.append(message)

    return messages


def get_value_by_path(d: dict, async_path: str) -> dict:
    keys = async_path.lstrip("#/").split("/")

    for part in keys:
        if part:
            d = d.get(part)
            if d is None:
                raise ValueError(f"Path {'/'.join(keys)} not found.")

    return d


def async_api_to_pyarrow_schema(schema: dict) -> pa.Schema:
    origin_schema = schema

    # recursively resolve the schema until no $refs are present
    # this is when the schema stabilizes and no changes happen anymore
    previous_schema = None
    while previous_schema != schema:
        previous_schema = schema
        schema = resolve_internal_refs(schema, origin_schema)

    t = find_event(schema)

    # if there are multiple schemas allowed, then we have to union them here
    schemas = []
    for message_schema in t:
        converted_message_schema = dict_to_pyarrow_schema(message_schema["payload"])

        schemas.append(converted_message_schema)

    return pa.unify_schemas(schemas)


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


def dict_to_pyarrow_schema(schema: dict) -> pa.schema:
    """
    This is the wrapper for the recursive _dict_to_pyarrow_schema function.
    """

    return pa.schema(_dict_to_pyarrow_schema(schema))


def _dict_to_pyarrow_schema(schema: dict) -> list[Field]:
    """
    This function accepts a schema as a dictionary (either parsed from JSON Schema or AsyncAPI YAML)
    and will convert it to a valid pyarrow schema
    """

    pyarrow_fields = []
    schema_iteration = [schema]

    if "allOf" in schema:
        schema_iteration = schema["allOf"]

    for s in schema_iteration:
        if "properties" in s:
            fields = s.get("properties").items()
        elif "additionalProperties" in s:
            fields = s.get("additionalProperties").get("properties").items()
        else:
            raise SchemaValidationError(
                {
                    "message": "Please further define contents of the object type via 'properties'.",
                    "schema": s,
                }
            )

        for field_name, field_properties in fields:
            # the __line__ field is used for reporting the problematic line and should not be analyzed
            if field_name == "__line__":
                continue

            field_type, field_format, field_example, line_nr = extract_field_properties(
                field_properties
            )

            if isinstance(field_type, list):
                # airbyte schema creates types of this structure: ['string', 'null']
                for subtype in field_type:
                    if subtype != "null":
                        field_type = subtype

            if field_type == "array":
                if "items" not in field_properties:
                    raise SchemaValidationError(
                        {
                            "message": "Please further define contents of your array type via 'items'.",
                            "schema": field_properties,
                        }
                    )

                if (
                    field_properties["items"]["type"] == "object"
                    or "object" in field_properties["items"]["type"]
                ):
                    resolved_object = _dict_to_pyarrow_schema(field_properties["items"])
                    pyarrow_type = pa.list_(pa.struct(resolved_object))

                else:
                    elem_type = map_datatypes(
                        *extract_field_properties(field_properties["items"])
                    )
                    pyarrow_type = pa.list_(elem_type)
            elif field_type == "object":
                pyarrow_type = _dict_to_pyarrow_schema(field_properties)
            elif "allOf" in field_properties:
                pyarrow_type = []
                for message in field_properties["allOf"]:
                    for pyarrow_field in _dict_to_pyarrow_schema(message):
                        pyarrow_type.append(pyarrow_field)
            else:
                pyarrow_type = map_datatypes(
                    field_type, field_format, field_example, line_nr
                )

            if pyarrow_type:
                if isinstance(pyarrow_type, list):
                    pyarrow_field = pa.field(field_name, pa.struct(pyarrow_type))
                    pyarrow_fields.append(pyarrow_field)
                else:
                    pyarrow_field = pa.field(field_name, pyarrow_type)
                    pyarrow_fields.append(pyarrow_field)

    return pyarrow_fields
