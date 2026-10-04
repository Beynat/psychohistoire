# Relecture 14 (suivi) — noyau v1.17, annexe v1.6

Relecture de suivi, conduite dans la session qui a lancé la relecture 13. Elle vérifie les corrections et ne compte pas pour le critère d'arrêt. Dépôt lu au commit `0db46a2`, identique aux tags `protocole-v1.17` et `annexe-phase3-v1.6`.

**Verdict.** L1 est corrigé, dans la collecte, le script et le texte. Douze des treize souhaitables sont traités. S1 ne l'est qu'à moitié : la réouverture par erratum ne tient pas, et un « non » prématuré redevient valable après l'échéance. Les corrections n'introduisent aucun défaut bloquant ni important ; je relève un souhaitable nouveau et trois défauts de rédaction.

**Ce que j'ai fait.** Lecture de la réponse et des diffs v1.16 → v1.17 (noyau, annexe, procédures, consigne, workflows, scripts). `tests.py` : huit tests conformes. `controle_banque.py` : conforme. Essais sur une copie : résolution (doublons, « non » prématuré, errata, annulations à 30 et 60 jours), Brent, gel, champs figés, calibration, puissance régénérée.

**Limites.** Workflows lus, pas exécutés. Le tri n'a été vérifié que par lecture du script.

## 1. Suivi de la relecture 13

| Point | Avis | Motif |
| --- | --- | --- |
| L1, première valeur collectée | Suffisante | Brent : avec des cotations des 2 et 3 novembre, la série s'arrête à octobre ; novembre n'apparaît qu'à la première cotation de décembre. Journal : 2 319 premières valeurs, sans le Brent de septembre. `resolution.py` lit le journal et date le fait de la collecte ; le test reproduit le scénario 3,4 révisé à 3,3 et donne « oui ». Texte de 8.8 conforme. |
| S1, « non » prématuré | Insuffisante | Le « non » est bien ignoré avant l'échéance, et l'étape 1 bis est précisée. Deux défauts restent (N1 ci-dessous). |
| S2, calibration | Suffisante | Mesure, référence, seuil et recalibration écrits en 8.6 ; `test_calibration` présent dans le bilan. Essai sur 150 jeux : 8 % de « recalibrer » pour un jeu calibré, 95 % pour des probabilités multipliées par 1,8. La recalibration elle-même n'est pas scriptée ; elle n'a pas à l'être avant le premier bilan. |
| S3, champs figés | Suffisante | Les quatre modifications (acte, événement, mode de taux de base, référence externe) font échouer le contrôle. Section 12 à jour. |
| S4, tests | Suffisante en partie | Les deux tests existent et passent. La description de `test_regles_de_resolution` annonce la réouverture par erratum, qui n'est pas testée ; l'annulation à 30 jours ne l'est pas non plus. Un test de réouverture aurait trouvé N1. |
| S5, tri | Suffisante | « Autre » est un fait public ; les deux axes sont séparés dans `stades_retenus` ; champs libres encadrés ; contrôle trimestriel réécrit. Écart mineur : un fait public non vérifié passe directement à « retombé » à la date de réexamen, sans la branche de prolongation de la table 11.3. |
| S6, identifiants d'agents | Suffisante | Scénario reproduit : « oui » d'agent-1 en 2026, deux « non » en 2027, résolution « non » par troisième avis. |
| S7, puissance | Suffisante | `puissance.json` se régénère à l'identique, et les chiffres du texte en sont repris (16 à 19 %, 26 à 32 % ; 25 à 31 % et 47 à 60 % avec P2c). Réserve : le texte dit que la puissance du critère de persistance « est publiée », mais elle ne figure pas dans `puissance.json`. |
| S8, questions cotées | Suffisante | Interdit ajouté à la consigne v1.4, limite écrite en 8.6. L'interdit n'est pas vérifiable ; c'est dit. |
| S9, double bilan | Suffisante | `verdict_8_6` combiné ; double calcul pour le taux de base. |
| S10, cohérence du texte | Suffisante | 4.5, en-tête de 8.6, 8.5 et références corrigés. |
| S11, robustesse | Suffisante | Brier à 1 pour une issue réalisée absente ; correspondances lues dans le gel ; `geler.py` refuse une date qui n'est pas celle du jour. |
| S12, documents périmés | Suffisante | Vérifié par le diff pour `phase1.md` et `phase3.md`. La case du rattrapage reste ouverte, comme condition de la phase 1. |
| S13, annulation | Suffisante | Deux recherches vaines : annulation à 31 jours. Une seule : rien à 31 jours, annulation à 61. Aucune : la question reste ouverte. |

## 2. Défauts introduits ou laissés par les corrections

### Bloquants et importants

Aucun.

### Souhaitables

**N1. La correction de S1 ne tient pas dans deux cas.**

- **Réouverture annulée au passage suivant.** Essai : deux « oui » erronés résolvent Q-EV-15 ; un erratum `rouverte` la rouvre ; `resolution.py` relancé la résout de nouveau « oui », car les propositions erronées sont toujours dans le registre. Le tri lance ce script trois fois par semaine. La section 8.8 dit qu'un erratum « peut rouvrir une question close à tort » : en pratique, la réouverture dure jusqu'au passage suivant.
- **« Non » prématuré compté après l'échéance.** Le script compare l'échéance à la date du jour, pas à la date de la proposition. Essai : deux « non » déposés en novembre 2026 sur Q-EV-01 sont ignorés jusqu'au 30 septembre 2028, puis résolvent la question « non » le 1er octobre 2028, sans aucune recherche à l'échéance.
- **Classement.** Souhaitable, pour le motif retenu en relecture 13 : les deux cas supposent une erreur d'agents. La question rouverte à tort n'est plus émise, donc perdue, mais aucune issue fausse n'entre dans un test sans erreur préalable.
- **Correction proposée.** Ignorer toute proposition émise avant le dernier erratum de réouverture de la question. Ignorer un « non » sur un événement « survenue » quand la proposition est émise avant l'échéance, quelle que soit la date du passage. Ajouter les deux cas à `test_regles_de_resolution`.

**N2. Règle des relectures de suivi (section 12).** Le texte ne dit pas ce que devient le compteur si une relecture de suivi, placée entre deux relectures de validation propres, relève un défaut important. Écrire qu'un tel défaut est corrigé puis relu par la validation suivante, qui seule fait foi.

**N3. Rédaction.**

- Annexe 11.2 : la phrase « Plus de 10 % de faux négatifs… entraînent une révision de la consigne de tri » est passée sous la puce « Champs libres » ; elle appartient à « Contrôle du tri ».
- Procédure du cycle, étape 1 bis : l'exemple « (Marine Le Pen absente de la liste officielle) » suit maintenant la phrase sur les événements « survenue », alors qu'il illustre un constat négatif.
- Noyau, section 12 : « …que les auteurs ; Deux sortes de relectures » (ponctuation).

**N4. Contrôle du journal des premières valeurs.** À ma connaissance, une poussée faite par le jeton d'un workflow ne déclenche pas d'autre workflow. Les lignes ajoutées par la collecte nocturne ne passent donc pas par le contrôle d'ajout seul ; une modification manuelle, elle, y passe. Je ne l'ai pas vérifié par exécution. Sans conséquence si c'est assumé : l'écrire.

## 3. Conclusion

Aucun défaut bloquant ni important dans les corrections. N1 est à traiter avant la relecture de validation, pour qu'elle ne le relève pas à son tour ; N3 se corrige en trois lignes.