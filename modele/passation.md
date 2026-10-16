# Passation — état du projet au 16 octobre 2026

Document de reprise pour une nouvelle session. Le dépôt fait foi ; ce fichier ne remplace ni `modele/protocole.md` ni `modele/journal.md`. **Feuille de route en cours : `modele/feuille_de_route.md`** (14 étapes, avancement en tête du fichier).

## Objet

Prévisions datées et notées sur la France, d'octobre 2026 à septembre 2028. Dépôt public `Beynat/psychohistoire`, interface `reseau.html` (frise actuelle, à remplacer par l'organigramme), piste exploratoire `index.html`. Le long terme et le modèle Monde sont d'autres modèles, hors v0.

## Comment travailler avec Nathan

- Français, clair, direct, synthétique, sans emoji, peu de mise en forme. Le challenger quand une faille est réelle.
- **Progression suivie dans la conversation** : tenir la liste des tâches (une par étape de la feuille de route) et indiquer en tête de chaque message d'avancement « Avancement : n / 14 ». Mettre à jour `modele/feuille_de_route.md` (tableau et journal d'avancement) à chaque étape terminée, commit et push.
- Pas d'échéances ni d'estimations de durée dans les plans (Nathan les juge biaisées) : un ordre d'exécution et un avancement suffisent.
- Autonomie : Nathan a délégué les décisions de la feuille de route ; ne revenir vers lui que pour une action irréversible sur les données, un arbitrage de structure ou une question qui change le résultat. Il valide les maquettes avant mise en ligne.
- Il repère vite les incohérences en lisant les sorties : lui montrer des sorties lisibles (décomposition « d'où vient ce chiffre ») plutôt que des agrégats.
- Organigramme : lisibilité avant tout ; pas de texte superflu sur la page (légende courte, pas de versions ni de pieds de carte) ; les explications vont dans le détail au clic.

## Règles en vigueur

- Protocole en retrait jusqu'à la v0 ajustée ; restent impératifs : registres en ajout seul, horodatage par script, contrôle à la poussée, tests avant chaque commit, contrôle par mutation pour chaque correction de code.
- **Corrections au fil de l'eau tant que la feuille de route n'est pas terminée** (décision de Nathan : pas de file de tickets ni de quarantaine, trop d'erreurs à corriger) ; chaque correction est journalisée avec sa cause. Ensuite, règle des trois cas (erreur irréversible sur les données, cycle bloqué, effet de plus de 5 points ou issue indéterminable).
- Évaluateurs : toujours indépendants, sans accès aux registres (`registre/*`), aux cycles (`data/cycles/*`) ni, pour une élicitation, aux tables existantes. Ensemble : trois Opus et deux Sonnet ; évaluateurs de tables : Opus et Sonnet.
- Une correction se déclenche sur un défaut identifié, pas sur un chiffre qui surprend ; ne jamais remplacer un avis élicité par une appréciation personnelle (leçon du 10 octobre : la correction × 0,4 de la candidature Le Pen a dû être annulée).

## État au 16 octobre 2026

- **Statut** : `definitif: false`, `v0: true`. Premier cycle noté le 1er novembre 2026 sur `registre/v0.jsonl` (gel 48 heures avant : aucune modification du réseau à partir du 30 octobre).
- **Feuille de route** : 13 étapes sur 14. Reste l'étape 8 : organigramme prêt, en attente de la validation de l'aperçu par Nathan (allégé le 16 octobre : risques rares en encart, flèches d'évolution sur 7 jours avec part « modèle » et part « faits », instantanés quotidiens dans `data/instantanes/`).
- **Réseau** : structure v0.10.1, tables v0.10 ; 23 pivots, 6 variables d'état. Réseau témoin gelé le 10 octobre (`modele/reseau/gele/`).
- **Nouveaux contrôles (revue du 16 octobre)** : rapport de dérive consigné pour chaque version (`scripts/derive.py`, `modele/reseau/derives.jsonl`, exigé par les tests ; nombres aléatoires communs) ; contrôles de vraisemblance (`scripts/controles.py` : persistance contre les séries, chemins des feuilles, issues fourre-tout), défauts non corrigés déclarés dans `derogations_controles` de la structure ; relecture de vraisemblance par un agent neuf à chaque passe.
- **En attente de Nathan** : validation de l'état « serré » de VE-SOND (proposé le 16 octobre ; le quasi-égalité RN – Mélenchon / RN – Philippe est jugée cohérente avec l'écart de 0,6 point en septembre) ; cinq points de structure de l'étape 11 (le point 5, hypothèse principale de VE-SOND, est réglé) ; causes prioritaires du pré-mortem du 11 octobre.
- **À faire après la proclamation de la primaire PS – Place publique (17 octobre)** : nœud du bénéficiaire du soutien écologiste, conditionnel à « soutien », relié au duel, élicité en deux rondes ; lève la dérogation « fourre-tout » de PV-ECOLO et porte l'effet de PV-GAUCHE.
- **Autres dérogations ouvertes** : VE-SOND depuis « centre » (levée par l'état « serré »), VE-ECART depuis « < 120 pb » (transition trop instable, à rééliciter sur la série BCE).
- **Écart principal** : EV-05 Le Pen, réseau 52,6 % contre 40,8 % pour la médiane des avis directs (pré-mortem du 11 octobre).
- **Cooke** : graines enregistrées le 1er de chaque mois ; lots actifs à partir de 12 graines résolues (`scripts/cooke.py`).
- **Scénarios de rupture et red team** : `modele/reseau/scenarios.json`, `scripts/scenarios.py`. Pré-mortems dans `modele/reseau/premortem/`.
- **Tests** : `python scripts/tests.py` (contrôle par mutation de chaque correction) et `python scripts/controle_banque.py`.

## Tâches planifiées

- Tri : `trig_01M5gsZGtbMwVYGUbaCRpELn`, lundi, mercredi et vendredi à 17 h 47.
- Cycle mensuel : `trig_01SJXN4Fmwjue8foVBeRXddV`, du 1er au 8 à 7 h 52.
- Résolution d'EV-10b : `trig_01KatJtQ4QF7JRzuh9WNcgaf`, le 17 octobre à 9 h 07.
- Routine hebdomadaire : `trig_01RYqZSkrEzpry2YkuKq4RFp`, lundi à 8 h 22.
- Passe bimensuelle du réseau : `trig_01PjDUhLo9E1voyVWbySUWgQ`, les 2 et 16 à 9 h 37 (red team, contrôles de vraisemblance, rapport de dérive et relecture par un agent neuf à chaque passe, réagrégation de Cooke le 16).
- Pré-mortem trimestriel : `trig_0156Pv5r7rZpjMMKkW8nZ5Rd`, le 5 de janvier, avril, juillet et octobre à 10 h 13.

Chacune ajoute une ligne au journal d'avancement de `modele/feuille_de_route.md` (redirigées le 10 octobre, étape 6).

## Contraintes à respecter

- Ne jamais demander ni afficher la clé Webstat (secret GitHub `WEBSTAT_KEY`).
- Aucune donnée d'essai dans `registre/protocole.jsonl` (verrou dans `registre.py`).
- Ne pas publier la caractérisation proposée des faits d'actualité ni d'éléments de vie privée (annexe, section 11.2).
- Journal des contrôles : branche `controles`, écrite par le seul workflow ; ne jamais y pousser.
- Sources : méthode de `modele/sources.md`. Une source n'est primaire que pour ses propres actes.

## Pour démarrer la nouvelle session

Lire ce fichier, `modele/feuille_de_route.md`, les rapports d'étape et le dernier pré-mortem ; vérifier les réponses de Nathan aux arbitrages en attente et à la maquette de l'organigramme (étape 8).
