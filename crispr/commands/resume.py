import click
from rich.prompt import Confirm
from crispr.state import State
from crispr.utils import console
from crispr.run import start_simulations


@click.command()
@click.option("--pool-size", "-p", default=4, help="number of workers to use")
def resume(pool_size):
    """Resume the last simulation."""
    state = State.load()
    if state is None:
        console.print("[red]No state found. Nothing to resume.")
        exit(0)

    console.print("[green]Found previous state.")
    console.print(state.__dict__)
    continue_run = Confirm.ask("Continue from last run?", default=True)
    if not continue_run:
        console.print("[red]Aborting.")
        exit(0)
    start_simulations(state.ned_path, pool_size, state=state)
