"""Package manual Schumann measure regions separately from notebook code."""

import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "sessions/02-building-an-edition"
SOURCE = SESSION / "examples/schumann/facsimile"
TARGET = SESSION / "notebooks/schumann-measure-boxes.zip"


def main():
    files = {name: (SOURCE / name).read_bytes() for name in ("boxes-checked.json", "boxes-exercise.json")}
    files["manifest.json"] = (json.dumps({"files_sha256": {
        name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())
    }}, indent=2) + "\n").encode()
    with zipfile.ZipFile(TARGET, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    print(f"Saved {TARGET.stat().st_size:,} bytes to {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
