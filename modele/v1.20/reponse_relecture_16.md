# Réponse à la relecture de suivi 16

Noyau v1.20 ; annexe v1.7 (inchangée) ; banque v1.6 ; consigne v1.5. Registre du protocole vide. Le fichier de la relecture est intitulé « Relecture de suivi 15 » ; il est rangé sous son numéro d'ordre, 16 (`v1.20/relecture_16_suivi.md`).

La relecture 16 est une relecture de suivi et ne compte pas pour le critère d'arrêt, qui reste à zéro. Elle ne relève aucun défaut bloquant ni important. Tous les points sont traités avant le premier gel, y compris ceux qui touchent des taux de base.

## Points de la relecture 15

- **I2.** Votre proposition est reprise : `controle/phase3.md` exige que le script du réseau écrive au registre, à chaque cycle, la marginale du réseau entièrement non calé avant toute sortie calée. Les deux autres engagements de 8.6 y sont aussi inscrits, le périmètre noté sur le taux de base et la copie aveugle.
- **S1, complément.** L'expression régulière couvre aussi `api.github.com/repos/Beynat/psychohistoire` et les principaux sites de paris : Betfair, Oddschecker, Winamax, Betclic, Unibet, Parions Sport, ZEbet, Bet365, Paddy Power, William Hill et Smarkets. La liste reste indicative ; la consigne interdit toute cote de paris.
- **S12 (c).** Je retire l'argument « aucun critère ne peut être daté », qui était faux : un critère de fenêtre n'a pas besoin de date. Le motif du report est le risque qu'une réforme institutionnelle en cours change l'objet de la consultation ou le régime des élections provinciales. L'événement passera par la procédure d'ajout et le double bilan.
- **S5.** Mon explication sur l'écart de taux décrivait en effet le défaut N4, et non un effet voulu ; elle est corrigée ci-dessous.

## Défauts introduits ou restants

**N1. Taux de base d'EV-15c.** Corrigé. Une classe est ajoutée, celle des périodes à majorité absolue (1962-1988 et 1993-2022 : aucune censure adoptée, λ de Jeffreys, soit 1,3 %). Le taux retenu est le mélange des classes « sans majorité » (28,0 %) et « majorité absolue » (1,3 %), avec un poids déclaré de 0,5, ce qui donne **14,7 %**. Le poids est inférieur aux 66,7 % d'EV-17, qui ne mesure que le groupe présidentiel ; une coalition peut former une majorité. Des poids de 0,33 à 0,67 donneraient 10 à 19 %, ce qui est écrit.

**N2. EV-46.**
- (a) Une seconde classe est ajoutée : les trois grands États de la zone euro, avec deux interventions ciblées (Italie et Espagne, 2011) sur 83,25 États-années. Elle est retenue, à **4,7 %** ; la classe de tous les États membres (2,2 %) devient la borne basse.
- (b) Le critère inclut l'OMT, et le nom devient « Achats ciblés de la BCE (TPI ou OMT) pour la France ».
- (c) Le motif erroné sur la borne a disparu avec le changement de classe.

**N3. Aveuglement de la phase 3.** Section 8.6. Les chemins retirés de la copie sont nommés : `registre/`, `data/cycles/*/ensemble/`, `data/bilans/`, `data.json` et `index.html`. La consultation du dépôt public et de sa page est interdite aux évaluateurs et à l'opérateur. Leurs adresses consultées sont listées et contrôlées comme celles de l'ensemble.

**N4. Pas nul à l'ancrage.** Corrigé. Pour une question ancrée, `questions.py` prend `pas = ecart_mois(dernier, cible)`, qui peut être nul ; sans ancrage, le pas reste d'au moins un mois.
- **Test.** `test_ancrage_pas_nul` gèle au jour même du dernier point quotidien de l'écart de taux. La question du mois du gel doit avoir un pas nul, celle du mois suivant un pas de 1.
- **Contrôle par mutation.** Avec `max(1, …)` rétabli, le test échoue.

**N5. Secondes périodes de P2e.** Les critères d'EV-28b et EV-33b précisent que seule compte une annonce ou une décision faite pendant leur fenêtre. Un cessez-le-feu ou une suspension antérieurs, même toujours en vigueur, ne comptent pas. Une nouvelle décision qui étend une suspension compte.

**N6. Motif d'EV-15b.** Corrigé. La classe de l'Assemblée sans majorité est une borne haute : son taux annuel inclut la censure budgétaire de 2024, alors que la fenêtre ne contient pas de budget initial. EV-15 retient une autre classe, propre à sa fenêtre. La valeur reste 7,4 %.

## Effets sur la puissance

P2b au 30 septembre 2027 : 17 à 19 % pour un écart de Brier de 0,02, 27 à 37 % pour 0,04. Avec P2c : 25 à 32 % et 49 à 59 %. Bilan final de 2028 : 28 grappes, 27 questions informatives, car EV-15c devient informative à son nouveau taux de base. Le texte de 8.6 reprend ces chiffres.

## Vérifications

`tests.py` : onze tests conformes. `controle_banque.py` : conforme. `evenements.py`, `taux_base.py` et `puissance.py` relancés.
