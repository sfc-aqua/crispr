from .registry import ParameterRegistry, ParameterKind, Parameter
import pytest


def test_registry():
    r = ParameterRegistry()
    r.register(
        Parameter[str](
            singular="title",
            plural=None,
            kind=ParameterKind.META,
            default_value=None,
            required=True,
        )
    )
    vars = r.create_default_config_vars()
    assert "title" in vars
    assert vars["title"] is None
    is_valid = r.validate_config_vars(vars)
    assert not is_valid
    vars["title"] = "test"
    is_valid = r.validate_config_vars(vars)
    assert is_valid


def test_validate_config_vars():
    r = init_registry()
    vars = {
        "num_bufs": [5],
        "num_nodes": [5],
        "title": "test",
        "network_type": "linear",
        "connection_type": "MIM",
        "config_ini_file": "config.ini",
    }
    is_valid = r.validate_config_vars(vars)
    assert is_valid


def test_cannot_register_same_parameter():
    r = ParameterRegistry()
    assert len(r.parameters) == 0
    print(r.parameters)
    r.register(
        Parameter[int](
            singular="num_buf",
            plural="num_bufs",
            kind=ParameterKind.PARAM,
            default_values=[50],
            required=True,
        )
    )
    assert len(r.parameters) == 1
    r.register(
        Parameter[int](
            singular="num_buf",
            plural="num_bufs",
            kind=ParameterKind.PARAM,
            default_values=[50],
            required=True,
        )
    )
    assert len(r.parameters) == 1


def init_registry() -> ParameterRegistry:
    registry = ParameterRegistry()
    registry.register(
        Parameter[int](
            singular="num_buf",
            plural="num_bufs",
            kind=ParameterKind.PARAM,
            default_values=[50],
            required=True,
        )
    )
    registry.register(
        Parameter[int](
            singular="num_node",
            plural="num_nodes",
            kind=ParameterKind.NETWORK_PARAM,
            default_values=[5],
            required=True,
        )
    )
    registry.register(
        Parameter[str](
            singular="network_type",
            plural="network_types",
            kind=ParameterKind.BUILT_IN,
            default_value="linear",
            required=True,
            options=["linear"],
        )
    )
    registry.register(
        Parameter[str](
            singular="connection_type",
            plural="connection_types",
            kind=ParameterKind.NETWORK_PARAM,
            default_value=None,
            required=True,
            options=["MIM", "MM"],
        )
    )
    registry.register(
        Parameter[str](
            singular="config_ini_file",
            plural=None,
            kind=ParameterKind.BUILT_IN,
            default_value="",
            required=True,
        )
    )
    return registry
