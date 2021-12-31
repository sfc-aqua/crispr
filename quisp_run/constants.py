import os
from rich.theme import Theme

QUISP_RUN_ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
QUISP_TEMPALTE_OMNETPP_INI = os.path.join(QUISP_RUN_ROOT_DIR, "templates", "omnetpp.ini")
QUISP_TEMPALTE_TOPOLOGY_DIR = os.path.join(QUISP_RUN_ROOT_DIR, "templates", "topology")

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
