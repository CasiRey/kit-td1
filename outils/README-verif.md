# Vérifier les références du TD 1

`verif_references.py` contre-vérifie `reference-td1.csv`. Il n'utilise que la bibliothèque standard de Python : pas de `venv`, pas de clé, pas de réseau.

Pour chaque question, il compare trois valeurs :

1. la valeur notée dans la colonne `revenue_cents` ;
2. le résultat de la requête de la colonne `sql`, réexécutée en lecture seule sur `data/boutique.sqlite` ;
3. un calcul indépendant fait directement sur les CSV du kit, en Python pur, sans SQL. L'âge y est calculé en années révolues au mois et au jour près.

Il ne remplace pas la référence : la référence reste **votre requête SQL exécutée sur la base**. Il sert à repérer une erreur de convention ou une valeur mal recopiée.

## Lancer

Depuis la racine du dépôt (sous Windows, remplacez `python3` par `python`) :

```
python3 outils/verif_references.py . reference-td1.csv
```

Le premier argument est le dossier qui contient `data/`, ici la racine du dépôt.

Le fichier doit avoir au moins les colonnes `case_id`, `sql` et `revenue_cents`. Des colonnes en plus, comme `auteur` ou `verifie_par`, ne gênent pas. Le Sheet « Suivi references TD1 » exporté en CSV (Fichier > Télécharger > CSV) fonctionne directement.

## Lire le résultat

| Statut | Signification | Que faire |
|---|---|---|
| `OK` | Les trois valeurs sont égales | Rien |
| `A FAIRE` | Pas de requête dans le fichier | Écrire la requête |
| `SQL KO` | La requête ne s'exécute pas | Lire le message d'erreur SQLite |
| `ECART ... verifier la convention` | Le SQL et le calcul CSV divergent | Relire les conventions : période `>=` début et `<` fin, âge révolu au mois et au jour, âge à la date de référence ou au jour de la commande |
| `ECART ... NULL au lieu de 0` | Aucune ligne ne correspond et la requête renvoie NULL | Entourer la somme de `COALESCE(..., 0)` |
| `ECART ... valeur notee differente` | La valeur notée n'est pas celle que renvoie la requête | Recopier la valeur renvoyée par la requête |

Un `OK` partout ne garantit pas que le prof validera la valeur : c'est lui qui a le corrigé. Ça montre seulement que deux méthodes indépendantes sont d'accord.

## Déclaration

Script écrit avec une aide IA (Claude Code), relu et testé par le groupe. Testé sur 20 requêtes SQL écrites séparément (20/20 concordantes) et sur 5 erreurs volontaires : âge calculé par simple différence d'années, requête invalide, requête absente, NULL au lieu de 0, valeur mal recopiée. Les 5 ont été détectées.
