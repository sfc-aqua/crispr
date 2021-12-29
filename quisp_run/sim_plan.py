from typing import List, Optional, TypedDict, Dict
import itertools
from quisp_run.sim_setting import SimSetting
DEFAULT_SIM_TARGET_PARAMETERS: List[str] = ["num_bufs", "num_nodes", "network_types", "connection_types", "config_ini_file"]
DEFAULT_SETTING_KEY_DICT: Dict[str, str] = {
    "num_bufs": "num_buf",
    "num_nodes": "num_node",
    "network_types": "network_type",
    "config_ini_file": "config_ini_file",
    "connection_types": "connection_type"
}

class ConfigVars(TypedDict):
    title: str
    num_nodes: Optional[List[int]]
    num_bufs: Optional[List[int]]
    network_types: Optional[List[str]]
    config_ini_file: str
    error: Optional[Exception]
    param_keys: List[str]
    setting_key_dict: Dict[str,str]

class SimPlan:
    config_vars: ConfigVars

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
        for params in itertools.product(*[self.config_vars[key] if isinstance(self.config_vars[key],list) else [self.config_vars[key]] for key in keys]):
            assert len(params) == len(keys)
            setting_keys = [self.config_vars["setting_key_dict"][k] for k in keys]
            settings.append(SimSetting(**dict(zip(setting_keys, params))))
        return settings


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
