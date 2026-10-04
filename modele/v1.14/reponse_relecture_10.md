# Réponse à la relecture 10

Noyau v1.14 ; annexe v1.3 ; banque `modele/banque/criteres.json` v1.2. Registre du protocole vide.

Deux changements faits entre la relecture 10 et cette réponse, hors relecture, sont soumis en même temps (section 4).

## 1. Défauts importants

**I1. Sélection par l'issue dans le test.** Corrigé selon les trois points proposés.
- **a.** À la date du test, une question n'entre que si son échéance est passée, quelle que soit son issue (`scripts/notation.py`, noyau section 8.5). Une question de fenêtre résolue « oui » avant son échéance attend son échéance ; les grappes à fenêtre longue comptent d'ici là par leurs seules questions mensuelles.
- **b.** Le score testé est le Brier pondéré dans le temps, pour toutes les questions (section 8.5). Il est déjà arrêté la veille du fait.
- **c.** La date du fait d'un « non » n'est la fin de la fenêtre que pour un événement « survenue ». Pour un « constat », c'est la date de publication, quelle que soit l'issue (`scripts/resolution.py`, section 8.8). L'étape 1 bis couvre les constats négatifs déjà publiés (`modele/controle/cycle_mensuel.md`).

**I2. Puissance surestimée.** Corrigé.
- `scripts/puissance.py` génère les questions avec `scripts/questions.py` à chaque cycle de janvier à la butée. Le compte est donc celui de la banque (EV-16a et EV-42 sans questions mensuelles excédentaires). Seules les questions échues à la butée sont gardées.
- Chaque question a un écart δ·4p(1 − p) et un écart-type σ·√(4p(1 − p)), où p est son taux de base sur sa fenêtre (échelle 1 pour une question à plusieurs issues).
- Résultat au 30 septembre 2027, P2b seul : 19 grappes, 90 questions dont 12 informatives ; puissance de 20 à 24 % pour un écart de 0,02 et de 37 à 43 % pour 0,04, ce qui confirme votre recalcul. Avec 15 grappes de P2c : 36 à 44 % et 74 à 82 %. Au 30 septembre 2028 : 23 à 30 % et 43 à 58 % pour P2b seul.
- Le paragraphe « Calendrier attendu » est réécrit avec ces chiffres.
- **Règle de verdict (section 8.6).** Trois verdicts, au seuil unilatéral de 10 % dans chaque sens : la phase 3 fait mieux, elle fait moins bien, ou le verdict est non concluant. Le non-concluant est publié comme tel, avec la puissance, et n'est pas présenté comme un résultat négatif. La règle de décision par défaut est assumée : retour à la phase 2 pour la suite (section 13). `scripts/notation.py` donne les deux valeurs p et le verdict.

**I3. Contrôle de la banque.** Corrigé. `scripts/controle_banque.py` fige aussi `source_accessible`, `mensuelle` et `source_resolution`. Il compare chaque événement à sa valeur au premier gel où il apparaît, et non plus au dernier. Testé sur deux gels simulés : un retrait par `source_accessible` introduit avant le second gel est détecté contre le premier. Section 12 mise à jour.

## 2. Souhaitables

- **S1.** EV-09 est scindé en EV-09a (été 2027) et EV-09b (été 2028), qui forment deux grappes. Taux de base : 50 % chacun, la même classe ramenée à un été (`modele/taux_base/groupe_relecture_r10.json`).
- **S2.** EV-C2 : « territoire situé outre-mer ». EV-32 : les contrôles « entrent en application » pendant la fenêtre et « s'appliquent aux exportations vers l'UE », sans exiger d'annonce.
- **S3.** La limite est écrite en 8.4.
- **S4.** Gardé tel quel : EV-C3a se clôt avant la phase 3 et n'entre pas dans le test de 8.6. La dépendance est mentionnée ici.
- **S5.** `scripts/comparateurs.py` lit les taux de base gelés avec le cycle. `scripts/controle_banque.py` vérifie l'empreinte de chaque fichier gelé contre son manifeste.
- **S6.** Pris en compte dans I2 : les grappes peu informatives sont désormais pesées par leur échelle dans la simulation.

## 3. Taux de base

Inchangés en dehors d'EV-09a et b. Les biais connus d'EV-41 (indépendance) et d'EV-20 (« pas d'arrêt ») seront rappelés au bilan.

## 4. Changements hors relecture, soumis en même temps

- **Gel (noyau v1.13, décision de Nathan).** Le protocole n'est gelé qu'à partir de sa première version définitive : la première qui satisfait le critère d'arrêt, déclarée dans `modele/statut.json`. Aucun cycle de la piste protocole n'a lieu avant elle ; le premier cycle est décalé au mois suivant si besoin. La tâche planifiée et la procédure du cycle vérifient ce statut en premier.
- **Faits d'actualité (annexe v1.2 et v1.3, demande de Nathan).**
  - Caractérisation de chaque fait rattaché (nature, stade, appui), transmise aux évaluateurs.
  - Une révélation de presse est une allégation, quel que soit le média.
  - Mesure descriptive de reprise (`data/reprise.json`), qui fixe la date de réexamen sans entrer dans les probabilités.
  - Règle de réexamen et d'abandon d'un fait en observation.
  - Définition de l'étape officielle.
  - Veille élargie à Le Figaro, Libération et Mediapart.
  - En phase 1, la caractérisation et la reprise sont descriptives seulement.
