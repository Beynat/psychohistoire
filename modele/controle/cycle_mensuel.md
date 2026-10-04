# Procédure du cycle mensuel — phase 1

Exécutée le 1er de chaque mois par la tâche planifiée du cycle mensuel (noyau, section 12). La tâche se déclenche chaque jour du 1er au 7 : si le cycle du mois est complet (lignes « ensemble direct » d'origine « cycle AAAA-MM » au registre), elle s'arrête aussitôt ; sinon elle reprend à la première étape non faite (le gel n'est jamais refait). Au-delà du 7, le cycle est déclaré manqué au journal, sans prévision rétroactive (règle de rattrapage). Chaque étape est commitée et poussée avant la suivante ; l'ordre garantit que les prévisions sont postérieures au gel et antérieures à toute autre recherche (section 8.2).

**Préalable : statut du protocole.** Si `modele/statut.json` indique `"definitif": false`, s'arrêter : aucun cycle n'est exécuté avant la première version définitive (noyau, section 12). Le consigner au journal une seule fois par mois.

0. **Ajouts à la banque** (facultatif, noyau, section 8.8). Au plus cinq événements, ajoutés à `modele/banque/ajouts.jsonl` avec `ajoute_le`, critère, source, motif, nature et taux de base sur classe de référence historique (champ `taux_base_estime`, au format d'un fichier de groupe) ; puis `python scripts/evenements.py` et `python scripts/taux_base.py` (qui échoue si un taux manque), commit et poussée. Jamais après le gel.
1. **Gel.** `python scripts/geler.py AAAA-MM-JJ AAAA-MM`, où AAAA-MM-JJ est la date réelle du jour d'exécution (relecture 8, G2), puis commit et poussée du dossier `data/cycles/AAAA-MM/gel/`.
1 bis. **Événements déjà survenus ou constatés.** Avant de générer les questions, deux agents distincts vérifient, pour chaque événement de `modele/evenements.json` encore ouvert, s'il s'est déjà produit au regard de son critère ; pour un événement de nature « constat » seulement, si le constat est déjà publié, y compris quand l'issue est négative ; un événement « survenue » ne reçoit jamais de « non » avant son échéance (le script l'ignorerait) (Marine Le Pen absente de la liste officielle, par exemple). La date du fait est alors la date de publication. Chaque constat, quelle que soit l'issue, est ajouté comme proposition (`registre/propositions.jsonl`), avec la date du fait (`date_fait`), puis `python scripts/resolution.py` le résout. La question n'est alors pas émise (section 8.2).
2. **Questions.** `python scripts/questions.py AAAA-MM-JJ AAAA-MM`, puis commit et poussée de `questions.json`.
3. **Comparateurs.** `python scripts/comparateurs.py AAAA-MM`, puis commit et poussée du registre.
4. **Ensemble direct.**
   - Préparer le fichier remis aux prévisionnistes : `python scripts/dossier.py AAAA-MM /tmp/previsionnistes.json` (questions et dossier de données gelées, rien d'autre).
   - Lancer cinq prévisionnistes indépendants, sur au moins trois modèles, avec `modele/consigne_ensemble.md` (v1.3 : dossier de données, au moins 10 recherches web déclarées, consacrées aux événements, issues imposées) et ce seul fichier.
   - Chacun écrit `<racine absolue du dépôt>/data/cycles/AAAA-MM/ensemble/<identifiant>.json` : le chemin absolu est donné dans le message de lancement.
   - Dès qu'un fichier est rendu : `python scripts/verifier_reponse.py AAAA-MM <fichier>`. S'il n'est pas conforme, le prévisionniste est relancé une seule fois avec la liste des défauts ; un second échec est consigné au journal et le cycle passe sans ensemble direct.
   - Lire les motifs : un seuil signalé comme décalé ou une question signalée comme déjà résolue est consigné pour le cycle suivant. Une question sur laquelle les prévisionnistes divergent de plus de 40 points est signalée comme critère possiblement ambigu (relecture 8, G3) et réexaminée avant le cycle suivant.
   - Puis `python scripts/ensemble.py AAAA-MM`, et commit et poussée dans l'heure (contrôle d'horodatage).
5. **Résolution.**
   - Pour chaque question d'événement dont l'échéance est passée, deux agents distincts cherchent la source de résolution prévue par le critère (noyau, section 8.8) et ajoutent une proposition avec la date du fait ; un agent qui ne trouve pas la source l'écrit par une proposition sans issue (`issue: null`), qui consigne la recherche (`registre/propositions.jsonl`, via `scripts/registre.py`).
   - Puis `python scripts/resolution.py`.
6. **Notation.** `python scripts/notation.py`, puis commit et poussée du bilan.
7. **Journal.** Une ligne dans `modele/journal.md` si un passage a été manqué ou rattrapé (règle de rattrapage, section 12).

En cas d'échec d'une étape : ne pas passer à la suivante, consigner l'échec au journal, reprendre au passage suivant sans prévision rétroactive.
