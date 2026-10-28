"""Tests for scripts/check_resources.py. Each BREACHED case uses a temp dir."""
import importlib.util
import json
import urllib.error
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_resources.py"
spec = importlib.util.spec_from_file_location("check_resources", SCRIPT)
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)

EM = chr(0x2014)
EN = chr(0x2013)
DRIVE = "C" + ":" + "/" + "Users"

GOOD_README = "# Thing\n\n## What it is\nx\n\n## How to use it\ny\n\n## Sources\nz\n"
GOOD_SKILL = "---\nname: demo\ndescription: Does a demo job.\n---\n\nSteps.\n"


def make_repo(root: Path) -> Path:
    (root / "resources" / "demo").mkdir(parents=True)
    (root / "resources" / "demo" / "README.md").write_text(GOOD_README, encoding="utf-8")
    plugin = root / "plugins" / "demo-plugin"
    (plugin / "skills" / "demo").mkdir(parents=True)
    (plugin / "skills" / "demo" / "SKILL.md").write_text(GOOD_SKILL, encoding="utf-8")
    (root / ".claude-plugin").mkdir()
    market = {
        "name": "demo-market",
        "owner": {"name": "Someone"},
        "plugins": [{"name": "demo-plugin", "source": "./plugins/demo-plugin"}],
    }
    (root / ".claude-plugin" / "marketplace.json").write_text(json.dumps(market), encoding="utf-8")
    (root / "DM-REPLIES.md").write_text(
        "Drafts. Each send needs the owner's approval.\n\n"
        "https://github.com/Someone/repo/tree/main/resources/demo\n",
        encoding="utf-8",
    )
    return root


def test_valid_repo_is_held(tmp_path):
    make_repo(tmp_path)
    assert cr.run_checks(tmp_path) == []
    assert cr.main([], root=tmp_path) == 0


def test_missing_section_breaches(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "resources" / "demo" / "README.md").write_text(
        "# Thing\n\n## What it is\nx\n\n## Sources\nz\n", encoding="utf-8"
    )
    reasons = cr.run_checks(tmp_path)
    assert any("How to use it" in r for r in reasons)
    assert cr.main([], root=tmp_path) == 1


def test_em_dash_breaches(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "notes.md").write_text("a " + EM + " b\n", encoding="utf-8")
    assert any("dash" in r for r in cr.run_checks(tmp_path))
    assert cr.main([], root=tmp_path) == 1


def test_en_dash_breaches(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "notes.txt").write_text("1" + EN + "2\n", encoding="utf-8")
    assert any("dash" in r for r in cr.run_checks(tmp_path))


def test_windows_drive_path_breaches(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "notes.md").write_text("see " + DRIVE + "/x\n", encoding="utf-8")
    assert any("Windows" in r for r in cr.run_checks(tmp_path))


def test_https_url_is_not_a_drive_path(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "notes.md").write_text("see https://example.com/a\n", encoding="utf-8")
    assert cr.run_checks(tmp_path) == []


def test_bad_marketplace_json_breaches(tmp_path):
    make_repo(tmp_path)
    (tmp_path / ".claude-plugin" / "marketplace.json").write_text("{not json", encoding="utf-8")
    assert any("marketplace.json" in r for r in cr.run_checks(tmp_path))


def test_missing_plugin_source_breaches(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "plugins" / "demo-plugin" / "skills" / "demo" / "SKILL.md").unlink()
    assert any("skill" in r.lower() for r in cr.run_checks(tmp_path))


def test_missing_plugin_dir_breaches(tmp_path):
    make_repo(tmp_path)
    market = {
        "name": "m",
        "owner": {"name": "S"},
        "plugins": [{"name": "ghost", "source": "./plugins/ghost"}],
    }
    (tmp_path / ".claude-plugin" / "marketplace.json").write_text(json.dumps(market), encoding="utf-8")
    assert any("ghost" in r for r in cr.run_checks(tmp_path))


def test_skill_without_description_breaches(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "plugins" / "demo-plugin" / "skills" / "demo" / "SKILL.md").write_text(
        "---\nname: demo\n---\nbody\n", encoding="utf-8"
    )
    assert any("description" in r for r in cr.run_checks(tmp_path))


def test_skill_without_name_breaches(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "plugins" / "demo-plugin" / "skills" / "demo" / "SKILL.md").write_text(
        "---\ndescription: x\n---\nbody\n", encoding="utf-8"
    )
    assert any("name" in r for r in cr.run_checks(tmp_path))


def test_dm_id_without_folder_breaches(tmp_path):
    make_repo(tmp_path)
    with (tmp_path / "DM-REPLIES.md").open("a", encoding="utf-8") as f:
        f.write("https://github.com/Someone/repo/tree/main/resources/nope\n")
    assert any("nope" in r for r in cr.run_checks(tmp_path))
    assert cr.main([], root=tmp_path) == 1


def test_online_404_breaches(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "notes.md").write_text("see https://example.com/gone\n", encoding="utf-8")
    breaches, errors = cr.check_online(cr.collect_links(tmp_path), fetch=lambda url: 404)
    assert breaches and not errors


def test_online_ok_links_pass(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "notes.md").write_text("see https://example.com/ok.\n", encoding="utf-8")
    seen = []

    def fetch(url):
        seen.append(url)
        return 200

    breaches, errors = cr.check_online(cr.collect_links(tmp_path), fetch=fetch)
    assert not breaches and not errors
    assert "https://example.com/ok" in seen  # trailing full stop stripped
    assert "https://example.com/ok." not in seen


def test_online_network_error_is_inconclusive(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "notes.md").write_text("see https://example.com/x\n", encoding="utf-8")

    def boom(url):
        raise urllib.error.URLError("offline")

    breaches, errors = cr.check_online(cr.collect_links(tmp_path), fetch=boom)
    assert not breaches and errors
    code = cr.main(["--online"], root=tmp_path, fetch=boom)
    assert code == 2


def test_online_main_breached_wins_over_inconclusive(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "notes.md").write_text("see https://example.com/x\n", encoding="utf-8")
    assert cr.main(["--online"], root=tmp_path, fetch=lambda url: 500) == 1


def test_head_then_get_fallback(monkeypatch):
    calls = []

    class Resp:
        def __init__(self, status):
            self.status = status

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout=None):
        calls.append((req.get_method(), req.get_header("User-agent"), timeout))
        if req.get_method() == "HEAD":
            raise urllib.error.HTTPError(req.full_url, 405, "no head", {}, None)
        return Resp(200)

    monkeypatch.setattr(cr.urllib.request, "urlopen", fake_urlopen)
    assert cr.fetch_status("https://example.com/") == 200
    assert [c[0] for c in calls] == ["HEAD", "GET"]
    assert all(c[1] for c in calls)
    assert all(c[2] == 15 for c in calls)
