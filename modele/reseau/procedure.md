# Procédure du réseau v0 (feuille de route v0, blocs 4 et 9)

Le réseau bayésien dynamique v0 prévoit les questions de la banque rattachées dans `structure_v0.json` (champ « mesures »), y compris les questions conjointes. Il tourne à chaque cycle, après l'ensemble direct, et à chaque passe bimensuelle.

## À chaque cycle (étape 4 bis de `modele/controle/cycle_mensuel.md`)

1. Mettre à jour `observations.json` : pour chaque variable d'état, l'état observé du mois écoulé et du mois en cours s'il est connu (définitions dans `structure_v0.json`, séries dans `data/etat/`). Pour une variable « maximum du mois », l'observation du mois en cours n'est qu'un minimum (le moteur la traite ainsi). Un pivot déjà tranché y est inscrit avec son issue et son mois.
2. `python3 scripts/reseau.py --controle` : écarts de plus de 10 points avec les probabilités directes des évaluateurs. Ils sont consignés au compte rendu ; ils ne bloquent pas l'émission.
3. `python3 scripts/reseau.py M --registre R` (R : registre du cycle), puis, si `modele/reseau/gele/manifeste.json` existe, `python3 scripts/reseau.py M --registre R --gele` (auteur « réseau v0 gelé »), puis commit et poussée dans l'heure. Les questions rapides du cycle (pool PR, `scripts/rapides.py`) sont prévues dans le même passage.

**Gel de 48 heures (étape 6).** Aucune modification de `structure_v0.json`, `tables_v0.json` ou `calendrier.json` dans les 48 heures qui précèdent le gel d'un cycle : le moteur refuse alors d'émettre le réseau courant (le réseau gelé reste émis). Les observations et les preuves (jalons, faits) restent des données et peuvent entrer.

**Réseau témoin gelé (étape 6).** À la fin du bloc 1 de la feuille de route, `python3 scripts/reseau.py --geler` copie la structure, les tables et le calendrier dans `modele/reseau/gele/` avec leurs empreintes ; cette version n'est plus jamais modifiée et est notée comme un auteur à part. Le gain des passes se lit comme l'écart de score entre le réseau courant et le réseau gelé (`modele/reseau/comparaison.md`).

## Passe bimensuelle (le 2 et le 16 de chaque mois, tâche planifiée)

Règles (journal du 10 octobre 2026) : aucune passe ne consulte les prévisions de l'ensemble ni des comparateurs sur une question ouverte ; chaque passe est inscrite au journal, avec son motif, avant toute publication de scores ; seules les prévisions telles qu'émises sont notées, chacune avec la version des tables.

1. Observations à jour (étape 1 ci-dessus), statuts des jalons (`scripts/jalons.py etat`), registre fantôme (`scripts/jalons.py fantome R`).
2. Contrôle de cohérence, puis examen des écarts, des émergences du tri (`data/reprise.json`) et des questions résolues depuis la passe précédente.
3. Corrections retenues : une correction se déclenche sur un défaut identifié (bogue, contradiction avec un fait daté ou une règle de droit, contrôle automatique en échec), jamais sur un chiffre qui surprend ; l'effet en points sert à fixer la priorité. Tant que la feuille de route n'est pas terminée, corrections au fil de l'eau, chacune journalisée avec sa cause ; ensuite, règle des trois cas (journal du 10 octobre 2026). Formes : structure (`structure_v0.json`), tables (nouvelle élicitation d'un nœud par trois évaluateurs, ou dérivation documentée dans le nœud), mesures. Chaque correction : ligne au journal, version des tables incrémentée.
4. Si les tables ou la structure ont changé, nouvelles prévisions du réseau pour les questions du dernier cycle (`python3 scripts/reseau.py M --registre R`), qui s'ajoutent aux précédentes sans les remplacer.

## Points ouverts pour la première passe

- EV-39, EV-52 (loi de VE-MOBIL) et EV-43 (table de mesure) : réélicités à l'étape 11 (fait).
- Dissolution après le second tour : découpée (PV-DISSOL2a, PV-DISSOL2b) le 10 octobre ; profils de risque élicités sur des tranches de dates réelles à l'étape 10 (fait).
- Popularité : aucune série mensuelle sourcée à l'élicitation (évaluateur E2) ; à brancher sur `data/etat/popularite.jsonl`.
- Revues programmées des agences de notation : profil calé sur les revues (étape 3), poids d'un mois sans revue élicité à l'étape 10 (fait).
- Sondages : la moyenne corrigée de l'erreur historique (`scripts/etat.py`, `data/etat/erreur_sondages.json` : RN +0,9 point, centre −0,5, gauche +3,1, droite −1,0) placerait la gauche devant le centre en septembre 2026 (19,5 contre 16,5), alors que la moyenne publiée place le centre deuxième. VE-SOND suit la moyenne publiée ; décider si la correction, établie sur le dernier mois avant le scrutin, doit s'appliquer six mois avant.
