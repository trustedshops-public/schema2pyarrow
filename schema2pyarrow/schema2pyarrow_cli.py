from pathlib import Path
from typing import List

import typer
import yaml
from pyarrow.lib import ArrowTypeError
from yaml import SafeLoader
import pyarrow as pa

from schema2pyarrow.exceptions import (
    MissingMetadataError,
    SchemaValidationError,
    UnsupportedTypeError,
    UnsupportedFormatError,
)
from schema2pyarrow.pyarrow_converter import async_api_to_pyarrow_schema
from rich.console import Console

app = typer.Typer()


class SafeLineLoader(SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        # Add 1 so line numbering starts at 1
        mapping["__line__"] = node.start_mark.line + 1
        return mapping


def convert_to_pyarrow(
    path: Path, metadata_path: Path = None
) -> tuple[bool, list[str]]:
    with open(path) as f:
        data = yaml.load(f, Loader=SafeLineLoader)

    to_print = [
        "[green]-------------------------------[/green]",
        f"[bold green]{path}[/bold green]",
        "[green]-------------------------------[/green]",
    ]

    try:
        converted_schema = async_api_to_pyarrow_schema(data)

        if metadata_path:
            with open(metadata_path) as f:
                data = yaml.safe_load(f)
                test_schema = async_api_to_pyarrow_schema(data)

            verify_metadata(converted_schema, test_schema)

        to_print.append(str(converted_schema))

    except SchemaValidationError as e:
        details = e.args[0]

        to_print.append(
            "[bold red]Your asyncapi-config can not be validated.[/bold red]"
        )
        to_print.extend(
            print_error_message(details["message"], details["schema"].pop("__line__"))
        )
        to_print.append(f"[red]Problematic definition:[/red] {details['schema']}")
        return False, to_print

    except ArrowTypeError as type_error:
        details = type_error.args[0]

        to_print.append(
            "[bold red]Your asyncapi-config contains different metadata types than expected.[/bold red]"
        )
        to_print.append(details)
        return False, to_print

    except MissingMetadataError:
        to_print.append(
            "[bold red]Your asyncapi-config does not contain the required metadata.[/bold red]"
        )
        to_print.append(f"[red]It should at least contain:[/red] {test_schema}")
        return False, to_print

    except UnsupportedTypeError as e:
        details = e.args[0]

        to_print.append(
            "[bold red]Your asyncapi-config uses an unsupported type. [/bold red]"
        )
        to_print.extend(print_error_message(details["message"], details["line_nr"]))
        return False, to_print

    except UnsupportedFormatError as e:
        details = e.args[0]

        to_print.append(
            "[bold red]Your asyncapi-config uses an unsupported format. [/bold red]"
        )
        to_print.extend(print_error_message(details["message"], details["line_nr"]))
        return False, to_print

    return True, to_print


def print_error_message(message: str, line_nr: int):
    return [f"[red]Problematic line:[/red] {line_nr}", f"[red]{message} [/red]"]


@app.command()
def asyncapi_to_pyarrow(
    paths: List[Path],
    check: bool = False,
    metadata_path: Path = None,
):
    """
    Returns an error if there is at least one problematic schema.
    """

    conversion_successful = True

    console = Console()
    console._force_terminal = True

    for path in paths:
        successful, to_print = convert_to_pyarrow(path, metadata_path)
        if not successful:
            conversion_successful = False
        if not successful or not check:
            console.print(*to_print, sep="\n")

    if not conversion_successful:
        raise typer.Exit(1)

    if check:
        console.print("All schemas passed.")


def verify_metadata(converted_schema: pa.Schema, extra_schema: pa.Schema):
    """
    Checks if the schema contains the mandatory fields.
    """

    combined_schema = pa.unify_schemas([converted_schema, extra_schema])

    if combined_schema != converted_schema:
        raise MissingMetadataError


if __name__ == "__main__":
    app()
