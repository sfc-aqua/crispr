import re, logging
from rich.logging import RichHandler
from rich.console import Console
from crispr.constants import CRISPR_ROOT_DIR, DEFAULT_RICH_CONSOLE_THEME

TIME_FORMAT_PATTERN = re.compile(r"\s*([\d.]+)m\s*([\d.]+)s")


def replace_path_placeholder(path_str: str) -> str:
    """convert placeholder string to a valid path string

    e.g.
    "${CRISPR_ROOT_DIR}/config/omnetpp.ini" -> "/home/user/crispr/config/omnetpp.ini"
    """
    return path_str.replace("${CRISPR_ROOT_DIR}", CRISPR_ROOT_DIR)


def parse_time(s: str) -> float:
    """parse `time` command result time"""

    match = re.search(TIME_FORMAT_PATTERN, s)
    if match is None:
        raise ValueError("Invalid time format: {}".format(s))
    return float(match.group(1)) * 60 + float(match.group(2))


console = Console(theme=DEFAULT_RICH_CONSOLE_THEME)
error_console = Console(theme=DEFAULT_RICH_CONSOLE_THEME, stderr=True)

FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(console=console)]
)

logger = logging.getLogger("rich")
