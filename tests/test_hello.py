import hello


def test_build_list_replaces_first_element():
    assert hello.build_list() == [3, 2, 3, "h", "gf"]


def test_main_output(capsys):
    hello.main()
    assert capsys.readouterr().out == "hello\ngf\n"
