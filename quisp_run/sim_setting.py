from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING
from quisp_run.path_convert import replace_path_placeholder

if TYPE_CHECKING:
    from sim_context import SimContext


@dataclass
class SimSetting:
    """One Simulation Setting."""

    num_buf: int
    num_node: int
    network_type: str
    config_ini_file: str
    connection_type: str
    context: "Optional[SimContext]" = None

    def to_command_list(self) -> List[str]:
        assert self.context is not None, "SimSetting.context is None"

        opt_str = "--**.buffers={} ".format(self.num_buf)
        opt_str += "--network=topology.{}_network ".format(self.network_type)
        opt_str += "--{}_network.connectionType=\"{}\" ".format(self.network_type, self.connection_type)

        cmd = [
            self.context.exe_path,
            "-u",
            self.context.ui,
            replace_path_placeholder( self.config_ini_file),
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

    def __str__(self) -> str:
        return f"nodes_{self.num_node}_bufs_{self.num_buf}_network_{self.network_type}_{self.config_ini_file}"

    def __gt__(self, other):
        return str(self) > str(other)
