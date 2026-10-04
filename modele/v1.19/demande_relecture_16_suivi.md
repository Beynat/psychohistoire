Bonjour,

Merci pour la relecture 15. Voici les corrections. Je vous demande une **relecture de suivi**, dans votre session actuelle : elle porte seulement sur la vérification des corrections, et ne compte pas pour le critère d'arrêt (noyau, section 12). Une relecture de validation, en session neuve, suivra.

Dépôt : https://github.com/Beynat/psychohistoire, tags `protocole-v1.19` et `annexe-phase3-v1.7` (annexe inchangée). Banque v1.5, consigne de l'ensemble v1.5. La réponse point par point est dans `modele/v1.19/reponse_relecture_15.md`.

Je vous demande :
1. Pour I1 à I3 et S1 à S14, dites si la correction est suffisante, insuffisante ou mal fondée, avec motif. S12 (c), Nouvelle-Calédonie, est différé : dites si le motif vous paraît recevable. Vous pouvez exécuter `python scripts/tests.py` (deux nouveaux tests, et des cas ajoutés à `test_regles_du_bilan`) et `python scripts/controle_banque.py`.
2. Vérifiez en particulier les nouveaux événements (EV-15b, EV-15c, EV-46, EV-28b, EV-33b) : critères, fenêtres, grappes et taux de base (`modele/taux_base/groupe_relecture_r15.json`).
3. Signalez tout défaut que les corrections auraient introduit, classé en bloquant, important ou souhaitable. Ne refaites pas de relecture d'ensemble.

Merci.
