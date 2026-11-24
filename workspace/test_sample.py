import time


def test_scopeguard():
    time.sleep(1)
    assert 2 + 2 == 4
