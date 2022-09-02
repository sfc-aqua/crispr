import pickle
import pandas as pd
from typing import List, Tuple, Any, Dict, TypedDict, Optional
from pandas import DataFrame
from matplotlib.axes import Axes

# QNodeAddre, QNicType, QNicIndex, QubitIndex
QubitKey = Tuple[int, int, int, int]

# Start, End, DurationType
Duration = Tuple[float, float, str]
BPAnnotation = Tuple[str, float, str]


class DurationCollector(TypedDict):
    last: Optional[float]
    usage: List[Duration]


class DurationResults(TypedDict):
    busy_times: "DurationCollectorDict"
    allocation_times: "DurationCollectorDict"
    bp_annotations: "List[BPAnnotation]"
    bp_lifetimes: "DurationCollectorDict"


DurationCollectorDict = Dict[QubitKey, DurationCollector]


def pivot_by_cond(df, params, x="num_node", value="user", cond=dict()):
    _df = df.query(" and ".join([f"{k} == {cond[k]}" for k in cond])) if cond else df

    def skip_elem(arr, elem):
        """Return a new array with the element removed."""
        return [e for e in arr if e != elem]

    return (
        _df.set_index(params)
        .reset_index(x)
        .pivot_table(index=x, columns=skip_elem(params, x), values=value)
    )


def load_results_from_pickle() -> "Tuple[DataFrame, List[str], List[Any], List[str]]":
    """load DataFrame, parameters, dataset and simulation names from './results.pickle' """
    with open("results.pickle", "rb") as f:
        dataset = pickle.load(f)
        all_params = dataset["__params__"]
        df = pd.DataFrame([dataset[k] for k in dataset if k != "__params__"])
        print(len(dataset), "results found")
        # removed keys to reduce params
        removed_keys = [k for k in df.columns if len(df[k].unique()) == 1]
        params = [k for k in all_params if k not in removed_keys]
        print("params: ", params)
        sim_names = [k for k in dataset.keys() if k != "__params__"]
        return df, params, dataset, sim_names


def load_logs_from_jsonl(sim_names: "List[str]") -> "Dict[str, DataFrame]":
    """this method loads the simulation results as a dict of DataFrames from jsonl files under 'results' dir"""
    logs = {}
    for sim_name in sim_names:
        logs[sim_name] = pd.read_json(
            f"./results/{sim_name}.jsonl", orient="records", lines=True
        )
    return logs


def record_to_qubit_key(record) -> "QubitKey":
    """this generates a qubit key tuple from 'BellPairGenerated', 'BellPairErased', and 'QubitStateChange' record"""
    return (
        record["address"],
        record["qnic_type"],
        record["qnic_index"],
        record["qubit_index"],
    )


def collect_duration_results(log: "DataFrame") -> "DurationResults":

    log = log.query(
        "event_type == 'BellPairGenerated' or event_type == 'BellPairErased' or event_type == 'QubitStateChange'"
    ).astype(
        {
            "address": "int32",
            "qnic_type": "int32",
            "qnic_index": "int32",
            "qubit_index": "int32",
        }
    )

    log["key"] = log.apply(record_to_qubit_key, axis=1)
    busy_times: "DurationCollectorDict" = {}
    allocation_times: "DurationCollectorDict" = {}
    bp_annotations: "List[Tuple[str, float, str]]" = []
    bp_lifetimes: "DurationCollectorDict" = {}
    last_bp_record: "Dict[QubitKey, Any]" = {}

    # collect event durations as tuple (start, end, data_kind)
    # this for loop iterates each event
    for _, rec in log.iterrows():
        key: QubitKey = rec["key"]
        event_type = rec["event_type"]
        now = rec["simtime"]

        # if busy: true, put the time into "last"
        # in later iteration, it finds busy: false,
        # and push the tuple (start, duration, data_kind) into "usage"
        if event_type == "QubitStateChange":
            if key not in busy_times:
                busy_times[key] = {"last": None, "usage": []}
            if key not in allocation_times:
                allocation_times[key] = {"last": None, "usage": []}

            if rec["busy"]:
                if busy_times[key]["last"] == None:
                    busy_times[key]["last"] = now
            else:
                last = busy_times[key]["last"]
                if last:
                    busy_times[key]["usage"].append((last, now - last, "qubit_busy"))
                    busy_times[key]["last"] = None

            if rec["allocated"]:
                if allocation_times[key]["last"] == None:
                    allocation_times[key]["last"] = now
            else:
                last = allocation_times[key]["last"]
                if last:
                    allocation_times[key]["usage"].append(
                        (last, now - last, "qubit_allocation")
                    )
                    allocation_times[key]["last"] = None

        elif event_type == "BellPairGenerated":
            bp_annotations.append(
                ("{}".format(int(rec["partner_addr"])), rec["simtime"], str(rec["key"]))
            )
            if key not in bp_lifetimes:
                bp_lifetimes[key] = {"last": rec["simtime"], "usage": []}

            last = bp_lifetimes[key]["last"]
            if key == (0, 0, 0, 9):
                print(f"bp gen log: {key} at ", rec["simtime"])

            if last is None:
                # normal case: just mark the simtime
                bp_lifetimes[key]["last"] = rec["simtime"]
            else:
                if key in last_bp_record:
                    if last_bp_record[key]["event_type"] == "BellPairGenerated":
                        raise RuntimeError(f"Invalid bp log state: {now} {key}")
                    if last_bp_record[key]["simtime"] == now:
                        bp_lifetimes[key]["usage"].append((last, now - last, "bp"))
                        bp_lifetimes[key]["last"] = None
                        del last_bp_record[key]

                else:
                    last_bp_record[key] = rec

        elif event_type == "BellPairErased":
            assert key in bp_lifetimes, f"Invalid bp log for qubit {key} at {now}. bp erased before generated"

            last = bp_lifetimes[key]["last"]
            if last is not None:
                bp_lifetimes[key]["usage"].append((last, now - last, "bp"))
                bp_lifetimes[key]["last"] = None
            else:
                if key in last_bp_record:
                    if last_bp_record[key]["simtime"] == now and last_bp_record[key]["event_type"] == "BellPairGenerated":
                        bp_lifetimes[key]["usage"].append((last, now - last, "bp"))
                        bp_lifetimes[key]["last"] = None

                if key == (0, 0, 0, 9):

                    print(f"invalid bp erased log: {key} at ", rec["simtime"])
                # raise RuntimeError(f"Invalid bp log: {key}")

    return {
        "busy_times": busy_times,
        "allocation_times": allocation_times,
        "bp_annotations": bp_annotations,
        "bp_lifetimes": bp_lifetimes,
    }


def calc_durations(log):
    results = collect_duration_results(log)

    def duration_to_tuples(
        durations: "DurationCollectorDict",
    ) -> "Tuple[List[str], List[float], List[float], List[str]]":
        usages: "List[Tuple[str,float, float, str]]" = []
        for key in durations:
            d: "DurationCollector" = durations[key]
            for us in d["usage"]:
                usages.append((str(key), us[0], us[1], us[2]))
        usages = sorted(usages)
        usages.reverse()
        titles, begins, width, ts = zip(*usages)
        return (titles, begins, width, ts)  # type: ignore

    return {
        "qubit_allocation": duration_to_tuples(results["allocation_times"]),
        "qubit_busy": duration_to_tuples(results["busy_times"]),
        "bp_lifetime": duration_to_tuples(results["bp_lifetimes"]),
        "bp_annotations": results["bp_annotations"],
    }


class PlotConfig(TypedDict):
    height: float
    color: str


PLOT_CONFIGS: "Dict[str, PlotConfig]" = {
    "qubit_busy": {"color": "#3475D0", "height": 0.8},
    "qubit_allocation": {"color": "#34D5D0", "height": 0.55},
    "bp_lifetime": {"color": "#E64646", "height": 0.25},
}


def plot_timeline(
    ax: "Axes", timelines, data_kind: "str", config: "Optional[PlotConfig]" = None
):
    if data_kind not in timelines:
        raise RuntimeError(
            f"data_kind: {data_kind} is not defined in timelines. pass proper data_kind: {list(timelines.keys())}"
        )
    timeline = timelines[data_kind]
    if config is None:
        if data_kind not in PLOT_CONFIGS:
            raise RuntimeError(
                f"data_kind: {data_kind} is not defined in PLOT_CONFIGS. pass config or specify proper data_kind: {list(PLOT_CONFIGS.keys())}"
            )
        config = PLOT_CONFIGS[data_kind]

    ax.barh(
        y=timeline[0],
        left=timeline[1],
        width=timeline[2],
        color=config["color"],
        height=config["height"],
        linewidth=0.5,
        edgecolor="black",
        alpha=0.5,
        label="qubit allocated by RuleEngine",
    )
