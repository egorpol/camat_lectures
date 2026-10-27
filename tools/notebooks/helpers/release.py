"""Schumann review, transfer and release helpers. No GitHub mutations or model calls."""
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
from urllib.parse import quote
import xml.etree.ElementTree as ET
from zipfile import ZipFile

REL_NS = "http://www.music-encoding.org/ns/mei"
REL_ID = "{http://www.w3.org/XML/1998/namespace}id"
REL_M = "{" + REL_NS + "}"


def release_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def release_write_once(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"Preserving a different existing file: {path}")
        return
    with path.open("xb") as output:
        output.write(data)


def release_json_once(path, value):
    release_write_once(path, (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode())


def make_review_record(project):
    project = Path(project)
    work = project / "edition/mei/work.mei"
    path = project / "edition/review.json"
    if path.exists():
        return path, json.loads(path.read_text())
    record = {"status": "not_reviewed", "reviewer": "", "date": "",
              "input_mei_sha256": release_hash(work), "intended_scope_mei_labels": [str(n) for n in range(1, 10)],
              "actually_reviewed_mei_labels": [], "source": "IMSLP 51556, printed p.8",
              "tasks": [{"task": name, "decision": "not_reviewed", "reason": ""}
                        for name in ["opening instruction/dynamic", "two opening slur phrases", "anchored editorial explanation"]],
              "validation_report": "edition/validation-review/run.json", "unresolved_issues": [],
              "whole_piece_approval": False, "model_contribution_and_human_corrections": ""}
    release_json_once(path, record)
    return path, record


def find_release_template():
    paths = [Path.cwd() / "schumann-release-template.zip",
             Path.cwd() / "sessions/02-building-an-edition/notebooks/schumann-release-template.zip"]
    return next((path for path in paths if path.is_file()), None)


def export_release_project(project, template, output):
    project, output = Path(project).resolve(), Path(output).resolve()
    if template is None:
        raise FileNotFoundError("Keep schumann-release-template.zip beside the notebook")
    mei = project / "edition/mei/work.mei"
    pages = project / "edition/pages/pages.json"
    review_path, review = make_review_record(project)
    identity = {"mei_sha256": release_hash(mei), "pages_sha256": release_hash(pages),
                "review_sha256": release_hash(review_path), "template_sha256": release_hash(template)}
    if output.exists():
        record = json.loads((output / "export.json").read_text())
        if record["identity"] != identity:
            raise FileExistsError("This export belongs to different inputs; use a new release attempt folder")
        print("Existing release project preserved; no files overwritten:", output)
        return record
    output.mkdir(parents=True)
    with ZipFile(template) as archive:
        manifest = json.loads(archive.read("template-manifest.json"))
        for name, expected in manifest["files_sha256"].items():
            parts = PurePosixPath(name).parts
            if not parts or name.startswith("/") or ".." in parts:
                raise ValueError("Unexpected template path")
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError(f"Template hash differs: {name}")
            release_write_once(output / name, data)
    release_write_once(output / "mei/work.mei", mei.read_bytes())
    exported_review = copy.deepcopy(review)
    validation = project / "edition/validation-review"
    if (validation / "run.json").is_file():
        for report_file in validation.rglob("*"):
            if report_file.is_file() and report_file.suffix in {".json", ".csv", ".txt"}:
                release_write_once(output / "validation-evidence" / report_file.relative_to(validation), report_file.read_bytes())
        exported_review["validation_report_in_working_project"] = exported_review.get("validation_report")
        exported_review["validation_report"] = "validation-evidence/run.json"
    release_json_once(output / "review.json", exported_review)
    page_manifest = json.loads(pages.read_text())
    exported_manifest = copy.deepcopy(page_manifest)
    exported_manifest["pdf"] = "../local/schumann-op68-no10-source-page.pdf"
    release_json_once(output / "pages/pages.json", exported_manifest)
    for page in page_manifest["pages"]:
        source = (pages.parent / page["image"]).resolve()
        if release_hash(source) != page["sha256"]:
            raise ValueError("Page image differs from the linked source manifest")
        release_write_once(output / "pages" / Path(page["image"]).name, source.read_bytes())
    pdf = (pages.parent / page_manifest["pdf"]).resolve()
    if pdf.is_file():
        if release_hash(pdf) != page_manifest["pdf_sha256"]:
            raise ValueError("Source excerpt differs from page manifest")
        release_write_once(output / "local/schumann-op68-no10-source-page.pdf", pdf.read_bytes())
    record = {"prepared_on": "2026-10-26", "identity": identity, "source_mei": str(mei),
              "working_mei_unchanged": release_hash(mei) == identity["mei_sha256"],
              "review_status": review["status"], "review_hash_matches_input": review["input_mei_sha256"] == identity["mei_sha256"],
              "human_approval_created": False, "github_mutations": 0,
              "media": "Local PDF/PNG copied for rehearsal; .gitignore excludes them and the public build omits them"}
    release_json_once(output / "export.json", record)
    return record


def make_friend_transfer(project, base_url="http://127.0.0.1:8781/"):
    project = Path(project).resolve()
    source = project / "edition/mei/work.mei"
    root = ET.parse(source).getroot()
    targets = []
    for graphic in root.findall("m:music/m:facsimile/m:surface/m:graphic", {"m": REL_NS}):
        old = graphic.get("target")
        image = (source.parent / old).resolve()
        if image.parent != project / "edition/pages":
            raise ValueError("Expected image in this edition's pages folder")
        url = base_url.rstrip("/") + "/pages/" + quote(image.name)
        targets.append({"original": old, "transfer": url, "image_sha256": release_hash(image)})
        graphic.set("target", url)
    if not targets:
        raise ValueError("No facsimile graphic found")
    output = source.with_name("mei-friend-transfer.mei")
    release_write_once(output, ET.tostring(root, encoding="UTF-8", xml_declaration=True))
    report = {"source_mei_sha256": release_hash(source), "transfer_sha256": release_hash(output),
              "targets": targets, "canonical_working_file": str(source),
              "warning": "Transfer-only localhost paths; restore them before publication"}
    release_json_once(project / "edition/mei-friend-transfer.json", report)
    return output, report


def check_friend_roundtrip(original, saved, output, transfer_record=None):
    """Save a separate restored candidate; report identity/music/link preservation."""
    original, saved, output = Path(original), Path(saved), Path(output)
    before, after = ET.parse(original).getroot(), ET.parse(saved).getroot()
    if transfer_record:
        if release_hash(original) != transfer_record["source_mei_sha256"]:
            raise ValueError("Original changed since the transfer was made")
        graphics = after.findall("m:music/m:facsimile/m:surface/m:graphic", {"m": REL_NS})
        if len(graphics) != len(transfer_record["targets"]):
            raise ValueError("Graphic count changed")
        for graphic, target in zip(graphics, transfer_record["targets"]):
            if graphic.get("target") != target["transfer"]:
                raise ValueError("Unexpected graphic target; inspect before restoring")
            graphic.set("target", target["original"])
    old_ids = {e.get(REL_ID) for e in before.iter() if e.get(REL_ID)}
    new_ids = [e.get(REL_ID) for e in after.iter() if e.get(REL_ID)]
    def signature(root):
        body = root.find("m:music/m:body", {"m": REL_NS})
        if body is None:
            raise ValueError("No musical body found")
        return [(e.tag, sorted(e.attrib.items()), (e.text or "").strip() if e.tag != REL_M + "annot" else "")
                for e in body.iter()]
    def facsimile(root):
        return [(e.tag, sorted(e.attrib.items())) for e in root.iter()
                if e.tag in {REL_M + tag for tag in ["facsimile", "surface", "graphic", "zone"]}]
    report = {"existing_ids_preserved": old_ids.issubset(new_ids), "ids_unique": len(new_ids) == len(set(new_ids)),
              "musical_structure_and_controls_preserved": signature(before) == signature(after),
              "facsimile_preserved_after_restore": facsimile(before) == facsimile(after),
              "original_sha256": release_hash(original), "saved_sha256": release_hash(saved),
              "human_source_review": "not_assessed", "metadata_and_annotation_prose": "Inspect the diff separately"}
    if not all(report[name] for name in ["existing_ids_preserved", "ids_unique", "musical_structure_and_controls_preserved", "facsimile_preserved_after_restore"]):
        raise ValueError("Round-trip structure changed: " + json.dumps(report))
    release_write_once(output, ET.tostring(after, encoding="UTF-8", xml_declaration=True))
    return report
