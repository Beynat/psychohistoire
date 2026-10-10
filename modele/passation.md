# Passation — état du projet au 10 octobre 2026 (15 h 30)

Document de reprise pour une nouvelle session. Le dépôt fait foi ; ce fichier ne remplace ni `modele/protocole.md` ni `modele/journal.md`. **Feuille de route en cours : `modele/feuille_de_route.md`** (14 étapes, avancement en tête du fichier).

## Objet

Prévisions datées et notées sur la France, d'octobre 2026 à septembre 2028. Dépôt public `Beynat/psychohistoire`, interface `reseau.html` (frise actuelle, à remplacer par l'organigramme), piste exploratoire `index.html`. Le long terme et le modèle Monde sont d'autres modèles, hors v0.

## Comment travailler avec Nathan

- Français, clair, direct, synthétique, sans emoji, peu de mise en forme. Le challenger quand une faille est réelle.
- **Progression suivie dans la conversation** : tenir la liste des tâches (une par étape de la feuille de route) et indiquer en tête de chaque message d'avancement « Avancement : n / 14 ». Mettre à jour `modele/feuille_de_route.md` (tableau et journal d'avancement) à chaque étape terminée, commit et push.
- Pas d'échéances ni d'estimations de durée dans les plans (Nathan les juge biaisées) : un ordre d'exécution et un avancement suffisent.
- Autonomie : Nathan a délégué les décisions de la feuille de route ; ne revenir vers lui que pour une action irréversible sur les données, un arbitrage de structure ou une question qui change le résultat. Il valide les maquettes avant mise en ligne.
- Il repère vite les incohérences en lisant les sorties : lui montrer des sorties lisibles (décomposition « d'où vient ce chiffre ») plutôt que des agrégats.

## Règles en vigueur

- Protocole en retrait jusqu'à la v0 ajustée ; restent impératifs : registres en ajout seul, horodatage par script, contrôle à la poussée, tests avant chaque commit, contrôle par mutation pour chaque correction de code.
- **Corrections au fil de l'eau tant que la feuille de route n'est pas terminée** (décision de Nathan : pas de file de tickets ni de quarantaine, trop d'erreurs à corriger) ; chaque correction est journalisée avec sa cause. Ensuite, règle des trois cas (erreur irréversible sur les données, cycle bloqué, effet de plus de 5 points ou issue indéterminable).
- Évaluateurs : toujours indépendants, sans accès aux registres (`registre/*`), aux cycles (`data/cycles/*`) ni, pour une élicitation, aux tables existantes. Ensemble : trois Opus et deux Sonnet ; évaluateurs de tables : Opus et Sonnet.
- Une correction se déclenche sur un défaut identifié, pas sur un chiffre qui surprend ; ne jamais remplacer un avis élicité par une appréciation personnelle (leçon du 10 octobre : la correction × 0,4 de la candidature Le Pen a dû être annulée).

## État au 10 octobre, 15 h 30

- **Statut** : `definitif: false`, `v0: true`, `premier_cycle_formel: null`. Premier cycle noté le 1er novembre 2026 sur `registre/v0.jsonl`.
- **Banque** v1.14 : 63 questions d'événement ; 33 rattachées au réseau, 30 hors réseau.
- **Réseau v0.4** (`modele/reseau/structure_v0.json`, `tables_v0.json`) : 20 pivots, 6 variables d'état. Changements du 10 octobre (journal) : dissolution après l'élection découpée (mai-juin 2027 / ensuite) ; chaîne présidentielle réélicitée sur dossier sourcé (`modele/reseau/dossiers/presidentielle_2026-10-10.md`, évaluateurs E4, E5, E6 dans `modele/reseau/elicitation_2026-10-10/`) : pourvoi au 12 mars, liste au 26 mars, duel conditionnel aux candidatures du centre, vainqueur selon Le Pen ou Bardella. Chiffres clés : candidature Le Pen 82 % (90 % sans arrêt au 12 mars, 47 % si rejet), majorité absolue 20 %.
- **Jalons** : vraisemblances par issue v2 (`modele/jalons/vraisemblances_v2.json`, évaluateurs J1, J2) ; 3 jalons équivalents à un état du réseau. Le registre fantôme lit encore la v1 (étape 2).
- **Revues méthodologiques** : `modele/reseau/revues/2026-10-10_revue_1.md` et `_2.md`. Bogues vérifiés et recommandations repris dans la feuille de route.
- **Organigramme** : maquette validée sur le fond par Nathan, non déployée ; sources dans `modele/interface/organigramme/` (voir son LISEZMOI). Remarques de Nathan déjà intégrées : événements et probabilités en titre, détail au clic, « d'où vient ce chiffre », jalons avec options avant et après. Dernier point soulevé : un fait qui tranche (Attal renonce) doit s'appliquer sans réduction et faire bouger tout le réseau (étape 2) ; mode « et si » demandé (étape 8).
- **Données régénérées chaque nuit** par le workflow de collecte : `data/interface_v1.json`, `data/carte_v0.json`.
- **Tests** : `python scripts/tests.py` (29 tests) et `python scripts/controle_banque.py`.

## Tâches planifiées

- Tri : `trig_01M5gsZGtbMwVYGUbaCRpELn`, lundi, mercredi et vendredi à 17 h 47.
- Cycle mensuel : `trig_01SJXN4Fmwjue8foVBeRXddV`, du 1er au 8 à 7 h 52.
- Résolution d'EV-10b : `trig_01KatJtQ4QF7JRzuh9WNcgaf`, le 17 octobre à 9 h 07.
- Routine hebdomadaire : `trig_01RYqZSkrEzpry2YkuKq4RFp`, lundi à 8 h 22.
- Passe bimensuelle du réseau : `trig_01PjDUhLo9E1voyVWbySUWgQ`, les 2 et 16 à 9 h 37 (alignée dans `procedure.md`, étape 6).

Chacune ajoute une ligne au journal d'avancement de `modele/feuille_de_route.md` (redirigées le 10 octobre, étape 6).

## Contraintes à respecter

- Ne jamais demander ni afficher la clé Webstat (secret GitHub `WEBSTAT_KEY`).
- Aucune donnée d'essai dans `registre/protocole.jsonl` (verrou dans `registre.py`).
- Ne pas publier la caractérisation proposée des faits d'actualité ni d'éléments de vie privée (annexe, section 11.2).
- Journal des contrôles : branche `controles`, écrite par le seul workflow ; ne jamais y pousser.
- Sources : méthode de `modele/sources.md`. Une source n'est primaire que pour ses propres actes.

## Pour démarrer la nouvelle session

Lire ce fichier, `modele/feuille_de_route.md`, les deux revues et les entrées du 10 octobre du journal ; recréer la liste des tâches (14 étapes) ; commencer par l'étape 1.
