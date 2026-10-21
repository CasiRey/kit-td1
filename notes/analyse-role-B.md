# Analyse du rôle B : groq:openai/gpt-oss-20b

Opérateur : Casimir (commit `19486c2`, « Traces batch B »). Lot réel du 21/10/2026, entre 14h47:05 et 14h48:18 UTC.
Traces brutes : [traces/traces-B.csv](../traces/traces-B.csv) et [traces/state-B.jsonl](../traces/state-B.jsonl).

Commande reconstituée d'après les traces (elle n'a pas été notée pendant la séance) : les 20 questions sont parties en une seule exécution, de C01 à C20 dans l'ordre, avec 3 à 4 secondes entre deux appels, soit la pause par défaut de 3 secondes plus la latence. C20 apparaît deux fois : la tentative en 429 puis la reprise.

```
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-20b --state state-B.jsonl --out traces-B.csv
```

Note rédigée par Yohann à partir des traces (aide IA déclarée ; prompts envoyés séparément à l'encadrant).

## Résultat

- 20 cellules, 21 tentatives : 20 réponses HTTP 200 et une erreur HTTP 429.
- 17 correctes, 3 incorrectes (C02, C09, C11), aucun SQL invalide. C20 est correcte à la deuxième tentative.
- 20 empreintes de prompt distinctes, une par question, identiques à celles des quatre autres modèles.
- Tokens : 12 814 en entrée, 4 948 en sortie. `tokens_reasoning` est renseigné (17 à quelques centaines selon la question) : gpt-oss-20b raisonne avec `reasoning_effort: low` et Groq renvoie cette mesure. `cost_native` est vide : Groq ne renvoie pas de coût.
- Par famille : période 6/6, produits 4/4, âge seul 2/5 (C08 et C10 justes), questions combinées 5/5.

## L'échec d'accès : C20, HTTP 429

Première tentative à 14:48:14 UTC : HTTP 429, « Rate limit reached for model `openai/gpt-oss-20b` ... on tokens per minute (TPM): Limit 8000, Used 7266, Requested 1145 ». Le lot a enchaîné 19 appels en environ une minute et a atteint la limite de 8 000 tokens par minute du compte Groq Free.

C'est un échec d'accès, pas une mauvaise réponse : le modèle n'a rien renvoyé, aucun SQL n'a été exécuté, le verdict est `not_executed` et les colonnes de tokens sont vides (mesure absente, pas zéro). Le programme a réessayé une fois, comme le protocole l'autorise pour une 429 : deuxième tentative à 14:48:18 UTC, HTTP 200, valeur juste. Les deux tentatives restent dans la trace ; la comparaison retient la dernière.

## Les trois mauvaises réponses

Les trois cellules ont un statut HTTP 200 et un SQL valide : le modèle a répondu, mais sa fenêtre de dates de naissance ne correspond pas à « 25 ans révolus ».

**C02 (âge au 2026-09-25) : 0 au lieu de 590 320.** `birth_date > '2025-09-25' AND birth_date <= '2026-09-25'` : la fenêtre ne recule que d'un an, elle sélectionne des clients de 0 an. Aucun client n'est né à cette période, d'où 0. La bonne fenêtre va du 2000-09-26 au 2001-09-25.

**C09 (âge au 2026-09-26) : 399 610 au lieu de 487 980.** `birth_date > '2001-09-26' AND birth_date <= '2026-09-26'` : il garde tous les clients de 0 à 24 ans. La bonne fenêtre va du 2000-09-27 au 2001-09-26.

**C11 (âge au 2026-12-01) : 322 160 au lieu de 446 690.** `birth_date > '2001-12-01' AND birth_date <= '2006-12-01'` : il garde les clients de 20 à 24 ans. La bonne fenêtre va du 2000-12-02 au 2001-12-01.

## Ce qu'on en retient pour le TD 2

Sur ce lot, gpt-oss-20b réussit la période, les produits et les cinq questions combinées, mais se trompe sur trois des cinq questions d'âge seul, toujours en se trompant de fenêtre de dates. La 429 montre aussi qu'un lot de 20 appels sans pause plus longue dépasse la limite de tokens par minute de Groq Free. Vingt questions et une seule exécution ne suffisent pas pour en tirer un taux général.
