# Analyse du rôle A : groq:openai/gpt-oss-120b

Rôle attribué à un autre membre du sous-groupe. Le lot ne fonctionnait pas sur son PC le 21/10/2026 ; il a été lancé par Simon (rôle E), avec son propre compte Groq, comme le protocole le permet (répartir les cellules entre les membres qui ont encore de la capacité). Lot réel du 21/10/2026, vers 14h48-14h52 UTC.
Traces brutes : [traces/traces-A.csv](../traces/traces-A.csv) et [traces/state-A.jsonl](../traces/state-A.jsonl).

## Capacité vérifiée avant le lancement

Limites lues dans la console Groq le 21/10/2026 à 16h46 (heure de Paris) pour `openai/gpt-oss-120b` : 30 requêtes par minute, 1 000 requêtes par jour, 8 000 jetons par minute, 200 000 jetons par jour. Déjà consommé : 3 requêtes (le `check_access.py` de Simon).

Avec la pause par défaut de 3 secondes (20 appels par minute, environ 800 à 1 000 jetons chacun), la limite de 8 000 jetons par minute risquait d'être dépassée. La pause a donc été portée à 10 secondes (`--pause 10`).

```
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --cases C01,C02 --state state-A.jsonl --out traces-A.csv --pause 10
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --cases C03,C04,...,C20 --state state-A.jsonl --out traces-A.csv --pause 10
```

## Résultat

- 20 cellules lancées, 20 réponses HTTP 200, une tentative par cellule, aucune reprise, aucune erreur 429.
- 20 correctes sur 20 : période 6/6, âge seul 5/5, produits 4/4, questions combinées 5/5.
- Latence de 0,6 à 2,7 secondes environ.

## Observations et hypothèses

Observé : gpt-oss-120b réussit les sept questions d'âge que Dots (rôle E) rate, dont C02, C08 et C11. Ce 20/20 vient d'une seule exécution de 20 questions à température 0 : c'est une observation sur ce lot, pas une garantie que le modèle ne se trompe jamais.

Documentation (portefeuille du 28/09/2026) : indice public 11,6 ; ce même modèle existe aussi sur OpenRouter en paiement au jeton à 0,15 / 0,60 USD HT par million de jetons (entrée / sortie, lu le 29/09/2026). La route utilisée ici est le plan gratuit de Groq.
