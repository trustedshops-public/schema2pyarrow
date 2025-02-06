import json
from pathlib import Path

import pyarrow as pa
import yaml

from schema2pyarrow.pyarrow_converter import (
    async_api_to_pyarrow_schema,
    dict_to_pyarrow_schema,
    find_event,
)
from tests.sample_schemas.example_schemas import (
    simple_schema,
    complex_schema,
    complex_array_schema,
)


def path(name) -> Path:
    return Path(Path(__file__).parent.resolve(), "sample_schemas", name)


def test_asyncapi_to_pyarrow_schema():
    with open(path("complex_schema.yaml")) as f:
        data = yaml.safe_load(f)

    pyarrow_schema = async_api_to_pyarrow_schema(data)

    assert pyarrow_schema == pa.schema(complex_schema)


def test_simple_json_to_pyarrow_schema():
    with open(path("simple_schema.json")) as f:
        data = json.load(f)

    pyarrow_schema = dict_to_pyarrow_schema(data)

    assert pyarrow_schema == pa.schema(simple_schema)


def test_complex_array_to_pyarrow():
    """
    Test if the converter can handle cases where the types are arrays containing objects.
    These object types can then also contain arrays of objects.
    """
    with open(path("complex_array_schema.yaml")) as f:
        data = yaml.safe_load(f)

    pyarrow_schema = async_api_to_pyarrow_schema(data)

    assert pyarrow_schema == pa.schema(complex_array_schema)


def test_find_event_one_of():
    schema = {
        "channels": {
            "channel_name": {
                "publish": {
                    "message": {"oneOf": [{"type": "object"}, {"type": "array"}]}
                }
            }
        }
    }
    expected_result = [{"type": "object"}, {"type": "array"}]
    assert find_event(schema) == expected_result


def test_find_event_messages():
    schema = {
        "channels": {
            "channel_name": {
                "messages": {
                    "__line__": {},
                    "message1": {"type": "object"},
                    "message2": {"type": "array"},
                }
            }
        }
    }
    expected_result = [{"type": "object"}, {"type": "array"}]
    assert find_event(schema) == expected_result
