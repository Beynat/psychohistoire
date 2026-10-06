Bonjour,

Je vous demande une **relecture de validation** du protocole Psychohistoire. Vous n'avez pas participé aux échanges de rédaction ; c'est voulu. Cette relecture est complète et compte pour le critère d'arrêt (noyau, section 12) : deux relectures de validation consécutives sans défaut bloquant ni important.

Dépôt : https://github.com/Beynat/psychohistoire, tags `protocole-v1.27` et `annexe-phase3-v1.7`. Le journal des contrôles est sur la branche `controles`.

À lire :
- `modele/protocole.md` (noyau) et `modele/annexe_phase3.md` (annexe) ;
- `modele/banque/criteres.json` (banque d'événements) et `modele/sources.md` ;
- `modele/consigne_ensemble.md` et les procédures de `modele/controle/` ;
- `scripts/` (registre, contrôle des registres, résolution, notation, questions, gel, rattrapage, tri, contrôle de la banque, puissance) et `.github/workflows/` ;
- `modele/journal.md` pour l'historique. Les relectures précédentes et leurs réponses sont dans `modele/v1.*/`. Ne vous y fiez pas : jugez le texte et le code tels qu'ils sont.

Le modèle de menace du contrôle des registres est fixé à la section 12 (« Limites du contrôle ») : il vise les erreurs et les incidents ; une manœuvre délibérée de l'opérateur n'est pas empêchée mais doit laisser une trace publique.

Je vous demande :
1. **Méthode.** Le protocole permet-il de conclure ce qu'il annonce ? Hypothèses, test de la section 8.6, puissance, calibration, règles de résolution, risques de fuite ou de biais.
2. **Fond.** La banque couvre-t-elle les sujets qui compteront d'ici septembre 2028, en France et à l'international ? Les critères sont-ils résolubles sans ambiguïté, sur des sources fiables ?
3. **Conformité du code au texte.** Vous pouvez exécuter `python scripts/tests.py` et `python scripts/controle_banque.py`, et faire vos propres essais sur une copie (hors ligne : `JOURNAL_CONTROLES` désigne une copie du journal).
4. Classez chaque défaut selon la grille de la section 12 du noyau (« Classement des défauts »), avec motif et, si possible, correction proposée :
   - **bloquant** : atteinte à l'antériorité ou à l'intégrité des registres, ou cycle inexécutable ;
   - **important** : biais systématique, dans un sens déterminé, d'un verdict de la section 8.6, ou issue de question indéterminable ou contestable. Décrivez le scénario concret et le sens du biais ;
   - **souhaitable** : tout le reste (couverture, précisions de critères sans ambiguïté avérée, rédaction, robustesse sans biais démontré, procédure des phases ultérieures, biais dans le sens prudent).

   Indiquez ce que vous n'avez pas vérifié.

Merci.
