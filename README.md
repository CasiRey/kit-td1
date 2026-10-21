# Next-Generation AI : TD du sous-groupe

ESILV, module Next-Generation AI (Trustworthy Generative AI), année 4, majeure Data & AI.
Dépôt partagé du sous-groupe du TD 1 (21/10/2026) au TD 3 (11/12/2026).

## Sous-groupe

- Numéro du sous-groupe et DIA : à compléter.
- Membres : Basile, Casimir, Lavinia, Simon, Yohann, Vianney, Augustin.
- Absents le 21/10/2026 : Vianney et Augustin.
- Qui a fait quoi : voir [reports/td1.md](reports/td1.md), section « Contributions ».

## Versions et environnement

| Élément | Valeur |
|---|---|
| Pack du cours | `2026-10-18-students-1` (18 octobre 2026) |
| Sélection de modèles | `modeles-autorises.json` daté du `2026-10-14` |
| Base | `data/boutique.sqlite`, seed `20260925`, SHA-256 `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2` |
| Python | 3.10 ou plus ; testé avec Python 3.13.13 sous Windows 11, `requests` 2.34.2, SQLite 3.50.4 |
| Comptes | Groq Free et OpenRouter (modèles `:free`), personnels, aucune carte ni crédit |

Aucune clé n'est dans ce dépôt. Les clés `GROQ_API_KEY` et `OPENROUTER_API_KEY` restent dans les variables d'environnement de chaque machine ; le `.gitignore` du kit exclut `.env`, `.venv/` et `ready-for-td1.txt`.

## Organisation du dépôt

| Emplacement | Contenu |
|---|---|
| racine | Le kit exécutable (`skeleton-multi-llm-en.py`, `sandbox_sqlite.py`, `check_access.py`, `verify-data.py`, `atelier-*.py`, `modeles-autorises.json`, `questions-td1.json`, `schema.sql`, `data/`) et les livrables du TD 1 |
| [`reference-td1.csv`](reference-td1.csv) | Les 20 requêtes de référence et leurs valeurs (R1) |
| [`traces-td1.csv`](traces-td1.csv), [`traces-td1.jsonl`](traces-td1.jsonl) | Les 5 lots fusionnés : 101 tentatives pour 100 cellules (R2) |
| [`model-question-comparison-en.csv`](model-question-comparison-en.csv) | Une ligne finale par modèle et question, avec la cause de chaque échec (R3) |
| [`five-model-summary-en.csv`](five-model-summary-en.csv) | Les 5 modèles : indice public, prix datés et sourcés, accès, résultats par famille |
| [`prompts-en.md`](prompts-en.md) | Le prompt système et le modèle de question, tels qu'envoyés |
| [`traces/`](traces/) | Les traces brutes de chaque opérateur (`traces-X.csv`, `state-X.jsonl`, X de A à E), jamais modifiées |
| [`notes/`](notes/) | L'analyse de chaque lot (`analyse-role-X.md`) et les notes d'accès |
| [`resultats/`](resultats/) | Le tableau croisé modèles × questions (une vue de la comparaison) |
| [`outils/`](outils/) | Les scripts du groupe (fusion, comparaison, tableau croisé, vérification des références) |
| [`reports/`](reports/) | Le rapport de chaque séance |
| [`prompts-ia/`](prompts-ia/) | Les demandes faites à une IA pour l'aide au code, telles qu'écrites |
| [`kit-docs/`](kit-docs/) | Les documents du kit (énoncés, protocole, guides, portefeuille, README d'origine), non modifiés |

## Rejouer le travail depuis un clone neuf

Sous Windows PowerShell, remplacez `python3` par `python` et activez le venv avec `.venv\Scripts\Activate.ps1`.

```bash
git clone https://github.com/CasiRey/kit-td1.git
cd kit-td1
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install requests
```

**1. Intégrité de la base et du kit (sans réseau)**

```bash
python3 verify-data.py
python3 check_access.py --no-network
```

**2. Références (R1).** Réexécute les 20 requêtes de `reference-td1.csv` et les compare à deux calculs indépendants : l'un en Python sur les CSV (`verif_references.py`), l'autre qui reconstruit chaque requête (`refs_all.py`).

```bash
python3 outils/verif_references.py . reference-td1.csv
python3 outils/refs_all.py
```

**3. Résultats des modèles, sans réseau ni clé.** `--rates` relit la trace fusionnée ; `--replay` réexécute les 100 SQL renvoyés par les modèles sur la base et doit redonner les mêmes verdicts (lignes de nature `replay`, à ne pas mélanger aux mesures réelles).

```bash
python3 skeleton-multi-llm-en.py --rates --state traces-td1.jsonl
python3 skeleton-multi-llm-en.py --replay traces-td1.jsonl --state traces-replay.jsonl --out traces-replay.csv
```

**4. Fusion et synthèses.** Recrée les livrables à partir des traces brutes de `traces/`.

```bash
python3 outils/merge_traces.py
python3 outils/make_comparison.py traces/traces-A.csv traces/traces-B.csv traces/traces-C.csv traces/traces-D.csv traces/traces-E.csv model-question-comparison-en.csv
python3 outils/pivot.py model-question-comparison-en.csv
python3 outils/export_prompts.py
```

**5. Relancer un lot réel (clés requises, consomme le quota).** Exemple du rôle D, en paquets de quatre questions pour rester sous la limite Groq de 8 000 tokens par minute. Un nouveau lot doit utiliser de nouveaux fichiers `--state` et `--out`.

```bash
export GROQ_API_KEY="..."
export OPENROUTER_API_KEY="..."
python3 check_access.py
python3 skeleton-multi-llm-en.py --run --models groq:qwen/qwen3.8-27b --cases C01,C02,C03,C04 --state state-D.jsonl --out traces-D.csv
```

## État du TD 1

Fait :

- 20 références calculées en SQL, vérifiées de façon indépendante et validées par l'encadrant ;
- 100 cellules réelles (5 modèles × 20 questions), 101 tentatives, une seule reprise (HTTP 429) ;
- comparaison des 100 cellules avec la cause de chaque échec, tableau croisé, résumé des 5 modèles.

| Modèle | Correctes | Période | Âge seul | Produits | Combinées |
|---|---|---|---|---|---|
| groq:openai/gpt-oss-120b | 20/20 | 6/6 | 5/5 | 4/4 | 5/5 |
| groq:openai/gpt-oss-20b | 17/20 | 6/6 | 2/5 | 4/4 | 5/5 |
| groq:qwen/qwen3.8-27b | 15/20 | 6/6 | 3/5 | 4/4 | 2/5 |
| openrouter:dots-studio/dots-3-note-preview:free | 13/20 | 6/6 | 2/5 | 4/4 | 1/5 |
| openrouter:cohere/north-mini-code:free | 12/20 | 6/6 | 0/5 | 4/4 | 2/5 |

Points ouverts : le numéro du sous-groupe, la cause précise des blocages de Lavinia et de Basile, les commandes exactes du lot B et les prompts d'aide au code de chaque membre (voir [prompts-ia/](prompts-ia/)).
