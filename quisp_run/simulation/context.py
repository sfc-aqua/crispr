import asyncio
from typing import TYPE_CHECKING
from rich.live import Live
from enum import Enum
from typing import Optional, List
from .setting import SimSetting
from .result import Result

if TYPE_CHECKING:
    from .plan import SimPlan


class OmnetppEnv(Enum):
    Cmdenv = "Cmdenv"
    Qtenv = "Qtenv"


class SimContext:
    """Shared simulation context. this is shared between all workers."""

    exe_path: str
    ui: OmnetppEnv
    ned_path: str
    working_dir: str
    pool_size: int
    simulations: asyncio.Queue[Optional[SimSetting]]
    results: asyncio.Queue[Optional[Result]]
    done: asyncio.Queue[None]
    live: Optional[Live]

    def __init__(
        self,
        exe_path: str,
        ui: OmnetppEnv,
        ned_path: str,
        working_dir: str,
        pool_size: int,
        plan: "SimPlan",
    ):
        self.exe_path = exe_path
        self.ui = ui
        self.ned_path = ned_path
        self.working_dir = working_dir
        self.pool_size = pool_size
        num_simulations = len(plan.settings)
        self.simulations = asyncio.Queue(num_simulations + pool_size)
        for setting in plan.settings:
            self.simulations.put_nowait(setting)
            setting.context = self
        for _ in range(pool_size):
            self.simulations.put_nowait(None)
        self.results = asyncio.Queue(num_simulations)
        self.done = asyncio.Queue(num_simulations)
        self.live = None

    def log(self, *args, **kwargs):
        if self.live is not None:
            self.live.console.log(*args, **kwargs)

    def print(self, *args, **kwargs):
        if self.live is not None:
            self.live.console.print(*args, **kwargs)
