Je mets à jour le dépôt aux tags `protocole-v1.14` et `annexe-phase3-v1.3` et je lis les pièces avant de répondre.

# Relecture 11 — noyau v1.14, annexe v1.3, banque v1.2

**Verdict.** Les trois défauts importants de la relecture 10 sont corrigés sur le fond, et j'ai reproduit la simulation de puissance (19 grappes, 20 à 25 % pour un écart de 0,02, fausse alarme à 10 %). Le passage au Brier pondéré introduit un biais nouveau dans le test central, et la caractérisation des faits oriente leur traitement sans vérification. Aucun défaut bloquant, deux importants : le critère d'arrêt n'est pas atteint.

Limites : je suis de la même famille de modèles que les auteurs, et ces relectures se suivent dans une seule session, alors que la section 12 prévoit des sessions séparées. Le critère d'arrêt conditionne désormais le premier cycle, donc cette limite pèse davantage.

## 1. Suivi de la relecture 10

| Point | Avis | Motif |
| --- | --- | --- |
| I1 a, questions échues seulement | Suffisante | `notation.py` filtre sur l'échéance, quelle que soit l'issue. |
| I1 b, score testé | Insuffisante | Le Brier pondéré est bien le score testé, mais il est calculé sur des périodes différentes selon l'auteur (J1). |
| I1 c, date du fait d'un constat | Suffisante | `resolution.py` distingue la nature ; l'étape 1 bis couvre les constats négatifs. Une phrase de la procédure reste à corriger (S6). |
| I2, puissance | Suffisante | Reproduite. Le résultat ne change pas avec le test par permutation de `notation.py`, ni avec une autre échelle (voir section 3). |
| I3, contrôle de la banque | Suffisante | Testé sur deux gels : un retrait par `source_accessible` avant le second gel est détecté contre le premier. Il reste un contournement mineur (S5). |
| S1, EV-09 scindé | Suffisante | Deux grappes, 50 % chacune. |
| S2, EV-C2 et EV-32 | Suffisante | Les deux formulations sont univoques. |
| S3, limite écrite en 8.4 | Suffisante | |
| S4, EV-C3a et b | Suffisante | Le maintien est justifié : C3a se clôt avant la phase 3. |
| S5, taux de base gelés, empreintes | Suffisante | |
| S6, poids des grappes | Suffisante | Traité par l'échelle dans la simulation. |

## 2. Changements hors relecture

### Gel à la première version définitive

Le principe est sain : aucun cycle avant un protocole stable, et la procédure vérifie `statut.json` en premier. Trois points de cohérence sont à régler (S1) : les dates de la section 3, la remise à zéro du compteur, et l'autorité qui déclare le statut.

### Faits d'actualité

**Cohérence avec le noyau.**
- La section 8.9 dit que le tri est limité en phases 1 et 2 « à ce seul cas » (donnée). L'annexe v1.3 y ajoute la caractérisation et la reprise, à titre descriptif. Les deux textes se contredisent.
- La règle « une révélation reste une allégation » est cohérente avec `sources.md` et avec le garde-fou des faits contestés (11.5).
- Le garde-fou du double compte (11.5) est respecté : la reprise n'entre dans aucune probabilité.

**Caractérisation par un modèle léger.** C'est le défaut important J2 : le modèle ne lit que des titres de flux, et son étiquette de stade décide du traitement du fait.

**Reprise sur sept flux.** La mesure ne fonctionne pas comme décrite (S2) :
- L'agent de tri ne reçoit pas la liste des faits déjà identifiés (`tri.py a-trier` ne transmet que les titres et les questions). Un même fait reçoit donc un identifiant nouveau à chaque passage, et sa reprise est sous-comptée.
- Le seuil « dépasse cinq sources distinctes » exige six flux sur sept. Deux sont des chaînes parlementaires, celui de Libération ne couvre que la une, et Mediapart est souvent à l'origine du fait. La branche à 14 jours ne se déclenchera presque jamais.
- Les compteurs sont cumulés : « sa reprise a augmenté » est vrai dès qu'un titre nouveau paraît.

**Lisibilité de la règle d'abandon.** Elle se lit mal, pour quatre raisons (S3) :
- La date est « fixée » à l'entrée en observation, mais dépend de la reprise de la première semaine, connue au septième jour.
- « Effet mesurable sur une série suivie » n'a ni seuil ni juge. Attribuer un mouvement de sondage à une affaire est un jugement causal fait à l'œil.
- L'issue après la prolongation unique de 30 jours n'est pas écrite.
- Le cas « effet mesurable sans étape officielle » n'a pas de traitement avant l'analyse trimestrielle.

## 3. Nouveaux défauts

### Bloquants

Aucun.

### Importants

**J1. Le Brier pondéré est moyenné sur des périodes différentes selon l'auteur.**

- **Constat.** `notation.py` fait partir la moyenne du premier jour de prévision de chaque auteur. Sur une question de fenêtre, l'ensemble direct prévoit depuis novembre 2026 et la phase 3 depuis janvier 2027. J'ai inscrit les mêmes probabilités aux mêmes dates pour les deux, avec deux prévisions antérieures pour l'ensemble : le score est de 0,518 pour l'ensemble contre 0,294 pour le modèle.
- **Problème.** Les prévisions lointaines sont en moyenne plus mauvaises. Le test de la section 8.6 favorise donc la phase 3 sur toutes les questions informatives, d'un montant très supérieur à l'écart de 0,02 qu'il cherche. Le verdict « fait mieux » peut venir de ce seul artefact. Le même effet joue pour un auteur qui manque un cycle.
- **Correction proposée.** Pour chaque comparaison, calculer la moyenne sur la période commune : du plus tardif des deux premiers jours de prévision à la veille du fait ou à l'échéance. L'écrire en 8.5 et ajouter un test à `tests.py`.

**J2. Le stade d'un fait est fixé sans vérification, alors qu'il décide de son traitement.**

- **Constat.**
  - La procédure confie la caractérisation au modèle léger, qui ne lit que les titres. L'annexe ne dit pas qui caractérise en phase 3.
  - Le stade oriente le fait : une allégation va en observation, un stade supérieur ouvre la preuve virtuelle. Il est transmis aux évaluateurs, qui doivent citer une classe de référence « de même stade ».
  - Les deux listes se contredisent : « plainte déposée » est au stade « procédure engagée », mais une plainte annoncée par le plaignant n'est pas une étape officielle.
- **Problème.** Une étiquette erronée, tirée d'un titre, peut déclencher une mise à jour de probabilité en phase 3 et ancrer les rapports de vraisemblance. L'exigence d'une source de résolution, posée par la définition de l'étape officielle, n'est appliquée par aucune étape de la procédure.
- **Correction proposée.**
  - Le stade par défaut est « allégation ».
  - Un stade supérieur n'est retenu qu'après vérification de l'étape officielle par deux agents, sur une source de la section 8.8, comme pour le cas « donnée ».
  - Aligner la liste des stades sur celle des étapes officielles.
  - Étendre le contrôle trimestriel du tri à la caractérisation.

### Souhaitables

- **S1. Gel et statut.**
  - La section 3 fixe encore la phase 1 au 1er novembre et la phase 2 au 1er décembre, alors que la section 12 autorise un décalage. Écrire les dates relativement au premier cycle.
  - Dire ce qui remet le compteur à zéro : toute modification du texte, ou seulement une relecture avec défaut important. Sans cela, corriger des souhaitables entre deux relectures propres rend le critère inatteignable ou ambigu.
  - Dire que le passage à `"definitif": true` est une décision humaine journalisée, et faire échouer le contrôle si un gel réel existe alors que le statut est faux.
- **S2. Reprise.**
  - Transmettre à l'agent de tri la liste des faits ouverts avec leur identifiant.
  - Mesurer la reprise sur sept jours glissants.
  - Unifier les seuils : « dépasse cinq » dans l'annexe, « au moins cinq » et « au moins trois » dans `interface/actualite.md`.
  - Corriger la description de `data/reprise.json`, qui dit encore « quatre flux ».
- **S3. Règle d'abandon.** La réécrire en table de décision, par exemple :

  | À la date de réexamen | Traitement |
  | --- | --- |
  | Étape officielle vérifiée depuis l'entrée | L'étape est un fait nouveau, traité selon le tableau ; le fait d'origine est clos |
  | Pas d'étape, reprise des 7 derniers jours au moins égale à celle des 7 premiers | Une prolongation de 30 jours, puis classement « retombé » |
  | Ni l'un ni l'autre | Classé sans effet, motif « retombé » |

  Retirer « effet mesurable sur une série » de la règle, ou le définir par un seuil chiffré fixé à l'avance.
- **S4. Étapes officielles déclenchées par un tiers.** Une saisine de la HATVP, un signalement au titre de l'article 40 ou la création d'une commission d'enquête peuvent venir d'un adversaire politique. Deux de ces actes suffisent à rendre l'affaire « candidate à un lien ». Ne compter que les actes de l'autorité elle-même (ouverture, décision).
- **S5. Gels.** Une réécriture cohérente du fichier gelé et de son manifeste passe le contrôle (testé). Ajouter `data/cycles/*/gel/` aux chemins contrôlés en ajout seul par le workflow.
- **S6. Procédure, étape 1 bis.** Le texte dit encore « chaque constat positif est ajouté comme proposition ». Écrire « chaque constat, quelle que soit l'issue ».
- **S7. Noyau 8.9 et section « 10 et 11 ».** Y inscrire l'usage descriptif de la caractérisation en phase 1, ou le retirer de l'annexe.
- **S8. Verdict non concluant.** Publier l'intervalle de confiance de l'écart moyen et la puissance recalculée sur les grappes réellement présentes à la date du test, plutôt que la puissance simulée à l'avance.
- **S9. Affichage public.** Le volet actualité publiera, sur un dépôt public, une qualification pénale ou de vie privée visant des personnes nommées, produite par un modèle léger. Je ne suis pas juriste, mais le risque d'atteinte à la présomption d'innocence et à la vie privée est réel. Afficher le titre et le lien de la source avec la mention « allégation non vérifiée », et ne pas afficher la nature « vie privée ».

### Simulation de puissance et verdict à trois issues

**Échelle 4p(1 − p).** Elle est acceptable. Un raisonnement en log-cotes donnerait plutôt un écart en e² et un écart-type en e^1,5. Le rapport signal sur bruit par question est le même, et la puissance recalculée ainsi ne bouge pas (20 à 23 % pour 0,02, 37 à 40 % pour 0,04).

**Effet de grappe.** Sa variance suit l'échelle moyenne de la grappe, mais le choc s'ajoute sans échelle à chaque question. C'est une approximation sans conséquence : la fausse alarme reste à 10 % avec le seuil de Student comme avec la permutation.

**Verdict à trois issues.** La règle est claire et cohérente avec les sections 3 et 13. Deux tests unilatéraux à 10 % donnent un risque global de 20 %, ce qui est dit. Tant que J1 n'est pas corrigé, le verdict « fait mieux » n'est pas fiable.

## 4. Critère d'arrêt

Cette relecture comporte deux défauts importants (J1 sur le noyau, J2 sur l'annexe) et aucun bloquant. Le compteur reste à zéro.

Les deux se corrigent sans décision de fond. Il faut ensuite deux relectures propres pour déclarer la version définitive, ce qui reste compatible avec un premier cycle au 1er novembre.

## Ce qui est solide

- La composition du test (questions échues, quelle que soit l'issue) et la date du fait selon la nature éliminent le biais vers l'alarmisme de la v1.12.
- La simulation de puissance repose sur les questions réellement émises et annonce à l'avance un verdict probablement non concluant.
- La règle « une révélation de presse est une allégation, quel que soit le média » et la définition de l'étape officielle donnent un cadre net au traitement des affaires.