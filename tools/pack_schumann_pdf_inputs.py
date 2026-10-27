"""Save the Schumann PDF workshop's notation/settings as a small data ZIP.

No scan, source PDF, source-image output or model weight is included.
Run this before tools/build_notebooks.py after changing the teaching starter.
"""

import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "sessions/02-building-an-edition"
TARGET = SESSION / "notebooks/schumann-edition-inputs.zip"


def main():
    settings = {
        "prepared_on": "2026-10-25",
        "work": "Schumann, Fröhlicher Landmann, Op.68 No.10",
        "original_filename": "imslp-51556-schumann-op68.pdf",
        "excerpt_filename": "schumann-op68-no10-source-page.pdf",
        "original_pdf_page": 8, "excerpt_pdf_page": 1, "printed_page": "8",
        "pypdf_version": "6.10.0", "dpi": 300,
        "expected_image_pixels": [4167, 5617],
        "music_pages": "1 | 8 | 1-5, 6-9, 10-13, 14-17, 18-21",
        "system_mei_labels": [[str(n) for n in range(a, b + 1)]
                              for a, b in [(1, 5), (6, 9), (10, 13), (14, 17), (18, 21)]],
        "reviewed_mei_labels": [str(n) for n in range(1, 10)],
        "scope": "Whole-piece technical carrier; labels 1–9 are the core editing passage. Further musical source review remains necessary.",
    }
    files = {
        "starter.mei": (SESSION / "examples/schumann/starter.mei").read_bytes(),
        "LICENSE": (SESSION / "examples/schumann/LICENSE").read_bytes(),
        "sources.json": (SESSION / "sources/sources.json").read_bytes(),
        "settings.json": (json.dumps(settings, ensure_ascii=False, indent=2) + "\n").encode(),
    }
    files["manifest.json"] = (json.dumps({"files_sha256": {
        name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())
    }}, indent=2) + "\n").encode()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(TARGET, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    print(f"Saved {TARGET.stat().st_size:,} bytes to {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
