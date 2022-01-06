from quisp_run.simulation import SimPlan
from quisp_run.utils import console, error_console
from quisp_run.parameter_registry import ParameterRegistry


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


def parse_config(plan_source: str, registry: ParameterRegistry) -> SimPlan:
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

    if not registry.validate_config_vars(config_vars):
        error_console.print("[red]Invalid configuration")
        exit(1)
    plan = SimPlan(config_vars, registry)
    return plan
