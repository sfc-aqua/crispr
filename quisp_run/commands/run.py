import os
import click
from quisp_run.run import start_simulations
from quisp_run.utils import console, error_console, logger
from quisp_run.state import State


@click.command()
@click.option(
    "--ui",
    "-u",
    default="Cmdenv",
    help="choose the UI to use: Cmdenv (default), Qtenv, Tkenv",
)
@click.option(
    "--ned-path",
    "-n",
    default="./modules:./channels:./networks",
    help="colon separated path list to NED files",
)
@click.option("--pool-size", "-p", default=4, help="number of workers to use")
@click.option("--quisp-root", "-r", default=None, help="QuISP root directory")
@click.option("--result-dir", "-o", default=None, help="result directory. default: ${PWD}/results")
@click.option(
    "--force",
    "-f",
    default=False,
    is_flag=True,
    help="ignore unfinished simulation and start new run",
)
@click.argument("simulation_plan_file_path", type=click.Path(exists=True), required=False)
def run(ui, ned_path, quisp_root, pool_size, result_dir, simulation_plan_file_path, force):
    state = State.load()
    if not force:
        if state is not None:
            console.print("[green]Found previous state.")
            console.print(
                "\n[green]if you want to resume the last simulation, "
                "type[cyan] $ quisp_run resume \n"
                "[green]or if you want to start a new simulation, "
                "add [cyan]-f[green] or [cyan]--force[green] option."
            )
            exit(0)

    state = State()

    # initialize state
    state.current_working_dir = os.getcwd()
    state.simulation_plan_file_path = simulation_plan_file_path
    state.quisp_root = quisp_root
    state.results_root_dir = (
        result_dir if result_dir else os.path.join(state.current_working_dir, "results")
    )
    if not os.path.isabs(state.results_root_dir):
        state.results_root_dir = os.path.abspath(state.results_root_dir)

    if state.simulation_plan_file_path is None:
        state.simulation_plan_file_path = os.path.join(state.current_working_dir, "simulation.plan")

    if state.quisp_root is None:
        state.quisp_root = os.path.join(state.current_working_dir)

    plan_path = state.simulation_plan_file_path
    if not os.path.exists(plan_path) or not os.path.isfile(plan_path):
        error_console.print(f"Simulation plan file not found: {plan_path}")
        exit(1)

    if not os.path.exists(state.quisp_root):
        error_console.print(f"quisp_root: {state.quisp_root} not found")
        exit(1)

    state.quisp_workdir = os.path.join(state.quisp_root, "quisp")
    exe_path = "./quisp"
    quisp_exe_path = os.path.join(state.quisp_root, exe_path)
    if not os.path.exists(quisp_exe_path):
        error_console.print(f"[red]quisp executable not found: %s", quisp_exe_path)
        exit(1)

    start_simulations(ned_path, pool_size, state, ui, exe_path)
