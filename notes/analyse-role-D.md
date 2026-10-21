# Analyse du rôle D : groq:qwen/qwen3.8-27b

Opérateur : Yohann. Lot réel lancé le 21/10/2026 entre 14h26 et 14h33 UTC, avec le compte Groq Free de Yohann.
Traces brutes : [traces/traces-D.csv](../traces/traces-D.csv) et [traces/state-D.jsonl](../traces/state-D.jsonl).

Commande utilisée, en cinq paquets de quatre questions (C01-C04, C05-C08, C09-C12, C13-C16, C17-C20), espacés d'environ 30 secondes pour rester sous la limite Groq de 8 000 tokens par minute :

```
python skeleton-multi-llm-en.py --run --models groq:qwen/qwen3.8-27b --cases C01,C02,C03,C04 --state state-D.jsonl --out traces-D.csv
```

## Résultat

- 20 cellules lancées, 20 réponses HTTP 200, une tentative par cellule, aucune reprise.
- 15 correctes, 4 incorrectes (C09, C15, C17, C19), 1 SQL invalide (C10).
- 20 empreintes de prompt distinctes, une par question.
- Tokens : 12 598 en entrée, 2 733 en sortie. La colonne `tokens_reasoning` est vide : le raisonnement est désactivé (`reasoning_effort: none`) et Groq ne renvoie pas cette mesure. C'est une mesure absente, pas un zéro. `cost_native` est vide aussi : Groq ne renvoie pas de coût.
- Par famille : période 6/6, produits 4/4, âge 5/10. Les cinq échecs portent tous sur l'âge.

## Les cinq échecs, lus dans les traces

Les cinq cellules ont un statut HTTP 200 : l'accès a fonctionné, le modèle a répondu. Ce sont des réponses fausses, pas des échecs d'accès.

**C09 (âge au 2026-09-26) : 0 au lieu de 487 980.** Le SQL calcule l'âge à la date de chaque commande (`o.date`) au lieu de la date de référence, qui n'apparaît pas dans la requête. Il exige aussi en même temps « jour-mois de commande >= jour-mois de naissance » et « < jour-mois de naissance + 26 ans », qui ont le même jour-mois. Aucune ligne ne passe, la somme vide devient 0 par `COALESCE`.

**C10 (âge au moment de la commande) : `sql_invalid`, « no such function: COALESE ».** Faute de frappe sur `COALESCE`, SQLite refuse la requête. En corrigeant seulement la faute, la requête donne 119 410 au lieu de 558 980 : sa deuxième branche (différence d'années 24, anniversaire pas encore passé) correspond à 23 ans, il fallait une différence de 26.

**C15 (période + âge au 2026-09-25) : 0 au lieu de 168 680.** La période est bien filtrée. L'âge est réduit à une comparaison de jour-mois sans l'année : « MM-DD de naissance <= 09-25 » et « > 09-25 » en même temps. Condition impossible, résultat 0.

**C17 (produits + période + âge au 2026-09-25) : 248 490 au lieu de 258 180.** Le SQL prend les nés en 2001 avant le 25/09 et les nés en 2000 à partir du 25/09. Les deux bornes sont décalées d'un jour : C001 (né le 2001-09-25, 25 ans pile ce jour-là) est exclu à tort (80 190), et C004 (né le 2000-09-25, 26 ans) est inclus à tort (70 500). Écart : 80 190 - 70 500 = 9 690, exactement la différence observée.

**C19 (produit d + période + âge au 2026-09-25) : 83 580 au lieu de 1 990.** Le SQL compare une année seule (« 2026 ») à une date complète (« 2026-09-25 ») en texte. « 2026 » <= « 2026-09-25 » est vrai en ordre alphabétique, donc le filtre devient « au moins 24 ou 25 ans » sans borne haute. Il garde 56 clients sur 59 au lieu des 6 qui ont 25 ans.

Chaque chiffre ci-dessus a été vérifié en réexécutant le SQL concerné sur `data/boutique.sqlite`.

## Ce qu'on en retient pour le TD 2

Hypothèse à confirmer avec les autres modèles : sur ce lot, qwen3.8-27b suffit pour les questions de période et de produits, mais n'est pas fiable seul sur les questions d'âge. Trois de ses erreurs sur cinq sont des conditions de jour-mois contradictoires ou mal bornées. Vingt questions ne suffisent pas pour en tirer un taux général.
