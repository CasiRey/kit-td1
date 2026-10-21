# Accès et préparation : Yohann

## Vérification d'accès

`python check_access.py` lancé une fois le 21/10/2026 à 16h10 (heure de Paris) : 4 vérifications locales OK et 5/5 modèles OK. Le fichier `ready-for-td1.txt` reste hors du dépôt (il est dans le `.gitignore` du kit) ; une copie est dans le Drive du groupe.

Appels de contrôle consommés : 3 Groq et 2 OpenRouter, comptés à part des 20 cellules du rôle D.

## Limites du compte Groq Free

Relevées dans la console Groq le 21/10/2026 vers 14h45, identiques pour `openai/gpt-oss-120b`, `openai/gpt-oss-20b` et `qwen/qwen3.8-27b` : 30 requêtes par minute, 1 000 par jour, 8 000 tokens par minute, 200 000 tokens par jour.

## Incident d'inscription Groq

Le 21/10/2026 : le lien de connexion envoyé par mail était déjà expiré, puis l'inscription a été refusée avec le code `signup_blocked` (ref `ad86787cbd1aa4d3a9229633bc1ceb8d`). La connexion a réussi plus tard sur un compte personnel. Hypothèse, non vérifiée : beaucoup d'inscriptions depuis le même réseau de l'école ce jour-là.

## Clé OpenRouter

Clé personnelle créée avec une limite de 1 $ et une expiration à 90 jours, sans achat de crédit. Les scripts du kit refusent aussi toute route payante (`provider.max_price` à zéro).
