import sqlite3

con = sqlite3.connect("data/boutique.sqlite")

requete = """
SELECT COALESCE(SUM(quantity_product * price), 0) AS revenue_cents
FROM orders
JOIN product ON orders.product_id = product.product_id
WHERE date >= '2026-06-01 00:00:00' AND date < '2026-06-02 00:00:00'

"""

for ligne in con.execute(requete):
    print(ligne)
    