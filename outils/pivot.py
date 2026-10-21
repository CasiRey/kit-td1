r"""
TD 1 - Models x questions pivot of the comparison CSV, for the plenary.

Run from the repository root, with one or several comparison files:
    python outils/pivot.py model-question-comparison-en.csv

Prints the matrix and writes resultats/pivot-td1.md (a view of the long CSV, not a second entry).
Symbols: OK correct, X incorrect, R sql_rejected / invalid, - not executed or missing.
"""
import csv
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "resultats" / "pivot-td1.md"
SYMBOL = {"correct": "OK", "incorrect": "X"}
CASES = [f"C{i:02d}" for i in range(1, 21)]


def main(paths):
    rows = []
    for p in paths:
        with open(p, newline="", encoding="utf-8-sig") as f:
            rows += list(csv.DictReader(f))

    cells, models = {}, []
    for r in rows:
        m = r["model_id"]
        if m not in models:
            models.append(m)
        cells[(m, r["case_id"])] = r["status"]

    def sym(status):
        if status is None or status == "not_executed":
            return "-"
        return SYMBOL.get(status, "R")

    lines = ["| model | " + " | ".join(c[1:] for c in CASES) + " | correct |",
             "|---|" + "---|" * len(CASES) + "---|"]
    for m in models:
        statuses = [cells.get((m, c)) for c in CASES]
        ok = sum(s == "correct" for s in statuses)
        run = sum(s not in (None, "not_executed") for s in statuses)
        lines.append(f"| {m} | " + " | ".join(sym(s) for s in statuses) + f" | {ok}/{run} |")

    text = "\n".join(lines)
    print(text)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        "# TD 1 - models x questions (view of the comparison CSV)\n\n"
        "OK correct, X incorrect, R rejected/invalid, - not executed\n\n" + text + "\n",
        encoding="utf-8")
    print(f"\nWritten: {OUT.relative_to(OUT.parent.parent).as_posix()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: pivot.py COMPARISON.csv [MORE.csv ...]")
    main(sys.argv[1:])
