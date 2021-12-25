#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import time
import pickle
import click
import sys
import os
import rich
import asyncio
import re
from rich.progress import Progress
from rich.theme import Theme
from rich.console import Console

progress_theme = Theme(
    {
        "log": "green",
        "status": "cyan",
        "num_events": "green",
        "ev_per_sec": "yellow",
    }
)
console = Console(theme=progress_theme)


def gen_cmd(exe_path, env, config_path, config_name, ned_path, opts):
    exe_path = "./quisp"
    cmd = [
        exe_path,
        "-u",
        env,
        config_path,
        "-c",
        config_name,
        "-n",
        ned_path,
    ]
    if opts:
        cmd += opts
    return cmd


async def run_quisp(cmd, workdir="./"):
    console.print(f"Working dir: {workdir}")
    console.print(f"Run: {' '.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=workdir,
    )
    with Progress(
        rich.progress.SpinnerColumn(),
        "[status]{task.description}",
        "[num_events]{task.fields[num_events]} events",
        "[ev_per_sec]{task.fields[ev_per_sec]} ev/sec",
        rich.progress.TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            "Starting Simulation", start_time=0, num_events=0, ev_per_sec=0
        )
        while True:
            if proc.stdout.at_eof() and proc.stderr.at_eof():
                break
            lines = []
            ev_per_sec = 0
            num_events = 0
            # stdout example:
            # ** Event #1225984   t=10.000104015903   Elapsed: 96.8616s (1m 36s)  76% completed  (76% total)
            #     Speed:     ev/sec=9170.57   simsec/sec=9.70194e-08   ev/simsec=9.45231e+10
            #     Messages:  created: 3759524   present: 15381   in FES: 9122

            while len(proc.stdout._buffer) > 0:
                buf = (await proc.stdout.readline()).decode().strip()
                if not buf:
                    break
                if buf.startswith("** Event"):
                    match = re.search("Event #(\d+)", buf)
                    if match:
                        num_events = int(match.group(1))
                if buf.startswith("Speed:"):
                    match = re.search(
                        "ev/sec=([0-9.]+)\s+simsec/sec=([0-9.\-\+e]+)\s+ev/simsec=([0-9.\-\+e]+)",
                        buf,
                    )
                    if match:
                        ev_per_sec = int(match.group(1))
                    lines.append(re.sub("\s+", ",", buf))
            if lines:
                progress.update(
                    task,
                    description=f"Running quisp",
                    ev_per_sec=ev_per_sec,
                    num_events=num_events,
                )
            await asyncio.sleep(1)
    await proc.communicate()


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
def run(ui, ned_path, config_file, config_name, quisp_root, dryrun):
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

    cmd = gen_cmd(exe_path, ui, config_file, config_name, ned_path, opts="")
    if dryrun:
        print(" ".join(cmd))
        exit(0)

    asyncio.run(run_quisp(cmd, quisp_workdir))


if __name__ == "__main__":
    run()
