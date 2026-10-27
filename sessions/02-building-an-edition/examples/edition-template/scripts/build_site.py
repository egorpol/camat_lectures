"""Build the static edition, with downloadable MEI and a source-commit record."""
import hashlib
import html
import json
from pathlib import Path
import subprocess
import shutil

from camat.web_edition import build_site

ROOT = Path(__file__).resolve().parents[1]


def main():
    target = ROOT / "_site"
    report = build_site(ROOT / "site.json", target)
    mei = ROOT / "mei/work.mei"
    sha = hashlib.sha256(mei.read_bytes()).hexdigest()
    revision = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--show-toplevel"], text=True, capture_output=True)
    commit = None
    dirty = None
    # A template inside the lecture checkout must not inherit the lecture commit.
    if revision.returncode == 0 and Path(revision.stdout.strip()).resolve() == ROOT:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", "HEAD"], text=True, capture_output=True)
        commit = head.stdout.strip() if head.returncode == 0 else None
        dirty = bool(subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=normal"], text=True).strip())
    review = json.loads((ROOT / "review.json").read_text())
    publication = {"source_commit": commit, "working_tree_dirty": dirty,
                   "build_kind": "Git commit" if commit and not dirty else "local/draft preview",
                   "mei_sha256": sha, "download_mei": "mei/work.mei",
                   "review_matches_mei": review.get("input_mei_sha256") == sha,
                   "review": review, "scope": "Three teaching tasks; not a full-piece edition",
                   "camat_build": report}
    (target / "publication.json").write_text(json.dumps(publication, indent=2) + "\n")
    shutil.copytree(ROOT / "LICENSES", target / "LICENSES")
    shutil.copyfile(ROOT / "NOTICES.md", target / "NOTICES.md")
    coverage = ROOT / "validation-runtime/coverage.json"
    if coverage.exists():
        (target / "validation-coverage.json").write_bytes(coverage.read_bytes())
    notes = (ROOT / "SOURCE.md").read_text()
    (target / "source-notes.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Source and PDF instructions</title>'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<body style="max-width:75ch;margin:2rem auto;padding:1rem;font:18px/1.6 system-ui">'
        '<h1>Source and PDF instructions</h1><pre style="white-space:pre-wrap;font:inherit">'
        + html.escape(notes) + '</pre><p><a href="index.html">Return to the edition</a></p></body></html>')
    assert hashlib.sha256((target / "mei/work.mei").read_bytes()).hexdigest() == sha
    print(f"Built {target}; MEI SHA-256 {sha}; source commit {commit or 'not yet committed'}")


if __name__ == "__main__":
    main()
