from typing import List, Dict, Any, Tuple
import itertools, os, time, shutil
from crispr.parameter_registry import ParameterRegistry
from crispr.simulation import SimSetting
from crispr.state import State
from crispr.utils import logger, error_console
from crispr.constants import (
    CRISPR_ROOT_DIR,
    CRISPR_TEMPALTE_IPYNB,
    CRISPR_TEMPALTE_OMNETPP_INI,
    CRISPR_TEMPALTE_TOPOLOGY_DIR,
)


class SimPlan:
    config_vars: Dict[str, Any]
    settings: List[SimSetting]
    result_dir: str
    ned_path: str
    registry: ParameterRegistry

    def __init__(self, config_vars: Dict[str, Any], registry: ParameterRegistry):
        self.config_vars = config_vars
        self.settings = []
        self.result_dir = ""
        self.ned_path = ""
        self.registry = registry

    def __getitem__(self, key):
        return self.config_vars[key]

    def has_error(self):
        return self.config_vars.get("error") is not None

    def populate(self) -> List[SimSetting]:
        def collect_parameters(variables: Dict[str, Any]):
            keys = []
            vals = []
            for p in self.registry.parameters:
                if p.plural:
                    if p.plural in variables and variables[p.plural] is not None:
                        vals.append(variables[p.plural])
                        keys.append(p.plural)
                        if (
                            p.singular
                            and p.singular in variables
                            and variables[p.singular] is not None
                        ):
                            error_console.print(
                                f'[yellow] warning: cannot use "{p.singular}" and "{p.plural}" parameter at the same time'
                            )
                    elif (
                        p.singular and p.singular in variables and variables[p.singular] is not None
                    ):
                        vals.append([variables[p.singular]])
                        keys.append(p.singular)
                elif p.singular and p.singular in variables and variables[p.singular] is not None:
                    vals.append([variables[p.singular]])
                    keys.append(p.singular)
            return keys, vals

        keys, vals = collect_parameters(self.config_vars)
        logger.debug("processed vars:")
        for kv in zip(keys, vals):
            logger.debug("  %s: %s", kv[0], kv[1])
        setting_keys = [self.registry.get_singular_name(k) for k in keys]
        settings = []
        for params in itertools.product(*vals):
            assert len(params) == len(keys)
            settings.append(SimSetting(context=None, fields=dict(zip(setting_keys, params))))
        self.settings = settings
        return settings

    def create_result_dir(self, results_root_dir: str) -> Tuple[str, str]:
        logger.debug("Results root dir: %s", results_root_dir)

        result_dir = os.path.join(results_root_dir, self.get_result_dir_name())
        os.makedirs(result_dir)
        ned_dir = os.path.join(result_dir, "ned")
        os.makedirs(ned_dir)
        self.result_dir = result_dir

        logger.debug("Creating result dir: %s", self.result_dir)
        shutil.copy(CRISPR_TEMPALTE_OMNETPP_INI, os.path.join(result_dir, "omnetpp.ini"))
        shutil.copy(CRISPR_TEMPALTE_IPYNB, os.path.join(result_dir, "analysis.ipynb"))
        topology_path = os.path.join(result_dir, "topology")
        shutil.copytree(CRISPR_TEMPALTE_TOPOLOGY_DIR, topology_path)
        self.ned_path = topology_path
        return (result_dir, ned_dir)

    def write_config(self):
        assert (
            self.result_dir != ""
        ), "SimPlan.result_dir is empty, call SimPlan.create_result_dir() first"
        logger.debug("Writing config to %s", self.result_dir)
        config_file_path = os.path.join(self.result_dir, "omnetpp.ini")
        with open(config_file_path, "a") as f:
            for setting in self.settings:
                setting.fields["config_ini_file"] = config_file_path
                config_str = setting.generate_config(self.result_dir, self.registry)
                f.write(f"[Config {setting.sim_name}]\n")
                f.write(config_str)
                f.write("\n\n")

    def set_result_dir(self, result_dir: str):
        self.result_dir = result_dir
        config_file_path = os.path.join(self.result_dir, "omnetpp.ini")
        for setting in self.settings:
            setting.fields["config_ini_file"] = config_file_path

    def get_result_dir_name(self) -> str:
        return (
            time.strftime("%Y-%m-%d_%H-%M-%S")
            + "-"
            + self.config_vars["title"].replace(" ", "_").replace("/", "_")
        )

    def restore(self, state: "State"):
        self.result_dir = state.result_dir
        config_file_path = os.path.join(self.result_dir, "omnetpp.ini")
        for setting in self.settings:
            setting.fields["config_ini_file"] = config_file_path
