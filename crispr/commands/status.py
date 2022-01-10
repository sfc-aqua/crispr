import click
import os, pickle
from crispr.state import State
from crispr.utils import console


@click.command()
def status():
    """Show the status of the last simulation."""
    state = State.load()
    if state is None:
        console.print("[red]No state found.")
        exit(0)
    console.print("[green]last simulation plan found")
    console.print(state.__dict__)
    results = None
    try:
        with open(os.path.join(state.result_dir, "results.pickle"), "rb") as f:
            results = pickle.load(f)
    except FileNotFoundError:
        console.print("[red]No simulation results found.")
        exit(0)
    console.print("result file loaded from:", os.path.join(state.result_dir, "results.pickle"))
    console.print(len(results), "simulation results found.")
