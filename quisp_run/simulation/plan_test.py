from quisp_run.simulation import SimPlan
from quisp_run.parameter_registry import init_registry, ParameterRegistry


def test_populate():
    registry = init_registry(ParameterRegistry())
    config_vars = registry.create_default_config_vars()
    config_vars["num_bufs"] = [4, 5, 6]
    config_vars["num_nodes"] = [1, 2, 3]
    config_vars["network_types"] = ["linear", "star"]
    config_vars["connection_types"] = ["MM"]
    config_vars["e2e_connection_enabled"] = True
    assert registry.validate_config_vars(config_vars)
    print(config_vars)
    plan = SimPlan(config_vars, registry)
    settings = plan.populate()
    # for s in sorted([str(s) for s in settings]):
    # print(s)
    assert len(settings) == 3 * 3 * 2
