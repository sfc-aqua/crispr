import sys
from quisp_run.simulation import SimPlan, new_config_vars


def parse_config(plan_source: str) -> SimPlan:
    config_vars = new_config_vars()
    try:
        exec(
            plan_source,
            {
                "__builtins__": {
                    "range": range,
                    "list": list,
                    "filter": filter,
                    "map": map,
                }
            },
            config_vars,
        )
    except IndentationError as e:
        print(e, file=sys.stderr)
        config_vars["error"] = e
    except Exception as e:
        print("Unexpected error:", e, file=sys.stderr)
        config_vars["error"] = e

    plan = SimPlan(config_vars)
    return plan
