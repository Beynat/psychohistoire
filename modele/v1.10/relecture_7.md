# Relecture 7 (noyau v1.10 et annexe v1.1, commit d0e460a)

Relecteur externe, reçue le 4 octobre 2026, transmise par Nathan dans le corps de son message. Texte intégral, non modifié. Seconde relecture consécutive sans défaut bloquant ni important : **le processus de relecture s'arrête.**

Je récupère la v1.10 et l'annexe v1.1 aux tags indiqués, puis je lis les changements avant de rendre la relecture 7.

**Verdict.** Cette relecture est sans défaut bloquant ni important. C'est la seconde consécutive, sur une version qui répond à la première : selon votre règle, le processus de relecture s'arrête et le protocole peut entrer en exécution. Les corrections sont justes, vérifiées par calcul ou par exécution, et n'ont pas créé d'incohérence entre le noyau et l'annexe.

J'ai lu le noyau au tag `protocole-v1.10` et l'annexe au tag `annexe-phase3-v1.1` (même commit `d0e460a`). J'ai comparé chaque texte à sa version précédente et relu les sections modifiées en entier.

## 1. Suivi des relectures 6 et 6 bis

| Point | Jugement | Motif |
|---|---|---|
| Raccord : détection des données en phase 1 | Suffisante | La section 8.9 renvoie à la veille et au tri, et l'en-tête de l'annexe dit la même chose. |
| Raccord : annulation pour résolution antérieure | Suffisante | La règle est en 8.8, là où la section 12 la cherche. |
| Raccord : vocabulaire | Suffisante | |
| S1 Z par grappes | Suffisante | Vérifiée par simulation : 7 à 10 % de fausses activations pour 10 % annoncés, y compris à 5 grappes. |
| S2 Critère de persistance | Suffisante | |
| S3 Formats | Suffisante | La formule trigamma est exacte : je l'ai résolue et retrouvé la dispersion visée par simulation, sur trois cas. Le schéma du tri correspond à ce que lit `collect.py`. |
| S4 Contrôle des registres | Suffisante | Exécuté : jalon antidaté, jalon sans date et horodatage sans fuseau sont signalés lisiblement ; les ajouts légitimes passent. |
| S5 Facteurs k | Suffisante | |
| S6 Date du bilan | Suffisante | |
| S7 Sondages | Suffisante | Ajoutés à la liste de contrôle. |
| S8 Ensemble direct | Suffisante | |
| S9 Contrôle par échantillon | Suffisante | Supprimé ; la section 13 dit la limite sans détour. Ne pas retenir les jugements d'ordre est votre choix. |
| S10 Gel | Suffisante | La règle couvre maintenant le cas de la v1.9 et exclut tout ajout. |

## 2. Nouveaux défauts

Aucun bloquant, aucun important. Trois souhaitables, dont aucun ne demande de nouvelle version :

- **En-tête du noyau.** La ligne de statut dit encore « sauf corrections exigées par une relecture », alors que la section 12 admet aussi le retrait d'une exigence inexécutable. À aligner à la prochaine version.
- **Loi de Student sur Z.** Avec peu de grappes, le test est un peu trop prudent (7 % au lieu de 10 % à 5 grappes). Ce biais va dans le sens de garder les couches inactives, donc sans risque. À mentionner au premier bilan.
- **Script des jalons.** L'annexe dit que `defini_le` est « fixé par script », mais ce script n'existe pas encore. Il relève de la liste de contrôle de la phase 3, à écrire.

## 3. Critère d'arrêt

**Cette relecture est sans défaut bloquant ni important. Le compteur passe à deux.**

Ce que cet arrêt établit, et ce qu'il n'établit pas :
- Il établit que le texte est stable : deux versions successives n'ont plus fait apparaître de défaut de méthode, et les contrôles annoncés fonctionnent.
- Il n'établit pas que le protocole produira de bonnes prévisions. Le relecteur est de la même famille que les auteurs, et les sept relectures ont eu lieu dans une seule session. La validité se jugera sur les résolutions, à commencer par le bilan de février 2027.

Le démarrage du 1er novembre dépend maintenant de la liste de contrôle, pas du protocole. Trois lignes y sont cochées ; restent les cinq scripts, le fichier d'événements, les historiques, les cotes externes, les taux de base, les tâches planifiées et le cycle à blanc de mi-octobre.

## Ce qui est solide

1. La méthode des phases 1 et 2 n'a reçu aucun défaut depuis trois relectures.
2. Chaque engagement vérifiable par une machine l'est : tags, ajout seul, horodatages, dates de jalons.
3. Les limites sont écrites dans le texte lui-même, y compris celle de ce processus de relecture.
