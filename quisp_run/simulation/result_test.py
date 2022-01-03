from .result import Result


def test_create_result():
    res = Result(num_buf=10, num_total_events=100, final_events_per_sec=10.0)
    assert res.num_buf == 10
    assert res.num_total_events == 100
    assert res.final_events_per_sec == 10.0


def test_serialize_result():
    res = Result(num_buf=10, num_total_events=100, final_events_per_sec=10.0)
    d = res.to_dict()
    res2 = Result.from_dict(d)
    assert res.num_buf == res2.num_buf
    assert res.num_total_events == res2.num_total_events
