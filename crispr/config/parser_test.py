import pytest
from crispr.config.parser import parse_config
from crispr.parameter_registry import ParameterRegistry, init_registry


def test_empty_plan():
    plan_source = ""
    with pytest.raises(SystemExit) as e:
        parse_config(plan_source, init_registry(ParameterRegistry()))
    assert e.value.code == 1


def test_simple_plan():
    plan_source = """
# simulation plan
title = "example plan"
num_bufs = [i for i in range(5, 100)]
num_nodes = [10, 20, 30, 40, 50]
network_types = ["linear"]
    """
    plan = parse_config(plan_source, ParameterRegistry())
    assert plan["title"] == "example plan"


def test_parse_indentation_error():
    plan_source = """
# simulation plan
title = "example plan"
    num_bufs = [i for i in range(5, 100)]
num_nodes = [10, 20, 30, 40, 50]
network_types = ["linear"]
    """
    plan = None
    try:
        plan = parse_config(plan_source, ParameterRegistry())
    except BaseException as e:
        assert e is not None
        assert isinstance(e, SystemExit)
    assert plan is None
