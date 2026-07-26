import sum as sum_module


def test_squares_default():
    assert sum_module.squares() == ["1:1", "2:4", "3:9", "4:16", "5:25"]


def test_squares_custom_n():
    assert sum_module.squares(2) == ["1:1", "2:4"]


def test_squares_non_positive_n():
    assert sum_module.squares(0) == []


def test_name_prints_each_square(capsys):
    sum_module.name(3)
    assert capsys.readouterr().out == "1:1\n2:4\n3:9\n"
