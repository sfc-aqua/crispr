import click
from crispr import config
from crispr.parameter_registry.registry import ParameterRegistry, init_registry
from crispr.utils import console
from rich.prompt import Confirm


@click.command()
@click.argument(
    "simulation_plan_file_path",
    type=click.Path(exists=True),
    required=False,
    default="simulation.plan",
)
def plan(simulation_plan_file_path: str):
    source = ""
    with open(simulation_plan_file_path, "rt") as f:
        source = f.read()
    registry = init_registry(ParameterRegistry())
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
