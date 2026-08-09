import json

from tests.test_latest_videos import MKBHD_ID, route_fetch
from youtube_latest import main


def test_human_output_lists_videos(monkeypatch, capsys):
    route_fetch(monkeypatch)
    code = main(["@mkbhd", "-n", "2"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Marques Brownlee" in out
    assert "Newest Long-Form Video" in out
    assert "https://www.youtube.com/watch?v=vid00000001" in out


def test_json_output_is_flat_list_and_iso_dates(monkeypatch, capsys):
    route_fetch(monkeypatch)
    code = main(["@mkbhd", "-n", "1", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert isinstance(data, list)
    assert data[0]["published"] == "2026-08-08T15:00:00+00:00"
    assert data[0]["video_id"] == "vid00000001"
    assert data[0]["channel_handle"] == "@mkbhd"
    assert data[0]["channel_name"] == "Marques Brownlee"
    assert data[0]["description"] == "A deep dive into the newest gadget."


def test_exit_code_1_when_any_channel_errors(monkeypatch, capsys):
    route_fetch(monkeypatch)
    code = main(["@nosuchchannel", "@mkbhd"])
    out = capsys.readouterr().out
    assert code == 1
    assert "error" in out.lower()


def test_human_output_groups_by_channel(monkeypatch, capsys):
    route_fetch(monkeypatch)
    code = main(["@mkbhd", MKBHD_ID, "-n", "1"])
    out = capsys.readouterr().out
    assert code == 0
    # channel header should appear once per channel, not once per video
    assert out.count("Marques Brownlee (@mkbhd)") == 1
    assert out.count(f"Marques Brownlee ({MKBHD_ID})") == 1


def test_include_shorts_flag_uses_mixed_feed(monkeypatch, capsys):
    route_fetch(monkeypatch)
    code = main(["@mkbhd", "-n", "3", "--include-shorts", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    titles = [d["title"] for d in data]
    assert titles == ["Newest Video", "Middle Video", "Oldest Video"]
