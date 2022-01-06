import asyncio, shutil, glob, os
from quisp_run.simulation import SimContext
from quisp_run.simulation.context import OmnetppEnv
from quisp_run.workers import Executor, Writer, job_display
from quisp_run.config import parse_config

from quisp_run.utils import console, error_console, logger
from quisp_run.state import State
from quisp_run.parameter_registry import ParameterRegistry, init_registry


def start_simulations(
    ned_path: str,
    pool_size: int,
    state: State,
    ui=OmnetppEnv.Cmdenv.value,
    exe_path="./quisp",
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
        state.result_dir, ned_dir = plan.create_result_dir(state.results_root_dir)
        plan.write_config()

        # copy quisp binnary and ned files to result dir
        ned_files = glob.glob(os.path.join(state.quisp_workdir, "**/*.ned"), recursive=True)
        for ned_file in ned_files:
            os.makedirs(
                os.path.dirname(os.path.join(ned_dir, ned_file[len(state.quisp_workdir) + 1 :])),
                exist_ok=True,
            )
            shutil.copy(ned_file, os.path.join(ned_dir, ned_file[len(state.quisp_workdir) + 1 :]))
        shutil.copy(
            os.path.join(state.quisp_workdir, exe_path), os.path.join(state.result_dir, "quisp_bin")
        )
        state.simulation_plan_file_path = shutil.copy(
            state.simulation_plan_file_path, state.result_dir
        )
        with open(os.path.join(state.result_dir, "commit.txt"), "w") as f:
            f.write(state.git_commit_rev)

        ned_path += ":" + plan.ned_path
        state.ned_path = ned_path
    else:
        plan.set_result_dir(state.result_dir)

    ctx = None

    async def run_workers():
        # setup workers
        sim_context = SimContext(
            exe_path, ui, state.ned_path, state.quisp_workdir, pool_size, plan, registry
        )
        state.num_simulations = sim_context.num_simulations
        ctx = sim_context
        executors = [Executor(i, sim_context) for i in range(pool_size)]
        worker_tasks = [asyncio.create_task(worker.run()) for worker in executors]
        display_task = asyncio.create_task(job_display(executors, sim_context, console))
        writer = Writer(sim_context)
        writer_task = asyncio.create_task(writer.run())
        # run workers
        await asyncio.gather(display_task, writer_task, *worker_tasks)

    try:
        asyncio.run(run_workers())
    finally:
        if ctx:
            state.num_finished = ctx.num_finished
            state.num_simulations = ctx.num_simulations
        state.save()
