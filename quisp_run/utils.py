import re
from rich.console import Console
from quisp_run.constants import QUISP_RUN_ROOT_DIR, DEFAULT_RICH_CONSOLE_THEME


def replace_path_placeholder(path_str: str) -> str:
    """convert placeholder string to a valid path string

    e.g.
    "${QUISP_RUN_ROOT_DIR}/config/omnetpp.ini" -> "/home/user/quisp_run/config/omnetpp.ini"
    """
    return path_str.replace("${QUISP_RUN_ROOT_DIR}", QUISP_RUN_ROOT_DIR)


def parse_time(s: str) -> float:
    """parse `time` command result time"""

    match = re.search("\s*([\d.]+)m\s*([\d.]+)s", s)
    if match is None:
        raise ValueError("Invalid time format: {}".format(s))
    return float(match.group(1)) * 60 + float(match.group(2))


console = Console(theme=DEFAULT_RICH_CONSOLE_THEME)
error_console = Console(theme=DEFAULT_RICH_CONSOLE_THEME, stderr=True)
