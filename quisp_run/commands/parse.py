import click
from quisp_run import config
from quisp_run.utils import console
from rich.prompt import Confirm


@click.command()
def parse_config():
    with open("simulation.plan", "rt") as f:
        source = f.read()
        sim_plan = config.parse_config(source)
        settings = sim_plan.populate()
        console.print(f"[green]{len(settings)} simulation settings populated.")
        console.print("\n[green]First Simulation Plan:")
        console.print("[magenta]name:", settings[0], settings[0].fields)
        if Confirm.ask("[green]Do you want to see the other simulation plans?", default=False):
            with console.pager():
                console.print(f"{len(settings)} simulation settings populated.")
                for s in settings:
                    console.print(s.fields)
