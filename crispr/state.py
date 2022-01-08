from datetime import datetime
from pathlib import Path
import os, json
from typing import Optional

HOME = str(Path.home())
STATE_FILE_DIR = os.path.join(HOME, ".local", "state", "quisp")
STATE_FILE_PATH = os.path.join(STATE_FILE_DIR, "state.json")


def encode(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class State:
    last_run: datetime
    results_root_dir: str
    result_dir: str
    current_working_dir: str
    simulation_plan_file_path: str
    quisp_root: str
    quisp_workdir: str
    ned_path: str
    loaded: bool
    num_simulations: int
    num_finished: int
    git_commit_rev: str

    def __init__(self):
        self.last_run = datetime.now()
        self.results_root_dir = ""
        self.result_dir = ""
        self.simulation_plan_file_path = ""
        self.quisp_root = ""
        self.quisp_workdir = ""
        self.ned_path = ""
        self.loaded = False
        self.num_simulations = 0
        self.num_finished = 0
        self.git_commit_rev = ""

    def save(self):
        if not os.path.isfile(STATE_FILE_PATH):
            os.makedirs(os.path.dirname(STATE_FILE_PATH), exist_ok=True)

        with open(STATE_FILE_PATH, "w") as f:
            json.dump(self.__dict__, f, default=encode)

    def delete(self):
        os.remove(STATE_FILE_PATH)

    @staticmethod
    def load() -> "Optional[State]":
        if not os.path.isfile(STATE_FILE_PATH):
            return None
        with open(STATE_FILE_PATH, "r") as f:
            data = json.load(f)
            return State.from_dict(data)

    @staticmethod
    def from_dict(data: dict) -> "State":
        state = State()
        state.last_run = datetime.fromisoformat(data["last_run"])
        state.result_dir = data["result_dir"]
        state.results_root_dir = data["results_root_dir"]
        state.simulation_plan_file_path = data["simulation_plan_file_path"]
        state.quisp_root = data["quisp_root"]
        state.quisp_workdir = data["quisp_workdir"]
        state.ned_path = data["ned_path"]
        state.num_simulations = data["num_simulations"]
        state.num_finished = data["num_finished"]
        state.git_commit_rev = data["git_commit_rev"]
        state.loaded = True
        return state
