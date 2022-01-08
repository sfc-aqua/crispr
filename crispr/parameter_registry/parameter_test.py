from .parameter import ParameterKind, Parameter


def test_parameter_default_value_singular():
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


def test_parameter_default_value_both_singular_n_plural():
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


def test_parameter_type_int():
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
    assert p.is_number()
    assert not p.is_bool()


def test_parameter_type_bool():
    p = Parameter[bool](
        singular="num_buf",
        plural="num_bufs",
        kind=ParameterKind.NETWORK_PARAM,
        default_values=[True, False],
        required=True,
    )
    assert p.validate_type("num_buf", "hoge") == False
    assert p.validate_type("num_buf", 123) == False
    assert p.validate_type("num_buf", [123]) == False
    assert p.validate_type("num_bufs", [123]) == False
    assert p.validate_type("num_bufs", [123, "hoge"]) == False
    assert not p.is_number()
    assert p.is_bool()


def test_equality():
    p = Parameter[int](
        singular="num_buf",
        plural="num_bufs",
        kind=ParameterKind.NETWORK_PARAM,
        default_values=[5],
        required=True,
    )
    p2 = Parameter[int](
        singular="num_buf",
        plural="num_bufs",
        kind=ParameterKind.NETWORK_PARAM,
        default_values=[5],
        required=True,
    )
    assert p == p2
    p2.required = False
    assert p != p2
