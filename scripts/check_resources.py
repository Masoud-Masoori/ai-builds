#!/usr/bin/env python3
"""Check the resource hub. Standard library only.

Exit codes: 0 HELD, 1 BREACHED (reasons listed), 2 INCONCLUSIVE (network errors only).

Checks:
  1. every resources/<id>/README.md has the sections What it is, How to use it, Sources
  2. no em dash or en dash in any text file
  3. no Windows drive paths in any text file
  4. .claude-plugin/marketplace.json parses, and every plugin it lists has a source folder
     with at least one skills/<name>/SKILL.md that has name and description frontmatter
  5. every resource id linked from DM-REPLIES.md exists as a folder under resources/
  6. with --online: every http(s) link in markdown answers with a status below 400
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REQUIRED_SECTIONS = ("what it is", "how to use it", "sources")
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules"}
BAD_DASHES = {chr(0x2014): "em dash", chr(0x2013): "en dash"}
DRIVE_PATH = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")
LINK = re.compile(r"https?://[^\s)>\]\"'`<]+")
DM_ID = re.compile(r"/resources/([a-z0-9][a-z0-9-]*)")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
USER_AGENT = "Mozilla/5.0 (compatible; creator-resources-link-check/1.0)"
TIMEOUT = 15


def text_files(root):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or SKIP_DIRS & set(path.relative_to(root).parts):
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue


def rel(root, path):
    return path.relative_to(root).as_posix()


def check_sections(root):
    reasons = []
    base = root / "resources"
    if not base.is_dir():
        return ["resources/ folder is missing"]
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        readme = folder / "README.md"
        if not readme.is_file():
            reasons.append(f"resources/{folder.name}/README.md is missing")
            continue
        headings = set()
        for line in readme.read_text(encoding="utf-8").splitlines():
            match = HEADING.match(line)
            if match:
                headings.add(match.group(1).strip().lower())
        for section in REQUIRED_SECTIONS:
            if section not in headings:
                label = {"what it is": "What it is", "how to use it": "How to use it", "sources": "Sources"}[section]
                reasons.append(f"resources/{folder.name}/README.md lacks the section '{label}'")
    return reasons


def check_text(root):
    reasons = []
    for path, text in text_files(root):
        for char, label in BAD_DASHES.items():
            if char in text:
                reasons.append(f"{rel(root, path)}: contains an {label} (dash rule)")
        if DRIVE_PATH.search(text):
            reasons.append(f"{rel(root, path)}: contains a Windows drive path")
    return reasons


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    data = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip().strip("\"'")
    return None


def check_skill(root, skill_md):
    where = rel(root, skill_md)
    front = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if front is None:
        return [f"{where}: no valid frontmatter block"]
    reasons = []
    for key in ("name", "description"):
        if not front.get(key):
            reasons.append(f"{where}: frontmatter is missing {key}")
    return reasons


def check_marketplace(root):
    path = root / ".claude-plugin" / "marketplace.json"
    if not path.is_file():
        return [".claude-plugin/marketplace.json is missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f".claude-plugin/marketplace.json does not parse: {error}"]
    reasons = []
    if not isinstance(data, dict):
        return [".claude-plugin/marketplace.json is not a JSON object"]
    for key in ("name", "owner", "plugins"):
        if key not in data:
            reasons.append(f"marketplace.json is missing '{key}'")
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        reasons.append("marketplace.json 'plugins' must be a non-empty list")
        return reasons
    for entry in plugins:
        name = entry.get("name") if isinstance(entry, dict) else None
        source = entry.get("source") if isinstance(entry, dict) else None
        if not name or source is None:
            reasons.append("marketplace.json: a plugin entry lacks name or source")
            continue
        if not isinstance(source, str):
            continue  # remote sources (github, url, ...) cannot be checked offline
        if ".." in source.split("/"):
            reasons.append(f"plugin '{name}': source '{source}' contains '..'")
            continue
        plugin_dir = (root / source).resolve()
        if not plugin_dir.is_dir():
            reasons.append(f"plugin '{name}': source folder '{source}' does not exist")
            continue
        skills_dir = plugin_dir / "skills"
        skill_files = sorted(skills_dir.glob("*/SKILL.md")) if skills_dir.is_dir() else []
        if not skill_files:
            reasons.append(f"plugin '{name}': no skills/<name>/SKILL.md found under '{source}'")
        for sub in sorted(p for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.is_dir() else []:
            if not (sub / "SKILL.md").is_file():
                reasons.append(f"plugin '{name}': skill folder '{sub.name}' has no SKILL.md")
        for skill_md in skill_files:
            reasons.extend(check_skill(root, skill_md))
    return reasons


def check_dm_ids(root):
    path = root / "DM-REPLIES.md"
    if not path.is_file():
        return ["DM-REPLIES.md is missing"]
    reasons = []
    for dm_id in sorted(set(DM_ID.findall(path.read_text(encoding="utf-8")))):
        if not (root / "resources" / dm_id).is_dir():
            reasons.append(f"DM-REPLIES.md links resource '{dm_id}' but resources/{dm_id}/ does not exist")
    return reasons


def run_checks(root):
    root = Path(root)
    return check_sections(root) + check_text(root) + check_marketplace(root) + check_dm_ids(root)


def collect_links(root):
    links = []
    for path, text in text_files(Path(root)):
        if path.suffix.lower() != ".md":
            continue
        for match in LINK.findall(text):
            url = match.rstrip(".,;:!?")
            if "{" in url or "}" in url:
                continue
            links.append((rel(Path(root), path), url))
    return links


def fetch_status(url):
    """HEAD first, then GET if HEAD is refused. Network failures raise OSError."""
    headers = {"User-Agent": USER_AGENT}
    try:
        request = urllib.request.Request(url, method="HEAD", headers=headers)
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status
    except urllib.error.HTTPError:
        pass  # some servers refuse HEAD; confirm with GET
    request = urllib.request.Request(url, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def check_online(links, fetch=None):
    fetch = fetch or fetch_status
    breaches, errors, seen = [], [], set()
    for where, url in links:
        if url in seen:
            continue
        seen.add(url)
        try:
            status = fetch(url)
        except OSError as error:
            errors.append(f"{where}: {url} network error: {error}")
            continue
        if status >= 400:
            breaches.append(f"{where}: {url} returned {status}")
    return breaches, errors


def main(argv=None, root=None, fetch=None):
    parser = argparse.ArgumentParser(description="Check the resource hub.")
    parser.add_argument("--online", action="store_true", help="also check that every link answers below 400")
    args = parser.parse_args(argv)
    root = Path(root) if root else Path(__file__).resolve().parent.parent
    reasons = run_checks(root)
    errors = []
    if args.online:
        breaches, errors = check_online(collect_links(root), fetch=fetch)
        reasons += breaches
    if reasons:
        print("BREACHED")
        for reason in reasons:
            print(f"  - {reason}")
        return 1
    if errors:
        print("INCONCLUSIVE (network errors only)")
        for error in errors:
            print(f"  - {error}")
        return 2
    print("HELD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
