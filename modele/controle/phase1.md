# Liste de contrôle — phase 1 (démarrage au 1er novembre 2026)

La phase 1 ne démarre que si chaque point est coché, avec le commit correspondant (protocole, section 3).

## Scripts

- [ ] `scripts/questions.py` : génération mécanique de la banque de questions (section 8.1), seuils aux quantiles 20, 50 et 80 de la marche aléatoire, grappes (section 8.3).
- [ ] `scripts/geler.py` : gel des données à date, empreinte des fichiers, commit avant toute prévision (section 8.2).
- [ ] `scripts/registre.py` : ajout des prévisions au registre, au format de la section 0.
- [ ] `scripts/notation.py` : Brier, score logarithmique, décomposition de Murphy, Brier pondéré dans le temps, tests par grappes (section 8.5).
- [ ] `scripts/puissance.py` : simulation de puissance publiée avant le premier cycle (section 8.3).
- [ ] `scripts/comparateurs.py` : persistance, taux de base, 50 % (section 8.4).

## Données et questions

- [ ] `modele/evenements.json` : événements et décisions de la phase 1, tirés du balayage v1, avec leurs critères de résolution (section 8.8).
- [ ] Historique long des séries (au moins 2010-2025) pour les quantiles de la marche aléatoire (section 8.1) ; la collecte ne garde que 24 mois.
- [ ] Collecte des cotes externes pour P1 : Polymarket et Metaculus, avec volume et écart entre offre et demande (section 4.5).
- [ ] Taux de base des comparateurs, avec leurs deux classes de référence (sections 7.3 et 8.4).
- [ ] Script de résolution : séries par script, événements sur source primaire, double résolution des cas ambigus (section 8.8).

## Ensemble direct

- [ ] Consigne des cinq prévisionnistes rédigée et versionnée.
- [ ] Agrégation par médiane non extrémisée, scriptée.

## Exécution

- [ ] Tâches planifiées créées : tri (trois fois par semaine), cycle mensuel (section 12).
- [ ] Règle de rattrapage testée sur un passage manqué simulé.
- [ ] Workflow de contrôle des registres actif.
- [x] Branche `main` protégée contre la poussée forcée et la suppression (ruleset actif depuis le 4 octobre 2026).
- [ ] Cycle à blanc mi-octobre sur la piste exploratoire, chaîne complète : gel, questions, prévisions, registre, notation.

## Prérequis de la phase 2 (1er décembre 2026)

- [ ] Écart de taux OAT-Bund journalier collecté (source primaire à identifier : Banque de France, Bundesbank).
- [ ] Historique journalier 2010-2025 pour le rétro-test (section 7.1).
