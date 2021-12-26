from typing import List
from dataclasses import dataclass
from enum import Enum


class OmnetppEnv(Enum):
    Cmdenv = "Cmdenv"
    Qtenv = "Qtenv"


@dataclass
class Command:
    exe_path: str
    ui: OmnetppEnv
    config_ini_file: str
    config_name: str
    ned_path: str
    opts: list

    def to_str(self) -> str:
        return " ".join(self.to_list())

    def to_list(self) -> List[str]:
        exe_path = "./quisp"
        cmd = [
            exe_path,
            "-u",
            self.ui,
            self.config_ini_file,
            "-c",
            self.config_name,
            "-n",
            self.ned_path,
        ]
        if self.opts:
            cmd += self.opts
        return cmd
