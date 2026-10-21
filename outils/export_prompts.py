r"""
TD 1 - Write prompts-en.md from the prompt constants of the skeleton, exactly as sent.

Run from the repository root:
    python outils/export_prompts.py

The file holds the system message, the user template and the schema inserted
into it. It also recomputes the SHA-256 fingerprint of C01 and compares it with
the fingerprint stored in the traces, to prove that the prompt shown is the one used.
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("skeleton", ROOT / "skeleton-multi-llm-en.py")
skeleton = importlib.util.module_from_spec(spec)
sys.modules["skeleton"] = skeleton
spec.loader.exec_module(skeleton)

schema = (ROOT / "schema.sql").read_text(encoding="utf-8")
questions = json.loads((ROOT / "questions-td1.json").read_text(encoding="utf-8"))
items = questions["questions"] if isinstance(questions, dict) else questions
c01 = next(q for q in items if q["id"] == "C01")
_, _, digest = skeleton.build_prompt(schema, c01["question"])

with open(ROOT / "traces-td1.csv", newline="", encoding="utf-8") as f:
    stored = {r["prompt_sha256"] for r in csv.DictReader(f) if r["case_id"] == "C01"}

text = f"""# Prompts used in TD 1

Copied by `outils/export_prompts.py` from `SYSTEM_PROMPT` and `USER_PROMPT_TEMPLATE` in
`skeleton-multi-llm-en.py`, unchanged since the kit of 14 October 2026. The same prompt was
sent to the five models; no variant was used.

Check: the SHA-256 fingerprint recomputed for C01 is `{digest}`; the traces store
{"the same value" if stored == {digest} else "a DIFFERENT value: " + ", ".join(sorted(stored))} for C01 on all five models.

## System message

```
{skeleton.SYSTEM_PROMPT}
```

## User template

`{{schema}}` is replaced by `schema.sql` (shown below) and `{{question}}` by the question text
from `questions-td1.json`.

```
{skeleton.USER_PROMPT_TEMPLATE}
```

## Schema inserted in `{{schema}}`

```sql
{schema.strip()}
```
"""
(ROOT / "prompts-en.md").write_text(text, encoding="utf-8")
print("prompts-en.md written; C01 fingerprint matches traces:", stored == {digest})
