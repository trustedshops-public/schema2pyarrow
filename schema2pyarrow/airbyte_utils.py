def prepare_airbyte_schema(schema: dict) -> dict:
    """
    Airbyte provides a schema, but it also provides some custom fields.

    These fields are attached to the schema here, when data is read from airbyte the schemas match exactly.
    """

    airbyte_extracted_at_string = {"_airbyte_extracted_at": {"type": "string"}}
    airbyte_extracted_at = {"_airbyte_extracted_at": {"type": "integer"}}
    airbyte_properties = {
        "_airbyte_raw_id": {"type": "string"},
        "_airbyte_generation_id": {"type": "integer"},
        "_airbyte_meta": {
            "type": "object",
            "properties": {
                "changes": {"type": "array", "items": {"type": "string"}},
                "sync_id": {"type": "integer"},
            },
        },
    }

    new_schema = {
        "type": "object",
        "properties": {
            **airbyte_properties | airbyte_extracted_at,
            "_airbyte_data": {
                "type": schema["type"],
                "properties": schema["properties"]
                | airbyte_properties
                | airbyte_extracted_at_string,
            },
        },
    }

    return new_schema
