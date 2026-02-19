from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Any, List

import httpx

# -----------------------
# Paths
# -----------------------
IN_PATH = Path("./data/addresses.csv")
OUT_PATH = Path("./data/result.csv")

# -----------------------
# API
# -----------------------
API_BASE = "http://localhost:8000"
CREATE_ENDPOINT = "/addresses"

# -----------------------
# Helpers
# -----------------------
def clean(s: Any) -> str:
    return "" if s is None else str(s).strip()


def post_address(client: httpx.Client, address: str) -> Dict[str, Any]:
    """
    Runs the full project flow via your backend:
    - Mapbox lookup inside backend
    - similarity scoring inside backend
    - saves into DB inside backend
    Returns the created Address JSON.
    """
    resp = client.post(f"{API_BASE}{CREATE_ENDPOINT}", json={"address": address})
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    if not IN_PATH.exists():
        raise FileNotFoundError(f"Missing input file: {IN_PATH.resolve()}")

    # Read CSV input
    with IN_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("addresses.csv is missing a header row.")
        if "address" not in reader.fieldnames:
            raise ValueError(f"addresses.csv must have an 'address' column. Found: {reader.fieldnames}")

        input_rows = list(reader)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    results: List[Dict[str, Any]] = []

    timeout = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)

    with httpx.Client(timeout=timeout) as client:
        for idx, row in enumerate(input_rows, start=1):
            address = clean(row.get("address"))

            if not address:
                results.append({"address": "", "matched_address": "", "similarity_score": 0.0})
                continue

            try:
                created = post_address(client, address)

                # Your API response model uses match_score + matched_address
                results.append(
                    {
                        "address": created.get("address", address),
                        "matched_address": created.get("matched_address", ""),
                        "similarity_score": float(created.get("match_score", 0.0)),
                    }
                )
            except Exception as e:
                # Continue on error; still write something to results.csv
                print(f"[{idx}/{len(input_rows)}] ERROR for '{address}': {e}")
                results.append(
                    {"address": address, "matched_address": "", "similarity_score": 0.0}
                )

            if idx % 25 == 0:
                print(f"Processed {idx}/{len(input_rows)}...")

    # Write results CSV
    with OUT_PATH.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(
            f_out,
            fieldnames=["address", "matched_address", "similarity_score"],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Done ✅  DB populated via API + results written to: {OUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
