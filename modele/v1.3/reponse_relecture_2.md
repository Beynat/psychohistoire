# Réponse à la relecture 2 (protocole v1.2 → v1.3)

Relecture : `relecture_2.md`. Protocole révisé : `../protocole.md`.
Légende : **accepté**, **accepté en partie** (avec limite explicite), **rejeté** (avec motif).

## Ligne générale

Le relecteur relève que la réponse à la relecture 1 acceptait tout, au prix d'un protocole inexécutable. La v1.3 corrige cette dérive par trois choix :
- le protocole est **phasé** : chaque phase doit battre la précédente pour que la suivante soit construite (section 3) ;
- les composantes sans données suffisantes (Linzer, ACLED, chocs d'événements sur l'écart de taux, distributions allemande et italienne) sont **retirées**, pas approchées ;
- trois points sont **rejetés** avec motif.

La v1.3 ajoute aussi une section nouvelle, non relue : les **mises à jour événementielles** (section 10). Elle est soumise en priorité à la relecture 3.

## Suivi des points de la relecture 1 jugés insuffisants

| Point | Décision | Correction |
| --- | --- | --- |
| B4 Antériorité | Accepté | Les deux registres sont créés en fichiers séparés, en ajout seul : `registre/exploratoire.jsonl` et `registre/protocole.jsonl`. Le tag ne peut pas être posé depuis l'environnement des agents (refus du proxy) : Nathan le pose manuellement sur le commit de la v1.3. En attendant, le commit horodaté fait foi. Section 0. |
| I1 Indépendance | Accepté en partie | Le volume d'élicitation est divisé par environ dix (réseau de 10 à 15 nœuds, section 3). Cela rend faisable un évaluateur d'une autre famille sur toutes les tables, en deux messages, un par tour. Pour le reste, la limite demeure : la diversité de famille n'est pas garantie à chaque tâche. Section 6.1. |
| I2, I3 Échelles et règle | Accepté | Voir N5. |
| I7 Contamination | Accepté | Voir N6. |
| Étalon externe | Rejeté | Voir les améliorations. |

## Défauts bloquants

| Point | Décision | Correction |
| --- | --- | --- |
| N1 Le critère d'échec ne teste pas la structure | Accepté | P2 est scindé en P2a (variables d'état), P2b (événements et décisions sans cote) et P2c (questions conjointes). Les questions conditionnelles sont remplacées par des questions conjointes du type « A et B avant telle date ». La structure est jugée sur P2b et P2c seulement. Une grappe correspond à une variable source sur une fenêtre trimestrielle sans chevauchement, avec un objectif d'au moins 40 grappes. La puissance est simulée et publiée avant le premier cycle, par un script. Sections 8.1, 8.3 et 8.6. |
| N2 Inexécutable avant le 1er novembre | Accepté | Protocole phasé (section 3) : **phase 1** au 1er novembre, ensemble direct et lignes de base ; **phase 2**, modèle de l'écart de taux et moyenne de sondages ; **phase 3** au 1er janvier 2027 au plus tard, réseau réduit de 10 à 15 nœuds ; **phase 4**, extension, seulement si la phase 3 bat la phase 1. Linzer, ACLED et les chocs d'événements sur l'écart de taux sont retirés (section 7.1). Chaque étape a une liste de contrôle, et tout ce qui est mécanique passe par des scripts (génération des questions, scores, agrégation, puissance). Le second balayage à un mois intervient avant la phase 3 ; il ne conditionne plus la phase 1. |

## Défauts importants

| Point | Décision | Correction |
| --- | --- | --- |
| N3 Calage indéfini | Accepté (proposition du relecteur) | Le nœud reste dans le réseau. On décale l'ordonnée de sa table, en log-cotes, jusqu'à ce que la marginale calculée égale la cote. Le marché fournit le niveau, le modèle la dépendance. Critères de fiabilité : volume cumulé d'au moins 100 000 dollars, écart entre l'offre et la demande d'au plus 3 points, et même événement résolu à un mois près. Sinon, pas de calage. Section 4.5. |
| N4 Élicitation mensuelle | Accepté | Élicitation à l'horizon naturel de l'événement, conversion en taux mensuel, puis contrôle du cumul sur 23 mois, présenté aux évaluateurs avant validation. Les parents continus sont discrétisés aux quantiles historiques 33 et 67. Tout cycle est cassé en renvoyant l'arc à la tranche suivante. Le plafond de trois parents est maintenu, avec une exception motivée par nœud (au plus quatre). Sections 4.2 et 7.4. |
| N5 Échelles et règle incomplètes | Accepté | Les seuils des cibles sont publiés (section 5.2). Les cibles passent à cinq : écart de taux, croissance, inflation, gouvernabilité et issue politique. L'issue politique désigne la présidentielle jusqu'en mai 2027, puis la majorité à l'Assemblée. La règle à cases est remplacée par un classement continu : score = impact × incertitude normalisée, avec l'entropie pour les nœuds à plus de deux issues. Les N premiers sont retenus, N étant fixé par la phase. Chaque cible doit être couverte par au moins un nœud. La catégorie « paramètre prédéterminé » est réservée aux variables. Un événement rare à fort impact n'en fait plus partie : il passe au registre des risques extrêmes (section 5.4). |
| N6 Test du jugement qui fuit | Accepté | Le test porte sur des questions ouvertes publiquement avant le 1er juillet 2026 (Metaculus, Polymarket, Good Judgment Open) et résolues ensuite. Il est conduit sans recherche web, sur un dossier figé. La coupure de chaque modèle est vérifiée par sondage de faits datés. Section 8.7. |
| N7 Dispersion et comparateurs | Accepté | La concentration des lois de Dirichlet repose sur la dispersion du premier tour, avec un plancher calé sur le test N6. L'alpha est publié, mais aucun nouveau passage n'est fait pour l'améliorer : un alpha faible élargit les lois. L'ensemble direct n'est pas extrémisé. La persistance est une marche aléatoire à la volatilité historique. Les seuils des questions de variables sont pris aux quantiles 20, 50 et 80 de cette marche. Sections 4.4, 6.1, 8.1 et 8.4. |
| N8 Pièces incohérentes | Accepté | Le registre exploratoire est séparé de `data.json`, qui reste l'état vivant de la page. Les pivots sont définis en section 2. Les politiques allemande et italienne sortent du modèle : elles n'entrent que par des séries observées (Bund et écart de taux italien, collectés). |

## Améliorations souhaitables

| Point | Décision | Correction |
| --- | --- | --- |
| Saltelli → régression | Accepté | Régression des sorties sur les jeux de paramètres. Section 4.6. |
| 100 trajectoires | Accepté | 1 000 trajectoires par jeu. |
| Seuil de calibration à 0,10 | Accepté | Le critère devient une erreur de calibration au-dessus du 90e centile de sa distribution simulée sous calibration parfaite, au même nombre de questions. Section 8.6. |
| « Simplifié » et persistance | Accepté | « Simplifié » signifie revenir à la phase précédente. « Moins bien que la persistance » signifie un écart de Brier significatif au seuil de 10 % en faveur de la persistance. |
| Étalon externe | **Rejeté** | Participer à ForecastBench ou à un tournoi Metaculus suppose une infrastructure de soumission hors de portée de ce projet. Un engagement conditionnel n'engageant à rien, nous le supprimons plutôt que de le maintenir. Il est remplacé par une comparaison systématique, sur P1, à la prévision communautaire Metaculus ou au prix Polymarket, ce qui est faisable et déjà prévu. |

## Remarques de processus

| Point | Décision | Correction |
| --- | --- | --- |
| Tout accepter alourdit | Accepté | Trois rejets dans cette réponse : l'étalon externe ci-dessus, plus les deux suivants. |
| Relecteur de la même famille | Accepté | La mise en production de la phase 3 est conditionnée à une relecture par un modèle d'une autre famille ou par un prévisionniste humain. La phase 1, qui ne dépend d'aucun choix structurel, peut démarrer avant. Section 11. |
| Matrice d'influences complète (MICMAC) | **Rejeté** | Avec 10 à 15 nœuds, les parents sont choisis directement par les évaluateurs, à partir des influences directes. L'analyse indirecte n'apporte rien à cette taille et coûterait environ 1 500 cases. Elle redevient obligatoire en phase 4. |
| Second balayage à un mois comme préalable | **Rejeté comme préalable** | Il est maintenu, mais avant la phase 3 seulement. La phase 1 ne dépend pas du balayage. |

## Réponses aux questions ouvertes

1. **Calage.** La proposition du relecteur est adoptée telle quelle (N3).
2. **Critère à 200 questions.** Exprimé en grappes, au moins 40. La puissance est publiée avant le premier cycle.
3. **Incertitude dérivée.** Adoptée sous la forme impact × √(p(1 − p)), avec l'entropie normalisée pour les nœuds à plus de deux issues. Un écart interquartile supérieur à 20 points est signalé. Pour les événements récurrents, la probabilité est remplacée par celle de survenue dans la fenêtre de la phase.

## Questions ouvertes pour la relecture 3

1. La section 10 (mises à jour événementielles) : la preuve virtuelle sur un nœud non observé est-elle le bon formalisme ? Le plafond du rapport de vraisemblance par événement est-il justifié ?
2. Le critère qui conserve ou supprime la couche événementielle (section 10.7) a-t-il une puissance suffisante, compte tenu du petit nombre de mises à jour attendues ?
3. Le phasage (section 3) laisse-t-il assez de questions résolues avant la présidentielle d'avril 2027 pour juger la phase 3 ?
