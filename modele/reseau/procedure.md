# Procédure du réseau v0 (feuille de route v0, blocs 4 et 9)

Le réseau bayésien dynamique v0 prévoit les questions de la banque rattachées dans `structure_v0.json` (champ « mesures »), y compris les questions conjointes. Il tourne à chaque cycle, après l'ensemble direct, et à chaque passe bimensuelle.

## À chaque cycle (étape 4 bis de `modele/controle/cycle_mensuel.md`)

1. Mettre à jour `observations.json` : pour chaque variable d'état, l'état observé du mois écoulé et du mois en cours s'il est connu (définitions dans `structure_v0.json`, séries dans `data/etat/`). Un pivot déjà tranché y est inscrit avec son issue et son mois.
2. `python3 scripts/reseau.py --controle` : écarts de plus de 10 points avec les probabilités directes des évaluateurs. Ils sont consignés au compte rendu ; ils ne bloquent pas l'émission.
3. `python3 scripts/reseau.py M --registre R` (R : registre du cycle), puis commit et poussée dans l'heure.

## Passe bimensuelle (le 1er et le 15 de chaque mois)

Règles (journal du 10 octobre 2026) : aucune passe ne consulte les prévisions de l'ensemble ni des comparateurs sur une question ouverte ; chaque passe est inscrite au journal, avec son motif, avant toute publication de scores ; seules les prévisions telles qu'émises sont notées, chacune avec la version des tables.

1. Observations à jour (étape 1 ci-dessus), statuts des jalons (`scripts/jalons.py etat`), registre fantôme (`scripts/jalons.py fantome R`).
2. Contrôle de cohérence, puis examen des écarts, des émergences du tri (`data/reprise.json`) et des questions résolues depuis la passe précédente.
3. Corrections retenues selon la règle des trois cas (journal du 10 octobre 2026) : structure (`structure_v0.json`), tables (nouvelle élicitation d'un nœud par trois évaluateurs, ou dérivation documentée dans le nœud), mesures. Chaque correction : ligne au journal, version des tables incrémentée.
4. Si les tables ou la structure ont changé, nouvelles prévisions du réseau pour les questions du dernier cycle (`python3 scripts/reseau.py M --registre R`), qui s'ajoutent aux précédentes sans les remplacer.

## Points ouverts pour la première passe

- EV-39 (journée à plus de 500 000 manifestants) : réseau 44 %, évaluateurs 55 % ; EV-52 proche de la borne haute : la loi de VE-MOBIL est à revoir (forte trop rare, modérée trop fréquente).
- EV-43 : réseau 48 %, évaluateurs 37 % ; table de mesure à revoir.
- Dissolution après le second tour : risque mensuel constant sur 17 mois, alors que la dissolution de début de mandat se concentre en mai-juin 2027 (évaluateur E3). Découper comme la censure.
- Popularité : aucune série mensuelle sourcée à l'élicitation (évaluateur E2) ; à brancher sur `data/etat/popularite.jsonl`.
