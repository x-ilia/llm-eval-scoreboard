"""Compare local JSON evaluation files; no model calls or provider SDK required."""
import argparse
import json
import math
from pathlib import Path
from statistics import mean

def normalize(text: str) -> str:
    return " ".join(text.casefold().split())

def load_run(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("name"), str) or not data["name"].strip():
        raise ValueError("each run needs a non-empty name")
    rows = data.get("cases")
    if not isinstance(rows, list) or not rows:
        raise ValueError("cases must be a non-empty list")
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each case must be an object")
        for field in ("id", "expected", "actual"):
            if not isinstance(row.get(field), str):
                raise ValueError(f"{field} must be a string")
        if not row["id"].strip() or row["id"] in seen:
            raise ValueError("case IDs must be non-empty and unique")
        seen.add(row["id"])
        for field in ("latency_ms", "cost_usd"):
            value = row.get(field)
            try:
                valid = type(value) in (float, int) and value >= 0 and math.isfinite(value)
            except OverflowError:
                valid = False
            if not valid:
                raise ValueError(f"{field} must be a finite nonnegative number")
    return data

def compare(paths: list[Path]) -> list[dict]:
    if not paths:
        raise ValueError("at least one run is required")
    runs = [load_run(path) for path in paths]
    reference = {row["id"]: row["expected"] for row in runs[0]["cases"]}
    names = set()
    results = []
    for run in runs:
        if run["name"] in names:
            raise ValueError("run names must be unique")
        names.add(run["name"])
        if {row["id"]: row["expected"] for row in run["cases"]} != reference:
            raise ValueError("runs must contain identical case IDs and expected answers")
        rows = run["cases"]
        matched = sum(normalize(row["actual"]) == normalize(row["expected"]) for row in rows)
        results.append({"name": run["name"], "cases": len(rows), "matched": matched,
                        "accuracy": round(matched / len(rows), 6),
                        "mean_latency_ms": round(mean(row["latency_ms"] for row in rows), 3),
                        "total_cost_usd": round(sum(row["cost_usd"] for row in rows), 8)})
    return sorted(results, key=lambda row: (-row["accuracy"], row["mean_latency_ms"], row["name"]))

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path, nargs="+")
    args = parser.parse_args(argv)
    try:
        report = compare(args.runs)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0
