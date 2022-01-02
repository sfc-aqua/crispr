from quisp_run.simulation import SimPlan, new_config_vars, SimSetting


def test_populate():
    config_vars = new_config_vars()
    config_vars["num_bufs"] = [4, 5, 6]
    config_vars["num_nodes"] = [1, 2, 3]
    config_vars["network_types"] = ["linear", "star"]
    config_vars["connection_types"] = ["MM"]
    plan = SimPlan(config_vars)
    settings = plan.populate()
