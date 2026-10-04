# Relecture de suivi 15 — noyau v1.19, annexe phase 3 v1.7, banque v1.5, consigne v1.5

Relecteur : Claude Opus 5.5, session de la relecture de validation 15. Date : 4 octobre 2026. Objet : vérification des corrections (`modele/v1.19/reponse_relecture_15.md`, commit 7179303). Relecture de suivi : elle ne compte pas pour le critère d'arrêt (noyau, section 12). Pas de relecture d'ensemble.

## Verdict

Les trois défauts importants sont corrigés. Les corrections n'introduisent aucun défaut bloquant ni important. S5 est insuffisant sur un cas, l'horizon 1 quand l'ancrage tombe dans le mois du gel. Cinq souhaitables nouveaux portent sur les événements ajoutés et sur l'aveuglement de la phase 3. Deux d'entre eux (N1, N2) touchent des taux de base, qui sont figés au premier gel : il faut donc les traiter avant celui-ci.

## Vérifications effectuées

- `python scripts/tests.py` : 10 tests passés. `python scripts/controle_banque.py` : banque conforme.
- Lecture du diff de v1.18 à v1.19 : noyau, consigne, procédures, `notation.py`, `questions.py`, `commun.py`, `comparateurs.py`, `verifier_reponse.py`, `controle_banque.py`, `geler.py`, `collecte/historique.py` et `collecte/webstat.py`.
- Banque générée sur une copie, avec un gel fictif au 4 octobre 2026 : grappes d'EV-15, 15b, 15c, 16a, 16b, C3a-C3b, 28-28b et 33-33b ; horizons et pas des questions ancrées.
- Écart-type de la loi ancrée pour l'écart de taux, ancrage le 1er du mois : 5,7 pb pour un pas de 0, 8,7 pb pour 1 et 13,5 pb pour 2 (variations mensuelles : 8,1 pb).
- Poids informatif par grappe de P2b au 30 septembre 2027 (`puissance.questions_banque`). Concordance de `data/puissance.json` avec la section 8.6.

## Défauts importants

**I1. Calibration. Suffisant.** `notation.py` filtre les questions échues, comme `comparer`. La calibration est calculée avec et sans ajouts, avec un verdict combiné. Le texte de 8.6 est aligné. `test_calibration_questions_echues` reprend le cas de la relecture et donne 0 question retenue.

**I2. Marginale non calée. Suffisant pour le texte.** La section 4.5 définit les prévisions notées comme celles du réseau entièrement non calé, sans propagation ni retouche de table. Les sections 7.4, 8.3 et 8.6 (limite connue) sont cohérentes avec elle. Aucun code n'est exigible avant la phase 3. Il faudra que le script du réseau écrive au registre, à chaque cycle, la marginale non calée avant toute sortie calée. Je propose de l'ajouter à `controle/phase3.md`.

**I3. Gouvernabilité. Suffisant.** EV-15b et EV-15c sont dans `criteres.json`. Leurs critères, fenêtres et nature sont corrects. Ce sont des grappes distinctes d'EV-15, et la banque générée le confirme. Le choix de la censure plutôt que de la démission est le bon. Le taux de base d'EV-15c pose question (N1).

## Souhaitables de la relecture 15

| Point | Avis | Motif |
| --- | --- | --- |
| S1 | Suffisant | Champ `adresses` obligatoire ; dépôt, page et marchés rejetés ; testé. La limite déclarative est écrite en 8.6. Complément mineur : la consigne interdit aussi les « cotes de paris », que l'expression régulière ne couvre pas (Betfair, Oddschecker, Winamax, etc.), ni `api.github.com/repos/Beynat/psychohistoire`. |
| S2 | Suffisant, sauf (a) | (b) et (c) conviennent ; `sans_chaque_grappe` est produit par `comparer`. Pour (a), voir N3. |
| S3 | Suffisant | `bilan_8_6_modele` fixe le sens de chaque test et la lecture du verdict est juste dans les trois cas : valeur ajoutée, persistance et taux de base. Le cas « valeur ajoutée » est testé. La multiplicité est mentionnée. |
| S4 | Suffisant | Traité avec I1. |
| S5 | Insuffisant | Voir N4. |
| S6 | Suffisant | La date est écrite à chaque `ecrire` réussi, `_collecte.json` est gelé et le refus est testé. Effet de bord : les essais qui gèlent hors date réelle doivent réécrire `_collecte.json`. Les tests le font. `puissance.py` émet désormais ses banques simulées sans questions de variable, sans conséquence puisqu'il ne lit que P2b. |
| S7 | Suffisant | `nom` et `sous_question` sont figés, dans le code et à la section 12. |
| S8 | Suffisant | — |
| S9 | Suffisant | — |
| S10 | Suffisant | Composantes par chevauchement, testées : C3a et C3b forment une grappe, 16a et 16b deux. Les nouvelles sous-questions (15b, 15c, 28b, 33b) ont des fenêtres disjointes de leur aînée et forment des grappes séparées, conformément à la règle. |
| S11 | Suffisant | Les huit critères sont précisés comme proposé. |
| S12 (a) | Suffisant | Report de la Chine et des États-Unis recevable : P2e est hors des critères de 8.6. Pour EV-28b, voir N5. |
| S12 (b) | Suffisant sur le principe | EV-46 est bien formé. Pour son taux de base, voir N2. |
| S12 (c) | Motif recevable, argument à corriger | Le report est acceptable. En revanche, « aucun critère ne peut être daté » n'est pas un vrai obstacle : un critère de fenêtre ne demande pas de date. Exemple : « une consultation des populations intéressées de Nouvelle-Calédonie ou l'élection des membres des assemblées de province a lieu avant le 30 septembre 2028 », résolu sur le Journal officiel. Le vrai motif est le risque qu'une réforme institutionnelle change l'objet de la consultation. Ajouté plus tard, l'événement passera par la procédure d'ajout et le double bilan avec et sans ajouts. C'est acceptable. |
| S13 | Suffisant | — |
| S14 | Suffisant | Testé. |

## Défauts introduits ou restants

Aucun bloquant, aucun important.

**N1. Taux de base d'EV-15c incohérent avec la banque (souhaitable, à traiter avant le premier gel).**
- **Le motif ne tient pas.** La classe retenue (Ve République, 4,1 %) l'est au motif que « la configuration de l'Assemblée après 2027 n'est pas connue ». Or la banque estime elle-même cette configuration : le taux de base d'EV-17 donne 66,7 % de chances que le groupe du président élu n'ait pas la majorité absolue. La classe retenue est dominée par des périodes à majorité absolue, ce qui contredit cette estimation.
- **Ce que donnerait un mélange.** Avec les deux classes déjà calculées : 0,667 × 28 % + 0,333 × environ 1 % ≈ 19 %. EV-17 mesure le groupe du président, pas l'absence de toute majorité, d'où une borne haute ; une pondération plus prudente ramène autour de 10 à 15 %.
- **Pourquoi c'est à faire maintenant.** Les taux de base sont figés au premier gel (`controle_banque.py`).
- **Correction proposée.** Retenir le mélange, avec ses poids déclarés dans le motif.

**N2. EV-46 : une seule classe de référence, et l'OMT oublié (souhaitable).**
- **(a) Seconde classe.** `phase1.md` admet l'exception, mais une seconde classe est disponible : interventions ciblées sur un grand État de la zone euro (Italie, Espagne, France) depuis 1999, soit 2 sur environ 3 × 27 États-années. Cela donne λ ≈ 0,025 par an et environ 5 % sur deux ans, au-dessus des 2,2 % retenus. Une note de l'Agence France Trésor ou de la BCE n'est pas nécessaire : les deux comptages sont publics.
- **(b) Critère.** Il exclut l'APP et le PEPP, mais ne dit rien de l'OMT, toujours ouvert à un État sous programme du MES. Écrire « TPI, ou opérations monétaires sur titres (OMT) en faveur de la France », ou exclure l'OMT expressément.
- **(c) Rédaction.** Le motif « ramenée à 2 % par la borne mécanique » est inexact : 2,2 % est au-dessus de la borne, qui ne s'applique pas.

**N3. Aveuglement de la phase 3 incomplet (souhaitable).** « Copie du dépôt dont les registres de prévisions sont retirés » ne suffit pas, pour trois raisons :
- les prévisions individuelles de l'ensemble sont aussi dans `data/cycles/*/ensemble/*.json` ;
- les bilans sont dans `data/bilans/`, et la page (`index.html`, `data.json`) peut les afficher ;
- le dépôt est public : un évaluateur doté de la recherche web peut le lire.

Correction : nommer les chemins retirés (`registre/`, `data/cycles/*/ensemble/`, `data/bilans/`, `data.json`) et interdire aux évaluateurs et à l'opérateur la consultation du dépôt public et de sa page, avec le même contrôle d'adresses que pour l'ensemble.

**N4. Ancrage quotidien : pas forcé à 1 quand la cible est le mois de l'ancrage (souhaitable).**
- **Le défaut.** `questions.py` calcule `pas = max(1, ecart_mois(dernier, cible))`. Quand le dernier point quotidien tombe dans le mois du gel, la question à horizon 1 (cible = ce mois) reçoit la loi « point du jour J → moyenne du mois suivant », au lieu de « point du jour J → moyenne du même mois ».
- **Constat sur la copie.** Avec un gel au 4 octobre 2026 et un ancrage au 1er octobre, les questions sur l'écart d'octobre et de novembre ont toutes deux un pas de 1. Elles ont donc la même loi, avec un écart-type de 8,7 pb, alors que la loi correcte pour octobre (pas 0) a un écart-type de 5,7 pb. Le comparateur de persistance est alors plus large qu'avant la correction (8,1 pb), ce qui va à l'inverse de S5.
- **Une erreur dans la réponse.** L'explication donnée (« le point de départ précède alors d'un mois et demi la moyenne visée ») décrit en réalité ce défaut.
- **Quand le cas se produit.** Lors d'un gel de rattrapage (du 2 au 7 du mois) dès que la série quotidienne a un point dans le mois. Un gel le 1er au matin n'est pas touché.
- **Correction.** Quand la question est ancrée, prendre `pas = ecart_mois(dernier, cible)` en autorisant 0 ; `variations_ancrees` gère déjà ce cas. Garder `max(1, …)` sans ancrage. Ajouter un test : un gel le 3 avec un point quotidien le 2 doit donner un pas de 0 à l'horizon 1.

**N5. Secondes périodes de P2e : sens conditionnel non écrit (souhaitable).**
- **Le problème.** Si EV-28 se résout « oui » (cessez-le-feu ou accord de paix avant le 30 septembre 2027), EV-28b demande une nouvelle annonce commune pendant la seconde période. Le taux de base repris (risque de fin de guerre, 20,5 %) n'a alors plus d'objet. Le fichier de taux le signale (« ne conditionne pas »), mais le critère ne dit pas comment lire la question dans ce cas. EV-33b pose la même question si une suspension partielle a déjà été décidée.
- **Correction.** Écrire dans le critère qu'une annonce faite pendant la première période et toujours en vigueur ne compte pas, et que seule une nouvelle annonce compte. Ou bien annuler EV-28b, avec motif, si EV-28 se résout « oui ». Pool descriptif, sans effet sur les verdicts.

**N6. Remarque sans défaut sur EV-15b.** La réponse dit avoir retenu la classe d'EV-15. Ce n'est pas le cas : EV-15 retient le taux des sessions budgétaires (une sur quatre), EV-15b le taux annuel (une sur 4,3 ans), qui inclut cette censure budgétaire alors que la fenêtre de janvier à mai ne contient pas de budget. 7,4 % reste défendable comme borne haute. Corriger le motif suffit.

## Non vérifié

- Exécution réelle de la collecte nocturne avec `_collecte.json` (écriture et commit par le workflow) : lu, pas observé.
- Exactitude des comptages historiques d'EV-15b, EV-15c, EV-46, EV-28b et EV-33b au-delà de leur cohérence interne.
- Phase 3 : aucun code (attendu).