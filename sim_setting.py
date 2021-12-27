from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from sim_context import SimContext


@dataclass
class SimSetting:
    """One Simulation Setting."""

    num_buf: int
    num_node: int
    network_type: str
    config_ini_file: str
    context: "Optional[SimContext]" = None

    def to_command_list(self) -> List[str]:
        assert self.context is not None, "SimSetting.context is None"

        opt_str = "--**.buffers={}".format(self.num_buf)

        cmd = [
            self.context.exe_path,
            "-u",
            self.context.ui,
            self.config_ini_file,
            "-c",
            self.config_name,
            "-n",
            self.context.ned_path,
            opt_str,
        ]
        return cmd

    @property
    def config_name(self) -> str:
        return "{}{}_mm_pur_es".format(self.network_type, self.num_node)

    @property
    def sim_name(self) -> str:
        return f"{self.config_name}-buf{self.num_buf}"

    def to_command_str(self) -> str:
        return " ".join(self.to_command_list())
