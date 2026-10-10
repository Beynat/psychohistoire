# Feuille de route : v0 ajustée (à partir du 10 octobre 2026)

Établie après deux revues méthodologiques indépendantes (`modele/reseau/revues/2026-10-10_revue_1.md` et `_2.md`), validée par Nathan. Elle remplace, pour la suite, la feuille de route v0 (document Claude Docs « Psychohistoire — feuille de route v0 », terminée).

**Avancement : 3 / 14 étapes (21 %).** Mis à jour à chaque étape terminée ; la progression est aussi donnée dans la conversation.

Décisions de Nathan :
- Toutes les étapes sont faites d'un seul tenant, dans l'ordre du tableau, y compris celles que les revues renvoyaient à plus tard. Aucune échéance de travail n'est fixée : les estimations de durée se sont révélées biaisées.
- Pas de file de tickets ni de quarantaine : il y a encore trop d'erreurs, elles se corrigent au fil de l'eau, chacune journalisée avec sa cause, tant que la feuille de route n'est pas terminée.
- La règle des trois cas s'applique ensuite.

## Bloc 1 : fiabiliser le modèle et l'interface

| # | Étape | Contenu | État |
|---|---|---|---|
| 1 | Bogues du moteur | Parent pas encore tranché traité comme son état de référence (règle : moyenne sous la loi a priori) ; multiplicateurs demandés sur la fenêtre mais appliqués au risque mensuel (conversion) ; article 12 en interdiction datée et non en multiplicateur ; extinction des faits imprévus (pas d'application jusqu'en 2028, pas de double compte) ; `--controle` étendu aux questions à plusieurs issues (EV-05 : Philippe 20 % contre 32 %) ; intervalle à 80 % sans bruit de simulation ; observation du mois en cours traitée comme un minimum ; agrégation sans droit de veto d'un zéro isolé. | fait |
| 2 | Moteur de preuve unique | Repondération des trajectoires par la vraisemblance des faits (jalons, faits imprévus, observations) : effet sur tout le réseau, vers l'aval et vers l'amont ; nombre effectif de trajectoires et alerte « combinaison trop rare ». Trois classes de faits : qui tranche (sans réduction, probabilité de retournement estimée), indice (réduction maintenue), allégation (sans effet). Classement des 50 jalons. Registre fantôme recalculé par ce moteur (vraisemblances v2, une issue par jalon). `faits.py` écrit des vraisemblances. | fait |
| 3 | Calendrier sourcé | `modele/reseau/calendrier.json` (budget, revues des agences dont Moody's le 23 octobre et S&P en novembre, parrainages le 12 mars, liste le 26 mars, tours de scrutin) ; dates de PV-BLOC et PV-GAUCHE alignées ; mois de revue des agences sur PV-NOTE ; test de calendrier. | fait |
| 4 | Élicitation contrôlée | Contrôles automatiques dans `tables.py` (référence minoritaire, sens opposés entre évaluateurs, justification vide, zéro isolé, marginale implicite) ; analyse de sensibilité (`scripts/sensibilite.py`) ; seconde ronde sur les nœuds en défaut, par ordre de sensibilité ; fin du calage du réseau sur l'avis direct des évaluateurs. | à faire |
| 5 | Hypothèses porteuses | `modele/reseau/hypotheses.json` : ce que la structure suppose sans le représenter (candidat RN = Le Pen ou Bardella, Philippe disponible, pas de vacance de la présidence…), probabilité de rupture tirée de précédents, signaux d'alerte reliés à la veille (`tri.py`) ; issue « autre candidat RN ». | à faire |
| 6 | Processus et notation | Version du réseau gelée à la fin du bloc 1, notée à part (« réseau v0 gelé ») ; gel 48 heures avant chaque cycle ; comparaison avec le témoin fixée d'avance ; pool de questions rapides (jalons, état des variables le mois suivant) pour valider plus tôt que 40 questions ; dates des passes alignées. | à faire |
| 7 | Tests automatiques | Batterie de tests avec contrôle par mutation, dont ceux qui auraient attrapé les erreurs du 10 octobre (base donnée pour la marginale, sens opposés, calendrier, parent non tranché, fait qui tranche). | à faire |
| 8 | Organigramme en ligne | Organigramme (maquette `modele/interface/organigramme/`) à la place de la frise de `reseau.html`, branché sur le moteur unique, avec le mode « et si » : cocher des faits et voir tout l'organigramme se recalculer. | à faire |

## Bloc 2 : étendre et consolider

| # | Étape | Contenu | État |
|---|---|---|---|
| 9 | Chocs imprévus | Points d'entrée déclarés dans la structure ; barème d'intensité par stade (allégation, procédure, mise en cause) calé sur des précédents sourcés (Fillon, Strauss-Kahn, Griveaux…) ; extinction par absorption dans les sondages ; nœuds rares (remplacement du candidat d'un bloc, fin anticipée du mandat). | à faire |
| 10 | Profils de risque | Probabilités cumulées à des dates réelles pour les pivots « à tout moment » sensibles (dissolution, censure, note, procédure, gouvernement) à la place du risque mensuel constant. | à faire |
| 11 | Réélicitation complète | Toutes les tables sur dossier sourcé, lois par cas, deux rondes (protocole IDEA), par ordre de sensibilité. | à faire |
| 12 | Pondération des évaluateurs | Mécanisme de Cooke sur les questions graines (jalons, états mensuels), activé dès que des résolutions existent. | à faire |
| 13 | Mouvements sociaux et ordre public | Sous-réseau branché sur la mobilisation et la popularité ; la mobilisation lycéenne agit sur des pivots ; rattachement des questions hors réseau qui ont un parent (EV-48, EV-49, EV-03, EV-44, EV-23, EV-11, EV-12, EV-14b). | à faire |
| 14 | Red team et pré-mortem | Red team de scénarios hors hypothèses à chaque passe ; pré-mortem périodique par un agent neuf, programmés. | à faire |

## Journal d'avancement

| Date | Étape | Fait |
|---|---|---|
| 10 oct. 2026 | – | Feuille de route établie et validée. |
| 10 oct. 2026 | 1 | Bogues du moteur corrigés (huit), structure et tables v0.5 ; effets dans `modele/reseau/rapports/2026-10-10_etape1.md`. |
| 10 oct. 2026 | 2 | Moteur de preuve unique, trois classes, 9 jalons qui tranchent sur 50, registre fantôme par le moteur ; `modele/reseau/rapports/2026-10-10_etape2.md`. |
| 10 oct. 2026 | 3 | Calendrier sourcé (24 entrées), PV-BLOC et PV-GAUCHE au 26 mars, profil des revues d'agences sur PV-NOTE ; `modele/reseau/rapports/2026-10-10_etape3.md`. |
