"""Export a local SVG/scan editorial packet; does not call a model provider.

python tools/export_svg_editorial.py --mei /path/to/edition/mei/work.mei --output /path/to/new-packet
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "notebooks/helpers"))
from svg_editorial import export_svg_editorial_packet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mei", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = export_svg_editorial_packet(args.mei, args.output)
    print("Packet:", args.output.resolve())
    print("Input SHA-256:", report["identity"]["input_mei_sha256"])
    print("Measures:", len(report["measures_in_svg"]), "mapped events:", report["events_mapped"])
    print("SVG variants render identical pixels:", report["normal_and_enriched_pixels_identical"])


if __name__ == "__main__":
    main()
