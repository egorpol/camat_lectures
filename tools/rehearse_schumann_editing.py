"""Rehearse the editing notebook and native watcher on an isolated project copy.

Uses prepared teacher fragments, never an LLM provider. Requires the CAMAT,
Jupyter and validation environment used for the other Schumann rehearsals.

python tools/rehearse_schumann_editing.py --project /path/to/schumann_edition_work --output /tmp/new-rehearsal
"""

import argparse
import json
from pathlib import Path
import shutil
import sys

import nbformat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_notebooks as builder


WATCH_CODE = '''import asyncio
import os
import time
from lxml import etree as LX

async def wait_for_reload(previous):
    for _ in range(100):
        if viewer._render_revision > previous and not viewer._watch_state["reloading"]:
            return {"before_revision": previous, "after_revision": viewer._render_revision,
                    "status": viewer.watch_status.value}
        await asyncio.sleep(0.1)
    raise AssertionError("No completed watch-triggered render within 10 seconds")

def apply_fragments(fragments, atomic):
    tree = LX.parse(str(WORK_MEI))
    for measure_id, xml in fragments:
        matches = tree.xpath('//*[@xml:id=$id]', id=measure_id)
        assert len(matches) == 1
        matches[0].append(LX.fromstring(xml.encode()))
    data = LX.tostring(tree, encoding="UTF-8", xml_declaration=True)
    if atomic:
        staged = WORK_MEI.with_name(".rehearsal-save.mei")
        staged.write_bytes(data)
        os.replace(staged, WORK_MEI)
    else:
        WORK_MEI.write_bytes(data)

await asyncio.sleep(1.2)  # watcher startup settling; keep the kernel event loop active
revision = viewer._render_revision
apply_fragments(FRAGMENTS[:2], atomic=False)
direct_save = await wait_for_reload(revision)
await asyncio.sleep(1.2)  # respect the watcher's short post-reload suppression window
revision = viewer._render_revision
apply_fragments(FRAGMENTS[2:], atomic=True)
atomic_save = await wait_for_reload(revision)
AUDIT = audit_editing_changes(BEFORE_MEI, WORK_MEI)
assert len(AUDIT["new_controls"]) == 6
assert "seminar-dynam-second-system" in viewer.viewer_html.value
assert "seminar-slur-pickup" in viewer.viewer_html.value
assert "Opening slur division" in viewer.viewer_html.value
print("Direct save:", direct_save)
print("Atomic replacement:", atomic_save)
print("New dynamic/slur IDs and annotation label present in rebuilt viewer HTML.")
'''


def main():
    from lxml import etree

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Use a new rehearsal directory: {args.output}")
    project = args.project.resolve()
    work = project / "edition/mei/work.mei"
    before_bytes = work.read_bytes()
    # Only the local edition is needed; PDF extraction and linking are not rerun.
    shutil.copytree(project / "edition", args.output / "schumann_edition_work/edition")
    source = ROOT / "tools/notebooks/02_live_editing.py"
    notebook = builder.build(source)
    # Extract only the six new top-level controls/annotation from the teacher key.
    solution = ROOT / "sessions/02-building-an-edition/teacher/schumann/exercise-solution.mei"
    tree = etree.parse(str(solution))
    ns = {"m": "http://www.music-encoding.org/ns/mei"}
    xml_id = "{http://www.w3.org/XML/1998/namespace}id"
    fragments = []
    for wanted in ("seminar-dynam-opening", "seminar-tempo-opening",
                   "seminar-dynam-second-system", "seminar-slur-pickup",
                   "seminar-slur-bar2", "seminar-annot-opening-slurs"):
        element, = tree.xpath('//*[@xml:id=$id]', id=wanted)
        fragments.append((element.getparent().get(xml_id), etree.tostring(element, encoding="unicode")))
    notebook.cells.extend([
        nbformat.v4.new_markdown_cell(
            "## Instructor rehearsal only: deterministic save simulation\n\n"
            "The student notebook above leaves editing to the participant. The following "
            "extra cells apply six **prepared teacher fragments on a scratch copy**, "
            "exercise both ordinary save and atomic replacement, and validate the result. "
            "These are not model responses or human source approval. The check observes "
            "native kernel/watch/widget state; VS Code frontend navigation is a separate rehearsal."),
        nbformat.v4.new_code_cell("FRAGMENTS = " + repr(fragments) + "\n" + WATCH_CODE),
    ])
    validation_cell = next(cell for cell in notebook.cells if cell.cell_type == "code"
                           and cell.source.startswith("VALIDATION_DIR ="))
    notebook.cells.append(nbformat.v4.new_code_cell(validation_cell.source))
    notebook.cells.append(nbformat.v4.new_code_cell('''viewer.stop_watch()
negative_checks = {}
for name, xpath, attr, value in [
    ("pitch", './/*[@xml:id="d1e338"]', "pname", "g"),
    ("graphic_path", './/m:graphic', "target", "missing.png"),
    ("existing_header", './/m:meiHead', "type", "unexpected"),
]:
    mutated = LX.parse(str(WORK_MEI))
    targets = mutated.xpath(xpath, namespaces={"m": MEI_NS})
    assert targets, name
    targets[0].set(attr, value)
    candidate = WORK_MEI.with_name(f"rejected-{name}.mei")
    candidate.write_bytes(LX.tostring(mutated, encoding="UTF-8", xml_declaration=True))
    try:
        audit_editing_changes(BEFORE_MEI, candidate)
    except ValueError:
        negative_checks[name] = "rejected"
    else:
        raise AssertionError(f"Guard missed protected change: {name}")
    finally:
        candidate.unlink()
checks = {"prepared_on": "2026-10-25", "method": "deterministic teacher fragments on scratch copy; no model inference",
          "audit": AUDIT, "watch": {"direct_save": direct_save, "atomic_save": atomic_save,
          "new_content_in_viewer_html": True, "stopped_after_test": True},
          "negative_guard_checks": negative_checks,
          "validation": {key: run.get(key) for key in ("conformance", "required_checks", "consumer_diagnostics", "executions")},
          "human_source_approval": "not_asserted", "provider_accounts_and_inference": "not_tested",
          "vs_code_frontend_navigation": "not_tested"}
(PROJECT / "edition/editing-rehearsal.json").write_text(json.dumps(checks, indent=2) + "\\n")
print(json.dumps(checks, indent=2))
'''))
    success = builder.execute(notebook, source.stem, args.output)
    assert work.read_bytes() == before_bytes, "Original project work file changed"
    print("Original project working file preserved.")
    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
