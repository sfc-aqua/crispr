from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING
from quisp_run.utils import replace_path_placeholder
import os

if TYPE_CHECKING:
    from .context import SimContext


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

        cmd = [
            self.context.exe_path,
            "-u",
            self.context.ui,
            replace_path_placeholder(self.config_ini_file),
            "-c",
            self.sim_name,
            "-n",
            self.context.ned_path,
        ]
        return cmd

    def generate_config(self, result_root_dir: str) -> str:
        config_str = ""
        config_str += "network=topology.{}_network\n".format(self.network_type)
        config_str += "**.buffers={}\n".format(self.num_buf)
        config_str += '{}_network.connectionType="{}"\n'.format(
            self.network_type, self.connection_type
        )
        config_str += "{}_network.numNodes={}\n".format(self.network_type, self.num_node)
        config_str += '**.tomography_output_filename="{}"\n'.format(
            os.path.join(result_root_dir, "results", self.sim_name)
        )

        traffic_pattern_index: int = 2
        num_purification: int = 1
        lone_initiator_addr: int = 0
        link_tomography_enabled: bool = False
        purification_type: str = "1001"
        config_str += "**.app.TrafficPattern={}\n".format(traffic_pattern_index)
        config_str += "**.app.LoneInitiatorAddress={}\n".format(lone_initiator_addr)
        config_str += "**.qrsa.hm.link_tomography={}\n".format(str(link_tomography_enabled).lower())
        config_str += "**.qrsa.hm.initial_purification={}\n".format(num_purification)
        config_str += "**.qrsa.hm.Purification_type={}\n".format(purification_type)
        return config_str

    @property
    def config_name(self) -> str:
        return "{}{}_mm_pur_es".format(self.network_type, self.num_node)

    @property
    def sim_name(self) -> str:
        return (
            f"buf{self.num_buf}-nodes-{self.num_node}-{self.network_type}-{self.connection_type}-"
        )

    def to_command_str(self) -> str:
        return " ".join(self.to_command_list())

    def __str__(self) -> str:
        return f"nodes_{self.num_node}_bufs_{self.num_buf}_network_{self.network_type}_{self.config_ini_file}"

    def __gt__(self, other):
        return str(self) > str(other)
