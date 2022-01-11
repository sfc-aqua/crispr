from .utils import parse_time


def test_parse_time():
    assert parse_time("100.0") == 100.0
    assert parse_time("5.733") == 5.733
