"""Recover the exact one-page source PDF. No download unless --download is set.

python scripts/prepare_source.py --original /path/to/imslp-51556-schumann-op68.pdf
python scripts/prepare_source.py --download
"""
import argparse
import hashlib
import io
from pathlib import Path
import urllib.request

from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
URL = "https://s9.imslp.org/files/imglnks/usimg/0/0a/IMSLP51556-PMLP02707-RS67.pdf"
ORIGINAL_SHA = "893ab03c376724a9f4474497130eb2d8510ba9d71f05bb270c8f6000b731e289"
EXCERPT_SHA = "3c634e9fa1c8b4f75df6abbd1f2edf9012625421abf2eee37e641e70e794ef8e"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if args.original:
        raw = args.original.read_bytes()
    elif args.download:
        request = urllib.request.Request(URL, headers={"User-Agent": "CAMAT-seminar-source/1.0"})
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read()
    else:
        parser.error("Supply --original or explicitly choose --download")
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("Source PDF does not match the frozen IMSLP 51556 file")
    writer = PdfWriter()
    writer.add_page(PdfReader(io.BytesIO(raw)).pages[7])
    writer.add_metadata({"/Title": "Schumann, Op. 68 No. 10 — source page",
                         "/Subject": "Full page 8 extracted without cropping from IMSLP 51556; printed page 8",
                         "/Creator": "pypdf 6.10.0"})
    stream = io.BytesIO()
    writer.write(stream)
    data = stream.getvalue()
    if hashlib.sha256(data).hexdigest() != EXCERPT_SHA:
        raise ValueError("Excerpt bytes differ; check the pinned pypdf version and extraction metadata")
    target = ROOT / "local/schumann-op68-no10-source-page.pdf"
    target.parent.mkdir(exist_ok=True)
    if target.exists() and target.read_bytes() != data:
        raise FileExistsError(f"Preserving a different file: {target}")
    if not target.exists():
        with target.open("xb") as output:
            output.write(data)
    print(f"Open this one-page PDF in the viewer: {target}")


if __name__ == "__main__":
    main()
