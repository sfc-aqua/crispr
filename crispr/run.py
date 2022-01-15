import asyncio, shutil, glob, os, subprocess
from crispr.simulation import SimContext
from crispr.simulation.context import OmnetppEnv
from crispr.workers import Executor, Writer, job_display
from crispr.config import parse_config

from crispr.utils import console, error_console, logger
from crispr.state import State
from crispr.parameter_registry import ParameterRegistry, init_registry
from crispr.constants import CRISPR_TEMPALTE_PARAMETERS_TOML


def start_simulations(
    ned_path: str,
    pool_size: int,
    state: State,
    ui=OmnetppEnv.Cmdenv.value,
    exe_path="./quisp",
):
    console.print(f"QuISP Working dir: {state.quisp_workdir}")
    console.print(f"Simulation plan: {state.simulation_plan_file_path}")
    registry = ParameterRegistry()

    with open(state.parameters_toml_path, "rt") as f:
        registry.load_from_toml(f.read())
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
        quisp_bin_path = os.path.join(state.quisp_workdir, exe_path)
        if not os.path.exists(quisp_bin_path):
            error_console.print(f"[red]QuISP binary not found at {quisp_bin_path}")
            exit(1)

        try:
            return_code = subprocess.run(
                ["./quisp/quisp", "-h"], stderr=subprocess.PIPE, stdout=subprocess.PIPE
            ).returncode
            if return_code != 0:
                error_console.print(f"[red]QuISP binary has error at {quisp_bin_path}")
                exit(1)
        except Exception as e:
            error_console.print(f"[red]falied to check QuISP binary at {quisp_bin_path}")
            error_console.print_exception()
            exit(1)
        shutil.copy(quisp_bin_path, os.path.join(state.result_dir, "quisp_bin"))
        state.simulation_plan_file_path = shutil.copy(
            state.simulation_plan_file_path, state.result_dir
        )
        state.parameters_toml_path = shutil.copy(state.parameters_toml_path, state.result_dir)
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
