from .registry import ParameterRegistry, ParameterKind, Parameter
import pytest


def test_registry():
    r = ParameterRegistry()
    r.find_by_name("title").default_value = None
    vars = r.create_default_config_vars()
    vars["config_ini_file"] = "test"
    vars["network_types"] = ["linear"]
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
        "link_type": "MIM",
        "config_ini_file": "config.ini",
    }
    is_valid = r.validate_config_vars(vars)
    assert is_valid


def test_cannot_register_same_parameter():
    r = ParameterRegistry()
    default_len = len(r.parameters)
    r.register(
        Parameter[int](
            singular="num_buf",
            plural="num_bufs",
            kind=ParameterKind.PARAM,
            default_values=[50],
            required=True,
        )
    )
    assert len(r.parameters) == default_len + 1
    r.register(
        Parameter[int](
            singular="num_buf",
            plural="num_bufs",
            kind=ParameterKind.PARAM,
            default_values=[50],
            required=True,
        )
    )
    assert len(r.parameters) == default_len + 1


def test_load_toml_file():
    toml_str = """
title = "hoge"

[parameter.num_buf]
plural = "num_bufs"
default_values = [5]
kind = "meta"
type = "int"
required = true
param_key = "beffers"

[parameter.num_node]
plural = "num_nodes"
default_values = [5]
kind = "param"
type = "int"
required = true
param_key = "nodes"
"""
    params = ParameterRegistry.extract_config(toml_str)
    r = ParameterRegistry()
    r.register_all(params)


def init_registry() -> ParameterRegistry:
    registry = ParameterRegistry()
    config_toml = """
title = "test config"

[parameter.num_buf]
plural = "num_bufs"
kind = "param"
type = "int"
required = true
default_values = [50]
param_key = "beffers"

[parameter.num_node]
plural = "num_nodes"
kind = "network_param"
type = "int"
default_values = [5]
required = true
param_key = "numNodes"

[parameter.network_type]
plural = "network_types"
kind = "built_in"
default_values = ["linear"]
required = true
param_key = "networkType"
type = "str"
options = ["linear"]

[parameter.link_type]
plural = "link_types"
kind = "network_param"
required = true
param_key = "connectionType"
type = "str"
options = ["MM", "MIM"]

[parameter.config_ini_file]
kind = "built_in"
required = true
param_key = ""
type = "str"
    """
    registry.register_all(ParameterRegistry.extract_config(config_toml))

    return registry
