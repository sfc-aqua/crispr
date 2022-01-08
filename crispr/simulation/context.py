import asyncio, pickle, os
from typing import TYPE_CHECKING
from rich.live import Live
from enum import Enum
from typing import Optional, List, Any
from .setting import SimSetting
from .result import Result
from crispr.parameter_registry import ParameterRegistry

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
    result_dir: str
    pool_size: int
    simulations: asyncio.Queue[Optional[SimSetting]]
    results: asyncio.Queue[Optional[Result]]
    last_results: Optional[Any]
    done: asyncio.Queue[None]
    live: Optional[Live]
    registry: ParameterRegistry
    num_simulations: int
    param_keys: List[str]

    def __init__(
        self,
        exe_path: str,
        ui: OmnetppEnv,
        ned_path: str,
        working_dir: str,
        pool_size: int,
        plan: "SimPlan",
        registry: ParameterRegistry,
    ):
        self.registry = registry
        self.exe_path = exe_path
        self.ui = ui
        self.ned_path = ned_path
        self.working_dir = working_dir
        self.pool_size = pool_size
        self.last_results = []
        num_simulations = len(plan.settings)
        self.num_simulations = num_simulations
        self.simulations = asyncio.Queue(num_simulations + pool_size)
        assert len(plan.settings) > 0, "No simulation settings found in plan."
        self.param_keys = list(plan.settings[0].fields.keys())
        for setting in plan.settings:
            self.simulations.put_nowait(setting)
            setting.context = self
        for _ in range(pool_size):
            self.simulations.put_nowait(None)
        self.result_dir = plan.result_dir
        self.results = asyncio.Queue(num_simulations)
        self.done = asyncio.Queue(num_simulations)
        self.live = None
        pickle_file_path = os.path.join(plan.result_dir, "results.pickle")
        if os.path.isfile(pickle_file_path):
            with open(pickle_file_path, "rb") as f:
                self.last_results = pickle.load(f)

    @property
    def num_finished(self):
        return self.done.qsize()

    def find_last_run(self, sim_name: str) -> Optional[Result]:
        if self.last_results is None:
            return None
        if sim_name in self.last_results:
            return Result.from_dict(self.last_results[sim_name])
        return None

    def log(self, *args, **kwargs):
        if self.live is not None:
            self.live.console.log(*args, **kwargs)

    def print(self, *args, **kwargs):
        if self.live is not None:
            self.live.console.print(*args, **kwargs)
