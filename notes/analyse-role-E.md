# Analyse du rôle E : openrouter:dots-studio/dots-3-note-preview:free

Rôle tenu par Simon, avec son propre compte OpenRouter (distinct de celui utilisé pour le rôle C). Lot réel du 21/10/2026, entre 12h51 et 12h57 UTC environ.
Traces brutes : [traces/traces-E.csv](../traces/traces-E.csv) et [traces/state-E.jsonl](../traces/state-E.jsonl).

Commandes utilisées : un test sur deux questions, puis les dix-huit autres, avec les mêmes fichiers d'état (les cellules déjà faites sont sautées).

```
python skeleton-multi-llm-en.py --run --models openrouter:dots-studio/dots-3-note-preview:free --cases C01,C02 --state state-E.jsonl --out traces-E.csv
python skeleton-multi-llm-en.py --run --models openrouter:dots-studio/dots-3-note-preview:free --cases C03,C04,...,C20 --state state-E.jsonl --out traces-E.csv
```

Avant le lot réel, un essai `--demo` (modèles simulés, sans réseau) a été lancé sur C01 et C02. Ses lignes sont dans `traces-demo.*`, de nature `simulation`, et n'entrent dans aucun résultat.

## Résultat

- 20 cellules lancées, 20 réponses HTTP 200, une tentative par cellule, aucune reprise, aucune erreur 429.
- 13 correctes, 7 incorrectes (C02, C08, C11, C15, C16, C17, C18), aucun SQL invalide ni rejeté.
- `cost_native` vaut 0 (route `:free`, prix plafonné à zéro par le script) et `tokens_reasoning` vaut 0 (raisonnement désactivé).
- Latence de 2,1 à 5,0 secondes environ.
- Par famille : période 6/6, produits 4/4, âge seul 2/5 (C09 et C10 justes), questions combinées 1/5 (seule C19 est juste). Les sept échecs portent tous sur l'âge.

## Les sept échecs, lus dans les traces

Les sept cellules ont un statut HTTP 200 et un SQL exécuté : ce sont des réponses fausses, pas des échecs d'accès.

**Cause principale, la « demi-fenêtre » d'âge (C02, C15, C16, C17, C18).** Avoir exactement 25 ans au 2026-09-25, c'est soit être né en 2001 avec l'anniversaire passé, soit être né en 2000 avec l'anniversaire pas encore arrivé. Le SQL exige `différence d'années = 25` et `anniversaire passé` : il ne garde que le premier cas et oublie les clients nés en 2000 après le 25 septembre. Les valeurs sont donc toutes trop basses.
- C02 : 321 340 au lieu de 590 320 (le filtre est en plus écrit deux fois, de façon redondante).
- C15 : 138 920 au lieu de 168 680 ; filtre de période correct.
- C16 : 211 260 au lieu de 376 740 ; filtre produits correct.
- C17 : 152 730 au lieu de 258 180 ; filtres période et produits corrects.
- C18 (âge au moment de la commande) : 39 580 au lieu de 62 480 ; même erreur, calculée sur `o.date`. C10, de la même famille mais sans période, est juste : le modèle n'est pas constant.

**C08 (âge au 2026-09-24) : 445 160 au lieu de 605 580.** Le modèle prévoit bien les deux cas, mais la première branche contient à la fois `<=` et `>=` sur le mois-jour : elle ne garde que les clients nés exactement un 24 septembre. La seconde branche (différence 26, anniversaire pas encore arrivé) est juste.

**C11 (âge au 2026-12-01) : 0 au lieu de 446 690.** Question mal lue : le SQL filtre `birth_date = '2001-12-01'` et des commandes passées le 2026-12-01. La date de référence est prise pour une date de commande ; aucune commande n'existe après septembre 2026, d'où 0.

## Observations et hypothèses

Observé : sur ce lot, Dots ne se trompe jamais sur la période ni sur les produits, et rate 7 questions d'âge sur 10. Hypothèse, à vérifier sur d'autres exécutions : la convention d'âge révolu (comparer le mois-jour, et non la seule différence d'années) est le point faible de ce modèle. Une seule exécution à température 0 ne mesure pas sa variabilité.

Documentation du modèle : absent du portefeuille du 28/09/2026. Sa page OpenRouter (lue le 21/10/2026) n'affiche aucun indice public ni route payante du même modèle, un seul fournisseur (AtlasCloud), et annonce le retrait du modèle le 31/12/2026. Indice et prix sont donc N/A dans `five-model-summary-en.csv`.

Aide d'une IA (Claude) : déclarée pour l'écriture des scripts d'`outils/` et la lecture des SQL en échec ; les explications ont été relues et vérifiées sur les traces.
