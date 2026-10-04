# Réponse à la relecture de suivi 14

Noyau v1.18 ; annexe v1.7. Registre du protocole vide. La relecture 14 est une relecture de suivi : elle ne compte pas pour le critère d'arrêt, qui reste à zéro.

## Souhaitables

**N1. Correction de S1.** Les deux cas sont corrigés dans `resolution.py` et testés.
- **Réouverture.** Pour chaque question rouverte par erratum, le script retient la date du dernier erratum de réouverture et ignore toute proposition émise à cette date ou avant. Votre essai (deux « oui » erronés sur Q-EV-15, erratum `rouverte`, nouveau passage) laisse désormais la question ouverte ; une nouvelle proposition postérieure la résout normalement.
- **« Non » prématuré.** Le script compare l'échéance à la date d'émission de la proposition, non à la date du passage. Deux « non » émis en novembre 2026 sur un événement « survenue » restent ignorés après l'échéance ; seule une recherche faite après l'échéance peut conclure « non ».
- **Tests.** `test_regles_de_resolution` couvre la réouverture (question laissée ouverte, puis résolue par une proposition postérieure), le « non » prématuré relu après l'échéance, et l'annulation à 30 jours (votre réserve sur S4).
- **Texte.** Section 8.8 : « les propositions émises avant lui ne comptent plus » ; « Une proposition « non » émise avant l'échéance d'un événement « survenue » est ignorée, même après l'échéance ». Étape 1 bis alignée.

**N2. Suivi et compteur.** Section 12 : « Un défaut bloquant ou important relevé par une relecture de suivi est corrigé, puis relu par la relecture de validation suivante, qui seule fait foi pour le compteur. »

**N3. Rédaction.**
- Annexe 11.2 : la phrase sur les faux négatifs est replacée sous « Contrôle du tri ».
- Étape 1 bis : l'exemple suit le constat négatif ; la phrase sur les événements « survenue » vient après, avec la date du fait à sa place.
- Section 12 : ponctuation corrigée.

**N4. Contrôle du journal.** Assumé et compensé : le workflow de collecte vérifie lui-même, avant sa poussée, que `data/premieres_valeurs.jsonl` n'est modifié que par ajout, et échoue sinon. Le contrôle des registres reste en place pour les modifications manuelles. Section 8.8 : « contrôlé dans le workflow de collecte lui-même, dont les poussées ne déclenchent pas le contrôle des registres ».

## Réserves

- **S5, fait public non vérifié.** `tri.py` applique désormais la table 11.3 aux faits publics non vérifiés comme aux mises en cause : à la date de réexamen, prolongation si la reprise se maintient, « retombé » sinon.
- **S7, persistance.** `data/puissance.json` publie la puissance du critère de persistance sur P2a : p minimale du test exact selon le nombre de grappes (0,25 ; 0,125 ; 0,0625 pour 2, 3, 4). Au seuil de 10 %, le rejet est impossible avec trois grappes, possible avec quatre seulement si les quatre écarts ont le même signe. Le texte renvoie à ce fichier.

## Vérifications

`tests.py` : huit tests conformes. `controle_banque.py` : conforme. `puissance.json` régénéré depuis le code.
