# Analyse du rôle C : openrouter:cohere/north-mini-code:free

Rôle attribué à Lavinia. Le lot ne fonctionnait pas sur son PC le 21/10/2026 ; il a été lancé par Yohann, avec son propre compte OpenRouter (distinct de celui de Simon, rôle E). Lot réel du 21/10/2026, entre 15h14 et 15h20 UTC.
Traces brutes : [traces/traces-C.csv](../traces/traces-C.csv) et [traces/state-C.jsonl](../traces/state-C.jsonl).

Commande utilisée, en quatre paquets de cinq questions (C01-C05, C06-C10, C11-C15, C16-C20), espacés d'environ 30 secondes :

```
python skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --cases C01,C02,C03,C04,C05 --state state-C.jsonl --out traces-C.csv
```

## Résultat

- 20 cellules lancées, 20 réponses HTTP 200, une tentative par cellule, aucune reprise, aucune erreur 429.
- 12 correctes, 6 incorrectes (C08, C10, C11, C15, C16, C17), 2 SQL invalides (C02, C09).
- 20 empreintes de prompt distinctes, une par question.
- Tokens : 11 194 en entrée, 2 529 en sortie. `tokens_reasoning` vaut 0 et `cost_native` vaut 0 sur toutes les lignes : OpenRouter renvoie ces mesures, et elles sont nulles (raisonnement désactivé, modèle gratuit). À comparer avec Groq (rôle D), où ces colonnes sont vides parce que la mesure n'est pas renvoyée.
- Latence de 0,8 à 6,0 secondes, contre environ 0,3 à 1 seconde pour qwen3.8-27b sur Groq.
- Par famille : période 6/6, produits 4/4, questions avec un âge 2/10 (seules C18 et C19 sont justes). Les huit échecs portent tous sur l'âge.

## Les huit échecs, lus dans les traces

Les huit cellules ont un statut HTTP 200 : l'accès a fonctionné, le modèle a répondu. Ce sont des réponses fausses, pas des échecs d'accès.

**C02 (âge au 2026-09-25) : `sql_invalid`, « syntax error near ")" ».** `CAST(strftime('%Y', '2026-09-25'))` sans type cible : il manque `AS INTEGER`. La requête construit aussi un modificateur de date à la main avec des `CASE` imbriqués.

**C08 (âge au 2026-09-24) : 1 188 090 au lieu de 605 580.** Le filtre garde les clients nés après le 2000-09-24 et avant le 2026-09-24 : il manque la borne « né au plus tard le 2001-09-24 ». Le filtre retient tous les clients de moins de 26 ans (13 clients au lieu de 6). La somme sur ces 13 clients donne exactement 1 188 090.

**C09 (âge au 2026-09-26) : `sql_invalid`, « syntax error near "AS" ».** Un alias `AS age` est écrit au milieu de la clause `WHERE`, ce que SQLite refuse. La condition compare en plus l'année de naissance elle-même à 25, et un `OR` sans parenthèses casse le reste du filtre.

**C10 (âge au moment de la commande) : 907 310 au lieu de 558 980.** Le SQL calcule l'âge à la date de chaque commande, mais ne le compare jamais à 25 : il garde toutes les lignes dont l'anniversaire de l'année est passé, quel que soit l'âge. Cette somme fait exactement 907 310.

**C11 (âge au 2026-12-01) : 0 au lieu de 446 690.** La différence d'années est écrite à l'envers (année de naissance moins 2026, entre -68 et -20) et comparée à 0 ou 1. Aucune ligne ne passe. Le chiffre 25 n'apparaît pas dans la requête.

**C15 (période + âge au 2026-09-25) : 314 020 au lieu de 168 680.** Même erreur que C08 : la borne basse est oubliée, le filtre garde tous les moins de 26 ans. Sur la période, cela donne exactement 314 020.

**C16 (produits + âge au 2026-09-25) : 80 190 au lieu de 376 740.** Les conditions se contredisent jusqu'à ne laisser que `birth_date = '2001-09-25'` (`date('2026-09-25', '-25 years') <= birth_date <= date('2026-09-25', '-25 years')`). Un seul client passe, C001, dont les achats de a, b et c font 80 190.

**C17 (produits + période + âge au 2026-09-25) : 0 au lieu de 258 180.** Mauvaises positions de sous-chaîne : sur « 2001-09-25 », `substr(birth_date,6,2)||'-'||substr(birth_date,1,4)` donne « 09-2001 » et `substr(birth_date,7,4)` donne « 9-25 ». Le calcul d'âge n'a plus de sens, aucune ligne ne vaut 25.

Chaque chiffre ci-dessus a été vérifié en réexécutant la requête ou la condition concernée sur `data/boutique.sqlite`.

## Ce qu'on en retient pour le TD 2

Sur ce lot, cohere/north-mini-code:free suffit pour les questions de période et de produits (10/10), mais échoue sur 8 des 10 questions qui contiennent un âge. Ses erreurs sont variées : borne oubliée, âge jamais comparé à 25, positions de sous-chaîne fausses, syntaxe invalide. Hypothèse pour la règle de routage : ne pas lui confier une question d'âge sans contrôle. Vingt questions ne suffisent pas pour en tirer un taux général.
