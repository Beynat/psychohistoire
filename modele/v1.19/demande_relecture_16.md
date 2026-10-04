Bonjour,

Je vous demande une **relecture de validation** du protocole Psychohistoire. Vous n'avez pas participé aux échanges de rédaction ; c'est voulu. Cette relecture est complète et compte pour le critère d'arrêt (noyau, section 12) : deux relectures de validation consécutives sans défaut bloquant ni important.

Dépôt : https://github.com/Beynat/psychohistoire, tags `protocole-v1.19` et `annexe-phase3-v1.7`.

À lire :
- `modele/protocole.md` (noyau) et `modele/annexe_phase3.md` (annexe) ;
- `modele/banque/criteres.json` (banque d'événements) et `modele/sources.md` ;
- `modele/consigne_ensemble.md` et les procédures de `modele/controle/` ;
- `scripts/` (résolution, notation, tri, gel, contrôle de la banque, puissance) et `.github/workflows/` ;
- `modele/journal.md` pour l'historique ; les relectures précédentes et leurs réponses sont dans `modele/v1.*/`. Ne vous y fiez pas : jugez le texte et le code tels qu'ils sont.

Je vous demande :
1. **Méthode.** Le protocole permet-il de conclure ce qu'il annonce ? Hypothèses, test de la section 8.6, puissance, calibration, règles de résolution, risques de fuite ou de biais.
2. **Fond.** La banque couvre-t-elle les sujets qui compteront d'ici septembre 2028, en France et à l'international ? Les critères sont-ils résolubles sans ambiguïté, sur des sources fiables ?
3. **Conformité du code au texte.** Vous pouvez exécuter `python scripts/tests.py` et `python scripts/controle_banque.py`, et faire vos propres essais sur une copie.
4. Classez chaque défaut en bloquant, important ou souhaitable, avec motif et, si possible, correction proposée. Indiquez ce que vous n'avez pas vérifié.

Merci.
