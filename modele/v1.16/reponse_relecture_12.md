# Réponse à la relecture 12

Noyau v1.16 ; annexe v1.5 ; banque v1.4. Registre du protocole vide. Choix de méthode pour K3 et K4 : options recommandées, sans préférence contraire de Nathan.

**Calendrier.** Le correcteur estime qu'un premier cycle au 1er novembre n'est plus possible. Ce n'est pas le cas : les relectures se font en quelques heures, et deux relectures propres d'ici fin octobre restent réalistes. Le risque d'un démarrage tardif est néanmoins écrit (S10).

## 1. Défauts importants

- **K1.** La section 8.5 définit désormais le score testé sur la période commune aux deux auteurs. Un test de bout en bout (`test_bout_en_bout`) passe par le chemin de `bilan` sur un cycle fictif : mêmes prévisions sur la période commune, écart nul.
- **K2.** `scripts/notation.py` calcule le test de la section 8.6 tel qu'il est écrit :
  - seules sont lues les banques des cycles présents dans le registre noté (`cycles_du_registre`), ce qui exclut les cycles d'essai du registre du protocole ;
  - critère de valeur ajoutée sur P2b et P2c seulement, avec et sans les ajouts ;
  - critère de persistance contre la persistance sur P2a et contre le taux de base sur P2b ;
  - un bilan descriptif sur toutes les questions.

  Le test de bout en bout vérifie qu'une question de P2e n'entre pas dans le critère, et que la question de fenêtre et ses mensuelles forment une seule grappe.
- **K3.** Option retenue : instantanés mensuels. Le test ne prend que les prévisions inscrites aux cycles (origine « cycle … ») ; l'apport des mises à jour continues est publié à part, sans décision (sections 8.5 et 8.6 ; `scripts/notation.py`).
- **K4.** Option retenue : une seule grappe pour les questions tranchées par la candidature et le premier tour de la présidentielle (EV-19, EV-20, EV-21, EV-23, EV-40, EV-41 ; champ `acte` de la banque). La puissance est recalculée et le texte précise qu'un verdict significatif reste une preuve faible.
- **K5.** Le stade ne s'applique qu'aux mises en cause. Un fait public d'une autre nature est établi quand deux agents l'ont vérifié sur une source de la section 8.8 (étape « fait public vérifié »), contesté sinon ; établi, il ne va pas en observation (annexe, section 11.2 ; `scripts/tri.py`).
- **K6.**
  - La caractérisation proposée par l'agent de tri n'est plus écrite dans le dépôt. Ne sont conservés que le type (mise en cause ou fait établi), les questions concernées et, pour une étape vérifiée, l'étape, sa source et la nature qu'elle établit (jamais « vie privée »).
  - `data/reprise.json` ne contient plus de caractérisation proposée.
  - `modele/interface/actualite.md` est aligné sur la section 11.6.
  - La correction a été poussée avant le premier passage planifié du tri.

## 2. Souhaitables

- **S1.** Le Brier est ½ Σ (p_k − y_k)², donc (p − y)² pour une question binaire. La convention est écrite en 8.5, avec l'unité des écarts de 8.6, et `notation.brier` est corrigé.
- **S2.** La section 8.5 décrit le test réellement utilisé : permutation des signes par grappe, Student pour la simulation.
- **S3.**
  - Les fichiers d'un cycle (questions et seuils compris) ne peuvent plus être modifiés ni supprimés une fois poussés (workflow).
  - Le pool d'une question est fixé à sa première émission ; une question de P2b calée en phase 3 reste dans P2b pour le test, sur sa marginale non calée (section 8.3).
  - Les taux de base sont figés au premier gel de chaque événement (`controle_banque.py`).
- **S4.**
  - Un ajout porte son taux de base (`taux_base_estime`), lu par `taux_base.py`, qui échoue si un taux manque. La procédure relance `taux_base.py` avant le gel.
  - `questions.py` lit la banque gelée avec le cycle, comme `comparateurs.py`.
  - L'ancien drapeau est renommé `taux_base_mode`.
- **S5.** Deux propositions ne valent deux avis que si elles viennent de deux agents distincts. Une question sans résolution concordante 60 jours après l'échéance est annulée. Les errata du registre des résolutions sont appliqués à la notation (`resolutions_effectives`).
- **S6.** Fait foi la première valeur collectée de la période ; sa date est la date du fait (section 8.8).
- **S7.** Les identifiants remis aux prévisionnistes sont anonymisés (`Q001`…). La correspondance est dans `data/cycles/<cycle>/anonymisation.json` et appliquée par `verifier_reponse.py` et `ensemble.py`.
- **S8.**
  - La décision de réexamen est prise une fois et inscrite en ajout seul (`data/tri/statuts.jsonl`).
  - Le stade n'est relevé que si deux agents ont vérifié la même étape.
  - Un fait retombé reste listé et clos.
  - L'« appel » et la création d'une commission d'enquête sont retirés des étapes officielles ; S4 de la relecture 11 est ainsi traité en entier.
  - Votre scénario (retombé, nouveaux titres, puis retombé de nouveau) reste « retombé » sur une simulation.
- **S9.**
  - EV-09a et EV-09b sont classés « survenue ».
  - La fenêtre d'EV-06 se clôt le 15 août 2028.
  - Une dépêche d'agence reprise intégralement et attribuée par un média de référence compte comme cette agence (section 8.8).
- **S10.**
  - Les grappes de P2c sont simulées pour des conjonctions à 10 %.
  - Au-delà d'un démarrage de la phase 3 au 1er avril 2027, le test de valeur ajoutée est déclaré non concluant d'avance (section 8.6).
  - La simulation des démarrages tardifs est publiée dans `data/puissance.json`.
- **S11.** La correction du biais commun est retirée (sections 8.4 et 12). L'écart au marché reste publié.
- **S12.** Annexe, section 10.1 : la loi a priori de M et les valeurs δ sont fixées à l'élicitation de la phase 3 et journalisées. La contrainte de centrage est écrite.
- **S13.**
  - La calibration est simulée avec les mêmes grappes.
  - L'échec méthodologique a une conséquence écrite.
  - Le centrage de Z est mentionné en 10.11, avec la publication de la calibration sans la couche.
- **S14.**
  - Le texte définitif est celui qu'a lu la seconde relecture propre, sans modification ultérieure (section 12).
  - La ligne de statut du noyau et l'en-tête de l'annexe renvoient à `statut.json`.
  - `statut.json`, `phase1.md`, `phase3.md` et `README.md` sont mis à jour.
- **S15.** Un test de bout en bout sur un cycle fictif couvre :
  - `geler.py`, `questions.py`, `comparateurs.py`, `resolution.py` et `notation.py` ;
  - la grappe unique, l'exclusion de P2e, la période commune et le refus des doublons d'agent.

## 3. Puissance actualisée

Pour P2b seul au 30 septembre 2027 : 14 grappes, 12 questions informatives, puissance de 17 à 19 % pour un écart de 0,02 et de 26 à 35 % pour 0,04. Avec 15 grappes de P2c à 10 % : 25 à 29 % et 47 à 59 %. Le test de valeur ajoutée est donc faible par construction, et le texte le dit.
