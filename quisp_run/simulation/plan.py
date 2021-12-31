from typing import List, Optional, TypedDict, Dict
import itertools, os, time, shutil
from quisp_run.simulation import SimSetting
from quisp_run.constants import (
    QUISP_RUN_ROOT_DIR,
    QUISP_TEMPALTE_OMNETPP_INI,
    QUISP_TEMPALTE_TOPOLOGY_DIR,
)

DEFAULT_SIM_TARGET_PARAMETERS: List[str] = [
    "num_bufs",
    "num_nodes",
    "network_types",
    "connection_types",
    "config_ini_file",
]

DEFAULT_SETTING_KEY_DICT: Dict[str, str] = {
    "num_bufs": "num_buf",
    "num_nodes": "num_node",
    "network_types": "network_type",
    "config_ini_file": "config_ini_file",
    "connection_types": "connection_type",
}


class ConfigVars(TypedDict):
    title: str
    num_nodes: Optional[List[int]]
    num_bufs: Optional[List[int]]
    network_types: Optional[List[str]]
    config_ini_file: str
    error: Optional[Exception]
    param_keys: List[str]
    setting_key_dict: Dict[str, str]


class SimPlan:
    config_vars: ConfigVars
    settings: List[SimSetting] = []
    result_dir: str = ""
    ned_path: str = ""

    def __init__(self, config_vars: ConfigVars):
        self.config_vars = config_vars

    def __getitem__(self, key):
        return self.config_vars[key]

    def has_error(self):
        return self.config_vars.get("error") is not None

    def populate(self) -> List[SimSetting]:
        keys = self.config_vars["param_keys"]
        setting_keys = [k for k in keys]
        settings = []
        for params in itertools.product(
            *[
                self.config_vars[key]
                if isinstance(self.config_vars[key], list)
                else [self.config_vars[key]]
                for key in keys
            ]
        ):
            assert len(params) == len(keys)
            setting_keys = [self.config_vars["setting_key_dict"][k] for k in keys]
            settings.append(SimSetting(**dict(zip(setting_keys, params))))
        self.settings = settings
        return settings

    def create_result_dir(self) -> str:
        root = os.path.join(QUISP_RUN_ROOT_DIR, "results")
        result_dir = os.path.join(root, self.get_result_dir_name())
        os.makedirs(result_dir)
        self.result_dir = result_dir
        shutil.copy(QUISP_TEMPALTE_OMNETPP_INI, os.path.join(result_dir, "omnetpp.ini"))
        topology_path = os.path.join(result_dir, "topology")
        shutil.copytree(QUISP_TEMPALTE_TOPOLOGY_DIR, topology_path)
        self.ned_path = topology_path
        return result_dir

    def write_config(self):
        assert (
            self.result_dir != ""
        ), "SimPlan.result_dir is empty, call SimPlan.create_result_dir() first"
        config_file_path = os.path.join(self.result_dir, "omnetpp.ini")
        with open(config_file_path, "a") as f:
            for setting in self.settings:
                setting.config_ini_file = config_file_path
                config_str = setting.generate_config(self.result_dir)
                f.write(f"[Config {setting.sim_name}]\n")
                f.write(config_str)
                f.write("\n\n")

    def get_result_dir_name(self) -> str:
        return (
            time.strftime("%Y-%m-%d_%H-%M-%S")
            + "-"
            + self.config_vars["title"].replace(" ", "_").replace("/", "_")
        )


def new_config_vars():
    return ConfigVars(
        title="",
        num_nodes=[],
        num_bufs=[],
        network_types=[],
        config_ini_file="${QUISP_RUN_ROOT_DIR}/config/omnetpp.ini",
        error=None,
        param_keys=DEFAULT_SIM_TARGET_PARAMETERS,
        setting_key_dict=DEFAULT_SETTING_KEY_DICT,
    )
