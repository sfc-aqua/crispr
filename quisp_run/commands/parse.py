import click
from quisp_run.config import parse_config
from quisp_run.utils import console


@click.command()
def parse_config():
    with open("simulation.plan", "r") as f:
        source = f.read()
        sim_plan = parse_config(source)
        console.print(sim_plan.populate()[0])
