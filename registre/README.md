# Registres

Fichiers en ajout seul : une ligne JSON par prévision émise. Une ligne n'est jamais modifiée ni supprimée ; une révision ajoute une ligne.

- `exploratoire.jsonl` : piste exploratoire (v0, v0.2 et ses mises à jour). Notée à part.
- `protocole.jsonl` : piste protocole, vide jusqu'au premier cycle (1er novembre 2026 au plus tôt).
- `essai.jsonl` (et `resolutions_essai.jsonl`, `propositions_essai.jsonl` s'ils existent) : cycles d'essai (cycle à blanc et essai planifié du 4 octobre 2026). Ses lignes portent `piste: protocole` parce qu'elles ont été produites par les scripts du protocole, mais c'est le fichier qui fait foi : rien de ce registre n'est noté avec la piste protocole (relecture 8).

Champs (protocole, section 0) : `question`, `emise` (date et heure), `probabilites` (en %), `piste` (et `phase` pour la piste protocole), `origine` (estimation initiale, cycle mensuel, jalon ou fait imprévu, avec sa référence), `donnees` (commit ou état des données gelées). Une erreur se corrige par une ligne d'erratum (`erratum: true`), jamais par réécriture.

- `fantome.jsonl` : probabilités qu'auraient les nœuds si les jalons étaient actifs (section 10.6). Créé avec les premiers jalons.
- `controles.jsonl` : journal des contrôles, écrit par le workflow « Contrôle des registres » (relecture de suivi 22, N1). Une ligne par ligne de registre poussée hors de sa fenêtre (`fichier`, `question`, `auteur`, `emise`, `execution`, `detecte_le`). Toute prévision inscrite est annulée pour la notation.
