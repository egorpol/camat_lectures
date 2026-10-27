"""Pack the publication template separately from notebook source; no scan pixels."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "sessions/02-building-an-edition"
TEMPLATE = SESSION / "examples/edition-template"


def main():
    licenses = TEMPLATE / "LICENSES"
    licenses.mkdir(exist_ok=True)
    upstream = ROOT.parent / "camat_v2/LICENSE"
    # These notices are already in the local source projects used in preparation.
    # Once copied, the template itself is self-contained.
    if upstream.exists():
        (licenses / "CAMAT-MIT.txt").write_bytes(upstream.read_bytes())
        text = upstream.read_text().replace("Copyright (c) 2025 Egor Polyakov", "Copyright (c) 2026 Egor Polyakov")
        (licenses / "Teaching-code-MIT.txt").write_text(text)
    if not (licenses / "CAMAT-MIT.txt").exists():
        raise FileNotFoundError("Retain the CAMAT license notice in the template")
    (licenses / "MEI-Sample-Collection-ECL-2.0.txt").write_bytes((SESSION / "examples/schumann/LICENSE").read_bytes())
    files = {p.relative_to(TEMPLATE).as_posix(): p.read_bytes() for p in sorted(TEMPLATE.rglob("*"))
             if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}
    files["sources.json"] = (SESSION / "sources/sources.json").read_bytes()
    manifest = {"prepared_on": "2026-10-26", "media_included": False,
                "files_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}
    files["template-manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    output = SESSION / "notebooks/schumann-release-template.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 26, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    print(f"Packed {len(files)} files, {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
