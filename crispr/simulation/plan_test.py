from crispr.simulation import SimPlan
from crispr.parameter_registry import init_registry, ParameterRegistry
from crispr.constants import CRISPR_TEMPALTE_PARAMETERS_TOML


def test_populate():
    toml = ""
    with open(CRISPR_TEMPALTE_PARAMETERS_TOML, "rt") as f:
        toml = f.read()
    registry = ParameterRegistry()
    registry.load_from_toml(toml)
    config_vars = registry.create_default_config_vars()
    config_vars["num_bufs"] = [4, 5, 6]
    config_vars["num_nodes"] = [1, 2, 3]
    config_vars["network_types"] = ["linear", "star"]
    config_vars["connection_types"] = ["MM"]
    config_vars["e2e_connection_enabled"] = True
    config_vars["title"] = "test"
    config_vars["link_tomography_enabled"] = True
    config_vars["num_purification_iteration"] = 1
    config_vars["num_measure"] = 0
    config_vars["number_of_bellpair"] = 0
    config_vars["purification_type"] = 1001
    config_vars["lone_initiator_addr"] = 0
    config_vars["traffic_pattern_index"] = 0
    assert registry.validate_config_vars(config_vars)
    print(config_vars)
    plan = SimPlan(config_vars, registry)
    settings = plan.populate()

    for s in sorted([str(s) for s in settings]):
        print(s)
    assert len(settings) == 3 * 3 * 2
