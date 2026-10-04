# Réponse à la relecture 11

Noyau v1.15 ; annexe v1.4. Registre du protocole vide.

## 1. Défauts importants

**J1. Brier pondéré sur des périodes différentes.** Corrigé. Pour chaque comparaison, `scripts/notation.py` calcule le Brier pondéré des deux auteurs sur la période commune : du plus tardif des deux premiers jours de prévision à la veille du fait ou à l'échéance (fonction `brier_pondere`). Le calcul par auteur reste publié pour la description, pas pour le test.
- Test ajouté (`test_brier_periode_commune`) : votre cas (mêmes probabilités aux mêmes dates, deux prévisions antérieures pour l'un) donne deux scores égaux sur la période commune ; sur la période propre, l'auteur précoce reste pénalisé, ce qui montre l'artefact corrigé.
- Vérifié de bout en bout sur un registre synthétique : écart nul, verdict non concluant.
- Règle écrite en 8.5 ; un auteur qui manque un cycle est traité de la même façon.

**J2. Stade fixé sans vérification.** Corrigé selon vos quatre points.
- L'agent de tri ne fait que proposer un stade (`stade_propose`). Le stade retenu est « allégation » par défaut.
- Un stade supérieur n'est retenu que si deux agents distincts ont vérifié l'étape officielle correspondante sur une source de la section 8.8. Chaque vérification est inscrite en ajout seul dans `data/tri/etapes.jsonl` (`scripts/tri.py etape`) ; `scripts/tri.py reprise` calcule le stade retenu. Étape 2 bis de la procédure de tri.
- La liste des stades est alignée sur celle des étapes officielles. Une plainte annoncée ou une saisine par un tiers est au stade « allégation ».
- Le contrôle trimestriel du tri porte aussi sur 30 caractérisations tirées au sort.
- C'est le stade retenu, et non le stade proposé, qui est transmis aux évaluateurs et affiché.

## 2. Souhaitables

- **S1. Gel et statut.**
  - Les dates de la section 3 sont relatives au premier cycle P (le 1er du mois qui suit la première version définitive, au plus tôt le 1er novembre 2026).
  - La règle du compteur est écrite en section 12 : il repart de zéro après une relecture avec défaut bloquant ou important. La correction de souhaitables, ou un changement relu par la relecture suivante, ne le remet pas à zéro si cette relecture est propre.
  - Le passage à « définitif » est une décision humaine journalisée. `scripts/controle_banque.py` échoue si un gel de cycle réel existe alors que le statut ne l'est pas.
- **S2. Reprise.**
  - L'agent de tri reçoit la liste des faits suivis avec leur identifiant (`tri.py a-trier`, champ `faits_suivis`).
  - La reprise est mesurée sur les sept premiers jours et sur les sept derniers jours glissants.
  - Un seul seuil, « au moins cinq sources distinctes », dans l'annexe et dans `modele/interface/actualite.md`.
  - La description de `data/reprise.json` est corrigée.
- **S3. Règle d'abandon.** Réécrite en table de décision, comme vous le proposiez. « Effet mesurable sur une série » est retiré : l'effet sur l'opinion passe par les sondages, sans attribution causale. La date de réexamen est fixée à l'entrée et ramenée à 14 jours au septième jour. La prolongation est unique, suivie du classement « retombé ». Le statut est calculé par script ; le cycle complet (observation, réexamen avancé, retombé, étape vérifiée) a été vérifié sur un fait simulé.
- **S4.** Seuls comptent les actes de l'autorité elle-même : une saisine ou un signalement par un tiers est une allégation. Le seuil « candidate à un lien » porte sur deux étapes vérifiées.
- **S5.** Le workflow de contrôle fait échouer toute modification ou suppression d'un fichier sous `data/cycles/*/gel/`.
- **S6.** Étape 1 bis : « chaque constat, quelle que soit l'issue ».
- **S7.** Section 8.9 et résumé des sections 10 et 11 du noyau : l'usage descriptif de la caractérisation et de la reprise en phase 1 y est inscrit.
- **S8.** Le verdict publie l'écart moyen par question, son intervalle à 80 % (rééchantillonnage des grappes) et la puissance recalculée sur les grappes présentes. Le risque global de 20 % des deux tests unilatéraux est écrit en 8.6.
- **S9.** Annexe, section 11.6. Pour une allégation, l'affichage se limite au titre et au lien de la source, avec la mention « allégation non vérifiée ». Aucune qualification pénale produite par un agent n'est affichée, seulement le stade retenu et l'étape vérifiée avec sa source. La nature « vie privée » n'est jamais affichée.

## 3. Sessions séparées

La remarque est juste : les relectures 8 à 11 ont été conduites dans une même session de relecteur. Nathan ouvrira une session neuve pour chaque relecture à partir de la 12e, comme le prévoit la section 12.
