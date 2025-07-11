"""zigma_api_to_csv.py
---------------------------------
Fetch weighbridge records from multiple Zigma Global API endpoints,
transform the data to Swaccha Andhra schema, and write the result
into a single CSV file.

Author: <your‑name>
Date: 2025‑06‑16
"""

import csv
import datetime as dt
import os
import sys
from typing import List, Dict, Any

import requests

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# API endpoints to query
ENDPOINTS: List[str] = [
    "https://zigmaglobal.in/vizagsac/api/product/search.php",
    "https://zigmaglobal.in/tpty/api/product/search.php",
    "https://zigmaglobal.in/palamaner/api/product/search.php",
    "https://zigmaglobal.in/donthalli/api/product/search.php",
    "https://zigmaglobal.in/madanapalle/api/product/search.php",
    "https://zigmaglobal.in/kuppam/api/product/search.php",
    "https://zigmaglobal.in/allipuram/api/product/search.php",
]

# Output folder and file name pattern
OUTPUT_DIR = "./output"
FILENAME_PATTERN = "zigma_weight_records_{ts}.csv"  # ts will be YYYYMMDD_HHMMSS

# Swaccha Andhra canonical column order
COLUMN_ORDER: List[str] = [
    "date", "time", "site_name", "agency_name", "material", "ticket_no", "vehicle_no",
    "transfer_party_name", "first_weight", "first_timestamp", "second_weight",
    "second_timestamp", "net_weight", "material_type", "first_front_image",
    "first_back_image", "second_front_image", "second_back_image", "site_incharge",
    "user_name", "cloud_upload_timestamp", "record_status", "net_weight_calculated",
    "_source_file", "_processed_timestamp", "_folder_source",
]

# ---------------------------------------------------------------------------
# TRANSFORMATION LOGIC
# ---------------------------------------------------------------------------

def transform_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map a single API record to the canonical schema."""

    # Helper to safely fetch keys (case‑sensitive API)
    def g(key: str, default: str = "") -> str:
        return str(raw.get(key, default)).strip()

    # Build transformed dict with defaults of empty string
    rec = {col: "" for col in COLUMN_ORDER}

    rec["date"] = g("Date")
    rec["time"] = g("Time")
    rec["site_name"] = g("Site")
    rec["agency_name"] = "zigma"  # static value
    rec["material"] = g("Material Name")
    rec["ticket_no"] = g("Ticket No")
    rec["vehicle_no"] = g("Vehicle No")
    rec["transfer_party_name"] = ""  # always empty/null per spec

    # Weighment details
    rec["first_weight"] = g("Loaded Weight")
    rec["first_timestamp"] = g("Load Weight Time")
    rec["second_weight"] = g("Empty Weight")
    rec["second_timestamp"] = g("Empty Weight Time")
    rec["net_weight"] = g("Net Weight")
    rec["material_type"] = g("Material Name")  # alias

    # Image paths and meta are not provided by API – leave blank

    # Add processing metadata
    rec["_processed_timestamp"] = dt.datetime.utcnow().isoformat()
    rec["_source_file"] = raw.get("_endpoint", "")  # injected later
    rec["_folder_source"] = "zigmaglobal_api"

    return rec

# ---------------------------------------------------------------------------
# DATA COLLECTION
# ---------------------------------------------------------------------------

def fetch_endpoint(url: str) -> List[Dict[str, Any]]:
    """Return list of JSON records from endpoint (or empty list on error)."""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        # API may return a list directly or a dict with a key – handle both
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # find first list value within dict
            for v in data.values():
                if isinstance(v, list):
                    return v
        print(f"Warning: Unrecognized payload structure from {url}")
    except Exception as exc:
        print(f"Error fetching {url}: {exc}")
    return []

# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def main():
    # 1. Gather data from all endpoints
    raw_records: List[Dict[str, Any]] = []
    for ep in ENDPOINTS:
        print(f"Fetching {ep} …")
        for rec in fetch_endpoint(ep):
            rec["_endpoint"] = ep  # annotate for lineage
            raw_records.append(rec)
    print(f"Fetched {len(raw_records)} total records.")

    if not raw_records:
        print("No data retrieved – exiting.")
        sys.exit(1)

    # 2. Transform records
    transformed: List[Dict[str, Any]] = [transform_record(r) for r in raw_records]

    # 3. Ensure output folder exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 4. Write CSV
    ts_str = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = os.path.join(OUTPUT_DIR, FILENAME_PATTERN.format(ts=ts_str))

    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMN_ORDER)
        writer.writeheader()
        writer.writerows(transformed)

    print(f"CSV written to {outfile} (rows: {len(transformed)})")


if __name__ == "__main__":
    main()
