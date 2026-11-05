"""Generate a PEP 503 "simple" package index from GitHub Release assets.

Wheels are far too large for PyPI, so they are attached to GitHub Releases.
This script turns the release list into a static index that pip and uv can
consume, so users can install by name:

    pip install opencv-python-cuda --extra-index-url https://breakthrough.github.io/opencv-python-cuda/packages/

Output layout (under --out; the "packages" directory name is configurable via
--index-dir, PEP 503 does not require any particular path):

    packages/index.html                    list of projects
    packages/<project>/index.html          one <a> per wheel, href = release
                                           download URL + "#sha256=<hex>"

Hashes come from the GitHub API's per-asset "digest" field, so nothing is
downloaded. Draft releases are skipped; prereleases are included unless
--stable-only is given. Exits nonzero if no wheels were found, so an empty
index is never deployed.

Usage:
    python tools/gen_simple_index.py --out <dir>
    python tools/gen_simple_index.py --json releases.json --out <dir>  (offline)

Set GITHUB_TOKEN to raise the API rate limit (optional; CI passes it).
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.request

DEFAULT_REPO = "Breakthrough/opencv-python-cuda"
REQUIRES_PYTHON = ">=3.7"
DEFAULT_INDEX_DIR = "packages"
API_ROOT = "https://api.github.com"


def normalize_name(name):
    """PEP 503 project-name normalization."""
    return re.sub(r"[-_.]+", "-", name).lower()


def fetch_releases(repo, token=None):
    """Return all releases for repo, following Link: rel="next" pagination."""
    url = "%s/repos/%s/releases?per_page=100" % (API_ROOT, repo)
    releases = []
    while url:
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        req.add_header("User-Agent", "gen_simple_index.py")
        if token:
            req.add_header("Authorization", "Bearer " + token)
        with urllib.request.urlopen(req) as resp:
            releases.extend(json.loads(resp.read().decode("utf-8")))
            url = _next_link(resp.headers.get("Link", ""))
    return releases


def _next_link(link_header):
    for part in link_header.split(","):
        m = re.match(r'\s*<([^>]+)>;\s*rel="next"', part)
        if m:
            return m.group(1)
    return None


def collect_wheels(releases, stable_only=False):
    """Return {project: [entry, ...]} in release order (newest first)."""
    projects = {}
    for rel in releases:
        if rel.get("draft"):
            continue
        if stable_only and rel.get("prerelease"):
            continue
        for asset in rel.get("assets", []):
            name = asset.get("name", "")
            if not name.endswith(".whl"):
                continue
            dist = name.split("-", 1)[0]
            project = normalize_name(dist)
            digest = asset.get("digest") or ""
            sha256 = ""
            if digest.startswith("sha256:"):
                sha256 = digest[len("sha256:"):]
            else:
                print("WARNING: no sha256 digest for %s; link will have no hash"
                      % name, file=sys.stderr)
            projects.setdefault(project, []).append({
                "filename": name,
                "url": asset["browser_download_url"],
                "sha256": sha256,
                "size": asset.get("size", 0),
                "tag": rel.get("tag_name", ""),
                "prerelease": bool(rel.get("prerelease")),
            })
    return projects


def render_root(projects):
    lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="pypi:repository-version" content="1.0">',
        "<title>Package index</title>",
        "</head>",
        "<body>",
    ]
    for project in sorted(projects):
        lines.append('<a href="%s/">%s</a>' % (project, html.escape(project)))
    lines += ["</body>", "</html>", ""]
    return "\n".join(lines)


def render_project(project, entries):
    lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="pypi:repository-version" content="1.0">',
        "<title>Links for %s</title>" % html.escape(project),
        "</head>",
        "<body>",
        "<h1>Links for %s</h1>" % html.escape(project),
    ]
    for e in entries:
        href = e["url"]
        if e["sha256"]:
            href += "#sha256=" + e["sha256"]
        size_mib = e["size"] / (1024.0 * 1024.0)
        kind = "prerelease" if e["prerelease"] else "release"
        lines.append("<!-- %s (%s), %.1f MiB -->" % (e["tag"], kind, size_mib))
        lines.append('<a href="%s" data-requires-python="%s">%s</a><br>' % (
            html.escape(href, quote=True),
            html.escape(REQUIRES_PYTHON, quote=True),
            html.escape(e["filename"]),
        ))
    lines += ["</body>", "</html>", ""]
    return "\n".join(lines)


def write_ascii(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = text.encode("ascii")  # raises if anything non-ASCII slipped in
    with open(path, "wb") as f:
        f.write(data)


def main():
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("--repo", default=DEFAULT_REPO, help="OWNER/NAME (default: %(default)s)")
    ap.add_argument("--out", default="index-out", help="output directory (default: %(default)s)")
    ap.add_argument("--index-dir", default=DEFAULT_INDEX_DIR,
                    help="name of the index directory under --out (default: %(default)s)")
    ap.add_argument("--json", help="read releases from this saved API response instead of GitHub")
    ap.add_argument("--stable-only", action="store_true", help="exclude prereleases")
    args = ap.parse_args()

    if args.json:
        with open(args.json, "r", encoding="utf-8") as f:
            releases = json.load(f)
    else:
        releases = fetch_releases(args.repo, os.environ.get("GITHUB_TOKEN"))

    projects = collect_wheels(releases, stable_only=args.stable_only)
    total = sum(len(v) for v in projects.values())
    if total == 0:
        print("ERROR: no wheel assets found in %d releases; refusing to write an empty index"
              % len(releases), file=sys.stderr)
        return 1

    index_dir = os.path.join(args.out, args.index_dir)
    write_ascii(os.path.join(index_dir, "index.html"), render_root(projects))
    for project, entries in projects.items():
        write_ascii(os.path.join(index_dir, project, "index.html"),
                    render_project(project, entries))
        print("%s: %d wheel(s)" % (project, len(entries)))
        for e in entries:
            print("  %s  (%s)" % (e["filename"], e["tag"]))
    print("wrote index to %s" % index_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
