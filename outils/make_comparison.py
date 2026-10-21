r"""
TD 1 - Build the rows of model-question-comparison-en.csv from the operators' trace files.

Run from the repository root, with the five raw trace files then the output:
    python outils/make_comparison.py traces/traces-A.csv traces/traces-B.csv traces/traces-C.csv traces/traces-D.csv traces/traces-E.csv model-question-comparison-en.csv

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

# Explanations for operator B (gpt-oss-20b, Groq), from the SQL and errors in traces-B.csv.
EXPLANATIONS.update({
    ("openai/gpt-oss-20b", "C02"): (
        "Wrong age window: birth_date > '2025-09-25' AND <= '2026-09-25' selects customers born "
        "in the last year (age 0) instead of 2000-09-26 to 2001-09-25; none exist, so 0. "
        "Valid SQL, wrong meaning."),
    ("openai/gpt-oss-20b", "C09"): (
        "Wrong age window: birth_date > '2001-09-26' AND <= '2026-09-26' keeps every customer "
        "aged 0 to 24 instead of those born 2000-09-27 to 2001-09-26. Valid SQL, wrong meaning."),
    ("openai/gpt-oss-20b", "C11"): (
        "Wrong age window: birth_date > '2001-12-01' AND <= '2006-12-01' keeps ages 20 to 24 on "
        "2026-12-01 instead of 25 (born 2000-12-02 to 2001-12-01). Valid SQL, wrong meaning."),
    ("openai/gpt-oss-20b", "C20"): (
        "Correct on attempt 2. Attempt 1 failed with HTTP 429 (Groq tokens-per-minute limit: "
        "8000, used 7266, requested 1145): an access failure, not a wrong answer; retried once "
        "by the skeleton as the protocol allows. Both attempts are in the raw trace."),
})

# Explanations for operator C (Cohere, OpenRouter), from the SQL in traces-C.csv.
# Every figure was checked by re-running the query or the condition on the database.
EXPLANATIONS.update({
    ("cohere/north-mini-code:free", "C02"): (
        "Invalid SQL (syntax error near ')'): CAST(strftime('%Y', '2026-09-25')) has no target "
        "type, AS INTEGER is missing. The query also builds a date modifier by hand with nested CASE."),
    ("cohere/north-mini-code:free", "C08"): (
        "Age lower bound missing: birth_date > '2000-09-24' AND <= '2026-09-24' keeps every "
        "customer under 26 (13 customers instead of 6); their total is exactly 1188090."),
    ("cohere/north-mini-code:free", "C09"): (
        "Invalid SQL (syntax error near 'AS'): an alias 'AS age' is written inside the WHERE "
        "clause; the condition also compares the birth year itself with 25."),
    ("cohere/north-mini-code:free", "C10"): (
        "Age at the time of the order is computed but never compared with 25: keeps every order "
        "line whose birthday of that year has passed; that total is exactly 907310."),
    ("cohere/north-mini-code:free", "C11"): (
        "Year difference reversed (birth year minus 2026, between -68 and -20) and compared with "
        "0 or 1; 25 never appears, no row passes, so 0."),
    ("cohere/north-mini-code:free", "C15"): (
        "Same error as C08: the age lower bound is missing, every customer under 26 is kept; "
        "period filter correct; total exactly 314020."),
    ("cohere/north-mini-code:free", "C16"): (
        "Contradictory bounds reduce the filter to birth_date = '2001-09-25' "
        "(date('2026-09-25','-25 years') <= birth_date <= the same date); only C001 remains, 80190."),
    ("cohere/north-mini-code:free", "C17"): (
        "Wrong substring positions: on '2001-09-25', substr(birth_date,6,2)||'-'||substr(birth_date,1,4) "
        "gives '09-2001' and substr(birth_date,7,4) gives '9-25'; the age never equals 25, so 0."),
})

# Explanations for operator D (Qwen, Groq), from the SQL in traces-D.csv.
EXPLANATIONS.update({
    ("qwen/qwen3.8-27b", "C09"): (
        "Age computed at each order date (o.date) instead of the reference date 2026-09-26, which "
        "is absent from the SQL; month-day >= birth month-day and < the month-day of birth + 26 "
        "years contradict each other, so 0."),
    ("qwen/qwen3.8-27b", "C10"): (
        "Invalid SQL: no such function COALESE (typo for COALESCE). With only the typo fixed the "
        "query gives 119410: its second branch (year difference 24, birthday not reached) is age "
        "23; it needed a difference of 26."),
    ("qwen/qwen3.8-27b", "C15"): (
        "Age reduced to a month-day comparison without the year: birth month-day <= '09-25' and "
        "> '09-25' at the same time; impossible condition, so 0. Period filter correct."),
    ("qwen/qwen3.8-27b", "C17"): (
        "Both age bounds one day off (born in 2001 before 09-25, or in 2000 from 09-25): excludes "
        "C001 (born 2001-09-25, aged 25 that day, 80190) and includes C004 (born 2000-09-25, "
        "aged 26, 70500); gap 9690, exactly the observed difference."),
    ("qwen/qwen3.8-27b", "C19"): (
        "Compares a year alone ('2026') with a full date ('2026-09-25') as text; '2026' <= "
        "'2026-09-25' is always true, so the filter has no upper age bound: 56 of 59 customers "
        "kept instead of 6."),
})


def main(trace_paths, out_path):
    last, order = {}, {}           # cell_id -> last attempt (file order, then attempts)
    for i, trace_path in enumerate(trace_paths):
        with open(trace_path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                r["trace_file"] = Path(trace_path).as_posix()
                order.setdefault(r["model_requested"], i)
                key = r["cell_id"]
                if key not in last or int(r.get("attempts") or 0) >= int(last[key].get("attempts") or 0):
                    last[key] = r

    out_rows, missing = [], []
    for r in sorted(last.values(), key=lambda r: (order[r["model_requested"]], r["case_id"])):
        status = r["verdict"]
        explanation = EXPLANATIONS.get((r["model_requested"], r["case_id"]), "")
        if status == "correct" and not explanation:
            explanation = "Value equals the checked reference."
        if status != "correct" and not explanation:
            missing.append(r["cell_id"])
            explanation = "TODO: read the SQL / error in the trace"
        # traces/traces-X.csv -> notes/analyse-role-X.md, the detailed reading of each failure
        note = Path("notes") / f"analyse-role-{Path(r['trace_file']).stem.split('-')[-1]}.md"
        if explanation != "Value equals the checked reference." and note.exists():
            explanation += f" See {note.as_posix()}."
        out_rows.append({
            "case_id": r["case_id"],
            "model_id": f'{r["provider"]}:{r["model_requested"]}',
            "trace_file": r["trace_file"],
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
    if len(sys.argv) < 3:
        sys.exit("usage: make_comparison.py TRACES.csv [MORE_TRACES.csv ...] OUTPUT.csv")
    main(sys.argv[1:-1], sys.argv[-1])
