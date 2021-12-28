from dataclasses import dataclass

from typing import Dict

from quisp_run.sim_setting import SimSetting


@dataclass
class Result:
    num_buf: int
    num_total_events: int
    final_events_per_sec: float
    setting: SimSetting
    user_time_str: str = ""
    sys_time_str: str = ""
    real_time_str: str = ""

    def to_dict(self) -> Dict:
        return {
            "num_buf": self.num_buf,
            "num_total_events": self.num_total_events,
            "final_events_per_sec": self.final_events_per_sec,
            "sys": self.sys_time_str,
            "user": self.user_time_str,
            "real": self.real_time_str,
        }
