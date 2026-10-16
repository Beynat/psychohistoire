# Passation — état du projet au 16 octobre 2026 (soir)

Document de reprise pour une nouvelle session. Le dépôt fait foi ; ce fichier ne remplace ni `modele/protocole.md` ni `modele/journal.md`. **Feuille de route en cours : `modele/feuille_de_route.md`** (14 étapes, avancement en tête du fichier).

## Objet

Prévisions datées et notées sur la France, d'octobre 2026 à septembre 2028. Dépôt public `Beynat/psychohistoire`, interface `reseau.html` (frise actuelle, à remplacer par l'organigramme), piste exploratoire `index.html`. Le long terme et le modèle Monde sont d'autres modèles, hors v0.

## Comment travailler avec Nathan

- Français, clair, direct, synthétique, sans emoji, peu de mise en forme. Le challenger quand une faille est réelle.
- **Progression suivie dans la conversation** : tenir la liste des tâches pour tout travail en plusieurs étapes (la feuille de route v0 ajustée est terminée). Mettre à jour `modele/feuille_de_route.md` (tableau et journal d'avancement) à chaque étape terminée, commit et push.
- Pas d'échéances ni d'estimations de durée dans les plans (Nathan les juge biaisées) : un ordre d'exécution et un avancement suffisent.
- Autonomie : Nathan a délégué les décisions de la feuille de route ; ne revenir vers lui que pour une action irréversible sur les données, un arbitrage de structure ou une question qui change le résultat. Il valide les maquettes avant mise en ligne.
- Il repère vite les incohérences en lisant les sorties : lui montrer des sorties lisibles (décomposition « d'où vient ce chiffre ») plutôt que des agrégats.
- Organigramme : lisibilité avant tout ; pas de texte superflu sur la page (légende courte, pas de versions ni de pieds de carte) ; les explications vont dans le détail au clic.

## Règles en vigueur

- Protocole en retrait jusqu'à la v0 ajustée ; restent impératifs : registres en ajout seul, horodatage par script, contrôle à la poussée, tests avant chaque commit, contrôle par mutation pour chaque correction de code.
- **Feuille de route terminée le 16 octobre 2026** : la règle des trois cas s'applique (erreur irréversible sur les données, cycle bloqué, effet de plus de 5 points ou issue indéterminable) ; chaque correction est journalisée avec sa cause et consignée dans le rapport de dérive.
- Évaluateurs : toujours indépendants, sans accès aux registres (`registre/*`), aux cycles (`data/cycles/*`) ni, pour une élicitation, aux tables existantes. Ensemble : trois Opus et deux Sonnet ; évaluateurs de tables : Opus et Sonnet.
- Une correction se déclenche sur un défaut identifié, pas sur un chiffre qui surprend ; ne jamais remplacer un avis élicité par une appréciation personnelle (leçon du 10 octobre : la correction × 0,4 de la candidature Le Pen a dû être annulée).

## État au 16 octobre 2026 (soir)

- **Statut** : `definitif: false`, `v0: true`. Premier cycle noté le 1er novembre 2026 sur `registre/v0.jsonl` (gel 48 heures avant : aucune modification du réseau à partir du 30 octobre).
- **Feuille de route terminée** (14 / 14). La règle des trois cas s'applique désormais aux corrections (erreur irréversible sur les données, cycle bloqué, effet de plus de 5 points ou issue indéterminable) ; chaque correction reste journalisée avec sa cause et consignée dans le rapport de dérive.
- **Application** : https://beynat.github.io/psychohistoire/organigramme.html (raccourci sur le téléphone de Nathan), onglets Organigramme (liste par thème sur téléphone, graphe sur ordinateur, flèches d'évolution sur 7 jours, risques rares en encart) et Actualité (`data/actualite.jsonl`, alimenté par le tri trois fois par semaine). Le mode « et si » est retiré de l'interface. Intégrée à `reseau.html` à la place de la frise.
- **Réseau** : structure et tables v0.11 ; 24 pivots (nouveau : PV-SOUTIEN), 6 variables d'état (VE-SOND à quatre états, dont « serré »). Réseau témoin gelé le 10 octobre (`modele/reseau/gele/`). J-048 invalidé.
- **Contrôles** : rapport de dérive consigné pour chaque version (`scripts/derive.py`, `derives.jsonl`, exigé par les tests) ; contrôles de vraisemblance (`scripts/controles.py`), dérogations dans la structure (reste : VE-ECART depuis « < 120 pb ») ; relecture de vraisemblance à chaque passe.
- **Points ouverts** : `modele/reseau/procedure.md` (VE-ECART, poids des cas de VE-SOND) ; cinq points de structure de l'étape 11 (le 5 est réglé) ; causes du pré-mortem du 11 octobre ; écart EV-05 Le Pen (réseau 52,6 % contre 40,8 % d'avis directs).
- **Tâches planifiées** : règle d'accès web ajoutée (WebFetch seulement sur des adresses rendues par une recherche) pour éviter les demandes d'autorisation.
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
