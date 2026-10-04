# Réponse à la relecture 5 (protocole v1.7 → v1.8 et annexe phase 3 v1.0)

Relecture : `relecture_5.md`. Textes révisés : `../protocole.md` (noyau) et `../annexe_phase3.md`.
Légende : **accepté**, **accepté en partie** (avec limite explicite), **rejeté** (avec motif).

Les deux défauts importants et tous les souhaitables sont acceptés, y compris les simplifications. La principale est la scission du texte : un noyau (sections 0 à 9, 12 et 13) et une annexe phase 3 (sections 10 et 11), versionnés, tagués et gelés séparément. La numérotation est conservée pour la continuité des renvois.

## Défauts importants

| Point | Décision | Correction |
| --- | --- | --- |
| F1 Unité de Z | Accepté | Un terme par question résolue. d est le déplacement cumulé dû à la couche, mesuré à la clôture : probabilité fantôme moins probabilité sans jalons, ou probabilité avec moins probabilité sans les faits imprévus. Le seuil est de 40 questions résolues pour l'activation comme pour la désactivation. Annexe, sections 10.6 et 10.11. |
| F2 Intégrité des registres | Accepté | `scripts/registre.py` fixe seul le champ `emise` à partir de l'horloge système et refuse toute valeur fournie. Le workflow vérifie, avec `--no-renames`, qu'aucune ligne n'est supprimée ou réécrite, qu'aucun fichier suivi n'est supprimé ou renommé, et que chaque nouvelle ligne de registre est datée dans les deux heures qui précèdent la poussée. La date de poussée fait foi. Les décisions de tri passent en JSONL ; le fichier d'octobre 2026, antérieur, est gelé tel quel et reste lu par la collecte. Les horodatages écrits à la main les 3 octobre font l'objet d'un erratum, écrit par le script. Le contrôle a été testé sur un cas conforme et sur un cas fautif (réécriture, renommage, horodatage hors fenêtre) : les quatre anomalies sont détectées. Noyau, sections 0 et 12 ; liste de contrôle. |

## Protection de branche

**Accepté.** Le motif est corrigé : un contrôle obligatoire imposerait des demandes de fusion et bloquerait la poussée directe de la collecte et des agents. La protection des tags `protocole-v*` et `annexe-phase3-v*` contre la suppression et la mise à jour est ajoutée ; c'est un réglage à faire par Nathan.

## Seuil d'application

**Accepté.** La première lecture du relecteur est retenue :
- le plancher porte sur la dispersion des log-rapports, en log-cotes ;
- l'erreur type est cette dispersion divisée par √n ;
- le plafond s'applique au rapport brut, avant la réduction par k.

Annexe, section 11.4.

## Souhaitables : cohérence

| Point | Correction |
| --- | --- |
| Calibration des jalons | Les quatre passages parlent désormais de la validation de la direction des mises à jour fantômes. P2d est déclaré descriptif, sans décision attachée. |
| Phasage | Les phases 2 et 3 suivent le calendrier ; seule la phase 4 est conditionnée à une victoire. Le retour à la phase précédente suit l'échec des critères de la section 8.6. |
| Pistes parallèles | La phrase est supprimée ; le registre fantôme est décrit comme entièrement scripté. |
| Évaluateurs des jalons | Cinq, sur au moins trois modèles, comme en section 6.1. |
| Comparateurs | Persistance pour les variables, taux de base pour les événements, et 50 %. |
| Critère 11.7 | Décision sur la seule statistique Z ; le test de signe est publié à titre descriptif. |
| Facteur k | Régression sur le log-rapport brut ; un facteur distinct, k_faits, pour les faits imprévus, estimé sur tous les avis de panel, y compris sous le seuil. |
| Plancher de dispersion | Formule écrite : le plus grand de 0,3 en log-cotes, de la dispersion du test 8.7 divisée par la pente de recalibration si elle est inférieure à 1, et de l'écart-type de l'écart aux cotes P1. Section 4.4. |
| Cas d | Reporté à la phase 4. En phase 3, un tel fait est en observation jusqu'à l'analyse trimestrielle. En phase 4, l'écart en log-cotes entre la ligne estimée et la ligne actuelle tient lieu de log-rapport. |
| Jalon de force | Une vraisemblance c sous l'intensité nulle est ajoutée. |
| Test 8.7 | Élargissement à l'Europe, puis au monde, s'il y a moins de 50 questions. |
| Banque d'événements | Tous les événements du balayage dotés d'un critère, sans sélection par l'agent. |

## Souhaitables : simplifications

| Point | Correction |
| --- | --- |
| Scinder le texte | Fait : noyau v1.8 et annexe v1.0. Le noyau résume l'annexe en quelques lignes ; une nouvelle section 8.9 y porte le cas « donnée », seul utilisé dès la phase 1. |
| Champ « rôle » | Supprimé. |
| Cas d | Reporté à la phase 4. |
| Fusion des critères | La section 10.11 devient le critère de direction commun ; la section 11.7 y renvoie. |

## Question pour la relecture 6

La scission a-t-elle laissé des renvois incohérents entre le noyau et l'annexe, et le noyau se lit-il désormais seul pour les phases 1 et 2 ?
