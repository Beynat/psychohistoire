# Registres

Fichiers en ajout seul : une ligne JSON par prévision émise. Une ligne n'est jamais modifiée ni supprimée ; une révision ajoute une ligne.

- `exploratoire.jsonl` : piste exploratoire (v0, v0.2 et ses mises à jour). Notée à part.
- `protocole.jsonl` : piste protocole, vide jusqu'au premier cycle (1er novembre 2026 au plus tôt).

Champs : `question`, `emise` (date et heure), `probabilites` (en %), `piste`, `origine` (estimation initiale, cycle mensuel ou mise à jour événementielle), `donnees` (état des données utilisé).
