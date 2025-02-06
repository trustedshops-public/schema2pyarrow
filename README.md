Schema to pyarrow converter
===
[![GitHub License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://github.com/trustedshops/schema2pyarrow/blob/main/LICENSE)
[![pre-commit](https://img.shields.io/badge/%E2%9A%93%20%20pre--commit-enabled-success)](https://pre-commit.com/)

This library provides a tool for converting JSON Schema and AsyncAPI YAML schemas to PyArrow schemas.
It supports a wide range of data types and formats, including integers, floats, strings, booleans, arrays, and objects.

## When to use this library

- **Contract-First Data Engineering:** By using a schema-first approach, you can define the structure of your data before it is generated.
This ensures that all stakeholders agree on the format of the data, reducing errors and miscommunication.

- **Verify data format:** With this library, you can verify that the data you receive has the correct format and only process it in this format.
This prevents errors and ensures that your data pipeline is robust and reliable.

- **No false positives:** By using a schema to define the data types, you avoid the need for PyArrow to guess the data types.
This eliminates false positives and ensures that your data is processed correctly.

- **AsyncAPI support:** AsyncAPI is a well-established format for defining APIs and data formats.
This library supports AsyncAPI, making it easy to integrate with backend and platform teams that use this format.

- **JSON Schema support:** JSON Schema is a widely-used format for defining the structure of JSON data. This library supports JSON Schema, making it easy to integrate with existing JSON-based data pipelines
### Benefits
Using this library provides several benefits, including:

- **Improved data quality:** By verifying the format of your data, you can ensure that it is correct and consistent.
- **Reduced errors:** By avoiding false positives and ensuring that your data is processed correctly, you can reduce errors and improve the reliability of your data pipeline.
- **Increased efficiency:** By using a schema-first approach, you can improve the efficiency of your data pipeline and reduce the time spent on data processing and validation.
- **Better collaboration:** By using a well-established format like AsyncAPI, you can improve collaboration between teams and stakeholders, ensuring that everyone agrees on the format of the data.


## Installation

Install this package via pip:
```
pip install schema2pyarrow
```

## Development

To install this package in development mode use:
```
pip install -e .
```

We are always happy to get PRs and Issues.
Please look into our [contribution guidelines](CONTRIBUTING.md) for more details.


## Usage
The library provides several functions for converting schemas to PyArrow schemas. The main functions are:

- async_api_to_pyarrow_schema(schema): Converts an AsyncAPI YAML schema to a PyArrow schema.
- dict_to_pyarrow_schema(schema): Converts a JSON Schema dictionary to a PyArrow schema.

Here is an example of how to use the dict_to_pyarrow_schema function:

```python
import json
from pathlib import Path
from schema2pyarrow.pyarrow_converter import dict_to_pyarrow_schema

with open(Path("tests/sample_schemas/simple_schema.json")) as f:
    data = json.load(f)

pyarrow_schema = dict_to_pyarrow_schema(data)
```

Here is an example of how to use async_api_to_pyarrow_schema:

```python
import yaml
from pathlib import Path
from schema2pyarrow.pyarrow_converter import async_api_to_pyarrow_schema

with open(Path("tests/sample_schemas/complex_schema.yaml")) as f:
    data = yaml.safe_load(f)

pyarrow_schema = async_api_to_pyarrow_schema(data)
```

Once the schema is converted it can be used in pyarrow to load data:

```python
import pyarrow.json as paj
from pathlib import Path

arrow_table = paj.read_json(
    Path("sample_data.jsonl"),
    parse_options=paj.ParseOptions(
        explicit_schema=pyarrow_schema, unexpected_field_behavior="error"
    ),
)
```

## Using the builtin CLI
This library also includes a CLI tool that can be used to convert AsyncAPI YAML schemas to PyArrow schemas.

It can be used to:
- **Convert schemas:** convert multiple AsyncAPI YAML schemas to PyArrow schemas.
- **Check for errors:** check for errors in the schema and only report problematic schemas (useful for a CI).

### Usage
To use the CLI tool, run the following command:

```bash
schema2pyarrow path/*/**/*.yaml --check
```

### Options
The CLI tool has the following options:

- **--check:** Check for errors in the schema. Useful in a CI where you are only interested in the errors.
- **--metadata-path:** A path to an AsyncAPI yaml file that will be used as an additional metadata check.

### Providing custom schema data to the CLI
The CLI also enables users to check that a specific block of data must be part of the schema.
A common use case is to include a metadata block that contains at least a leading key and the last updated timestamp.

To run the CLI with an additional metadata check, use the following command:

```bash
schema2pyarrow tests/sample_schemas/complex_schema.yaml --metadata-path tests/sample_schemas/metadata.yaml
```

If the provided metadata in the metadata file is not present in the schema under test, the CLI will exit with an error.
Specifying a null datatype in the extra metadata is also supported.
This is useful when verifying the existence of a specific key, regardless of its type.

## More Use-Cases
This library offers a range of use cases beyond its primary functionality. Here are a few examples:

### Converting Airbyte Schema with PyArrow
Airbyte provides a schema, but it includes custom fields in its output.
To match the data produced by Airbyte, you need to surround the schema with these additional fields.
Here's how you can prepare your Airbyte schema:

- Fetch the schema from Airbyte
- Use the prepare_airbyte_schema function to add the necessary fields
- Convert the schema to PyArrow using dict_to_pyarrow_schema

Example:

```python
from schema2pyarrow.pyarrow_converter import dict_to_pyarrow_schema
from schema2pyarrow.airbyte_utils import prepare_airbyte_schema

schema = fetch_schema_from_airbyte()
converted_schema = dict_to_pyarrow_schema(prepare_airbyte_schema(schema))
```
