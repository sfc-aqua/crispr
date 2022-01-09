from typing import Dict, Any
from schema import Schema, Optional, Or, SchemaError
from crispr.utils import error_console

PARAM_SCHEMA_SCHEMA = Schema(
    {
        "title": str,
        "parameter": {
            str: {
                "required": bool,
                "kind": Or("meta", "param", "network_param", "built_in"),
                Optional("param_key"): str,
                Optional("plural"): str,
                Optional("default_value"): Or(str, int, float, bool),
                Optional("default_values"): [str, int, float, bool],
                Optional("options"): [str, int, float, bool],
                "type": Or("str", "int", "float", "bool"),
            }
        },
    }
)


def validate_config(conf: Dict[str, Any]) -> bool:
    try:
        PARAM_SCHEMA_SCHEMA.validate(conf)
    except SchemaError as e:
        error_console.print("[red]Invalid Schema. Check your parameters.toml file")
        error_console.print(e)
        return False

    return True
