import os
from rich.theme import Theme

QUISP_RUN_ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

DEFAULT_RICH_CONSOLE_THEME = Theme(
    {
        "sim_name": "blue",
        "log": "green",
        "status": "cyan",
        "num_events": "green",
        "ev_per_sec": "yellow",
    }
)
