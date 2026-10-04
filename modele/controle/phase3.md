# Liste de contrôle — phase 3 (au plus tard P + 2 mois)

Ouverte le 4 octobre 2026 à partir de la relecture 7. À compléter avant le démarrage de la phase 3.

- [ ] `scripts/jalons.py` : écriture des définitions de jalons dans `modele/jalons/definitions.jsonl`, avec `defini_le` fixé par l'horloge système (annexe, section 10.7).
- [ ] `scripts/fantome.py` : calcul hebdomadaire du registre fantôme (annexe, section 10.6).
- [ ] `scripts/direction.py` : statistique Z par grappes, avec la loi de Student sous 15 grappes (annexe, section 10.11).
- [ ] Script du réseau : à chaque cycle, écrire au registre la marginale du réseau entièrement non calé avant toute sortie calée (noyau, section 4.5 ; relecture de suivi 16).
- [ ] Notation : une question d'un événement du périmètre sans prévision du modèle est notée sur le taux de base (noyau, section 8.6, « Périmètre »).
- [ ] Copie aveugle du dépôt pour les évaluateurs et l'opérateur, sans les chemins listés au noyau (section 8.6, « Aveuglement »), et contrôle de leurs adresses consultées.

## À reporter à la prochaine version du noyau

- Annexe, sections 10.4 et 10.11 : la statistique Z et le facteur k mesurent p et d « à la clôture de la question », ce qui sélectionne la prévision selon l'issue, comme le critère de calibration avant la v1.22. Les mesurer sur une prévision choisie indépendamment de l'issue (par exemple la première après l'activation de la couche) avant le démarrage de la phase 3 (relecture 17, souhaitable 1).

- Mentionner au premier bilan la légère prudence de la loi de Student sur Z avec peu de grappes (7 % au lieu de 10 % à 5 grappes).
