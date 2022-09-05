from typing import List, Optional, TYPE_CHECKING, Any, Dict
from crispr.parameter_registry.parameter import ParameterKind
from crispr.utils import replace_path_placeholder, logger
from crispr.parameter_registry import registry
import os

if TYPE_CHECKING:
    from .context import SimContext


class SimSetting:
    """One Simulation Setting."""

    context: "Optional[SimContext]"
    fields: Dict[str, Any]

    def __init__(self, context: "Optional[SimContext]", fields: Dict[str, Any]):
        self.context = context
        self.fields = fields

    def to_command_list(self) -> List[str]:
        assert self.context is not None, "SimSetting.context is None"
        logger.debug(
            f"[Executor.to_command_list] result_dir: {os.path.join(self.context.result_dir, 'omnetpp.ini')}"
        )
        result_dir = self.context.result_dir
        cmd = [
            os.path.join(result_dir, "quisp_bin"),
            "-u",
            self.context.ui,
            os.path.join(result_dir, "omnetpp.ini"),
            "-c",
            self.sim_name,
            "-n",
            os.path.join(result_dir, "ned") + ":" + os.path.join(result_dir, "topology"),
        ]
        return cmd

    def generate_config(self, result_root_dir: str, registry: registry.ParameterRegistry) -> str:
        """generate omnetpp.ini config file"""
        # built in configs
        network_name = "{}_network".format(self.fields["network_type"])
        config_str = ""
        config_str += "network=topology.{}\n".format(network_name)
        config_str += '**.tomography_output_filename="{}"\n'.format(
            os.path.join(result_root_dir, "results", self.sim_name)
        )
        config_str += '**.logger.log_filename="{}.jsonl"\n'.format(
            os.path.join(result_root_dir, "results", self.sim_name)
        )

        # dynamic parameters
        for key in self.fields:
            param_def = registry.find_by_name(key)
            parent = ""
            if param_def.kind == ParameterKind.NETWORK_PARAM:
                parent = network_name
            elif param_def.kind == ParameterKind.PARAM:
                parent = "**"

            if parent:
                config_str += f"{parent}."
                param_key = param_def.param_key
                value = self.fields[key]

                if param_def.is_number():
                    config_str += f"{param_key}={value}\n"
                elif param_def.is_bool():
                    config_str += f'{param_key}={"true" if value else "false"}\n'
                else:  # string
                    config_str += f'{param_key}="{value}"\n'

        return config_str

    @property
    def config_name(self) -> str:
        return self.__str__()

    @property
    def sim_name(self) -> str:
        return self.__str__().replace(" ", "_")

    def to_command_str(self) -> str:
        return " ".join(self.to_command_list())

    def __str__(self) -> str:
        s = ""
        for f in self.fields:
            if f == "config_ini_file":
                continue
            if f == "title":
                continue
            s += f + str(self.fields[f]) + "-"
        if len(s) > 127:
            s = ""
            for f in self.fields:
                if f == "config_ini_file":
                    continue
                if f == "title":
                    continue
                if len(f) > 6:
                    s += f.replace("num_", "")[:4] + str(self.fields[f]) + "-"
                else:
                    s += f + str(self.fields[f]) + "-"
        return s[:-1]

    def __gt__(self, other):
        return str(self) > str(other)
