# Liste de contrôle — phase 1 (démarrage au 1er novembre 2026)

La phase 1 ne démarre que si chaque point est coché, avec le commit correspondant (protocole, section 3).

## Scripts

- [ ] `scripts/questions.py` : génération mécanique de la banque de questions (section 8.1), seuils aux quantiles 20, 50 et 80 de la marche aléatoire, grappes (section 8.3).
- [ ] `scripts/geler.py` : gel des données à date, empreinte des fichiers, commit avant toute prévision (section 8.2).
- [x] `scripts/registre.py` : ajout des prévisions au registre, au format de la section 0, horodatage par l'horloge système (version initiale le 4 octobre 2026 ; à compléter par des tests).
- [ ] `scripts/notation.py` : Brier, score logarithmique, décomposition de Murphy, Brier pondéré dans le temps, tests par grappes (section 8.5).
- [ ] `scripts/puissance.py` : simulation de puissance publiée avant le premier cycle (section 8.3).
- [ ] `scripts/comparateurs.py` : persistance, taux de base, 50 % (section 8.4).

## Données et questions

- [x] `modele/evenements.json` : 21 événements du balayage v1 dotés d'un critère, 23 questions, dont 20 résolubles ; 3 non émises faute de source accessible (ACLED). Généré par `scripts/evenements.py` (4 octobre 2026).
- [x] Historique long des séries mensuelles et trimestrielles (taux 10 ans FR et DE et écart depuis 1990, IPCH depuis 1997, dette, PIB, chômage) : `collecte/historique.py`, `data/historique/` (4 octobre 2026).
- [x] Collecte des cotes externes pour P1 : Polymarket (232 marchés France, volume, écart offre-demande, drapeau de fiabilité), `collecte/cotes.py`. Metaculus exige un jeton : inaccessible, limite consignée (4 octobre 2026).
- [x] Taux de base des 20 questions résolubles, deux classes de référence ou plus, fourchette et classe retenue : `modele/taux_base/`, fusion `scripts/taux_base.py` → `modele/taux_base.json` (4 octobre 2026). Bornés entre 2 et 98 % pour le score logarithmique. Plusieurs comptages reposent sur des sources partielles, signalées dans le champ « incertitude » : à revoir au premier bilan.
- [ ] Script de résolution : séries par script, événements sur source primaire, double résolution des cas ambigus (section 8.8).

## Ensemble direct

- [ ] Consigne des cinq prévisionnistes rédigée et versionnée.
- [ ] Agrégation par médiane non extrémisée, scriptée.

## Exécution

- [ ] Tâches planifiées créées : tri (trois fois par semaine), cycle mensuel (section 12).
- [ ] Règle de rattrapage testée sur un passage manqué simulé.
- [ ] Workflow de contrôle des registres actif : ajout seul, `--no-renames`, horodatage dans la fenêtre de poussée, décisions de tri en JSONL (section 12).
- [x] Tags `protocole-v*` et `annexe-phase3-v*` protégés contre la suppression et la mise à jour (ruleset actif depuis le 4 octobre 2026).
- [x] Branche `main` protégée contre la poussée forcée et la suppression (ruleset actif depuis le 4 octobre 2026).
- [ ] Cycle à blanc mi-octobre sur la piste exploratoire, chaîne complète : gel, questions, prévisions, registre, notation.

## Prérequis de la phase 2 (1er décembre 2026)

- [ ] Écart de taux OAT-Bund journalier collecté. Aucune source gratuite sans clé trouvée pour l'OAT journalière (Webstat exige une clé, AFT bloque les scripts) ; le Bund journalier est disponible (Bundesbank). Piste : clé Webstat gratuite de la Banque de France.
- [ ] Historique journalier 2010-2025 pour le rétro-test (section 7.1).
- [ ] Source des sondages de la présidentielle identifiée et collectée (agrégat public ou instituts), avec l'historique des présidentielles 2002 à 2022 pour l'erreur des sondages (section 7.1).
