import pickle
from typing import Dict
from quisp_run.simulation import SimContext


class Writer:
    """Simulation log writer"""

    context: SimContext
    results: Dict = dict()

    def __init__(self, ctx: SimContext):
        self.context = ctx

    async def run(self):
        while True:
            result = await self.context.results.get()
            if result is None:
                break
            self.results[result.setting.sim_name] = result.to_dict()
            with open("tmp_results.pickle", "wb") as f:
                pickle.dump(self.results, f)
            self.context.log(result.to_log_str())
