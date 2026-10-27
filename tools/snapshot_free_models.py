"""Record OpenRouter's public free-model catalogue; makes no inference calls.

python tools/snapshot_free_models.py --output /tmp/free-models.json
python tools/snapshot_free_models.py --input /tmp/catalogue.json --output /tmp/free-models.json

Existing snapshots are preserved. Write a new filename when refreshing research.
"""

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import urllib.request

URL = "https://openrouter.ai/api/v1/models"


def snapshot(raw):
    catalogue = json.loads(raw)
    models = []
    for model in catalogue["data"]:
        prices = model.get("pricing", {})
        if not model["id"].endswith(":free"):
            continue
        if any(Decimal(prices.get(key, "-1")) != 0 for key in ("prompt", "completion")):
            continue
        models.append({key: model.get(key) for key in (
            "id", "name", "created", "context_length", "architecture", "pricing",
            "supported_parameters", "top_provider", "per_request_limits",
        )})
    return {
        "source": URL,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
        "selection": "IDs ending :free with zero prompt and completion prices; catalogue metadata, not tested inference",
        "count": len(models),
        "models": sorted(models, key=lambda item: item["id"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Filter an already downloaded public catalogue")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Preserving snapshot: {args.output}")
    if args.input:
        raw = args.input.read_bytes()
    else:
        request = urllib.request.Request(URL, headers={"User-Agent": "CAMAT-Seminar-Reference/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
    result = snapshot(raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"Recorded {result['count']} free variants in {args.output}")


if __name__ == "__main__":
    main()
