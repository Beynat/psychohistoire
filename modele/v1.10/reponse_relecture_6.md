# Réponse aux relectures 6 et 6 bis (noyau v1.9 → v1.10, annexe v1.0 → v1.1)

Relectures : `relecture_6.md` (sur la v1.8) et `relecture_6bis.md` (sur la v1.9). Textes révisés : `../protocole.md` et `../annexe_phase3.md`.

**Compteur du critère d'arrêt.** La relecture 6 est la première sans défaut bloquant ni important. La relecture 6 bis l'est aussi, mais elle porte sur un texte presque identique, à dix minutes d'écart : conformément à la recommandation du relecteur, elle n'est pas comptée. Le compteur est à un. La relecture 7, sur cette version, décidera de l'arrêt.

Tous les points sont acceptés.

## Raccords de la scission

| Point | Correction |
| --- | --- |
| Détection des données en phase 1 | La section 8.9 renvoie à la veille et au tri de l'annexe (11.2), limités en phases 1 et 2 au seul cas « donnée ». L'en-tête de l'annexe le dit aussi. |
| Annulation pour résolution antérieure | Ajoutée en section 8.8. |
| Vocabulaire | « Question » au lieu de « nœud » en section 8.9 ; le nœud n'est mentionné que pour la phase 3. |

## Souhaitables

| Point | Correction |
| --- | --- |
| S1 Corrélation résiduelle dans Z | Termes sommés par grappe, Z = Σ S_g / √(Σ S_g²). Loi de Student sous 15 grappes. Seules comptent les questions déplacées d'au moins 0,5 point. Annexe, section 10.11. |
| S2 Critère de persistance | « Si la persistance (variables) ou le taux de base (événements) bat le modèle ». Section 8.6. |
| S3 Formats | Schéma des lignes de tri (`lien`, `passage`, `fait`, `decision`, `motif`), annexe 11.2. Passage de la dispersion à la concentration de Dirichlet par la fonction trigamma, section 4.4. Formule du Brier pondéré dans le temps, section 8.5. |
| S4 Contrôle des registres | Un horodatage sans fuseau produit un message lisible. La date de définition des jalons (`defini_le`) est contrôlée à la poussée comme `emise`. Testé : un horodatage sans fuseau est signalé comme tel. |
| S5 Facteurs k | Estimation seulement à partir de 40 questions résolues, bornée entre 0 et 1. Annexe, section 10.4. |
| S6 Bilan de la phase 1 | Tenu à la première analyse trimestrielle, début février 2027. Section 12. |
| S7 Prérequis de la phase 2 | Source des sondages et historique 2002-2022 ajoutés à la liste de contrôle. |
| S8 Ensemble direct | Son écart au taux de base est publié à chaque bilan, sans décision attachée. Section 8.4. |
| S9 Contrôle par échantillon | Supprimé de la section 6.1. La section 13 garde la limite : aucun juge hors famille. La variante proposée (jugements d'ordre par Nathan) n'est pas retenue pour l'instant. |
| S10 Gel | Règle élargie : pendant le gel, une version n'est possible que pour corriger un défaut relevé en relecture, ou pour retirer une exigence devenue inexécutable, sur décision humaine journalisée. Tout ajout est exclu. Section 12. |

## Sur la remarque finale de la relecture 6

Le critère d'arrêt mesure la stabilité du texte face à un relecteur de la même famille, dans une même session, et non sa validité. La validité se jugera sur les résolutions (section 13). Cette lecture est la nôtre aussi.
