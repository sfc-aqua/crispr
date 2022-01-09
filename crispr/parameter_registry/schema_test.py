import pytest
from .schema import PARAM_SCHEMA_SCHEMA


def test_empty_schema():
    assert not PARAM_SCHEMA_SCHEMA.is_valid({})


def test_schema():
    PARAM_SCHEMA_SCHEMA.validate(
        {
            "title": "test",
            "parameter": {
                "test": {
                    "required": True,
                    "kind": "param",
                    "param_key": "test",
                    "type": "int",
                },
                "test2": {
                    "kind": "network_param",
                    "required": False,
                    "param_key": "test2",
                    "default_value": "test2",
                    "default_values": ["test2"],
                    "options": ["test2"],
                    "type": "str",
                },
            },
        }
    )
