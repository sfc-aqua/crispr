from quisp_run.simulation import SimPlan, new_config_vars
from quisp_run.utils import console, error_console
from quisp_run.parameter_registry import registry


def define_param(*args, **kwargs):
    console.print(args, kwargs)
    return str


CONFIG_EVAL_ENV_GLOBALS = {
    "__builtins__": {
        "range": range,
        "list": list,
        "filter": filter,
        "map": map,
        "print": print,
        "Param": define_param,
    }
}


def parse_config(plan_source: str) -> SimPlan:
    console.print("[yellow]Parsing simulation plan...")
    config_vars = registry.create_default_config_vars()
    try:
        exec(
            plan_source,
            CONFIG_EVAL_ENV_GLOBALS,
            config_vars,
        )

    except Exception as e:
        error_console.print("\n[red]Failed to parse the config file")
        error_console.print_exception(max_frames=0)
        config_vars["error"] = e
        exit(1)
    plan = SimPlan(config_vars)
    return plan
