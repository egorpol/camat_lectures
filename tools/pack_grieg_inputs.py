"""Pack the Grieg linking inputs into grieg-edition-inputs.zip.

The ZIP holds the Sample Collection MEI (unchanged), its licence, the sources
record, the page settings and the checked Edirom box files for both pages.
No scan, page image or detector run record (.run.json) is included: the run
record names PNG bytes that differ between poppler versions.

    .venv/bin/python tools/pack_grieg_inputs.py

Run it before tools/build_notebooks.py when one of the inputs changes.
"""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "sessions/03-linking-and-editing"
EXAMPLE = SESSION / "examples/grieg"
TARGET = SESSION / "notebooks/grieg-edition-inputs.zip"
MEI = "Grieg_Little_bird_Op43_No4.mei"


def main():
    sources = json.loads((SESSION / "sources/sources.json").read_text())
    excerpt = sources["classroom_pdf"]
    settings = {
        "prepared_on": "2026-11-12",
        "work": "Grieg, Vöglein, Op. 43 No. 4",
        "mei": MEI,
        "volume_filename": "imslp-28165-grieg-op43.pdf",
        "excerpt_filename": excerpt["filename"],
        "volume_pdf_pages": [m["original_pdf_page"] for m in excerpt["page_mapping"]],
        "printed_pages": [m["printed_page"] for m in excerpt["page_mapping"]],
        "pypdf_version": excerpt["tool_version"],
        "dpi": sources["page_images"]["dpi"],
        "image_pixels": sources["page_images"]["pixels"],
        "page_ids": sources["page_images"]["page_ids"],
        "layout": ["1 | 42 | 1-4, 5-9, 10-14, 15-17, 18-20",
                   "2 | 43 | 21-23, 24-26, 27-30, 31-35, 36-39"],
        "source_ref": "src.imslp28165",
    }
    files = {
        MEI: (EXAMPLE / MEI).read_bytes(),
        "LICENSE": (EXAMPLE / "LICENSE").read_bytes(),
        "sources.json": (SESSION / "sources/sources.json").read_bytes(),
        "settings.json": (json.dumps(settings, ensure_ascii=False, indent=2) + "\n").encode(),
    }
    for page_id in settings["page_ids"]:
        files[f"boxes/{page_id}.json"] = (EXAMPLE / "boxes" / f"{page_id}.json").read_bytes()
    checks = {MEI: sources["base_encoding"]["sha256"],
              **{f"boxes/{name}": entry["sha256"] for name, entry in sources["measure_boxes"]["files"].items()}}
    for name, expected in checks.items():
        if hashlib.sha256(files[name]).hexdigest() != expected:
            raise ValueError(f"{name} differs from sources.json")
    files["manifest.json"] = (json.dumps({"files_sha256": {
        name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())
    }}, indent=2) + "\n").encode()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(TARGET, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 11, 12, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    print(f"Saved {TARGET.stat().st_size:,} bytes to {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
