import click
from crispr import config
from crispr.parameter_registry.registry import ParameterRegistry, init_registry
from crispr.utils import console
from crispr.constants import CRISPR_TEMPALTE_PARAMETERS_TOML
from rich.prompt import Confirm


@click.command()
@click.option(
    "--parameter-schema",
    type=click.Path(exists=True),
    default=CRISPR_TEMPALTE_PARAMETERS_TOML,
    help="path to the parameter schema toml file",
)
@click.argument(
    "simulation_plan_file_path",
    type=click.Path(exists=True),
    required=False,
    default="simulation.plan",
)
def plan(simulation_plan_file_path: str, parameter_schema: str):
    source = ""
    with open(simulation_plan_file_path, "rt") as f:
        source = f.read()
    param_toml = ""
    with open(parameter_schema, "rt") as f:
        param_toml = f.read()
    registry = ParameterRegistry()
    registry.load_from_toml(param_toml)
    sim_plan = config.parse_config(source, registry)
    settings = sim_plan.populate()
    console.print(f"[green]{len(settings)} simulation settings populated.")
    console.print("\n[green]First Simulation Plan:")
    console.print("[magenta]name:", settings[0], settings[0].fields)
    if Confirm.ask("[green]Do you want to see the other simulation plans?", default=False):
        with console.pager():
            console.print(f"{len(settings)} simulation settings populated.")
            for s in settings:
                console.print(s.fields)
