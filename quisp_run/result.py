from dataclasses import dataclass

from typing import Dict

from quisp_run.sim_setting import SimSetting


@dataclass
class Result:
    num_buf: int
    duration: int
    num_total_events: int
    final_events_per_sec: int
    setting: SimSetting

    def to_dict(self) -> Dict:
        return {
            "num_buf": self.num_buf,
            "duration": self.duration,
            "num_total_events": self.num_total_events,
            "final_events_per_sec": self.final_events_per_sec,
        }
