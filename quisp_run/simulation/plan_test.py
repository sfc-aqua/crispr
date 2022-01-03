from quisp_run.simulation import SimPlan
from quisp_run.parameter_registry.registry import registry


def test_populate():
    config_vars = registry.create_default_config_vars()
    config_vars["num_bufs"] = [4, 5, 6]
    config_vars["num_nodes"] = [1, 2, 3]
    config_vars["network_types"] = ["linear", "star"]
    config_vars["connection_types"] = ["MM"]
    plan = SimPlan(config_vars)
    settings = plan.populate()
    # for s in sorted([str(s) for s in settings]):
    #     print(s)
    assert len(settings) == 3 * 3 * 2
