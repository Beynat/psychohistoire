# Relecture 6 (protocole v1.8 et annexe v1.0, commit f71ff8e)

Relecteur externe, reçue le 4 octobre 2026. Texte intégral, non modifié. Première relecture sans défaut bloquant ni important.

Je récupère la v1.8 et l'annexe aux tags indiqués, puis je lis les pièces avant de rendre la relecture 6.

**Verdict.** Cette relecture est sans défaut bloquant ni important : c'est la première du genre. Les deux défauts de la relecture 5 sont corrigés, la scission tient et le noyau se lit seul pour les phases 1 et 2. Il reste des souhaitables, dont un résidu de F1 que j'ai chiffré avant de le classer.

J'ai lu le noyau au tag `protocole-v1.8` et l'annexe au tag `annexe-phase3-v1.0` (même commit `f71ff8e`). J'ai exécuté le contrôle des registres et `scripts/registre.py` sur une copie du dépôt, avec dix cas.

## 1. Suivi de la relecture 5

| Point | Jugement | Motif |
|---|---|---|
| F1 Unité de Z | Suffisante | Un terme par question et un seuil unique de 40. Résidu chiffré plus bas (S1). |
| F2 Intégrité des registres | Suffisante | Vérifiée par exécution, voir ci-dessous. |
| Protection de branche | Suffisante | Le motif est corrigé et les tags sont couverts. |
| Seuil d'application | Suffisante | Plancher sur la dispersion, en log-cotes, plafond avant réduction. |
| Cohérence | Suffisante | Les douze points sont traités. Une suite sur le critère de persistance (S2). |
| Simplifications | Suffisantes | Scission faite, champ « rôle » supprimé, cas d reporté, critère commun. |

Le contrôle des registres se comporte comme annoncé :

| Cas testé | Résultat |
|---|---|
| Ajout par le script | Conforme |
| Ligne antidatée de trois jours | Détectée |
| Ligne réécrite | Détectée |
| Fichier renommé | Détecté |
| Ligne sans horodatage | Détectée |
| Décision de tri ajoutée en JSONL | Conforme |
| Entrée fournissant son propre horodatage | Refusée par le script |
| Prévision de la piste protocole sans phase | Refusée par le script |

Une ligne écrite à la main avec une heure plausible passe le contrôle. Ce n'est pas un défaut : la garantie vient de la fenêtre de deux heures mesurée côté serveur, pas du script.

## 2. Scission

**Le noyau se lit seul pour les phases 1 et 2.** Les renvois vers l'annexe sont tous marqués, et ceux de l'annexe vers le noyau tombent sur les bonnes sections. Trois raccords restent à faire :

- **Détection des données en phase 1.** La section 8.9 applique « un fait qui résout un nœud », mais la veille et le tri qui le détectent ne sont décrits que dans l'annexe (11.2), réservée à la phase 3. La liste de contrôle de la phase 1 prévoit pourtant le tri. Une phrase en 8.9 suffit : la détection passe par la veille et le tri de l'annexe, limités au cas « donnée ».
- **Annulation pour résolution antérieure.** La section 12 renvoie à la section 8.8 pour cette règle, qui n'y figure pas.
- **Vocabulaire.** La section 8.9 parle de « nœud » alors qu'il n'y a pas de réseau en phase 1 : écrire « question ».

## 3. Nouveaux défauts

Aucun bloquant, aucun important.

### Souhaitables

**S1. Corrélation résiduelle dans la statistique Z (annexe, 10.11).**
- **Constat.** Les questions d'un même lien restent corrélées (B, « A et B », nœuds en aval), et leurs déplacements sont de même signe.
- **Problème.** Le taux de fausse activation passe de 10 % à 11–16 % selon la corrélation, dans ma simulation. C'est nettement moins qu'avant correction (16 à 20 %, avec un seuil qui pouvait reposer sur quatre issues), d'où le classement en souhaitable.
- **Correction.** Sommer les termes par grappe (section 8.3) et normaliser par la variance entre grappes : le taux revient à 10–11 %. Préciser aussi que les 40 questions sont celles dont le déplacement n'est pas nul.

**S2. Critère de persistance devenu ambigu (noyau, 8.6).**
- **Constat.** La persistance n'est plus définie que pour les variables (8.4), mais le critère d'échec méthodologique porte encore sur « P2 ».
- **Correction.** Écrire : « si la persistance (variables) ou le taux de base (événements) bat le modèle ». À faire avant la première évaluation du critère.

**S3. Formats non écrits.**
- Le fichier de tri en JSONL n'a pas de schéma, alors que `collect.py` y lit une clé `lien` : une décision qui regrouperait plusieurs titres sous une autre clé ne marquerait aucun titre comme trié.
- Le passage de la dispersion en log-cotes à la concentration de la loi de Dirichlet n'est pas formulé (section 4.4).
- Le Brier pondéré dans le temps n'a pas de formule (section 8.5).

**S4. Contrôle des registres.**
- Un horodatage sans fuseau fait planter le contrôle au lieu de produire un message. Le résultat est le même (échec), mais le motif est illisible.
- La date de définition des jalons n'est pas contrôlée à la poussée comme l'est `emise`. Le gel à 7 jours repose donc sur la seule date de commit.

**S5. Estimation des facteurs k.** Aucun effectif minimal ni borne : n'estimer qu'à partir de 40 questions, et borner le résultat entre 0 et 1.

**S6. Bilan de la phase 1.** Le gel court « jusqu'au bilan de la phase 1 », qui n'a pas de date. La première analyse trimestrielle serait un repère naturel.

**S7. Prérequis de la phase 2.** La liste ne mentionne que l'écart de taux journalier. La source des sondages manque.

**S8. Ensemble direct.** Aucun critère ne le compare au taux de base. Publier cet écart à chaque bilan, sans décision attachée : si l'ensemble ne bat pas le taux de base, « battre la phase 1 » ne prouve pas grand-chose.

## 4. Critère d'arrêt

**Cette relecture est sans défaut bloquant ni important.** Le compteur passe à un. Une seconde relecture de ce type arrête le processus.

Deux remarques pour la suite :
- Aucun des souhaitables n'exige une nouvelle version avant le 1er novembre. S2 et le premier raccord de la section 2 méritent d'être corrigés à la prochaine version, quelle qu'en soit la cause.
- Je relis ce protocole pour la sixième fois dans la même session, et plusieurs corrections viennent de mes propres propositions. Le critère d'arrêt mesure donc la stabilité du texte face à un relecteur, pas sa validité. La validité se jugera sur les résolutions, comme le prévoit la section 13.

## Ce qui est solide

1. Le noyau des phases 1 et 2 n'a reçu aucun défaut de méthode depuis deux relectures.
2. L'intégrité des registres repose sur un contrôle exécuté côté serveur, vérifié sur des cas conformes et fautifs.
3. Les couches de la phase 3 sont inactives par défaut, et chacune a un critère d'activation centré et calculé par script.