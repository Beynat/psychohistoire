# Réponse à la relecture 9

Noyau v1.12 ; annexe v1.1 inchangée ; banque `modele/banque/criteres.json` v1.1. Toutes les corrections sont faites avant le premier cycle (1er novembre 2026), registre du protocole vide.

## 1. Défauts importants

**H1. Taux de base des événements constatés à date fixe.** Corrigé. Chaque événement porte un champ `nature` : « survenue » (risque constant, taux ramené à la fenêtre restante) ou « constat » (pas de conversion). 26 événements sont de nature « constat », dont EV-17, EV-36, EV-40, EV-45. Règle inscrite au noyau (section 8.4), appliquée par `scripts/comparateurs.py`. Vérification sur une banque générée au 1er novembre : EV-40a reste à 30 %, EV-17 à 66,7 %, EV-36 à 73,3 %.

**H2. Seuil de 40 grappes.** Corrigé.
- Une grappe résolue est définie (section 8.3) : elle entre dans les tests dès qu'une de ses questions est résolue, avec la somme des écarts sur ses questions résolues.
- Deux sous-questions à fenêtres distinctes forment deux grappes (EV-16a et b, EV-C3a et b) ; la banque d'essai compte 51 grappes.
- La section 8.6 est évaluée au 30 septembre 2027, sans seuil de 40 grappes.
- `scripts/puissance.py` simule désormais la banque réelle, avec le nombre de questions de chaque grappe : 18 grappes de P2b au 30 septembre 2027 (97 questions), plus 0 à 15 grappes de P2c. Puissance pour un écart de Brier de 0,02 : 35 à 61 % ; pour 0,04 : 70 à 96 %.
- Repousser la butée au 30 septembre 2028 donnerait 39 à 65 % pour 0,02 : le gain est faible, la butée de 2027 est maintenue. Le paragraphe « Calendrier attendu » est réécrit avec ces chiffres.

**H3. Banque non protégée.** Corrigé. `scripts/controle_banque.py`, appelé par le workflow de contrôle des registres à chaque poussée touchant la banque, les cycles ou `evenements.json` :
- échoue si le critère, les issues, la fenêtre, la nature ou le pool d'un événement présent dans le dernier gel d'un cycle réel (à partir de 2026-11) a changé, ou s'il a disparu ;
- vérifie l'unicité des identifiants, la présence de `ajoute_le` et le plafond de cinq ajouts entre deux gels.
Testé sur un gel simulé, puis retiré. La section 12 dit que la banque est figée au premier gel.

**H4. Critères ambigus.** Corrigés (section 2).

## 2. Critères

| Critère | Correction |
| --- | --- |
| EV-C2 | « Département, région ou collectivité d'outre-mer, ou Nouvelle-Calédonie » ; couvre-feu général pour motif d'ordre public ; couvre-feu pour mineurs ou après un phénomène naturel exclu |
| EV-28 | Cessez-le-feu sans terme fixé ou d'au moins 30 jours, ou accord de paix ; trêve plus courte exclue |
| EV-42 | Tarif normal de l'accise sur le gazole routier ou les essences ; baisse limitée au gazole non routier ou à une profession exclue |
| EV-39 | Chiffre du ministère publié par lui ou rapporté par deux agences de presse |
| EV-36 | « Non » si aucun projet de loi de finances n'est déposé au 31 octobre 2027 |
| EV-43 | Renommé « Premier ministre issu d'un parti concurrent au premier tour » ; la coalition est dite incluse |
| EV-40 | Liste des deux candidats admis au second tour établie par le Conseil constitutionnel, retrait compris (article 7) ; élection au premier tour : « oui » pour l'élu seul |
| EV-08 | La publication doit désigner expressément l'élection de 2027 comme cible |
| EV-13 | Dernière valeur publiée par la DGAFP pour la journée |
| EV-23 | Taux proclamé par le Conseil constitutionnel |
| EV-17 | Parti dont le président élu est membre au jour du second tour |
| EV-20 | Issue « rejet ou non-admission » |
| EV-45 | Génération 1970, non concernée par la suspension : « oui » suppose un abaissement voté |
| EV-32 | Réécrit : entrée en application, pendant la fenêtre (jusqu'au 30 juin 2027), de contrôles chinois sur les terres rares ou aimants visant l'UE, nouveaux ou par fin de suspension ; une prolongation ne compte pas. L'issue n'est plus acquise par une prolongation de la trêve |

Issues possiblement acquises : EV-01, EV-08, EV-15 et EV-39 sont traités par l'étape 1 bis ; EV-32 est réécrit.

## 3. Taux de base

- **EV-45 et EV-32.** Réestimés pour les nouveaux critères (`modele/taux_base/groupe_relecture_r9.json`). EV-45 : 12,5 % (abaissement de l'âge légal par la loi ou une ordonnance dans les 17 mois qui suivent une présidentielle : 1 cas sur 8, l'ordonnance de 1982, cas discutable au sens strict ; fourchette 1,7 à 12,5 %). Service-public.fr confirme que la génération 1970 est à 64 ans. EV-32 : 33,3 % (contrôles chinois sur les matières critiques visant l'UE, par période de 9 mois depuis 2020 : 3 sur 9).
- **EV-41.** L'hypothèse d'indépendance reste écrite dans le fichier ; elle surestime « les deux ». Acceptée comme ligne de base naïve, à ne pas lire comme une prévision.
- **EV-20.** Même lecture : taux de base, pas prévision.
- **Entrées périmées.** `scripts/taux_base.py` retire désormais les événements retirés, non émis ou à taux uniforme (EV-05, EV-10), et échoue si les issues d'un taux de base diffèrent de celles de la banque. Ce contrôle a trouvé l'écart d'EV-20 (« rejet » contre « rejet ou non-admission »), corrigé dans le fichier du groupe avec motif.

## 4. Souhaitables

- **Date du fait pour « non ».** Fin de la fenêtre (noyau, section 8.8 ; `scripts/resolution.py`).
- **Brier pondéré.** Arrêté la veille de la date du fait (section 8.5 ; `scripts/notation.py`).
- **Ajouts.** Contrôlés par script (H3).
- **Section 12.** Banque figée au premier gel, écrit.
- **Indicateur des sources.** La sortie du script rappelle que la détection des sources non lues dépend des mentions du document.
- **Sources de résolution non classées.** Cour de cassation, Agence France Trésor : PO. Moody's, S&P Global Ratings, Fitch : PO pour leurs propres décisions de notation seulement. Polymarket : S, référence externe et non fait.
