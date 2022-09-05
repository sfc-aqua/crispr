import pandas as pd
import math
from .analysis_utils import collect_duration_results

s = '''
{
  "simtime": {
    "79": 0.1,
    "210": 0.2,
    "269": 0.3,
    "279": 0.3,
    "696": 0.4,
    "772": 0.5,
    "837": 0.6,
    "844": 0.6,
    "984": 0.7,
    "990": 0.7
  },
  "event_type": {
    "79": "BellPairGenerated",
    "210": "BellPairErased",
    "269": "BellPairGenerated",
    "279": "BellPairErased",
    "696": "BellPairGenerated",
    "772": "BellPairErased",
    "837": "BellPairErased",
    "844": "BellPairGenerated",
    "984": "BellPairGenerated",
    "990": "BellPairErased"
  },
  "address": {
    "79": 2,
    "210": 2,
    "269": 2,
    "279": 2,
    "696": 2,
    "772": 2,
    "837": 2,
    "844": 2,
    "984": 2,
    "990": 2
  },
  "qnic_type": {
    "79": 0,
    "210": 0,
    "269": 0,
    "279": 0,
    "696": 0,
    "772": 0,
    "837": 0,
    "844": 0,
    "984": 0,
    "990": 0
  },
  "qnic_index": {
    "79": 1,
    "210": 1,
    "269": 1,
    "279": 1,
    "696": 1,
    "772": 1,
    "837": 1,
    "844": 1,
    "984": 1,
    "990": 1
  },
  "qubit_index": {
    "79": 2,
    "210": 2,
    "269": 2,
    "279": 2,
    "696": 2,
    "772": 2,
    "837": 2,
    "844": 2,
    "984": 2,
    "990": 2
  },
  "partner_addr": {
    "79": 1,
    "210": 1,
    "269": 1,
    "279": 1,
    "696": 1,
    "772": 1,
    "837": 1,
    "844": 1,
    "984": 1,
    "990": 1
  }
}
'''
log = pd.read_json(s)

def assert_durations(t1, t2):
    assert math.isclose(t1[0], t2[0])
    assert math.isclose(t1[1], t2[1])
    # assert t1[2] == t2[2]

def test_collect_durations_results():
    results = collect_duration_results(log) # type: ignore
    duration = results['bp_lifetimes'][(2,0,1,2)]["usage"]
    # assert len(duration) == 5
    for d in duration:
        print(d)
    assert_durations(duration[0],(0.1,0.1, "bp"))
    assert_durations(duration[1],(0.3,0.0, "bp"))
    assert_durations(duration[2],(0.4,0.1, "bp"))
    assert_durations(duration[3],(0.6,0.0, "bp"))
    assert_durations(duration[4],(0.7,0.0, "bp"))

