import pyarrow as pa

complex_schema = [
    pa.field(
        "metadata",
        pa.struct(
            [
                ("operation", pa.string()),
                ("publishedAt", pa.timestamp("ms")),
                ("sampleArray", pa.list_(pa.string())),
            ]
        ),
    ),
    pa.field(
        "example",
        pa.struct(
            [
                ("id", pa.string()),
                ("updatedAt", pa.timestamp("ns")),
                ("enabled", pa.bool_()),
                pa.field(
                    "Configuration",
                    pa.struct(
                        [
                            ("sampleInt", pa.int64()),
                            ("sampleTime", pa.string()),
                        ]
                    ),
                ),
                ("test-str", pa.string()),
            ]
        ),
    ),
]

simple_schema = [
    ("firstName", pa.string()),
    ("lastName", pa.string()),
    ("age", pa.int64()),
]

complex_array_schema = [
    pa.field(
        "data",
        pa.struct(
            [
                pa.field(
                    "id",
                    pa.list_(
                        pa.struct(
                            [
                                pa.field("name", pa.string()),
                                pa.field(
                                    "test_1",
                                    pa.list_(
                                        pa.struct([pa.field("name", pa.string())])
                                    ),
                                ),
                            ]
                        )
                    ),
                ),
            ]
        ),
    )
]
