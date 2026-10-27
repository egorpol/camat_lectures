"""Manual region exercise and protected Schumann facsimile integration."""

from pathlib import Path
import hashlib
import json
import os
import tempfile
import xml.etree.ElementTree as ET
import zipfile


def _link_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _link_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _link_write_once(path, data):
    path = Path(path)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"Preserving different file: {path}. Use a new attempt folder.")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as output:
            output.write(data)


def find_schumann_box_bundle(start=None):
    start = Path(start or Path.cwd()).resolve()
    name = "schumann-measure-boxes.zip"
    for folder in (start, *start.parents):
        for candidate in (folder / name, folder / "notebooks" / name,
                          folder / "sessions/02-building-an-edition/notebooks" / name):
            if candidate.is_file():
                return candidate
    raise FileNotFoundError(f"Copy {name} beside the notebook or run get_notebooks.py.")


def load_schumann_box_context(project, bundle):
    project = Path(project).resolve()
    checkpoint_file = project / "page-preparation-checkpoint.json"
    if not checkpoint_file.exists():
        raise FileNotFoundError("Run 02_pdf_preparation.ipynb first, or set PROJECT to that notebook's saved project.")
    checkpoint = json.loads(checkpoint_file.read_text())
    mei, pages = project / checkpoint["mei_input"], project / checkpoint["pages_json"]
    if _link_hash(mei) != checkpoint["mei_sha256"] or _link_hash(pages) != checkpoint["pages_json_sha256"]:
        raise ValueError("The page-preparation inputs changed; review that checkpoint before linking.")
    page = json.loads(pages.read_text())["pages"][0]
    with zipfile.ZipFile(bundle) as archive:
        expected = json.loads(archive.read("manifest.json"))["files_sha256"]
        if set(expected) != {"boxes-checked.json", "boxes-exercise.json"}:
            raise ValueError("Unexpected manual box bundle.")
        values = {}
        for name, digest in expected.items():
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError(f"Box data hash mismatch: {name}")
            values[name] = json.loads(data)
    checked, exercise = values["boxes-checked.json"], values["boxes-exercise.json"]
    image = pages.parent / page["image"]
    for data in (checked, exercise):
        if data["image_sha256"] != page["sha256"] or _link_hash(image) != data["image_sha256"]:
            raise ValueError("Manual regions belong to different source pixels; review the rendering before reusing them.")
        if data["image_pixels"] != [page["width"], page["height"]]:
            raise ValueError("Manual regions have different image geometry.")
    return {"project": project, "mei": mei, "pages_json": pages, "page": page,
            "image": image, "checked": checked, "exercise": exercise,
            "alignment": project / "edition/alignment.json"}


def _native_boxes(data):
    return {"measures": [{key: box[key] for key in ("ulx", "uly", "lrx", "lry")}
                         for box in data["measures"]]}


def diagnose_missing_pickup(context):
    """Exercise the real alignment gate in isolation; keep working boxes intact."""
    from camat.pdf_facsimile import build_measure_alignment
    manifest = json.loads(context["pages_json"].read_text())
    with tempfile.TemporaryDirectory(prefix="schumann-box-exercise-") as folder:
        folder = Path(folder)
        manifest["pages"][0]["image"] = os.path.relpath(context["image"], folder)
        _link_json(folder / "pages.json", manifest)
        _link_json(folder / "boxes" / f"{context['page']['page_id']}.json", _native_boxes(context["exercise"]))
        try:
            build_measure_alignment(folder / "pages.json", output=folder / "alignment.json")
        except ValueError as problem:
            message = str(problem)
            if "actual [4, 4, 4, 4, 4], expected [5, 4, 4, 4, 4]" not in message:
                raise
        else:
            raise AssertionError("The deliberately incomplete boxes unexpectedly passed.")
    _link_json(context["project"] / "edition/exercise-diagnostic.json", {
        "source": "Manually prepared teaching data; no detector called.", "status": "rejected as expected", "message": message})
    return message


def show_pickup_ruler(context):
    from PIL import Image
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.ticker import MultipleLocator
    crop = (320, 560, 1750, 1400)
    with Image.open(context["image"]) as image:
        region = image.crop(crop).convert("RGB")
    figure, axes = plt.subplots(figsize=(13, 7))
    axes.imshow(region, extent=(crop[0], crop[2], crop[3], crop[1]))
    for index, box in enumerate(context["exercise"]["measures"]):
        if box["system"] != 1:
            continue
        axes.add_patch(Rectangle((box["ulx"], box["uly"]), box["lrx"] - box["ulx"], box["lry"] - box["uly"],
                                 fill=False, edgecolor="tab:red", linewidth=2))
        axes.text(box["ulx"] + 12, box["uly"] + 12, f"box {index} / MEI {box['mei_label']}", va="top",
                  color="tab:red", bbox={"facecolor": "white", "edgecolor": "none"})
    axes.set(xlim=(crop[0], crop[2]), ylim=(crop[3], crop[1]),
             xlabel="Full-image x coordinate (pixels)", ylabel="Full-image y coordinate (pixels)",
             title="Missing pickup region: both staves, before box 0")
    axes.xaxis.set_major_locator(MultipleLocator(100)); axes.yaxis.set_major_locator(MultipleLocator(100))
    axes.grid(alpha=0.25)
    figure.tight_layout()
    output = context["project"] / "edition/previews/pickup-ruler.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=120)
    plt.show()
    plt.close(figure)


def correct_schumann_boxes(context, additions):
    from camat.pdf_facsimile import edit_measure_boxes, build_measure_alignment, draw_alignment_overlays
    path = context["pages_json"].parent / "boxes" / f"{context['page']['page_id']}.json"
    backup = path.with_name(path.stem + ".original.json")
    baseline = (json.dumps(_native_boxes(context["exercise"]), ensure_ascii=False, indent=2) + "\n").encode()
    if backup.exists():
        if backup.read_bytes() != baseline:
            raise ValueError("Working box baseline differs from this exercise; preserve it and use a new attempt.")
    else:
        _link_write_once(path, baseline)
    edit_measure_boxes(context["pages_json"], context["page"]["page_id"], add=additions)
    build_measure_alignment(context["pages_json"], output=context["alignment"])
    return draw_alignment_overlays(context["alignment"], context["project"] / "edition/overlays")


def _score_projection(path):
    ns = "{http://www.music-encoding.org/ns/mei}"
    body = ET.parse(path).getroot().find(ns + "music/" + ns + "body")
    def walk(element):
        if element.tag in {ns + "pb", ns + "sb"}:
            return None
        attributes = {k: v for k, v in element.attrib.items() if k != "facs"}
        if element.tag == ns + "mdiv":
            attributes.pop("n", None)  # The single unnumbered movement is explicitly numbered 1.
        return (element.tag, sorted(attributes.items()), (element.text or "").strip(),
                [value for child in element if (value := walk(child)) is not None])
    return walk(body)


def create_linked_schumann(context):
    """Generate in the final folder so relative graphic paths survive promotion."""
    from camat.pdf_facsimile import number_single_mdiv, integrate_pdf_facsimile, write_page_breaks
    folder = context["project"] / "edition/mei"
    folder.mkdir(parents=True, exist_ok=True)
    handles = [tempfile.NamedTemporaryFile(prefix=".schumann-", suffix=".mei", dir=folder, delete=False) for _ in range(2)]
    staged_input, candidate = [Path(handle.name) for handle in handles]
    for handle in handles:
        handle.close()
    baseline = folder / "linked-starter.mei"
    try:
        staged_input.write_text(number_single_mdiv(context["mei"].read_text()), encoding="utf-8")
        report = integrate_pdf_facsimile(staged_input, context["pages_json"], context["alignment"], candidate,
                                         source_ref="src.imslp51556")
        breaks = write_page_breaks(candidate, context["pages_json"], candidate)
        if _score_projection(context["mei"]) != _score_projection(candidate):
            raise ValueError("Linking changed musical content or existing IDs.")
        _link_write_once(baseline, candidate.read_bytes())
    finally:
        staged_input.unlink(missing_ok=True)
        candidate.unlink(missing_ok=True)
    report["output_mei"] = str(baseline)
    breaks["output_mei"] = str(baseline)
    _link_json(context["project"] / "edition/linking-report.json", {"integration": report, "breaks": breaks,
               "score_projection_unchanged": True, "controlled_change": "Number the sole unnumbered mdiv 1; add facsimile links and source breaks."})
    snapshot = context["project"] / "edition/checkpoints/linked-before-editing.mei"
    _link_write_once(snapshot, baseline.read_bytes())
    work = folder / "work.mei"
    created = not work.exists()
    if created:
        _link_write_once(work, baseline.read_bytes())
    checkpoint = {"stage": "linked teaching draft before expressive editing", "project": str(context["project"]),
                  "input_mei_sha256": _link_hash(context["mei"]), "linked_mei": "edition/mei/linked-starter.mei",
                  "linked_mei_sha256": _link_hash(baseline), "work_mei": "edition/mei/work.mei",
                  "work_created_now": created, "work_matches_linked_baseline": work.read_bytes() == baseline.read_bytes(),
                  "work_sha256_at_check": _link_hash(work), "snapshot": "edition/checkpoints/linked-before-editing.mei",
                  "snapshot_sha256": _link_hash(snapshot), "image_sha256": context["page"]["sha256"],
                  "alignment_sha256": _link_hash(context["alignment"]), "unreviewed_pages": report["unreviewed_pages"],
                  "measures_linked": report["measures_linked"], "zones": report["zones"], "surfaces": report["surfaces"],
                  "pb": breaks["pb"], "sb": breaks["sb"], "musical_content_and_existing_ids_preserved": True,
                  "scope": "Labels 1–9 are the core editorial passage; full-piece musical proofreading remains incomplete."}
    _link_json(context["project"] / "linked-stage-checkpoint.json", checkpoint)
    return baseline, work, checkpoint
