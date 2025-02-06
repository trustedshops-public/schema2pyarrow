class MissingMetadataError(Exception):
    """Raised when a required metadata is missing"""


class SchemaValidationError(Exception):
    """Raised when a schema is invalid"""


class UnsupportedTypeError(Exception):
    """Raised when a schema contains an unsupported type"""


class UnsupportedFormatError(Exception):
    """Raised when a schema contains an unsupported format"""
