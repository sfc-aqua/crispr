from rich import progress
from rich.console import Console
from rich.progress import Progres
from worker import Worker, WorkerStatus
from typing import List
import asyncio


def SimulationProgress(console):
    return Progress(
        progress.SpinnerColumn(),
        "[red]{task.fields[sim_name]}",
        "[status]{task.description}",
        "[num_events]{task.fields[num_events]} events",
        "[ev_per_sec]{task.fields[ev_per_sec]} ev/sec",
        progress.TimeElapsedColumn(),
        console=console,
    )


async def job_display(workers: List[Worker], tasks, console: Console):
    console.print("[status]Starting Simulation")
    with SimulationProgress(console) as progress:
        for worker in workers:
            worker.task_id = progress.add_task(
                "Starting",
                start_time=0,
                num_events=0,
                ev_per_sec=0,
                sim_name=worker.sim_name,
            )
        while True:
            for worker in workers:
                async with worker.lock:
                    if worker.task_id is not None:
                        if worker.sim_changed:
                            progress.reset(worker.task_id)
                            progress.update(
                                worker.task_id,
                                description=f"Starting",
                                ev_per_sec=worker.ev_per_sec,
                                num_events=worker.num_events,
                                sim_name=worker.sim_name,
                                start_time=0,
                            )
                            worker.sim_changed = False
                        else:
                            progress.update(
                                worker.task_id,
                                description=worker.status.value,
                                ev_per_sec=worker.ev_per_sec,
                                num_events=worker.num_events,
                                sim_name=worker.sim_name,
                            )
                            if worker.status == WorkerStatus.STOPPED:
                                progress.update(worker.task_id, visible=False)
                                progress.stop_task(worker.task_id)

            if tasks.empty():
                break
            await asyncio.sleep(0.25)
