# Liste de contrôle — phase 1 (démarrage au 1er novembre 2026)

La phase 1 ne démarre que si chaque point est coché, avec le commit correspondant (protocole, section 3).

## Scripts

- [ ] `scripts/questions.py` : génération mécanique de la banque de questions (section 8.1), seuils aux quantiles 20, 50 et 80 de la marche aléatoire, grappes (section 8.3).
- [ ] `scripts/geler.py` : gel des données à date, empreinte des fichiers, commit avant toute prévision (section 8.2).
- [ ] `scripts/registre.py` : ajout des prévisions au registre, au format de la section 0.
- [ ] `scripts/notation.py` : Brier, score logarithmique, décomposition de Murphy, Brier pondéré dans le temps, tests par grappes (section 8.5).
- [ ] `scripts/puissance.py` : simulation de puissance publiée avant le premier cycle (section 8.3).
- [ ] `scripts/comparateurs.py` : persistance, taux de base, 50 % (section 8.4).

## Ensemble direct

- [ ] Consigne des cinq prévisionnistes rédigée et versionnée.
- [ ] Agrégation par médiane non extrémisée, scriptée.

## Exécution

- [ ] Tâches planifiées créées : tri (trois fois par semaine), cycle mensuel (section 12).
- [ ] Règle de rattrapage testée sur un passage manqué simulé.
- [ ] Workflow de contrôle des registres actif.

## Prérequis de la phase 2 (1er décembre 2026)

- [ ] Écart de taux OAT-Bund journalier collecté (source primaire à identifier : Banque de France, Bundesbank).
- [ ] Historique journalier 2010-2025 pour le rétro-test (section 7.1).
