"""Check the edition; explicitly report narrower CI coverage without local scans.

Local: python scripts/check_edition.py
CI:    python scripts/check_edition.py --without-local-images
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from camat.mei_validation import run_mei_validation

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--without-local-images", action="store_true")
    args = parser.parse_args()
    result = run_mei_validation([ROOT / "mei/work.mei"], root=ROOT,
                               output_dir=ROOT / "validation-runtime",
                               check_resources=not args.without_local_images,
                               check_verovio=True)
    record = result.record
    checks = ["xml_references", "relaxng", "schematron", "input_hashes", "verovio"]
    if not args.without_local_images:
        checks.append("resources")
    failed = [name for name in checks if record["executions"][name]["status"] != "passed"]
    omitted = []
    if args.without_local_images and "xml_references" in failed:
        # CAMAT also checks graphic targets in its reference pass. Accept only
        # missing graphics explicitly declared by this edition's page manifest;
        # retain the raw failed report, and reject every other reference error.
        manifest = json.loads((ROOT / "pages/pages.json").read_text())
        image_paths = {(ROOT / "pages" / page["image"]).resolve() for page in manifest["pages"]}
        root = ET.parse(ROOT / "mei/work.mei").getroot()
        declared_targets = {g.get("target") for g in root.findall("{http://www.music-encoding.org/ns/mei}music/{http://www.music-encoding.org/ns/mei}facsimile/{http://www.music-encoding.org/ns/mei}surface/{http://www.music-encoding.org/ns/mei}graphic")
                            if (ROOT / "mei" / g.get("target", "")).resolve() in image_paths}
        findings = json.loads((ROOT / "validation-runtime/findings.json").read_text())
        errors = [f for f in findings if f["origin"] == "CAMAT xml_references" and f["severity"] == "error"]
        if errors and all(f["check"] == "missing_reference_document" and f["element"] == "graphic"
                          and f["actual"] in declared_targets for f in errors):
            omitted = errors
            failed.remove("xml_references")
    coverage = {"scope": "CI: XML/schema/references/rendering; local images omitted" if args.without_local_images
                else "Local: required conformance checks and Verovio, including local images",
                "checked": checks, "failed": failed, "conformance": record["conformance"],
                "xml_reference_status": record["executions"]["xml_references"]["status"],
                "expected_missing_local_graphics": omitted,
                "consumer_diagnostics": record["consumer_diagnostics"],
                "source_fidelity": "Requires a recorded human source comparison"}
    (ROOT / "validation-runtime/coverage.json").write_text(json.dumps(coverage, indent=2) + "\n")
    print(json.dumps(coverage, indent=2))
    if args.without_local_images:
        print("CI accepts only its declared local-image omissions. Raw full conformance may be failed/incomplete; this is not a full validation pass.")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
