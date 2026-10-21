# Rapport du TD 1 : comparer cinq modèles sur les mêmes questions

DIA4, sous-groupe 4. Séance du 21/10/2026. Pack `2026-10-18-students-1`, sélection de modèles du 14/10/2026.
Toutes les valeurs ci-dessous viennent des fichiers du dépôt ; chaque affirmation renvoie à sa preuve.

## 1. Ce qui a été fait

| Étape | Résultat | Preuve |
|---|---|---|
| Références | 20 requêtes SQL et leurs valeurs, vérifiées de façon indépendante, validées par l'encadrant | [reference-td1.csv](../reference-td1.csv) |
| Lots réels | 5 modèles × 20 questions = 100 cellules, 101 tentatives, toutes de nature `real` | [traces-td1.csv](../traces-td1.csv), [traces/](../traces/) |
| Lecture des traces | Une cause écrite pour chacun des 23 échecs et pour la reprise | [model-question-comparison-en.csv](../model-question-comparison-en.csv), [notes/](../notes/) |
| Synthèses | Tableau croisé et résumé des cinq modèles | [resultats/pivot-td1.md](../resultats/pivot-td1.md), [five-model-summary-en.csv](../five-model-summary-en.csv) |

Aucune ligne rejouée ni simulée n'entre dans ces résultats. Simon a fait un essai `--demo` (modèles simulés) avant son lot ; ces lignes de nature `simulation` ne sont pas dans le dépôt. Le mode `--replay` n'a servi qu'à vérifier que nos 100 SQL redonnent les mêmes verdicts hors ligne.

## 2. Les références (R1)

Simon a écrit les 20 requêtes ; Casimir les a déposées dans le dépôt (commit `524371b`). Conventions appliquées, celles du protocole :

- période fermée à gauche, ouverte à droite : `date >= début AND date < fin` ;
- âge révolu au mois et au jour : avoir 25 ans le 2026-09-25, c'est être né entre le 2000-09-26 et le 2001-09-25 inclus. La base contient des clients placés exprès aux bornes (C001 né le 2001-09-25, C004 né le 2000-09-25) ;
- « au moment de la commande » : l'âge est calculé à la date de chaque ligne de commande (C10, C18) ;
- chiffre d'affaires `SUM(quantity_product * price)` en centimes HT, `COALESCE(..., 0)` quand rien ne correspond (C06 et C14 valent 0 : aucune commande en 2025, ni après le 20/09/2026).

Vérifications indépendantes :

1. `outils/refs_all.py` (Simon) reconstruit chaque requête et recalcule le montant en Python pur sur les CSV : 20/20 identiques.
2. `outils/verif_references.py` (Yohann) réexécute les requêtes du fichier et les compare à un troisième calcul, écrit séparément, sur les CSV : 20/20, 0 écart.
3. Yohann a écrit séparément les requêtes de C13 à C16 : mêmes valeurs que Simon.
4. L'encadrant a validé les 20 valeurs pendant la séance.

## 3. Les traces (R2)

- Une ligne par appel, écrite automatiquement par `skeleton-multi-llm-en.py`. Les 5 lots bruts sont dans `traces/` ; `outils/merge_traces.py` les fusionne sans les modifier et vérifie chaque ligne fusionnée contre sa source.
- **Empreinte commune** : chaque question a une seule empreinte `prompt_sha256`, identique sur les cinq modèles (20 empreintes pour 100 cellules). Le même prompt a donc été envoyé à tous ; un écart entre modèles vient du modèle, pas de la formulation. Le prompt est dans [prompts-en.md](../prompts-en.md) ; `outils/export_prompts.py` recalcule l'empreinte de C01 et retrouve celle des traces.
- **Une reprise** : C20 du lot B, HTTP 429 puis HTTP 200 (voir la section 4).
- **Mesure absente et mesure nulle** : chez Groq, `cost_native` est vide (Groq ne renvoie pas de coût) et `tokens_reasoning` est vide pour qwen3.8-27b (raisonnement désactivé, mesure non renvoyée). Chez OpenRouter, ces deux colonnes valent 0 : la mesure existe et elle est nulle. Sur la tentative en 429 du lot B, toutes les colonnes de tokens sont vides : aucune réponse, donc rien à mesurer.

## 4. Résultats et causes des échecs (R3)

| Modèle | Opérateur | Correctes | Période | Âge seul | Produits | Combinées |
|---|---|---|---|---|---|---|
| groq:openai/gpt-oss-120b | Simon, pour Basile | 20/20 | 6/6 | 5/5 | 4/4 | 5/5 |
| groq:openai/gpt-oss-20b | Casimir | 17/20 | 6/6 | 2/5 | 4/4 | 5/5 |
| groq:qwen/qwen3.8-27b | Yohann | 15/20 | 6/6 | 3/5 | 4/4 | 2/5 |
| openrouter:dots-studio/dots-3-note-preview:free | Simon | 13/20 | 6/6 | 2/5 | 4/4 | 1/5 |
| openrouter:cohere/north-mini-code:free | Yohann, pour Lavinia | 12/20 | 6/6 | 0/5 | 4/4 | 2/5 |

Familles : période C01, C04 à C07, C20 ; âge seul C02, C08 à C11 ; produits C03, C12 à C14 ; combinées C15 à C19.

**Observé.** Les 23 mauvaises réponses portent toutes sur l'âge ; aucune erreur sur la période ni sur les produits. Toutes ont un statut HTTP 200 : le modèle a répondu, l'échec se lit dans le SQL renvoyé.

**Un échec d'accès, distinct d'une mauvaise réponse.** C20 du lot B, première tentative : HTTP 429, « tokens per minute (TPM): Limit 8000, Used 7266, Requested 1145 ». Aucun SQL n'est revenu, le verdict est `not_executed`. Le programme a réessayé une fois quatre secondes plus tard : HTTP 200, valeur juste. À l'inverse, C10 du lot D est une mauvaise réponse : HTTP 200, mais le SQL appelle `COALESE`, une fonction qui n'existe pas.

**Types d'erreurs lus dans le SQL** (détail par cellule dans [notes/](../notes/)) :

- fenêtre de naissance fausse : gpt-oss-20b sélectionne des clients de 0 an (C02), de 0 à 24 ans (C09) ou de 20 à 24 ans (C11) au lieu de 25 ans ;
- demi-fenêtre : Dots ne garde que les clients nés l'année « différence = 25 » dont l'anniversaire est passé, et oublie ceux de l'année précédente (C02, C15 à C18) ;
- borne oubliée ou âge jamais comparé à 25 : Cohere garde tous les moins de 26 ans (C08, C15) ou calcule l'âge sans le filtrer (C10) ;
- bornes décalées d'un jour : Qwen exclut C001 et inclut C004 sur C17 ; l'écart 80 190 - 70 500 = 9 690 est exactement l'écart observé ;
- comparaison de textes incompatibles : Qwen compare « 2026 » à « 2026-09-25 » en texte sur C19, ce qui supprime la borne haute ;
- SQL invalide : `COALESE` (Qwen, C10), `CAST` sans type et `AS age` dans le `WHERE` (Cohere, C02 et C09).

**Un consensus faux, à reprendre au TD 2.** Sur C11, Cohere et Dots renvoient tous deux 0 au lieu de 446 690, pour deux raisons différentes (différence d'années inversée pour Cohere ; date de référence prise pour une date de commande chez Dots). Deux autres modèles ont juste et le cinquième renvoie 322 160 : aucune valeur n'a la majorité sur cinq.

## 5. Changements et décisions

- **Modèle remplacé dans le kit** : le gabarit `five-model-summary-en.csv` citait encore `inclusionai/ling-3.0-flash-sante:free`, retiré le 14/10/2026. La ligne a été remplacée par `cohere/north-mini-code:free`, le modèle réellement utilisé.
- **Deux lots lancés par un autre membre** : le rôle A (Basile) a été lancé par Simon et le rôle C (Lavinia) par Yohann, parce que le lot ne fonctionnait pas sur leur PC. Chaque fois avec le compte personnel de l'opérateur ; C et E sont restés sur deux comptes OpenRouter différents, comme le demande le protocole.
- **Rythme des appels** : pour rester sous la limite Groq de 8 000 tokens par minute, le lot D a été envoyé par paquets de quatre questions espacés d'environ 30 secondes, et le lot A avec `--pause 10`. Le lot B, envoyé d'un trait avec la pause par défaut de 3 secondes, a reçu la seule 429 de la séance. Le lot C (OpenRouter) a ensuite été envoyé par paquets de cinq ; aucune autre 429.
- **Prix** : l'indice public vient du portefeuille du cours (28/09/2026). La route payante retenue est le prix OpenRouter du même modèle, relu le 21/10/2026 sur le catalogue public ; le tarif payant de Groq est cité dans la colonne `limits`. Cohere et Dots n'ont aucune route payante documentée : N/A, avec la raison.
- **Rangement du dépôt** : le kit exécutable et les livrables sont à la racine ; les documents du kit sont dans `kit-docs/` sans modification.

## 6. Limites

- Une seule exécution de 20 questions à température 0 par modèle : ces chiffres décrivent ce lot, pas un taux d'erreur général ni un classement durable. Un modèle peut répondre autrement à la même question.
- Les 20 questions couvrent trois conventions (période, âge, produits) sur une seule base de 59 clients ; elles ne disent rien d'autres types de requêtes (jointures plus profondes, agrégats par groupe, dates avec fuseau).
- Les opérateurs ont utilisé des comptes et des rythmes différents ; la latence dépend du fournisseur, de l'heure et de la charge des routes gratuites, elle ne mesure pas le modèle seul.
- Le 20/20 de gpt-oss-120b sur ce lot n'est pas une garantie : il faut d'autres exécutions pour mesurer sa variabilité.

## 7. Contributions

| Membre | Contribution au TD 1 |
|---|---|
| Simon | Les 20 requêtes de référence et `outils/refs_all.py` ; lots E (Dots) et A (gpt-oss-120b, pour Basile) ; `notes/analyse-role-A.md` et `analyse-role-E.md` ; scripts de comparaison et de tableau croisé ; lignes A et E du résumé |
| Casimir | Création du dépôt GitHub et dépôt des références ; lot B (gpt-oss-20b) ; `outils/test-c05.py` |
| Yohann | Requêtes indépendantes de C13 à C16 et `outils/verif_references.py` ; Drive et feuilles de suivi du groupe ; lots D (Qwen) et C (Cohere, pour Lavinia) ; notes des lots B, C et D ; fusion des traces, extension de la comparaison aux cinq lots, lignes B, C et D du résumé, `prompts-en.md`, README et ce rapport (avec Claude Code ; prompts envoyés séparément à l'encadrant) |
| Lavinia | Rôle C attribué ; le lot n'a pas pu être lancé depuis son PC le 21/10/2026 (cause non documentée), il a été repris par Yohann |
| Basile | Rôle A attribué ; le lot n'a pas pu être lancé depuis son PC le 21/10/2026 (cause non documentée), il a été repris par Simon |
| Vianney | Absent le 21/10/2026 |
| Augustin | Absent le 21/10/2026 |

## 8. Suite et aide demandée

- Avant le TD 2 : vérifier que chaque membre peut lancer le programme sur son PC (Lavinia et Basile n'ont pas pu le 21/10), et envoyer à l'encadrant les prompts d'aide au code de chaque membre, comme il l'a demandé.
- TD 2 : écrire `vote_k_sur_n` dans `skeleton-multi-llm-en.py` et le tester sur nos traces (C11 servira d'exemple de consensus faux et d'abstention) ; rédiger une règle de routage par famille de questions, en citant les cellules de ce TD. Hypothèse de départ, à vérifier : période et produits peuvent aller à n'importe lequel des cinq modèles ; les questions d'âge demandent gpt-oss-120b ou un contrôle.
- Aide demandée : aucune pour l'instant.
