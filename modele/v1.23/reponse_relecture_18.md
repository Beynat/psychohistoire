# Réponse à la relecture de suivi 18

Noyau v1.23 ; annexe v1.7 (inchangée) ; banque v1.7. Registre du protocole vide.

La relecture 18 est une relecture de suivi et ne compte pas pour le critère d'arrêt, qui reste à zéro. Elle juge suffisantes les corrections de I1 à I6 et retire la remarque sur les agents. Elle relève un défaut important introduit par la règle de I1. Selon la section 12, ce défaut est corrigé ici, et la relecture de validation suivante le relira ; elle seule fait foi pour le compteur.

## Défaut important introduit

**Cycle manqué récompensé quand le fait survient.** Corrigé selon votre proposition.
- **Règle.** Si le fait survient dans la fenêtre, la dernière prévision qui le précède vaut jusqu'au 1er du mois qui suit le fait, c'est-à-dire jusqu'au cycle prévu suivant, et non plus un mois après sa propre émission. Un cycle manqué est ainsi couvert par la prévision précédente, comme sans fait.
- **Test.** `test_brier_pondere_propre` vérifie aussi qu'un auteur qui manque les cycles 4 et 6, avec des prévisions identiques, n'obtient pas un meilleur score que l'auteur complet.
- **Contrôle par mutation.** Avec l'ancienne règle (un mois après l'émission), le test échoue : 0,147 pour l'auteur incomplet contre 0,151 pour l'auteur complet.
- **Texte.** Section 8.5.

## Remarques

- **Taux de base extrêmes (I3).** Les deux taux à 100 % (EV-C3b, EV-C4) reçoivent l'estimateur lissé (k + ½)/(n + 1), soit 92,9 %. Aucun autre taux de base retenu n'est à 0 ou à 100 %.
- **Questions de variables.** Le facteur de pondération est mentionné en 8.5 : il ne dépend pas de l'issue et vaut pour les deux auteurs. Je ne le neutralise pas, pour garder une seule règle de score.

## Vérifications

`tests.py` : douze tests conformes. `controle_banque.py` : conforme. `taux_base.py` relancé.
