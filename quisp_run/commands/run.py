import os, sys, asyncio
import click
from typing import List

from quisp_run.simulation import SimContext, SimSetting
from quisp_run.workers import Executor, Writer, job_display
from quisp_run.config import parse_config

from quisp_run.utils import console, error_console


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
@click.option("--quisp-root", "-r", default="../quisp", help="QuISP root directory")
def run(ui, ned_path, quisp_root, pool_size):
    if not os.path.exists(quisp_root):
        error_console.print(f"quisp_root: {quisp_root} not found")
        exit(1)

    quisp_workdir = os.path.join(quisp_root, "quisp")
    exe_path = "./quisp"

    if not os.path.exists(os.path.join(quisp_root, exe_path)):
        error_console.print(f"quisp executable not found")
        exit(1)

    asyncio.run(start_simulations(exe_path, ui, ned_path, quisp_workdir, pool_size))


async def start_simulations(exe_path, ui, ned_path, quisp_workdir, pool_size):
    console.print(f"Working dir: {quisp_workdir}")
    plan = None

    # populate simulation settings from simulation plan
    with open("simulation.plan", "r") as f:
        source = f.read()
        plan = parse_config(source)
        plan.populate()
    plan.create_result_dir()
    plan.write_config()
    ned_path += ":" + plan.ned_path
    sim_context = SimContext(exe_path, ui, ned_path, quisp_workdir, pool_size, plan)

    # setup workers
    executors = [Executor(i, sim_context) for i in range(pool_size)]
    worker_tasks = [asyncio.create_task(worker.run()) for worker in executors]
    display_task = asyncio.create_task(job_display(executors, sim_context, console))
    writer = Writer(sim_context)
    writer_task = asyncio.create_task(writer.run())

    # run workers
    await asyncio.gather(display_task, writer_task, *worker_tasks)
