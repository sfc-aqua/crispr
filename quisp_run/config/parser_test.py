from quisp_run.config.parser import parse_config


def test_empty_plan():
    plan_source = ""
    plan = parse_config(plan_source)
    assert plan["title"] == ""


def test_simple_plan():
    plan_source = """
# simulation plan
title = "example plan"
num_bufs = [i for i in range(5, 100)]
num_nodes = [10, 20, 30, 40, 50]
network_types = ["linear"]
    """
    plan = parse_config(plan_source)
    assert plan["title"] == "example plan"


def test_parse_indentation_error():
    plan_source = """
# simulation plan
title = "example plan"
    num_bufs = [i for i in range(5, 100)]
num_nodes = [10, 20, 30, 40, 50]
network_types = ["linear"]
    """
    plan = parse_config(plan_source)

    assert plan["title"] == ""
    assert isinstance(plan["error"], IndentationError)
