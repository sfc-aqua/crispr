import click
import os, pickle
from quisp_run.state import State
from quisp_run.utils import console


@click.command()
def status():
    state = State.load()
    if state is None:
        console.print("No state found.")
        exit(0)
    console.print(state.__dict__)
    with open(os.path.join(state.result_dir, "results.pickle"), "rb") as f:
        results = pickle.load(f)
        console.print("result file loaded from:", os.path.join(state.result_dir, "results.pickle"))
        console.print(results)
