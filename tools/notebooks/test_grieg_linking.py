"""Offline tests for drawing and reusing the session 3 page images."""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

for program in ("pdftoppm", "pdfinfo"):
    if shutil.which(program) is None:
        pytest.skip(f"needs Poppler's {program} on PATH", allow_module_level=True)

pdf_facsimile = pytest.importorskip("camat.pdf_facsimile")
HELPER = Path(__file__).resolve().parent / "helpers/grieg_linking.py"
DPI = 72
PAGE_POINTS = (80, 120)


@pytest.fixture(scope="module")
def H():
    namespace = {"__name__": "grieg_linking_test"}
    exec(compile(HELPER.read_text(encoding="utf-8"), str(HELPER), "exec"), namespace)
    return namespace


def _write_pdf(path, title):
    from pypdf import PdfWriter

    writer = PdfWriter()
    for _ in range(2):
        writer.add_blank_page(width=PAGE_POINTS[0], height=PAGE_POINTS[1])
    writer.add_metadata({"/Title": title})
    writer.write(path)


def _context(project):
    excerpt = project / "excerpt.pdf"
    return {
        "project": project,
        "excerpt": excerpt,
        "pages_json": project / "edition/pages/pages.json",
        "settings": {"dpi": DPI, "image_pixels": [points * DPI // 72 for points in PAGE_POINTS]},
        "sources": {"classroom_pdf": {"sha256": hashlib.sha256(excerpt.read_bytes()).hexdigest()}},
    }


def _page_files(pages_json):
    folder = pages_json.parent
    return {path.relative_to(folder): path.read_bytes() for path in folder.rglob("*") if path.is_file()}


@pytest.fixture
def fresh_context(tmp_path):
    _write_pdf(tmp_path / "excerpt.pdf", "Classroom excerpt")
    return _context(tmp_path)


@pytest.fixture(scope="module")
def stale_project(H, tmp_path_factory):
    project = tmp_path_factory.mktemp("stale_renderer")
    _write_pdf(project / "excerpt.pdf", "Classroom excerpt")
    context = _context(project)
    H["draw_pages"](context)
    path = context["pages_json"]
    manifest = json.loads(path.read_bytes())
    older_renderer = "pdftoppm version 26.10.0"
    if manifest["renderer"] == older_renderer:
        older_renderer = "pdftoppm version 26.09.0"
    manifest["renderer"] = older_renderer
    page = manifest["pages"][0]
    page.update(role="music", printed_page="42", systems=[{"measures": ["1"]}])
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (path.parent / "boxes" / f"{page['page_id']}.json").write_bytes(b'{"measures": [[1, 2, 30, 40]]}\n')
    return project


@pytest.fixture
def stale_context(stale_project, tmp_path):
    return _context(shutil.copytree(stale_project, tmp_path / "project"))


def test_draw_pages_fresh(H, fresh_context):
    """Draw both pages at the expected pixel size and record the renderer."""
    from PIL import Image

    path = fresh_context["pages_json"]
    assert not path.exists()
    assert H["_drawn_before"](fresh_context) is None

    H["draw_pages"](fresh_context)

    manifest = json.loads(path.read_bytes())
    version = subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True, check=True)
    assert manifest["renderer"] == (version.stderr or version.stdout).splitlines()[0]
    assert manifest["pdf_sha256"] == fresh_context["sources"]["classroom_pdf"]["sha256"]
    assert manifest["page_count"] == len(manifest["pages"]) == 2
    pixels = fresh_context["settings"]["image_pixels"]
    for page in manifest["pages"]:
        assert [page["width"], page["height"]] == pixels
        with Image.open(path.parent / page["image"]) as image:
            assert image.format == "PNG"
            assert image.size == tuple(pixels)
    assert (path.parent / "boxes").is_dir()


def test_draw_pages_same_renderer(H, fresh_context):
    """Reuse the recorded images on a rerun with the same renderer."""
    H["draw_pages"](fresh_context)
    path = fresh_context["pages_json"]
    before = _page_files(path)
    assert H["_drawn_before"](fresh_context) == json.loads(path.read_bytes())

    H["draw_pages"](fresh_context)

    assert _page_files(path) == before


def test_draw_pages_stale_renderer(H, stale_context):
    """Keep the reviewed manifest, PNGs and boxes after a Poppler update."""
    path = stale_context["pages_json"]
    before = _page_files(path)
    with pytest.raises(ValueError, match=r"^Cannot reuse pages\.json; changed: renderer\."):
        pdf_facsimile.render_pdf_pages(stale_context["excerpt"], path.parent, dpi=stale_context["settings"]["dpi"])

    H["draw_pages"](stale_context)

    assert _page_files(path) == before


@pytest.mark.parametrize(("change", "reason"), [
    ("corrupt_png", "image hash"),
    ("missing_png", "image hash"),
    ("dpi", "dpi"),
    ("source_id", "source_id"),
    ("pdf", "pdf_sha256"),
])
def test_draw_pages_refuses_changed_input(H, stale_context, change, reason):
    """Let CAMAT refuse changes that can invalidate pixel coordinates."""
    path = stale_context["pages_json"]
    manifest = json.loads(path.read_bytes())
    image = path.parent / manifest["pages"][1]["image"]
    if change == "corrupt_png":
        with image.open("ab") as output:
            output.write(b"\x00")
    elif change == "missing_png":
        image.unlink()
    elif change == "pdf":
        _write_pdf(stale_context["excerpt"], "Replacement excerpt")
        assert hashlib.sha256(stale_context["excerpt"].read_bytes()).hexdigest() != manifest["pdf_sha256"]
    else:
        manifest[change] = {"dpi": DPI + 1, "source_id": "another-source"}[change]
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    before = _page_files(path)
    with pytest.raises(ValueError, match=rf"^Cannot reuse pages\.json; changed: .*\b{reason}\b"):
        H["draw_pages"](stale_context)
    assert _page_files(path) == before


def test_draw_pages_missing_renderer(H, stale_context):
    """Reuse the reviewed images when the manifest has no renderer field."""
    path = stale_context["pages_json"]
    manifest = json.loads(path.read_bytes())
    del manifest["renderer"]
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    before = _page_files(path)

    H["draw_pages"](stale_context)

    assert _page_files(path) == before
