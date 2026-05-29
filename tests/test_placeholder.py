from workshop import cli


def test_cli_main_exists():
    assert callable(cli.main)
