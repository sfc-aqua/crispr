import os, asyncio, shutil
import click
from rich.prompt import Confirm
from quisp_run.simulation import SimContext
from quisp_run.workers import Executor, Writer, job_display
from quisp_run.config import parse_config

from quisp_run.utils import console, error_console
from quisp_run.state import State
from quisp_run.parameter_registry import ParameterRegistry, init_registry


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
@click.argument("simulation_plan_file_path", type=click.Path(exists=True), required=False)
def run(ui, ned_path, quisp_root, pool_size, simulation_plan_file_path):
    state = State.load()
    if state is not None:
        console.print("[green]Found previous state.")
        console.print(state.__dict__)
        continue_run = Confirm.ask("Continue from last run?", default=True)
        if not continue_run:
            state.delete()
            state = State()
    if state is None:
        state = State()

    if not state.loaded:
        state.current_working_dir = os.getcwd()
        state.simulation_plan_file_path = simulation_plan_file_path
        state.quisp_root = quisp_root

        if state.simulation_plan_file_path is None:
            state.simulation_plan_file_path = os.path.join(
                state.current_working_dir, "simulation.plan"
            )

        if state.quisp_root is None:
            state.quisp_root = os.path.join(state.current_working_dir)

    if not os.path.exists(state.simulation_plan_file_path) or not os.path.isfile(
        state.simulation_plan_file_path
    ):
        error_console.print(f"Simulation plan file not found: {state.simulation_plan_file_path}")
        exit(1)

    if not os.path.exists(state.quisp_root):
        error_console.print(f"quisp_root: {state.quisp_root} not found")
        exit(1)

    state.quisp_workdir = os.path.join(state.quisp_root, "quisp")
    exe_path = "./quisp"

    if not os.path.exists(os.path.join(state.quisp_root, exe_path)):
        error_console.print(f"[red]quisp executable not found")
        exit(1)

    start_simulations(exe_path, ui, ned_path, pool_size, state)


def start_simulations(
    exe_path,
    ui,
    ned_path: str,
    pool_size: int,
    state: State,
):
    console.print(f"QuISP Working dir: {state.quisp_workdir}")
    console.print(f"Simulation plan: {state.simulation_plan_file_path}")
    registry = init_registry(ParameterRegistry())
    plan = None

    # populate simulation settings from simulation plan
    with open(state.simulation_plan_file_path, "r") as f:
        source = f.read()
        plan = parse_config(source, registry)
        if state.loaded:
            plan.restore(state)
        plan.populate()

    if not plan.settings:
        error_console.print("[red]No simulation settings found in plan.")
        exit(1)

    if not state.loaded:
        state.result_dir = plan.create_result_dir()
        plan.write_config()
        state.simulation_plan_file_path = shutil.copy(
            state.simulation_plan_file_path, state.result_dir
        )
        ned_path += ":" + plan.ned_path
        state.ned_path = ned_path
    else:
        plan.set_result_dir(state.result_dir)

    async def run_workers():
        # setup workers
        sim_context = SimContext(
            exe_path, ui, state.ned_path, state.quisp_workdir, pool_size, plan, registry
        )
        executors = [Executor(i, sim_context) for i in range(pool_size)]
        worker_tasks = [asyncio.create_task(worker.run()) for worker in executors]
        display_task = asyncio.create_task(job_display(executors, sim_context, console))
        writer = Writer(sim_context)
        writer_task = asyncio.create_task(writer.run())
        await asyncio.gather(display_task, writer_task, *worker_tasks)

    try:
        # run workers
        asyncio.run(run_workers())
    finally:
        state.save()
