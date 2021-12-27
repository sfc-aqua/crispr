import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from .sim_setting import SimSetting
from .result import Result



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

    def __init__(
        self,
        exe_path: str,
        ui: OmnetppEnv,
        ned_path: str,
        working_dir: str,
        pool_size: int,
        simulations: List[SimSetting],
    ):
        self.exe_path = exe_path
        self.ui = ui
        self.ned_path = ned_path
        self.working_dir = working_dir
        self.pool_size = pool_size
        num_simulations = len(simulations)
        self.simulations = asyncio.Queue(num_simulations + pool_size)
        for setting in simulations:
            self.simulations.put_nowait(setting)
            setting.context = self
        for _ in range(pool_size):
            self.simulations.put_nowait(None)
        self.results = asyncio.Queue(num_simulations)
