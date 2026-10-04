# Relecture 5 (protocole v1.7, tag protocole-v1.7)

Relecteur externe, reçue le 4 octobre 2026. Texte intégral, non modifié.

Je récupère la v1.7 au tag indiqué et je lis les pièces avant de rendre la relecture 5.

**Verdict.** La v1.7 corrige correctement les cinq défauts de la relecture 4, et le noyau des phases 1 et 2 est stable. Il reste deux défauts importants : l'unité de la statistique Z, que j'avais laissée indéfinie dans ma proposition, et l'intégrité des registres, où j'ai constaté des horodatages postérieurs à leur commit et un contrôle qui échoue sur un ajout légitime. Cette relecture n'est donc pas une relecture sans défaut.

J'ai lu les pièces au tag `protocole-v1.7` (commit `69adb8b`, puis `a159cc4`). J'ai exécuté le contrôle des registres sur une copie du dépôt et refait les simulations.

## 1. Suivi de la relecture 4

| Point | Jugement | Motif |
|---|---|---|
| E1 Critère de direction | Suffisante dans la forme | La formule est la bonne. Son unité de calcul manque (F1). |
| E2 Activation et facteur k | Suffisante | Le registre fantôme règle le fond. Reste F1, et deux précisions sur k (souhaitables). |
| E3 Jalon inactif | Suffisante | |
| E4 Événements et résolution | Suffisante | La section 8.8 couvre qui résout, sur quelle source, et l'annulation. |
| E5 Biais commun | Suffisante | |
| Souhaitables | Suffisantes | Sauf le contrôle des registres (F2). |
| Faisabilité | Suffisante | La liste de contrôle est complète. Deux lignes à ajouter (F2). |

**Adaptation sur la protection de branche : fondée, motif à corriger.** GitHub permet d'appliquer une protection aux administrateurs. La vraie raison est ailleurs : un contrôle obligatoire imposerait de passer par des demandes de fusion et bloquerait la poussée directe de la collecte nocturne et des agents. Le contrôle détectif est donc le bon choix. Protéger aussi les tags `protocole-v*` contre la suppression serait cohérent, puisqu'ils font foi.

## 2. Seuil d'application

Oui, il est bien réglé, à une ambiguïté près. Le texte donne à l'erreur type un plancher « égal au plancher de dispersion », alors que l'une est un écart-type divisé par √5 et l'autre un écart-type. Les deux lectures donnent des couches très différentes (simulation, plancher de 0,3 en log, k = 0,5) :

| Rapport vrai | Plancher appliqué à la dispersion | Plancher appliqué à l'erreur type |
|---|---|---|
| 1 (aucun effet) | 0 % | 0 % |
| 1,5 | 33 % | 7 % |
| 1,75 | 74 % | 37 % |
| 2 | 93 % | 74 % |

- La première lecture est la bonne : elle ne laisse plus passer de bruit sans rendre la couche inerte. La seconde l'éteint presque sous un rapport de 2.
- Avec k = 0,5, un rapport brut doit dépasser 1,56 pour passer, et le rapport appliqué reste entre 1,25 et 1,73. Autour de 36 %, cela déplace un nœud de 5 à 13 points.
- À écrire : le plancher porte sur la dispersion, il est exprimé en log-cotes, et le plafond s'applique avant la réduction par k.

## 3. Nouveaux défauts

Aucun bloquant.

### Importants

**F1. L'unité de la statistique Z n'est pas définie.**
- **Constat.** La section 10.6 compte « chaque changement hebdomadaire » comme une mise à jour, et active les jalons à 30 mises à jour résolues. Plusieurs mises à jour d'une même question partagent une seule issue.
- **Problème.**
  - Trente mises à jour peuvent reposer sur quatre ou cinq issues indépendantes.
  - Le calcul continu en cours de fenêtre produit des mises à jour de même signe, semaine après semaine. Dans ce cas, des jalons sans information sont activés dans 16 à 20 % des simulations, au lieu des 10 % annoncés.
  - Le même défaut touche la section 11.7, quand plusieurs faits portent sur un même nœud.
- **Correction.** Un terme par question résolue : d est le déplacement cumulé entre la probabilité sans jalons et la probabilité fantôme à la clôture. Le taux de fausse activation revient alors à 10 %. Exprimer les seuils en questions résolues, avec le même nombre pour l'activation et la désactivation (le texte dit 30 d'un côté, 40 de l'autre). L'activation en sera retardée, ce qui est le bon défaut.

**F2. L'intégrité des registres n'est pas assurée.**
- **Constat.**
  - Des lignes du registre exploratoire sont datées après le commit qui les contient : « 16 h 50 » dans le commit de 16 h 48, « 17 h 10 » dans celui de 16 h 57. Le champ `emise` est donc écrit à la main par l'agent.
  - Le contrôle d'ajout seul échoue sur un ajout légitime au fichier de tri : ajouter un élément à un tableau JSON modifie la ligne précédente (une virgule). Je l'ai vérifié sur une copie.
  - Un fichier renommé puis réécrit échappe au contrôle. Je l'ai vérifié aussi.
- **Problème.** L'antériorité des prévisions est le fondement de la validation. Un horodatage déclaratif ne prouve rien, et un contrôle rouge trois fois par semaine dès la phase 1 masquera une vraie violation.
- **Correction.**
  - L'horodatage est écrit par `scripts/registre.py` à partir de l'horloge système, jamais par un agent.
  - Le workflow vérifie que chaque nouvelle ligne est datée dans l'heure qui précède la poussée. La date de poussée fait foi, et une question résolue avant elle est annulée.
  - Les décisions de tri passent en JSONL, une décision par ligne.
  - Le contrôle tourne avec `--no-renames`.
  - Ajouter ces points à `modele/controle/phase1.md`.

### Souhaitables : cohérence interne

- **Calibration des jalons.** Quatre passages disent encore que les jalons s'activent « une fois leur calibration vérifiée » (sections 2, 10, 10.9 et 13), alors que la section 10.6 les active sur Z. Le pool P2d n'a donc plus de décision attachée : le dire.
- **Phasage.** La section 3 affirme que « chaque phase doit battre la précédente », mais seule la phase 4 est conditionnée à une victoire.
- **Pistes parallèles.** La section 10.11 dit qu'aucune piste parallèle n'est nécessaire, alors que le registre fantôme en est une.
- **Évaluateurs.** La section 6.1 en exige cinq, la section 10.7 en prévoit trois pour les jalons.
- **Comparateurs.** Pour un événement, la persistance vaut désormais le taux de base : deux comparateurs identiques.
- **Critère 11.7.** Deux statistiques (Z et test de signe) pour une seule décision, sans règle de combinaison.
- **Facteur k.** Préciser que la régression porte sur le log-rapport brut. L'estimer séparément pour les faits imprévus, dont tous les avis du panel sont déjà enregistrés, y compris sous le seuil.
- **Plancher de dispersion.** Sa formule à partir du test 8.7 n'est toujours pas écrite, alors qu'il sert maintenant à deux endroits.
- **Cas d.** Dire que l'écart en log-cotes entre la ligne estimée et la ligne actuelle tient lieu de log-rapport pour le seuil et le plafond.
- **Jalon de force.** La vraisemblance sous l'intensité « nulle » n'est pas donnée.
- **Test 8.7.** Rien n'est prévu s'il existe moins de 50 questions : élargir alors au-delà de la France.
- **Banque d'événements.** Écrire « tous les événements du balayage dotés d'un critère », pour ôter le choix à l'agent.

### Souhaitables : simplifications

- **Scinder le texte.** Les sections 10 et 11 font environ 45 % du protocole et resteront inactives jusqu'à mi-2027. Un noyau (sections 0 à 9, 12 et 13) et une annexe « phase 3 », gelés séparément, rendraient le noyau lisible et stable.
- **Supprimer le champ « rôle »** (nécessaire ou favorable) : il ne sert plus depuis la fin du plafond hebdomadaire.
- **Reporter le cas d à la phase 4.** Avec 10 à 15 nœuds et une révision trimestrielle, un fait de ce type peut rester en observation jusqu'à l'analyse suivante.
- **Fusionner les sections 10.11 et 11.7** en un seul critère de direction.

## 4. Critère d'arrêt

Cette relecture n'est pas sans défaut important : aucun bloquant, deux importants (F1 et F2). Le compteur reste à zéro.

Les deux corrections sont courtes, et aucune ne touche la méthode de prévision. F1 ne concerne qu'une couche inactive jusqu'en 2027. F2 doit être réglé avant le 1er novembre, puisqu'il porte sur le registre de la phase 1.

## Ce qui est solide

1. Le noyau des phases 1 et 2 n'a reçu aucun défaut de méthode dans cette relecture.
2. La section 8.8 et la liste de contrôle rendent le démarrage vérifiable point par point.
3. Les erreurs sont corrigées par erratum et non par réécriture, y compris quand elles viennent du relecteur.