#!/usr/bin/env python3
"""Compute the Observability Portal savings baseline from a ticket export.

Stdlib only, same as the rest of the repo. Feed it a CSV of historical
alert/monitoring requests (see savings-baseline-template.csv and
docs/planning/savings-baseline.md for how to produce one) and it prints
the measured figures plus a paste-ready markdown block for the Savings
section of docs/planning/overview.md.

Usage:
  python3 compute_savings.py requests.csv
  python3 compute_savings.py requests.csv --default-minutes 45 --fte-hours 160

CSV columns (header required):
  request_id        any identifier (only counted, never parsed)
  created_at        when the request was raised - ISO 8601 or dd/mm/yyyy
  resolved_at       optional; when it was fulfilled - same formats
  handling_minutes  optional; hands-on engineer minutes if known.
                    Blank rows fall back to --default-minutes.
"""

import argparse
import csv
import statistics
import sys
from datetime import datetime

DATE_FORMATS = (
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y",
)


def parse_date(raw):
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date: {raw!r} (expected ISO 8601 or dd/mm/yyyy)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("csv_file")
    ap.add_argument("--default-minutes", type=float, default=45.0,
                    help="hands-on minutes assumed when handling_minutes is blank (default: 45)")
    ap.add_argument("--fte-hours", type=float, default=160.0,
                    help="engineer-hours per FTE-month used for the FTE fraction (default: 160)")
    args = ap.parse_args()

    rows = []
    with open(args.csv_file, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    if not rows:
        sys.exit("No data rows in CSV.")

    created = [parse_date(r.get("created_at")) for r in rows]
    if any(c is None for c in created):
        sys.exit("Every row needs created_at.")

    months = max(
        (max(created).year - min(created).year) * 12
        + (max(created).month - min(created).month) + 1,
        1,
    )
    per_month = len(rows) / months

    minutes = []
    assumed = 0
    for r in rows:
        raw = (r.get("handling_minutes") or "").strip()
        if raw:
            minutes.append(float(raw))
        else:
            minutes.append(args.default_minutes)
            assumed += 1
    avg_minutes = statistics.mean(minutes)
    hours_per_month = per_month * avg_minutes / 60.0

    waits = []
    for r, c in zip(rows, created):
        res = parse_date(r.get("resolved_at"))
        if res and res >= c:
            waits.append((res - c).total_seconds() / 86400.0)

    span = f"{min(created):%Y-%m} .. {max(created):%Y-%m}"
    print(f"Requests:            {len(rows)} over {months} month(s) ({span})")
    print(f"Requests/month:      {per_month:.1f}")
    print(f"Avg handling mins:   {avg_minutes:.1f}"
          + (f"  ({assumed}/{len(rows)} rows assumed {args.default_minutes:g} min)" if assumed else "  (all measured)"))
    print(f"Engineer-hours/mo:   {hours_per_month:.1f}  (~{hours_per_month / args.fte_hours:.2f} FTE)")
    if waits:
        print(f"Requester wait:      median {statistics.median(waits):.1f} days, "
              f"mean {statistics.mean(waits):.1f} days (n={len(waits)})")
    else:
        print("Requester wait:      no resolved_at data")

    print("\n--- paste into docs/planning/overview.md, Savings section ---\n")
    print(f"Measured over {span} ({len(rows)} requests): "
          f"{per_month:.0f} requests a month averaging {avg_minutes:.0f} engineer-minutes "
          f"of hands-on work each - {hours_per_month:.0f} engineer-hours a month "
          f"(~{hours_per_month / args.fte_hours:.1f} FTE) returned by self-service"
          + (f", with requesters currently waiting a median {statistics.median(waits):.1f} days per request."
             if waits else "."))


if __name__ == "__main__":
    main()
