import json

from tests.test_latest_videos import route_fetch
from youtube_latest import main


def test_human_output_lists_videos(monkeypatch, capsys):
    route_fetch(monkeypatch)
    code = main(["@mkbhd", "-n", "2"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Marques Brownlee" in out
    assert "Newest Video" in out
    assert "https://www.youtube.com/watch?v=vid00000001" in out


def test_json_output_is_valid_and_iso_dates(monkeypatch, capsys):
    route_fetch(monkeypatch)
    code = main(["@mkbhd", "-n", "1", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data[0]["videos"][0]["published"] == "2026-08-08T15:00:00+00:00"


def test_exit_code_1_when_any_channel_errors(monkeypatch, capsys):
    route_fetch(monkeypatch)
    code = main(["@nosuchchannel", "@mkbhd"])
    out = capsys.readouterr().out
    assert code == 1
    assert "error" in out.lower()
