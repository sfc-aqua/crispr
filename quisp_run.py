#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import sys
import os
import asyncio
from rich.theme import Theme
from rich.console import Console
from worker import Worker
from job_dispaly import job_display
from command import Command
theme = Theme(
    {
        "log": "green",
        "status": "cyan",
        "num_events": "green",
        "ev_per_sec": "yellow",
    }
)
console = Console(theme=theme)



async def start_simulations(
    exe_path, ui, config_file, config_name, ned_path, opts, dryrun, quisp_workdir
):
    cmd = Command(exe_path, ui, config_file, config_name, ned_path, opts)
    if dryrun:
        print(cmd.to_str())
        exit(0)
    console.print(f"Working dir: {quisp_workdir}")
    pool_size = 4
    task_size = 100
    tasks = asyncio.Queue(task_size + pool_size)
    for i in range(task_size):
        tasks.put_nowait(cmd)
    for _ in range(pool_size):
        tasks.put_nowait(None)

    results = asyncio.Queue(task_size)
    workers = [Worker(i) for i in range(pool_size)]
    worker_tasks = [asyncio.create_task(worker.run(tasks, results, quisp_workdir)) for worker in workers]

    display = asyncio.create_task(job_display(workers, console))
    await asyncio.gather(display, *worker_tasks)


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
    "--config-name",
    "-s",
    default="linear50_mm_pur_es",
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
def run_cmd(ui, ned_path, config_file, config_name, quisp_root, dryrun):
    if not os.path.exists(quisp_root):
        print(f"quisp_root: {quisp_root} not found", file=sys.stderr)
        exit(1)

    quisp_workdir = os.path.join(quisp_root, "quisp")
    exe_path = "./quisp/quisp"

    if not os.path.exists(os.path.join(quisp_root, exe_path)):
        print(f"quisp executable not found", file=sys.stderr)
        exit(1)

    config_file = os.path.abspath(os.path.join(os.getcwd(), "benchmarks", config_file))

    # add benchmark dir to ned path
    ned_path += ":" + os.path.abspath(os.path.join(os.getcwd(), "benchmarks"))


    asyncio.run(
        start_simulations(
            exe_path, ui, config_file, config_name, ned_path, [], dryrun, quisp_workdir
        )
    )

if __name__ == "__main__":
    run_cmd()
