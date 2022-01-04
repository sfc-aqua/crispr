import asyncio, re
from typing import List, Optional
from enum import Enum
from rich.progress import TaskID
from rich.console import Console
from quisp_run.simulation import Result, SimContext, SimSetting
from quisp_run.utils import parse_time


class WorkerStatus(Enum):
    WAINTING_FOR_TASK = "Waiting for task"
    STARTING = "Starting"
    RUNNING = "Running"
    FINISHING = "Finishing"
    FINISHED = "Finished"
    STOPPED = "Stopped"
    ERROR = "Error"


class Executor:
    """Simulation executor. it takes a simulation setting from the context and runs it."""

    id: int
    task_id: Optional[TaskID]
    context: SimContext
    setting: Optional[SimSetting]
    user_time: float
    real_time: float
    sys_time: float
    error_messages: str
    console = Console()

    # these fields are refered by job_diplay, so you need to aquire lock before writing to it.
    lock: asyncio.Lock
    num_events: int
    ev_per_sec: float
    sim_name: str
    sim_changed: bool
    status: WorkerStatus

    def __init__(self, id: int, context: SimContext):
        self.id = id
        self.task_id = None
        self.lock = asyncio.Lock()
        self.num_events = 0
        self.ev_per_sec = 0
        self.sim_name = ""
        self.sim_changed = False
        self.status = WorkerStatus.WAINTING_FOR_TASK
        self.context = context
        self.user_time = -1.0
        self.sys_time = -1.0
        self.real_time = -1.0
        self.setting = None

    async def run(self):
        """main coroutine of the worker. fetch a sim setting and run it."""
        await self.set_status(WorkerStatus.WAINTING_FOR_TASK)
        ctx = self.context
        while True:
            setting: Optional[SimSetting] = await ctx.simulations.get()
            if setting is None:
                await self.set_status(WorkerStatus.STOPPED)
                break

            last_run_result = self.context.find_last_run(setting.sim_name)
            if last_run_result is not None:
                await ctx.results.put(last_run_result)
                await ctx.done.put(None)
                continue

            await self.switch_simulation(setting)
            cmd_list = setting.to_command_list()
            await self.run_quisp(cmd_list)
            result = self.get_result()
            await ctx.results.put(result)
            await ctx.done.put(None)

    def get_result(self) -> Result:
        assert self.setting is not None
        return Result(
            setting=self.setting,
            sim_name=self.sim_name,
            params=self.setting.fields,
            num_total_events=self.num_events,
            final_events_per_sec=self.ev_per_sec,
            real_time=self.real_time,
            user_time=self.user_time,
            sys_time=self.sys_time,
            error_message=self.error_messages,
        )

    async def set_status(self, status: WorkerStatus):
        async with self.lock:
            self.status = status

    async def switch_simulation(self, setting: SimSetting):
        self.setting = setting
        async with self.lock:
            self.sim_name = setting.sim_name
            self.num_events = 0
            self.ev_per_sec = 0
            self.sim_changed = True
            self.sys_time = -1.0
            self.user_time = -1.0
            self.real_time = -1.0
            self.error_messages = ""
            self.status = WorkerStatus.STARTING

    async def run_quisp(self, cmd: List[str]):
        proc = await asyncio.create_subprocess_shell(
            "time " + " ".join(cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.context.working_dir,
        )
        if proc.stdout is None or proc.stderr is None:
            return
        stdout = proc.stdout
        stderr = proc.stderr
        running = False  # whether quisp's initializing phase is finished or not
        while True:
            if stdout.at_eof() and stderr.at_eof():
                break
            lines = []

            # stdout example:
            # ** Event #1225984   t=10.000104015903   Elapsed: 96.8616s (1m 36s)  76% completed  (76% total)
            #     Speed:     ev/sec=9170.57   simsec/sec=9.70194e-08   ev/simsec=9.45231e+10
            #     Messages:  created: 3759524   present: 15381   in FES: 9122

            while len(stdout._buffer) > 0:  # type: ignore
                buf = (await proc.stdout.readline()).decode().strip()
                if not buf:
                    break
                if buf.startswith("<!> Error"):
                    await self.set_status(WorkerStatus.ERROR)
                if buf.startswith("End."):
                    running = False
                    await self.set_status(WorkerStatus.FINISHING)

                if buf.startswith("** Event"):
                    if not running:
                        running = True
                        await self.set_status(WorkerStatus.RUNNING)
                    match = re.search("Event #(\d+)", buf)
                    if match:
                        async with self.lock:
                            self.num_events = int(match.group(1))
                if buf.startswith("Speed:"):
                    match = re.search(
                        "ev/sec=([0-9.]+)\s+simsec/sec=([0-9.\-\+e]+)\s+ev/simsec=([0-9.\-\+e]+)",
                        buf,
                    )
                    if match:
                        async with self.lock:
                            self.ev_per_sec = float(match.group(1))
                    lines.append(re.sub("\s+", ",", buf))
            while len(stderr._buffer) > 0:  # type: ignore
                buf = (await proc.stderr.readline()).decode().strip()
                # parse time command output
                if buf.startswith("real"):
                    self.real_time = parse_time(buf.split("\t")[1])
                elif buf.startswith("sys"):
                    self.sys_time = parse_time(buf.split("\t")[1])
                elif buf.startswith("user"):
                    self.user_time = parse_time(buf.split("\t")[1])
                elif buf:
                    self.context.log("[red]Err: ", buf)
                    self.error_messages += buf + "\n"
                    await self.set_status(WorkerStatus.ERROR)
            await asyncio.sleep(1)
        await proc.communicate()
        await self.set_status(WorkerStatus.FINISHED)
