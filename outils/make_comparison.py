r"""
TD 1 - Build the rows of model-question-comparison-en.csv from one operator's trace file.

Run from the kit-td1 folder, for example for operator E:
    .venv\Scripts\python.exe make_comparison.py traces-E.csv comparison-E.csv

- one final row per model/question: the LAST attempt of each cell_id is kept
  (all attempts stay in the raw trace file);
- columns of the template: case_id, model_id, trace_file, cell_id, nature,
  status, value_cents, reference_cents, explanation;
- explanations come from the EXPLANATIONS dictionary below, written after reading
  the SQL of each failed cell. A failed cell without an explanation is flagged.
"""
import csv
import sys
from pathlib import Path

COLUMNS = ["case_id", "model_id", "trace_file", "cell_id", "nature",
           "status", "value_cents", "reference_cents", "explanation"]

# Explanations for operator E (Dots, OpenRouter), from the SQL in traces-E.csv.
HALF_AGE = ("Age convention broken: keeps only year difference = 25 with birthday already "
            "reached; misses customers with year difference = 26 whose birthday has not come "
            "yet (still 25). Valid SQL, wrong meaning.")
EXPLANATIONS = {
    ("dots-studio/dots-3-note-preview:free", "C02"): HALF_AGE + " (reference date 2026-09-25)",
    ("dots-studio/dots-3-note-preview:free", "C08"): (
        "Age convention broken: the first branch requires the birthday to be exactly 09-24 "
        "(<= and >= on month-day), so customers aged 25 with an earlier birthday are missed; "
        "the second branch (year difference 26, birthday not reached) is right."),
    ("dots-studio/dots-3-note-preview:free", "C11"): (
        "Question misread: filters birth_date = '2001-12-01' (exact birthday) and orders "
        "placed on 2026-12-01; the reference date is not an order date and no order exists "
        "then, so 0."),
    ("dots-studio/dots-3-note-preview:free", "C15"): HALF_AGE + " Period filter correct.",
    ("dots-studio/dots-3-note-preview:free", "C16"): HALF_AGE + " Product filter correct.",
    ("dots-studio/dots-3-note-preview:free", "C17"): HALF_AGE + " Period and product filters correct.",
    ("dots-studio/dots-3-note-preview:free", "C18"): (
        "Age at the time of the order: same half-window error computed on o.date (year "
        "difference 25 and birthday reached only); misses customers in year difference 26 "
        "before their birthday. Period filter correct. C10, same family without period, is correct."),
}


def main(trace_path, out_path):
    with open(trace_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    last = {}                      # cell_id -> last attempt (file order, then attempts)
    for r in rows:
        key = r["cell_id"]
        if key not in last or int(r.get("attempts") or 0) >= int(last[key].get("attempts") or 0):
            last[key] = r

    out_rows, missing = [], []
    for r in sorted(last.values(), key=lambda r: (r["model_requested"], r["case_id"])):
        status = r["verdict"]
        explanation = EXPLANATIONS.get((r["model_requested"], r["case_id"]), "")
        if status == "correct" and not explanation:
            explanation = "Value equals the checked reference."
        if status != "correct" and not explanation:
            missing.append(r["cell_id"])
            explanation = "TODO: read the SQL / error in the trace"
        out_rows.append({
            "case_id": r["case_id"],
            "model_id": f'{r["provider"]}:{r["model_requested"]}',
            "trace_file": Path(trace_path).name,
            "cell_id": r["cell_id"],
            "nature": r["nature"],
            "status": status,
            "value_cents": r["value"],
            "reference_cents": r["reference"],
            "explanation": explanation,
        })

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(out_rows)

    ok = sum(r["status"] == "correct" for r in out_rows)
    print(f"{len(out_rows)} rows written to {out_path} ({ok} correct)")
    if missing:
        print("Failed cells still without explanation:", ", ".join(missing))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: make_comparison.py TRACES.csv OUTPUT.csv")
    main(sys.argv[1], sys.argv[2])
