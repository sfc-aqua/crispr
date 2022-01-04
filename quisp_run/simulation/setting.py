from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING, Any, Dict
from quisp_run.parameter_registry.parameter import ParameterKind
from quisp_run.utils import replace_path_placeholder
from quisp_run.parameter_registry import registry
import os

if TYPE_CHECKING:
    from .context import SimContext


class SimSetting:
    """One Simulation Setting."""

    # num_buf: int
    # num_node: int
    # network_type: str
    # config_ini_file: str
    # connection_type: str
    context: "Optional[SimContext]" = None
    fields: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, context: "Optional[SimContext]", fields: dict):
        self.context = context
        self.fields = fields

    def to_command_list(self) -> List[str]:
        assert self.context is not None, "SimSetting.context is None"

        cmd = [
            self.context.exe_path,
            "-u",
            self.context.ui,
            replace_path_placeholder(self.fields["config_ini_file"]),
            "-c",
            self.sim_name,
            "-n",
            self.context.ned_path,
        ]
        return cmd

    def generate_config(self, result_root_dir: str) -> str:
        # built in configs
        network_name = "{}_network".format(self.fields["network_type"])
        config_str = ""
        config_str += "network=topology.{}\n".format(network_name)
        config_str += '**.tomography_output_filename="{}"\n'.format(
            os.path.join(result_root_dir, "results", self.sim_name)
        )

        # dynamic parameters
        for key in self.fields:
            param_def = registry.find_by_name(key)
            if param_def.kind == ParameterKind.NETWORK_PARAM:
                if param_def.is_number():
                    config_str += "{}.{}={}\n".format(
                        network_name, param_def.param_key, self.fields[key]
                    )
                else:
                    config_str += '{}.{}="{}"\n'.format(
                        network_name, param_def.param_key, self.fields[key]
                    )
            elif param_def.kind == ParameterKind.PARAM:
                config_str += "**.{}={}\n".format(param_def.param_key, self.fields[key])

        # traffic_pattern_index: int = 2
        # num_purification: int = 1
        # lone_initiator_addr: int = 0
        # link_tomography_enabled: bool = False
        # purification_type: str = "1001"
        # config_str += "**.app.TrafficPattern={}\n".format(traffic_pattern_index)
        # config_str += "**.app.LoneInitiatorAddress={}\n".format(lone_initiator_addr)
        # config_str += "**.qrsa.hm.link_tomography={}\n".format(str(link_tomography_enabled).lower())
        # config_str += "**.qrsa.hm.initial_purification={}\n".format(num_purification)
        # config_str += "**.qrsa.hm.Purification_type={}\n".format(purification_type)
        return config_str

    @property
    def config_name(self) -> str:
        return self.__str__()

    @property
    def sim_name(self) -> str:
        return self.__str__()

    def to_command_str(self) -> str:
        return " ".join(self.to_command_list())

    def __str__(self) -> str:
        s = ""
        for f in self.fields:
            if f == "config_ini_file":
                continue
            s += f + "_" + str(self.fields[f]) + "-"
        if len(s) > 127:
            s = ""
            for f in self.fields:
                if f == "config_ini_file":
                    continue
                if len(f) > 6:
                    s += f.replace("num_", "")[:4] + "_" + str(self.fields[f]) + "-"
                else:
                    s += f + "_" + str(self.fields[f]) + "-"
        return s[:-2]

    def __gt__(self, other):
        return str(self) > str(other)
