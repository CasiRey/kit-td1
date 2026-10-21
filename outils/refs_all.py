r"""
TD 1 - References for the twenty questions C01 to C20.

Run from the repository root:
    python outils/refs_all.py

1. Builds one SQLite SELECT per question and runs it on data/boutique.sqlite
   (opened read-only).
2. Recomputes the same amount independently in pure Python from the CSV files.
3. Prints both values side by side and writes references-all.csv
   (case_id, sql, revenue_cents) to copy into reference-td1.csv.

Conventions (protocol, section 1):
- period closed on the left, open on the right: date >= start AND date < end
- completed age: year difference minus 1 if the birthday (month-day)
  has not yet come on the reference date
- "at the time of the order": the age is computed on the date of each order line
- revenue = SUM(quantity_product * price), integer cents excl. VAT, 0 if nothing matches
"""
import csv
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"            # the script lives in outils/, the database at the repository root
DB = DATA / "boutique.sqlite"

# Parameters of each question, read from questions-td1-en:
#   period = (start, end) or None, products = list or None,
#   ref = reference date for "exactly 25 on ...", at_order = age at the time of the order
CASES = {
    "C01": dict(period=("2026-03-01 00:00:00", "2026-06-01 00:00:00")),
    "C02": dict(ref="2026-09-25"),
    "C03": dict(period=("2026-01-01 00:00:00", "2026-07-01 00:00:00"), products=["a", "b", "c"]),
    "C04": dict(period=("2026-01-01 00:00:00", "2026-10-01 00:00:00")),
    "C05": dict(period=("2026-06-01 00:00:00", "2026-06-02 00:00:00")),
    "C06": dict(period=("2025-01-01 00:00:00", "2026-01-01 00:00:00")),
    "C07": dict(period=("2026-05-31 00:00:00", "2026-06-01 00:00:00")),
    "C08": dict(ref="2026-09-24"),
    "C09": dict(ref="2026-09-26"),
    "C10": dict(at_order=True),
    "C11": dict(ref="2026-12-01"),
    "C12": dict(products=["a", "b", "c"]),
    "C13": dict(period=("2026-04-01 00:00:00", "2026-05-01 00:00:00"), products=["a", "c"]),
    "C14": dict(period=("2026-10-01 00:00:00", "2026-12-01 00:00:00"), products=["a", "b", "c"]),
    "C15": dict(period=("2026-03-01 00:00:00", "2026-06-01 00:00:00"), ref="2026-09-25"),
    "C16": dict(products=["a", "b", "c"], ref="2026-09-25"),
    "C17": dict(period=("2026-01-01 00:00:00", "2026-07-01 00:00:00"), products=["a", "b", "c"], ref="2026-09-25"),
    "C18": dict(period=("2026-05-01 00:00:00", "2026-06-01 00:00:00"), at_order=True),
    "C19": dict(period=("2026-09-01 00:00:00", "2026-10-01 00:00:00"), products=["d"], ref="2026-09-25"),
    "C20": dict(period=("2026-06-01 00:00:00", "2026-09-01 00:00:00")),
}


# ---------- SQL ----------

def build_sql(period=None, products=None, ref=None, at_order=False):
    sql = ("SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents "
           "FROM orders o JOIN product p ON p.product_id = o.product_id")
    if ref or at_order:
        sql += " JOIN customers c ON c.customer_id = o.customer_id"
    where = []
    if period:
        where.append(f"o.date >= '{period[0]}' AND o.date < '{period[1]}'")
    if products:
        where.append("o.product_id IN (" + ", ".join(f"'{x}'" for x in products) + ")")
    if ref:
        # completed age on the reference date: year diff - 1 if birthday not reached
        where.append(f"({int(ref[:4])} - CAST(substr(c.birth_date, 1, 4) AS INTEGER)"
                     f" - ('{ref[5:10]}' < substr(c.birth_date, 6, 5))) = 25")
    if at_order:
        # completed age on the date of the order line
        where.append("(CAST(substr(o.date, 1, 4) AS INTEGER) - CAST(substr(c.birth_date, 1, 4) AS INTEGER)"
                     " - (substr(o.date, 6, 5) < substr(c.birth_date, 6, 5))) = 25")
    if where:
        sql += " WHERE " + " AND ".join(where)
    return sql


# ---------- Independent check in pure Python, from the CSV files ----------

def read_csv(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def completed_age(birth, day):
    """birth 'YYYY-MM-DD', day 'YYYY-MM-DD...' -> completed age in years."""
    by, bm, bd = int(birth[0:4]), int(birth[5:7]), int(birth[8:10])
    ry, rm, rd = int(day[0:4]), int(day[5:7]), int(day[8:10])
    return ry - by - (1 if (rm, rd) < (bm, bd) else 0)


def python_revenue(orders, prices, births, period=None, products=None, ref=None, at_order=False):
    total = 0
    for o in orders:
        if period and not (period[0] <= o["date"] < period[1]):
            continue
        if products and o["product_id"] not in products:
            continue
        birth = births[o["customer_id"]]
        if ref and completed_age(birth, ref) != 25:
            continue
        if at_order and completed_age(birth, o["date"]) != 25:
            continue
        total += int(o["quantity_product"]) * prices[o["product_id"]]
    return total


def main():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    con.execute("PRAGMA query_only = 1")
    print("Products in the base:", con.execute(
        "SELECT product_id, price FROM product ORDER BY product_id").fetchall())
    leap = con.execute(
        "SELECT COUNT(*) FROM customers WHERE substr(birth_date, 6, 5) = '02-29'").fetchone()[0]
    print("Customers born on 29 February:", leap)

    prices = {r["product_id"]: int(r["price"]) for r in read_csv("product.csv")}
    births = {r["customer_id"]: r["birth_date"] for r in read_csv("customers.csv")}
    orders = read_csv("orders.csv")

    results = []
    print()
    print(f"{'case':<5} {'SQL':>12} {'Python/CSV':>12}  check")
    for case_id, params in CASES.items():
        sql = build_sql(**params)
        rows = con.execute(sql).fetchall()
        assert len(rows) == 1 and len(rows[0]) == 1, f"{case_id}: not 1 row x 1 column"
        s = rows[0][0]
        p = python_revenue(orders, prices, births, **params)
        print(f"{case_id:<5} {s:>12} {p:>12}  {'OK' if s == p else 'MISMATCH'}")
        results.append((case_id, sql, s))
    con.close()

    out = HERE / "references-all.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "sql", "revenue_cents"])
        w.writerows(results)
    print(f"\nWritten: {out.name}")


if __name__ == "__main__":
    main()
