"""Contre-vérification indépendante des 20 références du TD 1.

Calcule chaque question directement sur les CSV du kit (Python pur, sans SQL),
réexécute chaque requête SQL du reference-td1.csv en lecture seule sur
boutique.sqlite et compare les trois valeurs :
  - la valeur notée dans le fichier ;
  - la valeur renvoyée par la requête SQL ;
  - la valeur du calcul indépendant sur les CSV.

Ce script ne remplace pas la référence : la référence est la requête SQL
exécutée sur la base. Il sert à détecter une erreur de convention.

Usage :
  python verif_references.py <chemin vers kit-td1> <reference-td1.csv>
"""
import csv
import sqlite3
import sys
from datetime import date
from pathlib import Path

ABC = {"a", "b", "c"}

# Paramètres de chaque question, recopiés de questions-td1-en.md :
#   period   = (début inclus, fin exclue) ou None
#   products = ensemble de produits ou None
#   age      = ("ref", date) : 25 ans révolus à cette date
#              ("order",)    : 25 ans révolus le jour de la commande
#              None          : pas de filtre d'âge
QUESTIONS = {
    "C01": dict(period=("2026-03-01 00:00:00", "2026-06-01 00:00:00")),
    "C02": dict(age=("ref", date(2026, 9, 25))),
    "C03": dict(products=ABC, period=("2026-01-01 00:00:00", "2026-07-01 00:00:00")),
    "C04": dict(period=("2026-01-01 00:00:00", "2026-10-01 00:00:00")),
    "C05": dict(period=("2026-06-01 00:00:00", "2026-06-02 00:00:00")),
    "C06": dict(period=("2025-01-01 00:00:00", "2026-01-01 00:00:00")),
    "C07": dict(period=("2026-05-31 00:00:00", "2026-06-01 00:00:00")),
    "C08": dict(age=("ref", date(2026, 9, 24))),
    "C09": dict(age=("ref", date(2026, 9, 26))),
    "C10": dict(age=("order",)),
    "C11": dict(age=("ref", date(2026, 12, 1))),
    "C12": dict(products=ABC),
    "C13": dict(products={"a", "c"}, period=("2026-04-01 00:00:00", "2026-05-01 00:00:00")),
    "C14": dict(products=ABC, period=("2026-10-01 00:00:00", "2026-12-01 00:00:00")),
    "C15": dict(period=("2026-03-01 00:00:00", "2026-06-01 00:00:00"), age=("ref", date(2026, 9, 25))),
    "C16": dict(products=ABC, age=("ref", date(2026, 9, 25))),
    "C17": dict(products=ABC, period=("2026-01-01 00:00:00", "2026-07-01 00:00:00"),
                age=("ref", date(2026, 9, 25))),
    "C18": dict(period=("2026-05-01 00:00:00", "2026-06-01 00:00:00"), age=("order",)),
    "C19": dict(products={"d"}, period=("2026-09-01 00:00:00", "2026-10-01 00:00:00"),
                age=("ref", date(2026, 9, 25))),
    "C20": dict(period=("2026-06-01 00:00:00", "2026-09-01 00:00:00")),
}


def age_on(birth: date, day: date) -> int:
    # années révolues : on retire 1 si l'anniversaire n'est pas encore passé ce jour-là
    return day.year - birth.year - ((day.month, day.day) < (birth.month, birth.day))


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compute_from_csv(kit: Path) -> dict[str, int]:
    price = {r["product_id"]: int(r["price"]) for r in read_csv(kit / "data" / "product.csv")}
    birth = {r["customer_id"]: date.fromisoformat(r["birth_date"])
             for r in read_csv(kit / "data" / "customers.csv")}
    lines = read_csv(kit / "data" / "orders.csv")

    def keep(line, period=None, products=None, age=None):
        if period and not (period[0] <= line["date"] < period[1]):
            return False
        if products and line["product_id"] not in products:
            return False
        if age:
            day = age[1] if age[0] == "ref" else date.fromisoformat(line["date"][:10])
            if age_on(birth[line["customer_id"]], day) != 25:
                return False
        return True

    return {cid: sum(int(l["quantity_product"]) * price[l["product_id"]] for l in lines if keep(l, **params))
            for cid, params in QUESTIONS.items()}


def run_sql(db: Path, sql: str):
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        con.execute("PRAGMA query_only = 1")
        rows = con.execute(sql).fetchall()
    finally:
        con.close()
    if len(rows) != 1 or len(rows[0]) != 1:
        raise ValueError(f"{len(rows)} ligne(s) au lieu d'une seule ligne d'une seule colonne")
    return rows[0][0]


def main():
    # Pas de mode « calcul seul » : le script vérifie des requêtes, il ne fournit pas les réponses.
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    kit = Path(sys.argv[1])
    expected = compute_from_csv(kit)

    # Les messages affichés sont sans accents : le terminal Windows les affiche mal.
    rows = {r["case_id"].strip(): r for r in read_csv(Path(sys.argv[2]))}
    problems = 0
    for cid, value in expected.items():
        row = rows.get(cid)
        if not row or not (row.get("sql") or "").strip():
            print(f"{cid}  A FAIRE    (pas de requete dans le fichier)")
            continue
        recorded = (row.get("revenue_cents") or "").strip()
        try:
            got = run_sql(kit / "data" / "boutique.sqlite", row["sql"])
        except Exception as e:  # requête invalide : on la signale sans s'arrêter
            print(f"{cid}  SQL KO     {e}")
            problems += 1
            continue
        notes = []
        if got is None:
            notes.append("la requete renvoie NULL au lieu de 0 (COALESCE manquant)")
        elif got != value:
            notes.append(f"SQL={got} mais calcul CSV={value} : verifier la convention")
        if recorded != str(got):
            notes.append(f"valeur notee={recorded or 'vide'} differente du resultat SQL={got}")
        if notes:
            problems += 1
            print(f"{cid}  ECART      " + " ; ".join(notes))
        else:
            print(f"{cid}  OK         {got}")
    print(f"\n{problems} ecart(s) sur {len(expected)} questions.")


if __name__ == "__main__":
    main()
