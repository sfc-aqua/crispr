from .utils import parse_time


def test_parse_time():
    assert parse_time("1m40.0s") == 100.0
    assert parse_time("0m5.733s") == 5.733
