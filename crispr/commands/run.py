import os
import click
from git import Repo
from crispr.run import start_simulations
from crispr.utils import console, error_console, logger
from crispr.state import State
from crispr.constants import CRISPR_TEMPALTE_PARAMETERS_TOML


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
@click.option(
    "--parameter-toml-path",
    type=click.Path(exists=True),
    default=CRISPR_TEMPALTE_PARAMETERS_TOML,
    help="path to the parameter schema toml file",
)
@click.argument(
    "ini_file_or_simulation_plan_file_path", type=click.Path(exists=True), required=False
)
def run(
    ui,
    ned_path,
    quisp_root,
    pool_size,
    result_dir,
    ini_file_or_simulation_plan_file_path,
    force,
    parameter_toml_path,
):
    """Run a new experiment."""
    state = State.load()
    if not force:
        if state is not None:
            console.print("[green]Found previous state.")
            console.print(
                "\n[green]if you want to resume the last simulation, "
                "type[cyan] $ crispr resume \n"
                "[green]or if you want to start a new simulation, "
                "add [cyan]-f[green] or [cyan]--force[green] option."
            )
            exit(0)

    state = State()

    if ini_file_or_simulation_plan_file_path and ini_file_or_simulation_plan_file_path.endswith(
        ".ini"
    ):
        state.ini_file_path = ini_file_or_simulation_plan_file_path
    else:
        simulation_plan_file_path = ini_file_or_simulation_plan_file_path
        state.simulation_plan_file_path = simulation_plan_file_path

    # initialize state
    state.current_working_dir = os.getcwd()
    state.quisp_root = quisp_root
    state.results_root_dir = (
        result_dir if result_dir else os.path.join(state.current_working_dir, "results")
    )
    state.parameters_toml_path = parameter_toml_path
    if not os.path.isabs(state.results_root_dir):
        state.results_root_dir = os.path.abspath(state.results_root_dir)

    if state.simulation_plan_file_path is None:
        state.simulation_plan_file_path = os.path.join(state.current_working_dir, "simulation.plan")

    if state.parameters_toml_path is None:
        state.parameters_toml_path = CRISPR_TEMPALTE_PARAMETERS_TOML

    if state.quisp_root is None:
        state.quisp_root = os.path.join(state.current_working_dir)

    plan_path = state.simulation_plan_file_path
    if not state.ini_file_path:
        if not os.path.exists(plan_path) or not os.path.isfile(plan_path):
            error_console.print(f"Simulation plan file not found: {plan_path}")
            exit(1)

    if not os.path.exists(state.quisp_root):
        error_console.print(f"quisp_root: {state.quisp_root} not found")
        exit(1)

    state.quisp_workdir = os.path.join(state.quisp_root, "quisp")
    repo = None
    try:
        repo = Repo(state.quisp_root)
    except Exception as e:
        error_console.print("Cannot open quisp repository:", e)
        exit(1)
    state.git_commit_rev = repo.head.object.name_rev
    exe_path = "./quisp"
    quisp_exe_path = os.path.join(state.quisp_root, exe_path)
    if not os.path.exists(quisp_exe_path):
        error_console.print(f"[red]quisp executable not found: %s", quisp_exe_path)
        exit(1)

    start_simulations(ned_path, pool_size, state, ui, exe_path)
