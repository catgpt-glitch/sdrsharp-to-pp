#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SDR# Frequencies.xml -> SDR++ frequency_manager_config.json converter

- Reads SDR# "Frequencies.xml"
- Merges bookmarks into SDR++ "frequency_manager_config.json"
- Creates/updates SDR++ lists based on SDR# GroupName
- Keeps existing SDR++ lists/bookmarks (does not delete)

Usage:
  python sdrsharp_to_sdrpp.py Frequencies.xml frequency_manager_config.json --out frequency_manager_config.json.new
  (then replace the original json after 확인)

Notes:
- SDR++ 'mode' enum may differ by version/build.
  If modes look wrong, adjust MODE_MAP below.
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# ---- SDR++ mode mapping (adjust if needed) ----
# Common guess:
# 0=NFM, 1=WFM, 2=AM, 3=DSB, 4=USB, 5=LSB, 6=CW, 7=RAW
MODE_MAP = {
    "NFM": 0,
    "WFM": 1,
    "AM":  2,
    "DSB": 3,
    "USB": 4,
    "LSB": 5,
    "CW":  6,
    "RAW": 7,
}

def safe_list_name(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return "General"
    # SDR++ list key is a string; keep it simple
    return name.replace("/", "_").replace("\\", "_").replace("\n", " ").strip()

def parse_sdrsharp_xml(xml_path: Path):
    """
    Returns a list of dict entries:
    {
      name: str,
      group: str,
      freq_hz: float,
      detector: str,
      bandwidth_hz: float|None,
      is_fav: bool
    }
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    entries = []
    for me in root.findall("MemoryEntry"):
        name = (me.findtext("Name") or "").strip()
        group = (me.findtext("GroupName") or "").strip()
        detector = (me.findtext("DetectorType") or "").strip().upper()

        freq_txt = (me.findtext("Frequency") or "").strip()
        try:
            freq_hz = float(freq_txt)
        except ValueError:
            continue

        bw_txt = (me.findtext("FilterBandwidth") or "").strip()
        bandwidth_hz = None
        if bw_txt:
            try:
                bandwidth_hz = float(bw_txt)
            except ValueError:
                bandwidth_hz = None

        fav_txt = (me.findtext("IsFavourite") or "").strip().lower()
        is_fav = fav_txt in ("true", "1", "yes")

        if not name:
            # Fallback: make a name from frequency if missing
            name = f"{int(freq_hz)} Hz"

        entries.append({
            "name": name,
            "group": group,
            "freq_hz": float(freq_hz),
            "detector": detector,
            "bandwidth_hz": bandwidth_hz,
            "is_fav": is_fav,
        })

    return entries

def load_sdrpp_json(json_path: Path):
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "lists" not in data or not isinstance(data["lists"], dict):
        data["lists"] = {}
    return data

def ensure_list(data, list_name: str):
    lists = data["lists"]
    if list_name not in lists or not isinstance(lists[list_name], dict):
        lists[list_name] = {"showOnWaterfall": True, "bookmarks": {}}
    if "bookmarks" not in lists[list_name] or not isinstance(lists[list_name]["bookmarks"], dict):
        lists[list_name]["bookmarks"] = {}
    if "showOnWaterfall" not in lists[list_name]:
        lists[list_name]["showOnWaterfall"] = True
    return lists[list_name]

def merge_entries_into_sdrpp(data, entries, flatten=False, fav_prefix=False):
    added = 0
    updated = 0

    for e in entries:
        group_name = "General" if flatten else safe_list_name(e["group"])
        lst = ensure_list(data, group_name)
        bookmarks = lst["bookmarks"]

        # SDR++ bookmarks are keyed by name. Avoid overwrite collisions.
        key = e["name"].strip()
        if fav_prefix and e["is_fav"]:
            key = "★ " + key

        base_key = key
        n = 2
        while key in bookmarks:
            # If same frequency & mode, treat as update; otherwise create unique key
            existing = bookmarks.get(key, {})
            if (
                isinstance(existing, dict)
                and float(existing.get("frequency", -1)) == float(e["freq_hz"])
            ):
                break
            key = f"{base_key} ({n})"
            n += 1

        mode = MODE_MAP.get(e["detector"], MODE_MAP.get("NFM", 0))
        bw = e["bandwidth_hz"]
        if bw is None:
            # Reasonable defaults if missing
            if e["detector"] == "WFM":
                bw = 200000.0
            elif e["detector"] == "NFM":
                bw = 12000.0
            else:
                bw = 10000.0

        new_obj = {
            "frequency": float(e["freq_hz"]),
            "bandwidth": float(bw),
            "mode": int(mode),
        }

        if key in bookmarks:
            bookmarks[key] = new_obj
            updated += 1
        else:
            bookmarks[key] = new_obj
            added += 1

    return added, updated

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frequencies_xml", type=Path, help="SDR# Frequencies.xml")
    ap.add_argument("sdrpp_json", type=Path, help="SDR++ frequency_manager_config.json")
    ap.add_argument("--out", type=Path, default=None, help="Output path (default: print to stdout)")
    ap.add_argument("--flatten", action="store_true", help="Put all bookmarks into SDR++ 'General' list")
    ap.add_argument("--fav-prefix", action="store_true", help="Prefix favourites with '★ '")
    args = ap.parse_args()

    entries = parse_sdrsharp_xml(args.frequencies_xml)
    data = load_sdrpp_json(args.sdrpp_json)

    added, updated = merge_entries_into_sdrpp(
        data, entries, flatten=args.flatten, fav_prefix=args.fav_prefix
    )

    out_text = json.dumps(data, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(out_text, encoding="utf-8")
        print(f"OK: wrote {args.out} (added={added}, updated={updated}, total_in_xml={len(entries)})")
    else:
        print(out_text)

if __name__ == "__main__":
    sys.exit(main())
