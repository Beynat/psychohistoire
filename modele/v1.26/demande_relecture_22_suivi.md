Bonjour,

Merci pour la relecture de validation 21. Je vous demande une **relecture de suivi** (noyau, section 12) : elle vérifie seulement les corrections et ne compte pas pour le critère d'arrêt.

Dépôt : https://github.com/Beynat/psychohistoire, tag `protocole-v1.26` (annexe inchangée, `annexe-phase3-v1.7`). Réponse point par point : `modele/v1.26/reponse_relecture_21.md`.

À vérifier :
1. **B1.** Format de l'erratum de prévision (`scripts/registre.py`), application et délai de sept jours dans `scripts/notation.py` (fonction `annulations`), sections 0, 8.8 (« Émission et poussée ») et 12, procédures `controle/cycle_mensuel.md` et `controle/tri.md`.
2. **I1.** Unicité de la prévision de cycle dans `notation.bilan`, appliquée avant les exclusions liées au fait ; signalement par le workflow `.github/workflows/controle-registres.yml` ; section 8.5.
3. **I2.** Critère d'EV-35 (`modele/banque/criteres.json`, banque v1.9).
4. **D1 (interne).** Rattrapage : `questions.py` (date de gel du manifeste), `comparateurs.py` et `ensemble.py` (pas de nouvelle exécution d'une étape faite), section 12 et `controle/cycle_mensuel.md`. Merci de juger aussi le classement proposé.
5. **Défauts introduits.** Les corrections créent-elles une sélection, un poids ou une durée qui dépend de l'issue, ou une prévision postérieure à ce qu'elle prétend précéder ? En particulier : le délai de l'erratum, et le fait qu'une ligne annulée compte comme première prévision du cycle.

Tests : `python scripts/tests.py` (17 tests) et `python scripts/controle_banque.py`.

Classez chaque défaut selon la grille de la section 12 et indiquez ce que vous n'avez pas vérifié. Merci.
