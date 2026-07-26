import pytest

import multiply


@pytest.mark.parametrize(
    "a,b,expected",
    [(2, 4, 8), (0, 5, 0), (-3, 3, -9), (2.5, 2, 5.0), ("ab", 2, "abab")],
)
def test_multiply(a, b, expected):
    assert multiply.multiply(a, b) == expected


def test_main_output(capsys):
    multiply.main()
    assert capsys.readouterr().out == "8\n"
