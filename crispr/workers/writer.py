import pickle, os
from typing import Dict
from crispr.simulation import SimContext


class Writer:
    """Simulation log writer"""

    context: SimContext
    results: Dict

    def __init__(self, ctx: SimContext):
        self.context = ctx
        self.results = {"__params__": ctx.param_keys}

    async def run(self):
        while True:
            result = None
            try:
                result = await self.context.results.get()
            except RuntimeError as e:
                self.context.log("[red]Writer Error: ", e)
            if result is None:
                break
            self.results[result.sim_name] = result.to_dict()
            with open(os.path.join(self.context.result_dir, "results.pickle"), "wb") as f:
                pickle.dump(self.results, f)
            self.context.log(result.to_log_str())
