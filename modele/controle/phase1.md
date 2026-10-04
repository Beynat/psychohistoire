# Liste de contrôle — phase 1 (démarrage au 1er novembre 2026)

La phase 1 ne démarre que si chaque point est coché, avec le commit correspondant (protocole, section 3).

## Scripts

- [x] `scripts/questions.py` : banque de questions, seuils aux quantiles de la marche aléatoire, grappes, pools (environ 57 questions et 35 grappes par cycle).
- [x] `scripts/geler.py` : gel des données, manifeste à empreintes SHA-256, gel jamais réécrit.
- [x] `scripts/registre.py` : ajout au registre, horodatage par l'horloge système, propositions et résolutions ; tests dans `scripts/tests.py`.
- [x] `scripts/notation.py` : Brier, logarithmique, Murphy, Brier pondéré dans le temps, test par grappes à permutation de signes.
- [x] `scripts/puissance.py` : puissance publiée dans `data/puissance.json` (environ 61 à 79 % à 40 grappes pour un écart de Brier de 0,02 ; fausse alarme 9 à 10 %).
- [x] `scripts/comparateurs.py` : persistance, taux de base ramené à la fenêtre, 50 %.

## Données et questions

- [x] `modele/evenements.json` : 21 événements du balayage v1 dotés d'un critère, 23 questions, dont 20 résolubles ; 3 non émises faute de source accessible (ACLED). Généré par `scripts/evenements.py` (4 octobre 2026).
- [x] Historique long des séries mensuelles et trimestrielles (taux 10 ans FR et DE et écart depuis 1990, IPCH depuis 1997, dette, PIB, chômage) : `collecte/historique.py`, `data/historique/` (4 octobre 2026).
- [x] Collecte des cotes externes pour P1 : Polymarket (232 marchés France, volume, écart offre-demande, drapeau de fiabilité), `collecte/cotes.py`. Metaculus exige un jeton : inaccessible, limite consignée (4 octobre 2026).
- [x] Taux de base des 20 questions résolubles, deux classes de référence ou plus, fourchette et classe retenue : `modele/taux_base/`, fusion `scripts/taux_base.py` → `modele/taux_base.json` (4 octobre 2026). Bornés entre 2 et 98 % pour le score logarithmique. Plusieurs comptages reposent sur des sources partielles, signalées dans le champ « incertitude » : à revoir au premier bilan.
- [x] `scripts/resolution.py` : séries par script, événements par propositions d'agents concordantes, troisième avis, annulation.

## Ensemble direct

- [x] Consigne des cinq prévisionnistes rédigée et versionnée : `modele/consigne_ensemble.md` (v1.0).
- [x] Agrégation par médiane non extrémisée, scriptée : `scripts/ensemble.py` (au moins 5 prévisionnistes et 3 modèles, contrôle des réponses).

## Exécution

- [x] Procédure du cycle mensuel écrite : `modele/controle/cycle_mensuel.md`.
- [x] Procédure du tri écrite : `modele/controle/tri.md`, avec `scripts/tri.py` (4 octobre 2026).

- [ ] Tâches planifiées créées : tri (trois fois par semaine), cycle mensuel (section 12).
- [ ] Règle de rattrapage testée sur un passage manqué simulé.
- [x] Clé API Webstat en secret GitHub `WEBSTAT_KEY` ; OAT quotidienne (TEC 10, depuis 2010) collectée chaque nuit par `collecte/webstat.py` ; seuils de l'écart calés sur le niveau quotidien corrigé du décalage avec la série BCE (4 octobre 2026).
- [ ] Workflow de contrôle des registres actif : ajout seul, `--no-renames`, horodatage dans la fenêtre de poussée, décisions de tri en JSONL (section 12).
- [x] Tags `protocole-v*` et `annexe-phase3-v*` protégés contre la suppression et la mise à jour (ruleset actif depuis le 4 octobre 2026).
- [x] Branche `main` protégée contre la poussée forcée et la suppression (ruleset actif depuis le 4 octobre 2026).
- [x] Cycle à blanc sur la piste exploratoire, chaîne complète (4 octobre 2026) : `data/cycles/2026-10/ESSAI.md`. Quatre problèmes trouvés et corrigés ; un reste ouvert (série quotidienne de l'OAT).

## Prérequis de la phase 2 (1er décembre 2026)

- [x] Écart de taux OAT-Bund journalier collecté depuis 2010 : TEC 10 (Banque de France) moins Bund 10 ans (Bundesbank, courbe Svensson). Décalage moyen avec la série BCE : environ −9 pb sur 12 mois, corrigé à l'ancrage.
- [ ] Historique journalier 2010-2025 pour le rétro-test (section 7.1).
- [ ] Source des sondages de la présidentielle identifiée et collectée (agrégat public ou instituts), avec l'historique des présidentielles 2002 à 2022 pour l'erreur des sondages (section 7.1).
