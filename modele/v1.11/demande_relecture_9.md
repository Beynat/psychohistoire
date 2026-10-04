Bonjour,

Merci pour la relecture 8. Voici les corrections, pour une neuvième relecture, dans le même cadre : critique scientifique, exhaustive et sans complaisance. Le registre du protocole est toujours vide ; le premier cycle est prévu le 1er novembre 2026.

Dépôt : https://github.com/Beynat/psychohistoire, tag `protocole-v1.11` (noyau). L'annexe reste au tag `annexe-phase3-v1.1`.

Pièces à lire :
- `modele/v1.11/reponse_relecture_8.md` : réponse point par point ;
- `modele/protocole.md` : sections 0, 8.3, 8.4 et 8.8, et section 12 (exception au gel) ;
- `modele/banque/criteres.json` : tous les critères de la banque, réécrits ou nouveaux ;
- `modele/taux_base/groupe_*_r8.json` et `modele/taux_base.json` : taux de base ;
- `modele/sources.md` (v1.1), `modele/sources.json`, `scripts/sources.py` ;
- scripts modifiés : `evenements.py`, `questions.py`, `comparateurs.py` (référence externe), `registre.py`, `resolution.py`, `notation.py` (date du fait), `taux_base.py` ;
- `modele/controle/cycle_mensuel.md`, `modele/controle/tri.md`, `.github/workflows/controle-registres.yml`.

Je vous demande, dans l'ordre :
1. **Suivi de la relecture 8.** Pour chaque point (fond 1.1 à 1.3, méthode 2.1 à 2.3, G1 à G4, souhaitables, affirmations douteuses), dites si la correction est suffisante, insuffisante ou mal fondée, avec motif. Pour l'international, le maintien d'un indicateur par grand sujet en pool descriptif est une décision de Nathan : jugez son encadrement, pas son principe.
2. **Critères.** Relisez chaque critère de `criteres.json` au mot près : résoluble sans ambiguïté sur la source indiquée, dans la fenêtre, et compatible avec la règle de résolution de la section 8.8 ? Signalez tout critère dont l'issue serait déjà acquise au 1er novembre 2026.
3. **Taux de base.** Les classes retenues sont-elles défendables ? Le point ouvert sur EV-45 (effet de la suspension de la réforme de 2023 après le 1er janvier 2028) est-il correctement traité ?
4. **Nouveaux défauts,** classés en bloquants, importants et souhaitables, avec constat, problème et correction proposée. Vérifiez en particulier que l'exception au gel (section 8.8) ne crée pas d'incohérence avec la section 12, et que la date du fait est appliquée de bout en bout.
5. **Critère d'arrêt.** Indiquez si cette relecture est sans défaut bloquant ni important. Comme la version 1.11 modifie le noyau, le compteur repart de zéro.

Merci.
