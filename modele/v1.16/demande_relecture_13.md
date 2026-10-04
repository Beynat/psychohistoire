Bonjour,

Je vous demande une relecture critique, scientifique, exhaustive et sans complaisance du protocole d'un projet de prévision sur la France (octobre 2026 – septembre 2028). Merci de la conduire dans une session neuve, sans accès aux échanges de rédaction ; tout ce qu'il faut est dans le dépôt. Les relectures précédentes (1 à 12) et les réponses sont dans `modele/v1.*/` ; la plus récente est la relecture 12 (`modele/v1.16/relecture_12.md`).

Dépôt : https://github.com/Beynat/psychohistoire, tags `protocole-v1.16` (noyau) et `annexe-phase3-v1.5` (annexe). Le registre du protocole est vide ; aucun cycle n'aura lieu avant la première version définitive (noyau, section 12).

Pièces à lire :
- `modele/protocole.md` (noyau) et `modele/annexe_phase3.md` (annexe) ;
- `modele/v1.16/reponse_relecture_12.md` ;
- `modele/journal.md`, `modele/statut.json` ;
- `modele/banque/criteres.json`, `modele/taux_base.json`, `modele/sources.md` ;
- `scripts/` (notamment `notation.py`, `resolution.py`, `comparateurs.py`, `questions.py`, `dossier.py`, `puissance.py`, `controle_banque.py`, `tri.py`, `tests.py`) et `.github/workflows/` ;
- `modele/controle/` (procédures du cycle et du tri, listes de contrôle).

Je vous demande, dans l'ordre :
1. **Suivi de la relecture 12.** Pour chaque point (K1 à K6, S1 à S15), dites si la correction est suffisante, insuffisante ou mal fondée, avec motif.
2. **Relecture d'ensemble.** Signalez tout défaut du noyau, de l'annexe, de la banque ou des scripts, même ancien, classé en bloquants, importants et souhaitables, avec constat, problème et correction proposée. Exécutez `python scripts/tests.py` si vous le pouvez.
3. **Critère d'arrêt.** Indiquez explicitement si cette relecture est sans défaut bloquant ni important.

Merci.
