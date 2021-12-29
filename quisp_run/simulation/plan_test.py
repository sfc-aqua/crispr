from quisp_run.simulation import SimPlan, new_config_vars, SimSetting


def test_populate():
    config_vars = new_config_vars()
    config_vars["num_bufs"] = [4, 5, 6]
    config_vars["num_nodes"] = [1, 2, 3]
    config_vars["network_types"] = ["linear", "star"]
    plan = SimPlan(config_vars)
    settings = plan.populate()
    params = [
        (1, 4, "linear"),
        (1, 4, "star"),
        (1, 5, "linear"),
        (1, 5, "star"),
        (1, 6, "linear"),
        (1, 6, "star"),
        (2, 4, "linear"),
        (2, 4, "star"),
        (2, 5, "linear"),
        (2, 5, "star"),
        (2, 6, "linear"),
        (2, 6, "star"),
        (3, 4, "linear"),
        (3, 4, "star"),
        (3, 5, "linear"),
        (3, 5, "star"),
        (3, 6, "linear"),
        (3, 6, "star"),
    ]
    assert sorted(settings) == sorted(
        [
            SimSetting(
                config_ini_file="config/omnetpp.ini",
                **dict(zip(["num_node", "num_buf", "network_type"], p))
            )
            for p in params
        ]
    )
