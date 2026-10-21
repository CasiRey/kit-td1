r"""
TD 1 - Merge the five operators' raw traces into traces-td1.csv and traces-td1.jsonl.

Run from the repository root:
    python outils/merge_traces.py

- reads traces/traces-A.csv ... traces-E.csv and traces/state-A.jsonl ... state-E.jsonl;
- keeps every attempt (retries and access errors included), in operator order A to E;
- writes one CSV under a single header and one JSONL, then checks that each merged
  row is equal, field by field, to its source row. The source files are not modified.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPERATORS = ["A", "B", "C", "D", "E"]


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    header, rows, records = None, [], []
    for op in OPERATORS:
        fields, lot = read_csv(ROOT / "traces" / f"traces-{op}.csv")
        if header is None:
            header = fields
        elif fields != header:
            raise SystemExit(f"traces-{op}.csv: columns differ from traces-A.csv")
        rows += lot
        records += read_jsonl(ROOT / "traces" / f"state-{op}.jsonl")
        print(f"{op}: {len(lot)} CSV rows")

    with open(ROOT / "traces-td1.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    with open(ROOT / "traces-td1.jsonl", "w", newline="\n", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    _, merged = read_csv(ROOT / "traces-td1.csv")
    assert merged == rows, "merged CSV differs from the sources"
    assert read_jsonl(ROOT / "traces-td1.jsonl") == records, "merged JSONL differs from the sources"
    cells = {r["cell_id"] for r in rows}
    print(f"traces-td1.csv: {len(rows)} rows (attempts) for {len(cells)} cells; "
          f"traces-td1.jsonl: {len(records)} lines; both equal to their sources")


if __name__ == "__main__":
    main()
