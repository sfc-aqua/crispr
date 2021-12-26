from rich import progress
from rich.console import Console
from rich.progress import Progress
from worker import Worker
from typing import List
import asyncio


def SimulationProgress(console):
    return Progress(
        progress.SpinnerColumn(),
        "[status]{task.description}",
        "[num_events]{task.fields[num_events]} events",
        "[ev_per_sec]{task.fields[ev_per_sec]} ev/sec",
        progress.TimeElapsedColumn(),
        console=console,
    )


async def job_display(workers: List[Worker], console: Console):
    console.print("[status]Starting Simulation")
    with SimulationProgress(console) as progress:
        for worker in workers:
            worker.task_id = progress.add_task(
                "Starting Simulation", start_time=0, num_events=0, ev_per_sec=0
            )
        while True:
            for worker in workers:
                async with worker.lock:
                    if worker.task_id is not None:
                        progress.update(
                            worker.task_id,
                            description=f"Running quisp",
                            ev_per_sec=worker.ev_per_sec,
                            num_events=worker.num_events,
                        )
            await asyncio.sleep(0.5)
