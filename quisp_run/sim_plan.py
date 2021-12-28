from typing import List, Optional, TypedDict


class ConfigVars(TypedDict, total=False):
    title: str
    num_nodes: Optional[List[int]]
    num_bufs: Optional[List[int]]
    network_types: Optional[List[str]]
    error: Optional[Exception]
    __sim_target: Optional[List[str]]

class SimPlan():
    config_vars: ConfigVars

    def __init__(self, config_vars: ConfigVars):
        self.config_vars = config_vars

    def __getitem__(self, key):
        return self.config_vars[key]

    def has_error(self):
        return self.config_vars.get("error") is not None

    def populate():
        pass

def new_config_vars():
    return ConfigVars(title="", num_nodes=[], num_bufs=[], network_types=[], error=None)
