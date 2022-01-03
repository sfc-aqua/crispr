import click
from quisp_run import config
from quisp_run.utils import console


@click.command()
def parse_config():
    with open("simulation.plan", "rt") as f:
        source = f.read()
        sim_plan = config.parse_config(source)
        console.print(sim_plan.populate()[0])
