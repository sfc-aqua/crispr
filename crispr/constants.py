import os
from rich.theme import Theme

CRISPR_ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
CRISPR_TEMPALTE_OMNETPP_INI = os.path.join(CRISPR_ROOT_DIR, "templates", "omnetpp.ini")
CRISPR_TEMPALTE_IPYNB = os.path.join(CRISPR_ROOT_DIR, "templates", "analysis.ipynb")
CRISPR_TEMPALTE_TOPOLOGY_DIR = os.path.join(CRISPR_ROOT_DIR, "templates", "topology")
CRISPR_TEMPALTE_PARAMETERS_TOML = os.path.join(CRISPR_ROOT_DIR, "templates", "parameters.toml")

DEFAULT_RICH_CONSOLE_THEME = Theme(
    {
        "task_name": "magenta",
        "sim_name": "blue",
        "log": "green",
        "status": "cyan",
        "num_events": "green",
        "ev_per_sec": "yellow",
    }
)
