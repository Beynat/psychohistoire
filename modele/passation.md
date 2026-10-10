# Passation — état du projet au 10 octobre 2026 (fin de journée)

Document de reprise pour une nouvelle session. Le dépôt fait foi ; ce fichier ne remplace ni `modele/protocole.md` ni `modele/journal.md`. Feuille de route et avancement : document Claude Docs « Psychohistoire — feuille de route v0 » (https://claude.ai/code/artifact/635d3393-6acd-43fd-9c3d-52bcac6a0666), tenu à jour à chaque étape.

## Objet

Prévisions datées et notées sur la France, d'octobre 2026 à septembre 2028. Dépôt public `Beynat/psychohistoire`, interface `reseau.html` (carte des pivots, témoin et réseau, actualité, échéances) à côté de la piste exploratoire `index.html`. Le long terme (psychohistoire proprement dite) et le modèle Monde sont d'autres modèles, hors v0.

## Règles en vigueur (journal du 10 octobre 2026)

- **Protocole en retrait jusqu'à la v0 ajustée.** Restent impératifs : registres en ajout seul, horodatage par script, contrôle à la poussée, tests avant chaque commit, contrôle par mutation pour chaque correction de code.
- **Règle de correction des trois cas.** On ne corrige tout de suite qu'une erreur irréversible sur les données, une erreur qui empêche un cycle de tourner, ou une erreur qui change une probabilité ou un score de plus de 5 points ou rend une issue indéterminable. Le reste va à la liste de la v0 ajustée (feuille de route). Pas de tour de vérification par principe.
- **Amélioration continue du réseau.** Passes bimensuelles ; aucune passe ne consulte les prévisions de l'ensemble ou des comparateurs sur une question ouverte ; chaque passe est journalisée avant toute publication de scores ; seules les prévisions telles qu'émises sont notées (chaque ligne porte la version des tables).
- **Autonomie.** Nathan a délégué toutes les décisions de la feuille de route et autorisé les tâches planifiées listées ci-dessous ; il suit l'avancement dans le document de la feuille de route. On ne revient vers lui que pour une action irréversible sur les données.
- **Modèles.** Ensemble : trois Opus et deux Sonnet (Haiku et Fable écartés). Deux modèles au lieu de trois : écart assumé pendant la v0.

## État

- **Statut** (`modele/statut.json`) : `definitif: false`, `v0: true`, `premier_cycle_formel: null`. Les cycles mensuels tournent dès le 1er novembre 2026 sur `registre/v0.jsonl` (annonces et propositions suffixées `_v0`). `scripts/registre.py` refuse toute écriture dans `registre/protocole.jsonl` tant que le protocole n'est pas définitif. La banque n'est figée qu'à partir de `premier_cycle_formel`.
- **Banque** v1.14 : 63 questions d'événement (49 événements) ; questions sur le mouvement lycéen (EV-10, 10b, 47), la loi « casseurs-payeurs » (EV-48), le ministre de l'Éducation nationale (EV-49), le Premier ministre (EV-50), les interpellations (EV-51), la mobilisation agricole (EV-14b), la mobilisation à 30 jours (EV-52, horizon intermédiaire par ses questions mensuelles). Quatre questions conjointes (pool P2c) dans `modele/banque/conjointes.json`.
- **Témoin** : consigne v1.6 (au moins cinq pages lues, motifs propres à chaque question, contrôlés par `scripts/verifier_reponse.py`).
- **Réseau v0** : `modele/reseau/structure_v0.json` (v0.2 : 19 pivots, 6 variables d'état mensuelles, 33 questions rattachées dont 4 conjointes), `tables_v0.json` (trois évaluateurs, agrégation `scripts/tables.py`), `observations.json`, moteur `scripts/reseau.py`, procédure `modele/reseau/procedure.md` (avec ses points ouverts). Faits imprévus : `scripts/faits.py` (seuil d'application), appliqués par le moteur depuis `modele/reseau/faits.jsonl`.
- **Jalons** : 50 jalons sur 16 liens (`modele/jalons/definitions.jsonl`), statuts et registre fantôme par `scripts/jalons.py`, critère de direction par `scripts/direction.py`. Sans effet sur les probabilités tant que la direction n'est pas validée (40 questions résolues).
- **Séries d'état** : `data/etat/` (popularité Ifop, sondages, journées de mobilisation) ; `scripts/etat.py` en tire les états mensuels.
- **Tri** : faits sans question suivis sous un identifiant stable, émergence à 50 titres en sept jours (`data/reprise.json`).
- **Cycle d'essai 2026-10-v0** (`registre/essai_v0.jsonl`) : comparateurs, ensemble (5 prévisionnistes) et réseau. EV-10b se résout le 17 octobre.
- **Tests** : `python scripts/tests.py` (28 tests) et `python scripts/controle_banque.py`.

## Tâches planifiées

- Tri : `trig_01M5gsZGtbMwVYGUbaCRpELn`, lundi, mercredi et vendredi à 17 h 47.
- Cycle mensuel : `trig_01SJXN4Fmwjue8foVBeRXddV`, du 1er au 8 à 7 h 52 (registre v0, réseau après l'ensemble).
- Résolution d'EV-10b : `trig_01KatJtQ4QF7JRzuh9WNcgaf`, le 17 octobre à 9 h 07.
- Routine hebdomadaire (jalons, séries, émergences) : `trig_01RYqZSkrEzpry2YkuKq4RFp`, lundi à 8 h 22.
- Passe bimensuelle du réseau : `trig_01PjDUhLo9E1voyVWbySUWgQ`, les 2 et 16 à 9 h 37.

Chacune ajoute une ligne au tableau « Avancement » de la feuille de route.

## Reste à faire pour la v0

- Indicateurs structurels IS-02 à IS-05 (en cours au 10 octobre) et leur branchement comme contexte des pivots.
- Correction historique de la moyenne des sondages (`scripts/etat.py`, CORRECTION).
- Points ouverts de `modele/reseau/procedure.md` (EV-39 et EV-43, dissolution de début de mandat, revues programmées des agences).
- Liste de la v0 ajustée (feuille de route).

## Contraintes à respecter

- Ne jamais demander ni afficher la clé Webstat (secret GitHub `WEBSTAT_KEY`).
- Aucune donnée d'essai dans `registre/protocole.jsonl` (verrou dans `registre.py`).
- Ne pas publier la caractérisation proposée des faits d'actualité ni d'éléments de vie privée (annexe, section 11.2).
- Journal des contrôles : branche `controles`, écrite par le seul workflow ; ne jamais y pousser.
- Sources : méthode de `modele/sources.md`. Une source n'est primaire que pour ses propres actes.

## Préférences de Nathan

Français, style clair, direct et synthétique, sans emoji, peu de mise en forme. Le challenger quand une faille est réelle, pas par principe. Avancer sans bloquer sur des sujets de second ordre.
