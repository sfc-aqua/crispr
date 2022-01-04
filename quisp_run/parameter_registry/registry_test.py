from .registry import ParameterRegistry, ParameterKind, Parameter


class TestParameter:
    def test_parameter_default_value_singular(self):
        p = Parameter[str](
            singular="config_ini_file",
            plural=None,
            kind=ParameterKind.BUILT_IN,
            default_value="config.ini",
            required=True,
        )
        assert p.validate()
        k, v = p.default_key_value()
        assert k == "config_ini_file"
        assert v == "config.ini"

    def test_parameter_default_value_both_singular_n_plural(self):
        p = Parameter[int](
            singular="num_buf",
            plural="num_bufs",
            kind=ParameterKind.PARAM,
            default_values=[5],
            required=True,
        )
        assert p.validate()
        k, v = p.default_key_value()
        assert k == "num_bufs"
        assert v == [5]

    def test_parameter_type(self):
        p = Parameter[int](
            singular="num_buf",
            plural="num_bufs",
            kind=ParameterKind.NETWORK_PARAM,
            default_values=[5],
            required=True,
        )
        assert p.validate_type("num_buf", "hoge") == False
        assert p.validate_type("num_buf", 123) == True
        assert p.validate_type("num_buf", [123]) == False
        assert p.validate_type("num_bufs", [123]) == True
        assert p.validate_type("num_bufs", [123, "hoge"]) == False


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


def init_registry() -> ParameterRegistry:
    registry = ParameterRegistry()
    registry.register(
        Parameter(
            singular="num_buf",
            plural="num_bufs",
            kind=ParameterKind.PARAM,
            default_value=[],
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
