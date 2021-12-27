from rich import progress
from rich.console import Console, Group
from rich.progress import Progress
from rich.live import Live
from sim_context import SimContext
from worker import Worker, WorkerStatus
from typing import List
import asyncio


def simulation_progress(console: Console) -> Progress:
    return Progress(
        progress.SpinnerColumn(),
        "[red]{task.fields[sim_name]}",
        "[status]{task.description}",
        "[num_events]{task.fields[num_events]} events",
        "[ev_per_sec]{task.fields[ev_per_sec]} ev/sec",
        progress.TimeElapsedColumn(),
        console=console,
    )


async def job_display(
    workers: List[Worker],
    context: SimContext,
    console: Console,
):
    console.print("[status]Starting Simulation")
    total_progress = Progress(
        "[status]{task.description}",
        progress.BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "[progress.bar]{task.completed}/{task.total}",
        progress.TimeElapsedColumn(),
    )
    sim_progress = simulation_progress(console)
    progress_group = Group(Group(sim_progress), total_progress)  # type: ignore
    with Live(progress_group):
        for worker in workers:
            worker.task_id = sim_progress.add_task(
                "Starting",
                start_time=0,
                num_events=0,
                ev_per_sec=0,
                sim_name=worker.sim_name,
            )
        total_progress_task = total_progress.add_task(
            "total", total=context.simulations.qsize()
        )
        while True:
            for worker in workers:
                async with worker.lock:
                    if worker.task_id is not None:
                        if worker.sim_changed:
                            sim_progress.reset(worker.task_id)
                            sim_progress.update(
                                worker.task_id,
                                description="Starting",
                                ev_per_sec=worker.ev_per_sec,
                                num_events=worker.num_events,
                                sim_name=worker.sim_name,
                                start_time=0,
                            )
                            worker.sim_changed = False
                        else:
                            sim_progress.update(
                                worker.task_id,
                                description=worker.status.value,
                                ev_per_sec=worker.ev_per_sec,
                                num_events=worker.num_events,
                                sim_name=worker.sim_name,
                            )
                            if worker.status == WorkerStatus.STOPPED:
                                sim_progress.update(worker.task_id, visible=False)
                                sim_progress.stop_task(worker.task_id)

            if context.simulations.empty():
                break
            total_progress.update(
                total_progress_task, completed=context.results.qsize()
            )
            await asyncio.sleep(0.25)
        total_progress.update(total_progress_task, advance=1)
