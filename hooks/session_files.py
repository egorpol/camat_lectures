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
        # Publish the source record explicitly, without exposing sources/local/.
        provenance = session / "sources/sources.json"
        if provenance.is_file():
            files.append(File(provenance.relative_to(ROOT).as_posix(), src_dir=str(ROOT),
                              dest_dir=config["site_dir"], use_directory_urls=config["use_directory_urls"]))
        for folder in FOLDERS:
            # Notebook runs create ignored working projects containing scans.
            # Publish only the top-level portable downloads, never runtime trees.
            paths = ((session / folder).glob("*") if folder == "notebooks"
                     else (session / folder).rglob("*"))
            for path in sorted(paths):
                if not path.is_file() or path.name.startswith(".") or "__pycache__" in path.parts:
                    continue
                if folder == "notebooks" and path.suffix not in {".ipynb", ".zip"}:
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
