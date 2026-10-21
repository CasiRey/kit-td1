# Prompts de Yohann (Claude Code)

Outil : Claude Code, application de bureau, modèle Claude Opus 5.5. Session du 21/10/2026.
Les demandes sont recopiées telles qu'elles ont été écrites, fautes de frappe comprises. Les messages purement organisationnels (création des comptes, questions sur le déroulé du TD) ne sont pas repris ; aucune clé n'a été transmise à l'IA.

## 1. Requêtes de référence C13 à C16

> ok on sest deja reparti les question moi je fais les questions 13 14 15 16

Produit : les quatre requêtes SQL de C13 à C16 et un script qui les exécute en lecture seule sur `data/boutique.sqlite`, puis recalcule les quatre montants en Python pur sur les CSV. Vérification : les deux calculs donnent les mêmes valeurs (107 740, 0, 168 680, 376 740), identiques à celles de Simon dans `reference-td1.csv`. Les requêtes appliquent les conventions du protocole (période `>=` / `<`, âge révolu au mois et au jour, `COALESCE` à 0) ; l'IA n'a fourni aucun montant, seulement des requêtes exécutées sur la base.

## 2. Script de contre-vérification des 20 références

> Oui, fais un script de contre-vérification sur les CSV pour les 20 questions, que je partage au groupe.

Produit : `outils/verif_references.py` et `outils/README-verif.md`. Vérification : testé sur 20 requêtes SQL écrites séparément (20/20 concordantes) et sur cinq erreurs volontaires (âge par simple différence d'années, requête invalide, requête absente, NULL au lieu de 0, valeur mal recopiée), toutes détectées. Le mode qui affichait les 20 valeurs sans fichier a été retiré, pour que le script vérifie des requêtes sans fournir les réponses.

## 3. Lecture des échecs des lots C et D

Les lots C et D ont été lancés par Yohann dans son terminal, avec ses clés ; l'IA n'a jamais eu les clés. Après chaque paquet, la capture de la sortie était envoyée, par exemple :

> je continue

Produit : `notes/analyse-role-C.md` et `notes/analyse-role-D.md`. Vérification : chaque cause a été confirmée en réexécutant le SQL ou la condition concernée sur la base (par exemple C17 de Qwen : 80 190 - 70 500 = 9 690, l'écart observé).

## 4. Dépôt GitHub du groupe

> casimir a fait un github pour quon depose tout et quon soit corda en temps reel. analyse le github dis moi si tarr a y acceder si il est adapter au td et tu le rempli de ce que jai fait si cest le cas

> C'est mon compte perso YohannBDY qui a l'accès. Pousse sous ce compte, avec son adresse noreply GitHub.

Produit : l'analyse du dépôt (public, aucune clé dans l'historique), le `.gitattributes` qui garde les traces octet pour octet, les commits des lots D et C. Vérification : les traces téléchargées depuis GitHub ont la même empreinte SHA-256 que les fichiers d'origine.

## 5. Reprise du rôle C

> bon lavinia arrive pas a faire son role C parce que ca marche pas sur son pc du coup je vais le faire a sa place

Produit : les commandes du lot C, la note dans le suivi d'équipe et `notes/analyse-role-C.md`.

## 6. Fusion, synthèses, rangement, README et rapport

> en gros comme avec lavinia bas ca marchait pas dcp cest sim qui la fait pour lui. fais la suite complet bien propre et ordonne les dossier pour que tout soit bien rangé

Produit : le rangement du dépôt (`kit-docs/`, `traces/`, `notes/`, `outils/`, `resultats/`, `reports/`, `prompts-ia/`), `outils/merge_traces.py`, `outils/export_prompts.py`, l'extension de `outils/make_comparison.py` et `outils/pivot.py` (scripts de Simon) aux cinq lots, `notes/analyse-role-B.md`, les lignes B, C et D de `five-model-summary-en.csv`, `prompts-en.md`, `README.md` et `reports/td1.md`.

Vérification : la fusion compare chaque ligne fusionnée à sa source ; `skeleton-multi-llm-en.py --rates` et `--replay` redonnent les mêmes scores (20, 17, 15, 13 et 12 sur 20) ; les 40 lignes de comparaison de Simon sont restées identiques ; l'empreinte du prompt recalculée pour C01 est celle des traces ; les prix des lignes B, C et D ont été relus le 21/10/2026 sur le catalogue OpenRouter et la documentation Groq.
