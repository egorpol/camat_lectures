"""Build the session notebooks from the sources in tools/notebooks/.

A source is a percent-format script, NN_name.py, written to
sessions/NN-*/notebooks/NN_name.ipynb. Cell markers:

    # %% [markdown]                  Markdown cell; its lines start with "# "
    # %%                             code cell
    # %% install                     the install cell (skipped by --execute: the venv has no pip)
    # %% helpers: mei grid checks    collapsed code cell with helpers/mei.py, grid.py, checks.py, in this order

The helper files are pasted verbatim, so they must not import each other.
helpers/{mei,grid,checks}.py port docs/javascripts/lib/; check with
tools/notebooks/check_parity.py.

    .venv/bin/python tools/build_notebooks.py             # write the notebooks
    .venv/bin/python tools/build_notebooks.py --check     # exit 1 if a notebook is out of date
    .venv/bin/python tools/build_notebooks.py --execute [--outdir DIR]
                                                          # also run each with nbclient; executed copies go to DIR
"""

import argparse
import sys
import tempfile
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "tools" / "notebooks"
HELPERS = SOURCES / "helpers"
HELPER_HEADER = (
    "# Helper functions for this notebook. Run this cell; you do not need to read it.\n"
    "# They follow the same rules as the demos on the course page.\n\n"
)


def parse(path):
    cells = []
    kind, lines = None, []

    def flush():
        if kind is None:
            return
        text = "\n".join(lines).strip("\n")
        if kind == "markdown":
            text = "\n".join(line[2:] if line.startswith("# ") else line.lstrip("#") for line in text.split("\n"))
            cells.append(nbformat.v4.new_markdown_cell(text))
        elif kind == "install":
            cells.append(nbformat.v4.new_code_cell(text, metadata={"tags": ["install"]}))
        elif kind.startswith("helpers:"):
            names = kind.split(":", 1)[1].split()
            code = "\n\n".join((HELPERS / f"{name}.py").read_text().strip("\n") for name in names)
            if text:
                code += "\n\n" + text
            meta = {"tags": ["helpers"], "jupyter": {"source_hidden": True}}
            cells.append(nbformat.v4.new_code_cell(HELPER_HEADER + code, metadata=meta))
        else:
            cells.append(nbformat.v4.new_code_cell(text))

    for line in path.read_text().split("\n"):
        if line.startswith("# %%"):
            flush()
            marker = line[4:].strip()
            kind = "markdown" if marker == "[markdown]" else marker or "code"
            lines = []
        else:
            lines.append(line)
    flush()
    return cells


def build(path):
    nb = nbformat.v4.new_notebook()
    nb.cells = parse(path)
    for i, cell in enumerate(nb.cells):
        cell.id = f"c{i:02d}"  # stable ids: rebuilding an unchanged source gives the same file
    nb.metadata = {
        "kernelspec": {"name": "python3", "display_name": "Python 3 (ipykernel)", "language": "python"},
        "language_info": {"name": "python"},
    }
    nbformat.validate(nb)
    return nb


def target(path):
    session = next((ROOT / "sessions").glob(path.name[:2] + "-*"))
    return session / "notebooks" / (path.stem + ".ipynb")


def execute(nb, name, outdir):
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError

    run = nbformat.from_dict(nb)
    run.cells = [c for c in run.cells if "install" not in c.metadata.get("tags", [])]
    client = NotebookClient(run, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(outdir)}})
    try:
        client.execute()
        ok = True
    except CellExecutionError as error:
        print(f"{name}: FAILED\n{str(error)[:3000]}")
        ok = False
    nbformat.write(run, outdir / f"{name}.ipynb")
    outputs = [o for c in run.cells if c.cell_type == "code" for o in c.get("outputs", [])]
    scores = sum(o.get("data", {}).get("text/html", "").count("<svg") for o in outputs)
    images = sum("image/png" in o.get("data", {}) for o in outputs)
    stderr = [o for o in outputs if o.get("name") == "stderr"]
    print(f"{name}: {'ok' if ok else 'error'}, {len(run.cells)} cells, {scores} scores, {images} plots, {len(stderr)} stderr outputs")
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--outdir", type=Path)
    args = parser.parse_args()
    outdir = args.outdir or Path(tempfile.mkdtemp(prefix="notebooks-"))
    failed = False
    for path in sorted(SOURCES.glob("[0-9][0-9]_*.py")):
        nb = build(path)
        out = target(path)
        text = nbformat.writes(nb) + "\n"
        if args.check:
            if not out.exists() or out.read_text() != text:
                print(f"out of date: {out.relative_to(ROOT)}")
                failed = True
            continue
        out.parent.mkdir(exist_ok=True)
        out.write_text(text)
        print(f"wrote {out.relative_to(ROOT)}")
        if args.execute:
            outdir.mkdir(parents=True, exist_ok=True)
            failed |= not execute(nb, path.stem, outdir)
    if args.execute:
        print(f"executed copies in {outdir}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
