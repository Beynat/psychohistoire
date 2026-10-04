# Psychohistoire

Projet personnel, théorique et récréatif, inspiré de la psychohistoire d'Isaac Asimov : lire l'actualité à travers des indicateurs structurels et des précédents historiques, pour émettre des prévisions chiffrées, datées et vérifiables, produites par des agents IA.

- `index.html` : la page publiée sur GitHub Pages.
- `data.json` : indicateurs, moments pivots, prévisions et journal, mis à jour par les relevés et analyses. L'historique Git de ce fichier fait foi pour le registre des prévisions.
- `data/collecte.json` : données ouvertes collectées chaque nuit, sans IA, par `collecte/collect.py` (GitHub Actions).
- `data/veille.json` : titres d'actualité relevés chaque nuit par le même script, sans IA.
- `data/tri/` : décisions de tri de la veille, un fichier par mois, écrites par l'agent de tri.
- `registre/` : registres des prévisions, en ajout seul (piste exploratoire et piste protocole), écrits uniquement par `scripts/registre.py`.

Aucune de ces probabilités ne constitue un conseil.

## Méthode

Le protocole scientifique en vigueur est `modele/protocole.md` (le noyau, version taguée), complété par `modele/annexe_phase3.md` pour la phase 3, avec son journal (`modele/journal.md`) et les relectures externes (`modele/v1.2/`, `modele/v1.3/`, `modele/v1.4/`, `modele/v1.6/`, `modele/v1.7/`, `modele/v1.8/`, `modele/v1.10/`). Les probabilités affichées actuellement par la page relèvent de la **piste exploratoire** (v0, v0.2), produite avant le protocole et notée à part.
