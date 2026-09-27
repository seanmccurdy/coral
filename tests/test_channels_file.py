import json

import pytest

from tests.test_latest_videos import route_fetch
from youtube_latest import latest_videos_from_file, main


def write_channels(tmp_path, content):
    path = tmp_path / "channels.txt"
    path.write_text(content)
    return path


def test_reads_one_channel_per_line(monkeypatch, tmp_path):
    route_fetch(monkeypatch)
    path = write_channels(tmp_path, "@mkbhd\nmkbhd\n")
    results = latest_videos_from_file(path, n=1)
    assert [r["channel_handle"] for r in results] == ["@mkbhd", "@mkbhd"]


def test_skips_blank_lines_comments_and_whitespace(monkeypatch, tmp_path):
    route_fetch(monkeypatch)
    path = write_channels(
        tmp_path,
        "# my favourite channels\n\n  @mkbhd  \n\n# another comment\n",
    )
    results = latest_videos_from_file(path, n=1)
    assert [r["channel_handle"] for r in results] == ["@mkbhd"]


def test_kwargs_pass_through(monkeypatch, tmp_path):
    route_fetch(monkeypatch)
    path = write_channels(tmp_path, "@mkbhd\n")
    results = latest_videos_from_file(path, n=2)
    assert len(results) == 2


def test_missing_file_raises_file_not_found(tmp_path):
    try:
        latest_videos_from_file(tmp_path / "nope.txt")
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_cli_file_flag(monkeypatch, tmp_path, capsys):
    route_fetch(monkeypatch)
    path = write_channels(tmp_path, "@mkbhd\n")
    code = main(["-f", str(path), "-n", "1", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data[0]["channel_handle"] == "@mkbhd"


def test_cli_file_flag_combines_with_positional_channels(monkeypatch, tmp_path, capsys):
    route_fetch(monkeypatch)
    path = write_channels(tmp_path, "@mkbhd\n")
    code = main(["mkbhd", "-f", str(path), "-n", "1", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    # positional channels first, then the file's channels
    assert [d["channel_handle"] for d in data] == ["@mkbhd", "@mkbhd"]


def test_cli_requires_channels_or_file(capsys):
    with pytest.raises(SystemExit) as e:
        main([])
    assert e.value.code == 2
    assert "channel" in capsys.readouterr().err.lower()
