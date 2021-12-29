import os
from quisp_run.constants import QUISP_RUN_ROOT_DIR


def replace_path_placeholder(path_str: str) -> str:
    """convert placeholder string to a valid path string

    e.g.
    "${QUISP_RUN_ROOT_DIR}/config/omnetpp.ini" -> "/home/user/quisp_run/config/omnetpp.ini"
    """
    return path_str.replace("${QUISP_RUN_ROOT_DIR}", QUISP_RUN_ROOT_DIR)
