Bonjour,

Merci pour la relecture 17. Voici les corrections. Je vous demande une **relecture de suivi**, dans votre session actuelle : elle porte seulement sur la vérification des corrections et ne compte pas pour le critère d'arrêt (noyau, section 12). Une relecture de validation, en session neuve, suivra.

Dépôt : https://github.com/Beynat/psychohistoire, tags `protocole-v1.22` et `annexe-phase3-v1.7` (annexe inchangée). Banque v1.7, consigne v1.5. La réponse point par point est dans `modele/v1.22/reponse_relecture_17.md`.

Je vous demande :
1. Pour I1 à I6 et les souhaitables 1 à 10, dites si la correction est suffisante, insuffisante ou mal fondée, avec motif. Vous pouvez reprendre vos scripts d'essai : en particulier, refaites votre simulation de I1 sur le nouveau `brier_pondere` (signature `brier_pondere(lignes, issue, debut, echeance, date_fait)`) et celle de I2 sur la nouvelle sélection de la prévision de calibration. `python scripts/tests.py` et `python scripts/controle_banque.py` passent.
2. Signalez tout défaut que les corrections auraient introduit, classé selon la grille de la section 12. Ne refaites pas de relecture d'ensemble.

Merci.
