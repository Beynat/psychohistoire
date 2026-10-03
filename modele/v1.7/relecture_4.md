# Relecture 4 (protocole v1.6, tag protocole-v1.6)

Relecteur externe, reçue le 3 octobre 2026. Texte intégral, non modifié.

Je récupère la v1.6 au tag indiqué et je lis les pièces avant de rendre la relecture 4.

**Verdict.** La v1.6 ne contient plus de défaut bloquant : les jalons inactifs par défaut, le seuil d'application et le gel règlent le fond de la relecture 3. Il reste cinq défauts importants, dont un vient de ma propre proposition : le critère de direction que j'avais suggéré est mal centré. Les trois premiers se corrigent par un seul dispositif, un registre fantôme calculé par script.

J'ai lu les pièces au tag `protocole-v1.6` (commit `3a2225f`). Les chiffres viennent de simulations refaites pour cette relecture, sous hypothèses indiquées.

## 1. Suivi de la relecture 3

| Point | Jugement | Motif |
|---|---|---|
| D1 Formalisme des jalons | Suffisante | M racine, type « état aval », inactivité par défaut. Deux suites : E2 et E3. |
| D2 Décroissance, plafond | Suffisante | Le calcul continu est correct. Le facteur k reste indéfini (E2). |
| D3 Critères de maintien | Mal fondée | L'erreur est la mienne : le test de signe contre 50 % est mal centré (E1). |
| D4 Preuve virtuelle | Suffisante | |
| D5 Cas « paramètre », Bardella | Suffisante | La section 11.3 parle de « premier tour », la section 11.4 d'un tour unique : à aligner. |
| D6 Une seule famille | Suffisante en partie | La correction du biais crée une asymétrie (E5). |
| D7 Tri et veille | Suffisante | |
| D8 Moyens d'exécution | Suffisante dans le texte | Rien n'existe encore au dépôt (section 4). |
| D9, D10, D11 | Suffisantes | Le README du registre garde les anciens champs. |
| N1, N3, N7 | Suffisantes | |
| N6 Dossier figé | Suffisante en principe | Le choix des pages archivées reste un jugement fait après coup (souhaitables). |
| Phasage | Suffisante | Le calendrier et la puissance sont écrits en section 8.6. |

**Rejet (lecture par un humain formé aux probabilités).** Fondé : la contrainte est réelle, le risque est contenu par l'inactivité par défaut, et la limite est écrite en section 13. Le critère d'arrêt repose donc sur un relecteur de la même famille, ce que le texte assume.

## 2. Questions ouvertes

**Le seuil d'application rend-il la couche inerte ?** Non, c'est l'inverse : à trois évaluateurs il laisse passer du bruit. Simulation avec la dispersion observée sur MAJ-001 (écart-type de 0,3 en log), puis avec un consensus de famille (0,1) :

| Rapport vrai | 3 évaluateurs | 5 évaluateurs | 3 évaluateurs, consensus |
|---|---|---|---|
| 1,00 (aucun effet) | 18 % | 6 % | 19 % |
| 1,11 | 23 % | 10 % | 50 % |
| 1,5 | 66 % | 62 % | 100 % |
| 2 | 95 % | 95 % | 100 % |

- Un fait sans effet passe près d'une fois sur cinq, avec un rapport apparent de 1,28.
- Des évaluateurs corrélés qui s'accordent sur un rapport de 1,1 passent une fois sur deux.
- Correction : cinq évaluateurs par défaut, un plancher d'erreur type égal au plancher de dispersion (section 4.4), et une amplitude minimale, par exemple un rapport d'au moins 1,25 après réduction.

**La règle d'activation est-elle bien posée ?** Non, pour deux raisons (E2) :
- elle vérifie la probabilité marginale des jalons, alors que l'activation utilise leur rapport a/b ;
- elle active par absence de preuve : à 30 jalons, un jeu calibré passe à 74 %, un jeu deux fois trop confiant à 41 %.

**Le facteur k est-il transposable ?** Non. Le test 8.7 porte sur des probabilités directes, pas sur des rapports de vraisemblance, et le texte ne dit pas comment k en est tiré. Il s'estime directement sur le registre fantôme (E2).

## 3. Nouveaux défauts

Aucun bloquant.

### Importants

**E1. Le critère de direction est mal centré (10.11 et 11.7).**
- **Constat.** On compare à 50 % la part des mises à jour qui « rapprochent de l'issue réalisée ».
- **Problème.** Une hausse exacte de 36 à 40 % est comptée fausse six fois sur dix. À l'inverse, des baisses sans information sur des événements peu probables sont comptées justes 76 % du temps et passent le test dans 98 % des cas. Des mises à jour exactes ne le passent que dans 30 à 37 % des cas.
- **Correction.** Remplacer le test par la statistique Z = Σ d(y − p) / √(Σ d² p(1 − p)), où d est le déplacement, p la probabilité avant et y l'issue. Elle est centrée quel que soit p : 10 % de fausses alarmes dans tous les cas simulés, 51 à 55 % de puissance à 40 mises à jour. Garder le test de signe pour la variante « donnée arrivée ensuite ».

**E2. Porte d'activation et facteur k.**
- **Constat et problème.** Voir section 2 : la porte teste la mauvaise quantité, et k n'a pas de définition opérante.
- **Correction.**
  - Tenir un registre fantôme : le script calcule chaque semaine la probabilité qu'auraient les nœuds si les jalons étaient actifs. C'est déjà l'affichage « indicatif ».
  - Activer quand la statistique Z de E1 est significative sur ce registre.
  - Estimer k par régression logistique de l'issue sur le log-rapport proposé, avec la probabilité avant en décalage : le coefficient est k.
  - D'ici là, fixer k à 0,5 et le déclarer arbitraire.

**E3. Un jalon inactif fait taire un fait décisif.**
- **Constat.** La règle de priorité (10.5) interdit de traiter comme fait imprévu un fait prévu comme jalon. Les jalons sont inactifs par défaut, et les paramètres ne sont révisés qu'au trimestre.
- **Problème.** Si le PS dépose une motion de censure et que ce dépôt est un jalon, la probabilité de censure ne bouge pas. Un fait mineur imprévu, lui, peut la déplacer. Définir un jalon sur un précurseur important le neutralise.
- **Correction.** Tant que les jalons sont inactifs, un jalon observé ou manqué est renvoyé à la section 11 comme un fait ordinaire (panel, seuil, plafond). Ses vraisemblances gelées ne servent qu'au registre fantôme.

**E4. Banque d'événements de la phase 1 et règles de résolution absentes.**
- **Constat.** La section 8.1 prévoit des questions sur « événements et décisions », mais la sélection de la section 5 ne s'applique qu'au réseau de la phase 3. Aucune section ne dit qui résout une question, sur quelle source, ni que faire d'un cas ambigu.
- **Problème.** La phase 1 est la référence contre laquelle la phase 3 sera jugée. Sans liste ni règle, les agents improviseront les deux.
- **Correction.**
  - Fixer avant le 1er novembre un fichier d'événements tiré du balayage v1, dont les critères de résolution sont déjà écrits dans `fusion.md`.
  - Ajouter une section courte sur la résolution : par script pour les séries, par source primaire officielle pour les événements, avec deux agents en cas d'ambiguïté et l'annulation de la question si le désaccord persiste.

**E5. La correction du biais commun fausse le critère 8.6.**
- **Constat.** Si l'écart aux cotes est systématique, les estimations du modèle sur P2 sont corrigées (8.4). L'ensemble direct ne l'est pas.
- **Problème.** Les deux partagent le même biais. Corriger un seul côté donne au modèle un avantage qui vient des marchés, pas de la structure.
- **Correction.** Appliquer la même correction aux deux, ou juger le critère 8.6 sur les estimations non corrigées.

### Souhaitables

- **Seuil d'application.** Les trois corrections de la section 2.
- **Test 8.7.** Fixer une règle mécanique de choix des captures (texte de la question et liste fixe de pages à la date) et un nombre minimal de questions, par exemple 50.
- **Jalons.**
  - Les couples (a, b) ne couvrent pas un jalon précédent « en cours » ou « invalidé ».
  - Plus aucun jalon ne distingue l'intensité faible de la forte.
- **Contrôle des registres.**
  - Il ne couvre pas `data/tri.json`, que son en-tête annonce.
  - Il échouera sur tout changement de statut dans un fichier de jalons : mettre les statuts dans un journal séparé.
  - Il signale sans bloquer : une protection de branche sur `main` (contrôle requis, pas de poussée forcée) est un réglage à faire par Nathan.
- **Tri.** La liste `decides` de `tri.json` grossit sans limite : un fichier par mois suffirait.
- **Date du scrutin.** La section 5.2 écrit « 2 mai 2027 » alors que la section 5.1 la soumet au décret : écrire « second tour ».
- **Piste exploratoire.** Le fait EV-01 est passé en observation parce que la série primaire donne 82 pb en août. Les prévisions P-005 et PV-08, estimées sur un niveau de 120 pb non vérifié, méritent une note au registre.

## 4. Faisabilité de la phase 1

Oui, à condition de compléter la liste de contrôle. Les six scripts sont simples et quatre semaines suffisent, mais aucun n'existe encore (`scripts/` est absent). Il manque à la liste :
- le fichier d'événements et les règles de résolution (E4) ;
- l'historique long des séries, nécessaire aux quantiles de la marche aléatoire (la collecte ne garde que 24 mois) ;
- la collecte des cotes externes pour P1, avec volume et écart entre offre et demande (seule la présidentielle sur Polymarket est collectée) ;
- les taux de base des comparateurs, avec leurs deux classes de référence ;
- un cycle à blanc mi-octobre sur la piste exploratoire, pour tester la chaîne complète avant le premier cycle réel.

Compléter une liste de contrôle n'est pas une version du protocole. La section sur la résolution en est une.

## 5. Critère d'arrêt

Cette relecture n'est pas une relecture sans défaut : aucun bloquant, mais cinq importants (E1 à E5). Le compteur reste à zéro. Les corrections sont courtes, et aucune ne touche la phase 1 en dehors de E4.

## Ce qui est solide

1. L'inversion du défaut : jalons et faits imprévus ne peuvent plus dégrader les probabilités sans avoir passé un seuil.
2. Le gel du protocole et l'annulation de MAJ-001 par ajout d'une ligne, sans réécriture : la règle a été appliquée à sa première occasion.
3. Le calendrier et la puissance du verdict de la phase 3 sont écrits dans le protocole, y compris le retour probable par défaut à la phase 2.