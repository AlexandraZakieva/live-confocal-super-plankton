#!/usr/bin/env python3
"""
TSV QC + File_list builder (CLI)

Usage:
  python tsv_qc_filelist.py <input_table_1.tsv> <input_table_2.csv> [-o OUTPUT_DIR]

- <input_table_1.tsv> must contain at least columns:
    name
    (BioSamples_ID is auto-detected even if the header differs)
    Channel Name 1..4, Channel Visualized Entity Name 1..4,
    Channel Visualized Entity Type 1..4, Channel Label 1..4   (missing → blank)

- <input_table_2.csv> must contain columns:
    name, tile, acquisition_date, acquisition_location
  (If a header cell contains an inline comment like "acquisition_location | http://…",
   the part after '|' is stripped automatically.)

Outputs (in OUTPUT_DIR, default: directory of <input_table_2>):
  - Conversion_QC.tsv
  - File_list.tsv

File_list specifics:
  • Data rows:
      Files = LiveConfocalSuperPlankton/zipped_omezarrs/<name>_<tile>.ome.zarr.zip
      acquisition_metadata (last col) = <name>.tsv
  • After data rows, append one row per unique acquisition_metadata with:
      Files = LiveConfocalSuperPlankton/CZI_metadata/<name>.tsv
      all other columns empty
"""

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Iterable

# ---- Config: channel columns to append to File_list (probe columns removed)
CHANNEL_COLS: List[str] = []
for i in range(1, 5):
    CHANNEL_COLS += [
        f"Channel Name {i}",
        f"Channel Visualized Entity Name {i}",
        f"Channel Visualized Entity Type {i}",
        f"Channel Label {i}",
    ]

FILES_PREFIX = "LiveConfocalSuperPlankton/zipped_omezarrs/"
METADATA_PREFIX = "LiveConfocalSuperPlankton/CZI_metadata/"

# ---- Helpers
def clean_header_field(h: str) -> str:
    return h.split("|", 1)[0].strip()

def read_tsv_as_dicts(path: Path, clean_header: bool = False) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        first = f.readline()
        if not first:
            return []
        headers = [h.strip() for h in first.rstrip("\n").split("\t")]
        if clean_header:
            headers = [clean_header_field(h) for h in headers]
        reader = csv.DictReader(
            [("\t".join(headers))] + f.readlines(),
            delimiter="\t",
            quoting=csv.QUOTE_MINIMAL
        )
        rows: List[Dict[str, str]] = []
        for row in reader:
            rows.append({k: (row.get(k, "") or "").strip() for k in headers})
        return rows

def read_csv_as_dicts(path: Path, clean_header: bool = False) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",", skipinitialspace=True)
        if reader.fieldnames is None:
            return []
        orig_headers = reader.fieldnames
        headers = [clean_header_field(h) for h in orig_headers] if clean_header else list(orig_headers)
        rows: List[Dict[str, str]] = []
        for row in reader:
            fixed = {}
            for orig, cleaned in zip(orig_headers, headers):
                fixed[cleaned] = (row.get(orig, "") or "").strip()
            rows.append(fixed)
        return rows

def looks_like_biosample(val: str) -> bool:
    v = (val or "").strip()
    if not v:
        return False
    lower = v.lower()
    upper = v.upper()
    return (
        "ebi.ac.uk/biosamples" in lower
        or "biosamples/samples/" in lower
        or "SAME" in upper
        or "SAMN" in upper
        or "SAMD" in upper
    )

def pick_biosamples_column(header: List[str], rows: List[Dict[str, str]]) -> Tuple[str, int]:
    candidates = [
        "BioSamples_ID", "BioSamples ID",
        "BioSample_ID", "BioSample ID",
        "BioSamples_URL", "BioSample_URL",
        "BioSamples link", "BioSample link",
        "Sample Accession", "sample_accession",
    ]
    counts: Dict[str, int] = {h: 0 for h in header}
    for r in rows[:1000]:
        for h in header:
            if looks_like_biosample(r.get(h, "")):
                counts[h] += 1
    header_pick = next((c for c in candidates if c in header), None)
    best_col = max(counts, key=lambda h: counts[h]) if counts else None
    if best_col and (header_pick is None or counts[best_col] > counts.get(header_pick, -1)):
        return best_col, counts[best_col]
    if header_pick is not None:
        return header_pick, counts.get(header_pick, 0)
    if best_col and counts[best_col] > 0:
        return best_col, counts[best_col]
    raise RuntimeError("Could not detect BioSamples column in input_table_1.")

def last_one_wins_map(rows: List[Dict[str, str]], key_col: str, val_cols: Iterable[str]) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for r in rows:
        nm = r.get(key_col, "").strip()
        if not nm:
            continue
        out.setdefault(nm, {})
        for vc in val_cols:
            out[nm][vc] = (r.get(vc, "") or "").strip()
    return out

def ensure_columns(rows: List[Dict[str, str]], required: Iterable[str], table_name: str):
    if not rows:
        raise RuntimeError(f"{table_name} appears empty.")
    missing = [c for c in required if c not in rows[0]]
    if missing:
        raise RuntimeError(f"{table_name} is missing required column(s): {', '.join(missing)}")

def write_tsv(path: Path, header: List[str], rows: Iterable[Dict[str, str]]):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(h, "") for h in header])

# ---- Main
def main():
    ap = argparse.ArgumentParser(description="Build Conversion_QC.tsv and File_list.tsv from two tables.")
    ap.add_argument("table1", type=Path, help="<input_table_1> TSV path")
    ap.add_argument("table2", type=Path, help="<input_table_2> CSV path")
    ap.add_argument("-o", "--outdir", type=Path, default=None, help="Output directory (default: alongside <input_table_2>)")
    args = ap.parse_args()

    table1: Path = args.table1
    table2: Path = args.table2
    outdir: Path = args.outdir or table2.parent

    if not table1.exists():
        raise SystemExit(f"Not found: {table1}")
    if not table2.exists():
        raise SystemExit(f"Not found: {table2}")
    outdir.mkdir(parents=True, exist_ok=True)

    # Read tables: TSV for table1, CSV for table2
    t1 = read_tsv_as_dicts(table1, clean_header=False)
    t2 = read_csv_as_dicts(table2, clean_header=True)  # strip header inline comments (after '|')
    if not t1 or not t2:
        raise SystemExit("One of the input files is empty or has no header.")

    # Table 2 sanity
    req2 = ["name", "tile", "acquisition_date", "acquisition_location"]
    ensure_columns(t2, req2, "input_table_2 (CSV)")

    # Table 1 sanity
    if "name" not in t1[0]:
        raise SystemExit("input_table_1 (TSV) must contain column: name")

    # Detect BioSamples column
    t1_header = list(t1[0].keys())
    bios_col, bios_matches = pick_biosamples_column(t1_header, t1)
    print(f"[info] Using BioSamples column: '{bios_col}' (content matches: {bios_matches})")

    # Build map name -> BioSamples_ID + channels
    t1_val_cols = [bios_col] + CHANNEL_COLS
    name_to_t1 = last_one_wins_map(t1, "name", t1_val_cols)

    # File_list header (add acquisition_metadata as the LAST column)
    file_list_header = (
        ["Files", "name", "BioSamples_ID", "tile", "acquisition_date", "acquisition_location"]
        + CHANNEL_COLS
        + ["acquisition_metadata"]
    )

    file_list_rows: List[Dict[str, str]] = []
    counts_in_t2: Dict[str, int] = {}
    unique_meta_in_order: List[str] = []
    seen_meta: set = set()

    for r in t2:
        nm = r.get("name", "").strip()
        if not nm:
            continue
        counts_in_t2[nm] = counts_in_t2.get(nm, 0) + 1

        tile = r.get("tile", "").strip()
        acq_date = r.get("acquisition_date", "").strip()
        acq_loc = r.get("acquisition_location", "").strip()

        files_val = f"{FILES_PREFIX}{nm}_{tile}.ome.zarr.zip"
        acquisition_metadata_val = f"{nm}.tsv"

        if acquisition_metadata_val not in seen_meta:
            seen_meta.add(acquisition_metadata_val)
            unique_meta_in_order.append(acquisition_metadata_val)

        mapped = name_to_t1.get(nm, {})
        bios_val = (mapped.get(bios_col, "") or "").strip()

        row = {
            "Files": files_val,
            "name": nm,
            "BioSamples_ID": bios_val,
            "tile": tile,
            "acquisition_date": acq_date,
            "acquisition_location": acq_loc,
            "acquisition_metadata": acquisition_metadata_val,
        }
        for c in CHANNEL_COLS:
            row[c] = (mapped.get(c, "") or "").strip()
        file_list_rows.append(row)

    # Append one blank row per unique acquisition_metadata:
    # Files = LiveConfocalSuperPlankton/CZI_metadata/<name>.tsv, others empty
    for meta in unique_meta_in_order:
        blank_row = {h: "" for h in file_list_header}
        blank_row["Files"] = f"{METADATA_PREFIX}{meta}"
        file_list_rows.append(blank_row)

    # Conversion_QC
    names_t1 = set(name_to_t1.keys())
    names_t2 = set(counts_in_t2.keys())
    all_names = sorted(names_t1 | names_t2)

    qc_header = ["name", "in_input_table_1", "count_in_input_table_2", "status"]
    qc_rows: List[Dict[str, str]] = []
    for nm in all_names:
        in1 = "TRUE" if nm in names_t1 else "FALSE"
        cnt = counts_in_t2.get(nm, 0)
        if in1 == "TRUE" and cnt == 0:
            status = "Missing in input_table_2"
        elif in1 == "FALSE" and cnt > 0:
            status = "Missing in input_table_1"
        elif in1 == "FALSE" and cnt == 0:
            status = "Absent in both"
        else:
            status = "OK"
        qc_rows.append({
            "name": nm,
            "in_input_table_1": in1,
            "count_in_input_table_2": str(cnt),
            "status": status
        })

    # Write outputs
    qc_path = outdir / "Conversion_QC.tsv"
    fl_path = outdir / "File_list.tsv"
    write_tsv(qc_path, qc_header, qc_rows)
    write_tsv(fl_path, file_list_header, file_list_rows)

    print(f"[done] Wrote:\n  • {qc_path}\n  • {fl_path}")

if __name__ == "__main__":
    main()
