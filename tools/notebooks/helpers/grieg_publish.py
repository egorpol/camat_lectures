"""Grieg's Vöglein: the edition folder as a GitHub repository, and its live page.

Pasted after grieg_linking.py in the same cell; it uses that file's functions.
The repository is the folder grieg_edition_work/edition itself, so the other
notebooks keep working on the same files and the relative image paths stay valid.
"""

import re
import subprocess
import tempfile
import urllib.error
import urllib.request

COURSE_SITE = "https://egorpol.github.io/camat_lectures/"
WORK_ID = "voglein"
GITIGNORE = """# Written by the notebooks for your own checks; not part of the edition
validation-*/
overlays/
checkpoints/
# The live page, built by GitHub Actions
_site/
"""
WORKFLOW = """name: Live page
# Builds the live page with CAMAT's site builder and publishes it with GitHub Pages,
# each time a commit arrives on GitHub.
on:
  push:
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"
      - run: pip install camat==0.2.8
      - run: camat-build-site site.json _site
      - uses: actions/upload-pages-artifact@v5
        with:
          path: _site
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v5
"""


def open_repository_folder(project):
    """Continue from 03_grieg_linking: the edition folder with the linked work.mei."""
    project = Path(project).resolve()
    edition = project / "edition"
    work = edition / "mei/work.mei"
    if not (work.is_file() and "<facsimile" in work.read_text(encoding="utf-8")):
        raise FileNotFoundError("This notebook continues from 03_grieg_linking.ipynb. Run that notebook to the end "
                                "first, in the same folder, then run this cell again.")
    context = load_inputs(project)
    context["edition"] = edition
    print("The folder that becomes your repository:", _short(edition, project))
    return context


def _git(context, *args):
    """Run git in the edition folder: (ok, output)."""
    try:
        done = subprocess.run(["git", *args], cwd=context["edition"], capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        return False, "git is not installed or not on the PATH"
    except subprocess.TimeoutExpired:
        return False, "git did not answer within a minute"
    return done.returncode == 0, (done.stdout or done.stderr).strip()


def _write_once(path, text, label):
    """Write a file the first time; later keep it, so that your own changes stay."""
    if path.exists():
        same = path.read_text(encoding="utf-8") == text
        print(f"  {label}: {'already there' if same else 'already there, with your changes; kept as it is'}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  {label}: written")


def _readme(context, names):
    witness = context["sources"]["printed_witness"]
    names = names.strip() or "(your names)"
    return f"""# Grieg, *Vöglein*, Op. 43 No. 4: a facsimile-linked edition

A student edition from the seminar [From Digital Edition to Computational Music Analysis]({COURSE_SITE})
(winter 2026/27). Every bar of the MEI file is linked to its place on two page images of the printed source.

- `mei/work.mei`: the edition, by {names}. It starts from the encoding by Maja Hartwig and Kristina Richts in the
  [MEI Sample Collection](https://github.com/music-encoding/sample-encodings) (ECL-2.0, see `LICENSE-encoding.txt`;
  the file declares itself public domain). Its header records what was changed, by whom and when.
- `pages/`: printed pages 42 and 43 of Edvard Grieg, *Klavierwerke*, vol. 1, ed. Hermann Kretzschmar, Leipzig:
  C. F. Peters, plate 8800, from [IMSLP file {witness['imslp_file_id']}](https://imslp.org/wiki/Special:ImagefromIndex/{witness['imslp_file_id']})
  (public domain; scanned by piupianissimo), drawn at 300 dpi. `pages/boxes/` holds the box of each bar; `pages/pages.json` and
  `alignment.json` are CAMAT's records of the pages and boxes.
- `reviews/`: the peer-review sheet, once it is written.
"""


def prepare_repository(context, names=""):
    """Write README, licence and .gitignore into the edition folder, and list what will be published."""
    edition = context["edition"]
    print("In the edition folder:")
    _write_once(edition / "README.md", _readme(context, names), "README.md, the description on GitHub")
    _write_once(edition / "LICENSE-encoding.txt", (context["inputs"] / "LICENSE").read_text(encoding="utf-8"),
                "LICENSE-encoding.txt, the licence of the encoding")
    _write_once(edition / ".gitignore", GITIGNORE, ".gitignore, the folders Git leaves out")
    ignored = ("validation-", "overlays", "checkpoints", "_site", ".git")
    files = sorted(p for p in edition.rglob("*") if p.is_file()
                   and not any(part.startswith(ignored) for part in p.relative_to(edition).parts))
    print(f"\nWhat goes into the repository ({len(files)} files, {sum(p.stat().st_size for p in files) / 1e6:.1f} MB):")
    for path in files:
        print(f"  {path.relative_to(edition).as_posix():<40} {path.stat().st_size / 1000:>6.0f} KB")
    print("\nLeft out: the check reports (validation-…), the pictures with boxes drawn on them (overlays),")
    print("the copies before linking and editing (checkpoints), and the PDFs, which are outside this folder.")
    print(f"\nThe folder to open in VS Code:\n  {edition}")


def check_repository(context):
    """Is the edition folder a repository, and does GitHub have its last commit? Prints the links."""
    if not (context["edition"] / ".git").is_dir():
        print("The edition folder is not a repository yet. Publish it from VS Code (the steps above), "
              "then run this cell again.")
        return
    ok, branch = _git(context, "branch", "--show-current")
    ok2, remote = _git(context, "remote", "get-url", "origin")
    if not ok:
        print(f"git did not work: {branch}")
        return
    found = re.match(r"(?:https://github\.com/|git@github\.com:)([^/]+)/([^/]+?)(?:\.git)?/?$", remote) if ok2 else None
    if not found:
        print("The repository has no address on GitHub yet. In VS Code, click Publish Branch in the "
              "Source Control view, then run this cell again.")
        return
    owner, repo = found.groups()
    _, head = _git(context, "rev-parse", "HEAD")
    _, changed = _git(context, "status", "--porcelain")
    ok3, listed = _git(context, "ls-remote", f"https://github.com/{owner}/{repo}.git", f"refs/heads/{branch}")
    on_github = listed.split()[0] if ok3 and listed else None
    context["github"] = {"owner": owner, "repo": repo, "branch": branch, "commit": on_github}
    print(f"Your repository: https://github.com/{owner}/{repo} (branch {branch})")
    if on_github == head:
        print("✓ GitHub has your last commit.")
    elif on_github:
        print("! GitHub has an older commit than your folder. In VS Code, click Sync Changes, then run this cell again.")
    else:
        print("✗ GitHub does not show this branch. Is the repository public, and was the push finished? "
              "Run the cell again in a minute.")
        return
    if changed:
        files = [line[3:] for line in changed.splitlines()]
        print(f"! Not committed yet ({len(files)}): {', '.join(files[:6])}{' …' if len(files) > 6 else ''}")
    raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{on_github}/mei/work.mei"
    print(f"\nYour file in mei-friend (as in the commit GitHub has now):\n  https://mei-friend.mdw.ac.at/?file={raw}")


def write_live_page(context, title="Grieg, Vöglein, Op. 43 No. 4", names=""):
    """Write site.json and the GitHub Actions workflow, and build the site once here to check it."""
    from camat.web_edition import SiteConfigError, build_site
    edition = context["edition"]
    repo = context.get("github", {}).get("repo", "grieg-voglein")
    config = {
        "title": title,
        "subtitle": "A facsimile-linked edition" + (f" by {names.strip()}" if names.strip() else ""),
        "storage_prefix": re.sub(r"[^a-z0-9-]", "-", repo.lower()),
        "works": [{"id": WORK_ID, "title": "Vöglein", "mei": "mei/work.mei"}],
        "facsimile": {"type": "pdf", "pages": "pages/pages.json", "pdf": False, "images": {"copy": True}},
    }
    print("In the edition folder:")
    _write_once(edition / "site.json", json.dumps(config, indent=2, ensure_ascii=False) + "\n",
                "site.json, what the live page shows")
    _write_once(edition / ".github/workflows/live-page.yml", WORKFLOW,
                ".github/workflows/live-page.yml, the instructions for GitHub")
    with tempfile.TemporaryDirectory() as folder:
        try:
            report = build_site(edition / "site.json", Path(folder) / "site")
        except SiteConfigError as error:
            print("\n✗ The page cannot be built yet:")
            for problem in error.problems:
                print("  ", problem)
            return
    work = report["works"][0]
    print(f"\n✓ Built a test copy here: {work['measures']} bars, {work['measures_with_zone']} of them with a box, "
          f"{work['facsimile_pages']} page images, {report['bytes'] / 1e6:.1f} MB. GitHub builds the same.")


def check_live_page(context):
    """Is the live page online? Prints its address."""
    github = context.get("github")
    if not github:
        print("Run the repository check in part 1 first.")
        return
    owner, repo = github["owner"], github["repo"]
    url = f"https://{owner.lower()}.github.io/{repo}/"
    try:
        with urllib.request.urlopen(urllib.request.Request(url + "works.json", headers={"User-Agent": "camat-seminar"}),
                                    timeout=30) as answer:
            online = answer.status == 200
    except urllib.error.HTTPError:
        online = False
    except urllib.error.URLError as problem:
        print(f"The page could not be reached ({problem.reason}). Check the internet connection and run the cell again.")
        return
    if online:
        print(f"✓ Your live page is online:\n  {url}")
        print(f"  A link to one bar, for example bar 20:  {url}#{WORK_ID}/20")
        print("If it still shows an older state, wait a minute and reload the page (Ctrl+Shift+R, on a Mac Cmd+Shift+R).")
    else:
        print(f"Not online yet: {url}")
        print(f"Look at https://github.com/{owner}/{repo}/actions: a run of 'Live page' takes about a minute. "
              "A red cross means it failed: click it to see why. No run at all: check that Settings → Pages "
              "→ Source says GitHub Actions, and that you clicked Sync Changes.")
