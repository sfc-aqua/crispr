#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
import click
import sys
import os
import asyncio
from rich.theme import Theme
from rich.console import Console
from quisp_run.worker import Worker
from quisp_run.job_dispaly import job_display
from quisp_run.sim_setting import SimSetting
from quisp_run.sim_context import SimContext
from quisp_run.writer import Writer

theme = Theme(
    {
        "sim_name": "blue",
        "log": "green",
        "status": "cyan",
        "num_events": "green",
        "ev_per_sec": "yellow",
    }
)
console = Console(theme=theme)


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
@click.option(
    "--config-file", "-c", default="./benchmark.ini", help="configuration file to use"
)
@click.option(
    "--sim-name",
    "-s",
    default=None,
    help="configuration name to run",
)
@click.option("--quisp-root", "-r", default="../quisp", help="QuISP root directory")
@click.option(
    "--dryrun",
    "-d",
    is_flag=True,
    default=False,
    help="dry run, show the command without running QuISP",
)
def run_cmd(ui, ned_path, config_file, sim_name, quisp_root, dryrun):
    if not os.path.exists(quisp_root):
        print(f"quisp_root: {quisp_root} not found", file=sys.stderr)
        exit(1)

    quisp_workdir = os.path.join(quisp_root, "quisp")
    exe_path = "./quisp"

    if not os.path.exists(os.path.join(quisp_root, exe_path)):
        print(f"quisp executable not found", file=sys.stderr)
        exit(1)

    config_file = os.path.abspath(os.path.join(os.getcwd(), "benchmarks", config_file))

    # add benchmark dir to ned path
    ned_path += ":" + os.path.abspath(os.path.join(os.getcwd(), "benchmarks"))

    asyncio.run(
        start_simulations(
            exe_path, ui, config_file, sim_name, ned_path, [], dryrun, quisp_workdir
        )
    )


async def start_simulations(
    exe_path, ui, config_file, sim_name, ned_path, opts, dryrun, quisp_workdir
):
    # if dryrun:
    #     print(cmd.to_str())
    #     exit(0)

    console.print(f"Working dir: {quisp_workdir}")
    pool_size = 8
    sim_setings = []
    num_bufs = range(5, 100)
    num_nodes = [10, 20, 30, 40, 50]
    network_types = ["linear"]
    for network_type in network_types:
        for num_buf in num_bufs:
            for num_node in num_nodes:
                sim_setings.append(
                    SimSetting(num_buf, num_node, network_type, config_file)
                )

    sim_context = SimContext(
        exe_path, ui, ned_path, quisp_workdir, pool_size, sim_setings
    )

    workers = [Worker(i, sim_context) for i in range(pool_size)]
    worker_tasks = [asyncio.create_task(worker.run()) for worker in workers]
    display_task = asyncio.create_task(job_display(workers, sim_context, console))
    writer = Writer(sim_context)
    writer_task = asyncio.create_task(writer.run())
    await asyncio.gather(display_task,writer_task, *worker_tasks)

def main():
    print("cmd:main()")
    run_cmd()
if __name__ == "__main__":
    main()
