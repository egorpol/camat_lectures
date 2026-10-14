"""MkDocs hook: publish each session's examples and notebooks next to its page.

The sources stay in sessions/NN-slug/{examples,notebooks}/; the site serves
them at sessions/NN-slug/examples/... so the page can fetch them and link to
them for download.
"""

from pathlib import Path

from mkdocs.structure.files import File

ROOT = Path(__file__).resolve().parent.parent
FOLDERS = ("examples", "notebooks")


def on_files(files, config):
    for session in sorted((ROOT / "sessions").glob("[0-9][0-9]-*")):
        for folder in FOLDERS:
            for path in sorted((session / folder).rglob("*")):
                if not path.is_file() or path.name.startswith(".") or "__pycache__" in path.parts:
                    continue
                if path.suffix == ".md":
                    continue
                files.append(
                    File(
                        path.relative_to(ROOT).as_posix(),
                        src_dir=str(ROOT),
                        dest_dir=config["site_dir"],
                        use_directory_urls=config["use_directory_urls"],
                    )
                )
    return files
