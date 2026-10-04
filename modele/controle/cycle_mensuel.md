# Procédure du cycle mensuel — phase 1

Exécutée le 1er de chaque mois par la tâche planifiée du cycle mensuel (noyau, section 12). Chaque étape est commitée et poussée avant la suivante ; l'ordre garantit que les prévisions sont postérieures au gel et antérieures à toute autre recherche (section 8.2).

1. **Gel.** `python scripts/geler.py AAAA-MM-01`, puis commit et poussée du dossier `data/cycles/AAAA-MM/gel/`.
2. **Questions.** `python scripts/questions.py AAAA-MM-01`, puis commit et poussée de `questions.json`.
3. **Comparateurs.** `python scripts/comparateurs.py AAAA-MM`, puis commit et poussée du registre.
4. **Ensemble direct.**
   - Lancer cinq prévisionnistes indépendants, sur au moins trois modèles, avec `modele/consigne_ensemble.md` et la seule liste de questions.
   - Chacun écrit `data/cycles/AAAA-MM/ensemble/<identifiant>.json`.
   - Puis `python scripts/ensemble.py AAAA-MM`, et commit et poussée dans l'heure (contrôle d'horodatage).
5. **Résolution.**
   - Pour chaque question d'événement dont l'échéance est passée, deux agents distincts cherchent la source primaire et ajoutent une proposition (`registre/propositions.jsonl`, via `scripts/registre.py`).
   - Puis `python scripts/resolution.py`.
6. **Notation.** `python scripts/notation.py`, puis commit et poussée du bilan.
7. **Journal.** Une ligne dans `modele/journal.md` si un passage a été manqué ou rattrapé (règle de rattrapage, section 12).

En cas d'échec d'une étape : ne pas passer à la suivante, consigner l'échec au journal, reprendre au passage suivant sans prévision rétroactive.
