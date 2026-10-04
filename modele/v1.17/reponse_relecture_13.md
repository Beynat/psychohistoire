# Réponse à la relecture 13

Noyau v1.17 ; annexe v1.6 ; consigne de l'ensemble v1.4. Registre du protocole vide.

**Changement de règle (décision de Nathan, section 12).** Les relectures sont désormais de deux sortes :
- **Relecture de suivi** : dans la session courante du relecteur, elle ne vérifie que les corrections et ne compte pas pour le critère d'arrêt.
- **Relecture de validation** : complète, en session neuve. Seules les relectures de validation comptent pour le critère d'arrêt.

## 1. Défaut important

**L1. Première valeur collectée.** Corrigé, sans changement de méthode.
- **Brent.** `collecte/historique.py` n'écrit un mois de `brent_mensuel` qu'une fois complet, c'est-à-dire quand une cotation du mois suivant est présente. Septembre 2026 n'est donc plus dans la série au 4 octobre.
- **Journal.** `scripts/premieres_valeurs.py`, lancé par la collecte nocturne, inscrit en ajout seul dans `data/premieres_valeurs.jsonl` chaque période qui apparaît pour la première fois, pour chaque variable (série, période, valeur, date de collecte). Le fichier est sous le contrôle d'ajout seul.
- **Résolution.** `resolution.py` résout une question de variable sur ce journal, et prend la date de collecte comme date du fait. Sans entrée au journal, la question reste ouverte.
- **Test.** `test_regles_de_resolution` reprend votre scénario : valeur collectée à 3,4, puis révisée à 3,3 dans la série, puis résolution. L'issue suit la première valeur (« oui », date du fait celle de la collecte).
- **Texte.** La section 8.8 nomme le journal et la règle des mois complets.

## 2. Souhaitables

- **S1. « Non » prématuré.**
  - `resolution.py` ignore une proposition « non » sur un événement « survenue » avant son échéance (testé).
  - Un erratum avec `"rouverte": true` rouvre une question close à tort ; `questions.py` et `tri.py` lisent les résolutions avec les errata appliqués.
  - L'étape 1 bis réserve le constat négatif aux événements « constat ».
- **S2. Critère de calibration.** La mesure est le terme de fiabilité de Murphy en dix classes, sur les questions binaires de P2b et P2c, prévisions de cycle.
  - Référence : la loi sous calibration parfaite, simulée avec les mêmes grappes (copule gaussienne, ρ = 0,3).
  - Seuil : 90e centile.
  - Recalibration : régression logistique en log-cotes estimée sur les questions résolues.
  - Écrit en 8.6 et scripté (`notation.test_calibration`, publié par auteur dans le bilan). Vérifié : un jeu calibré est jugé conforme, un jeu dont les probabilités sont multipliées par 1,8 déclenche la recalibration.
- **S3.** `acte`, `evenement`, `taux_base_mode` et `reference_externe` sont ajoutés aux champs figés (`controle_banque.py`) et à la liste de la section 12.
- **S4. Tests.** Deux tests discriminants sont ajoutés :
  - `test_regles_de_resolution` : un avis par agent et par passage, « non » prématuré, annulation à 60 jours, absence d'annulation sans recherche, première valeur collectée ;
  - `test_regles_du_bilan` : cycles d'essai exclus, instantanés mensuels, grappe par acte.

  Contrôle par mutation : retirer le dédoublonnage ou les instantanés fait désormais échouer un test.
- **S5. Tri.**
  - Les natures « décision ou déclaration publique » et « autre » sont des faits publics. Les deux axes (étapes judiciaires, vérification d'un fait public) sont distincts, donc indépendants de l'ordre de lecture.
  - Un fait public non vérifié est contesté : il va en observation et suit la table de réexamen.
  - `fait` et `motif` sont écrits en termes neutres, sans qualification ni nom de personne (annexe 11.2, procédure de tri).
  - Le contrôle trimestriel porte sur le type et le rattachement, seuls conservés.
- **S6.** Le dédoublonnage se fait par agent et par passage (jour de la proposition) : votre scénario sur deux ans aboutit à une résolution par troisième avis.
- **S7. Puissance.**
  - Le texte dit que les chiffres sont des bornes hautes : couverture partielle de P2b par le modèle, grappes de P2c probablement liées à la présidentielle.
  - Il dit aussi que le critère de persistance sur P2a ne peut presque pas rejeter, et annonce un bilan final descriptif au 30 septembre 2028.
  - `data/puissance.json` est régénéré depuis le code, et les chiffres du texte en sont repris : 16 à 19 % et 26 à 32 % pour P2b seul.
- **S8.** La consigne v1.4 interdit aux prévisionnistes les marchés et agrégateurs de prévisions, et les articles qui en rapportent les cotes. La limite résiduelle (fuite dans la presse) est écrite en 8.6.
- **S9.**
  - Verdict combiné : non concluant si les bilans avec et sans ajouts diffèrent (`verdict_8_6`).
  - Le double calcul est fait aussi pour le taux de base sur P2b.
  - Sur P2a, il n'y a pas d'ajout possible, les ajouts étant des événements.
- **S10.**
  - Section 4.5 précisée : une question déjà émise dans un autre pool y reste.
  - En-tête de 8.6 : pools indiqués pour chaque critère.
  - Section 8.5 : arrêt la veille du fait quand il survient au plus tard à l'échéance, ce qui aligne le texte sur le script.
  - Diebold et Mariano retirés des références.
  - Historique des versions de l'en-tête renvoyé au journal.
- **S11.**
  - Brier sommé sur les issues de la question et sur l'issue réalisée.
  - `questions.py` lit `correspondances_p1.json` dans le gel.
  - `geler.py` refuse une date qui n'est pas celle du jour pour un cycle réel (option `--essai` pour les essais).
  - Plancher d'EV-05 : à rappeler au bilan de P1.
- **S12.** `phase1.md`, `phase3.md`, `README.md` et les docstrings sont à jour. La case du rattrapage reste ouverte : c'est une condition de la phase 1, à remplir avant le premier cycle.
- **S13.** L'annulation à 30 jours exige que deux agents aient consigné une recherche vaine (proposition sans issue). Celle à 60 jours exige au moins un avis ou une recherche. Sans aucune recherche, la question reste ouverte et est signalée (testé).
