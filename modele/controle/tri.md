# Procédure du tri de l'actualité — phases 1 et 2

Exécutée lundi, mercredi et vendredi par la tâche planifiée du tri (noyau, section 12 ; annexe, section 11.2). En phases 1 et 2, le tri ne sert qu'au cas « donnée » (noyau, section 8.9) : repérer un fait qui résout une question d'événement ouverte. Il ne juge aucune matérialité et ne modifie aucune probabilité.

1. **Titres à trier.** `python scripts/tri.py a-trier /tmp/tri.json`. Si aucun titre n'est à trier, s'arrêter sans commit.
2. **Tri.** Un sous-agent léger (modèle sonnet) lit `/tmp/tri.json` et rien d'autre du dépôt :
   - il regroupe les titres par fait, en supprimant les doublons ;
   - il rattache chaque fait à une question ouverte dont il pourrait remplir le critère, ou à « non rattaché » ;
   - il écrit une décision par titre, au format JSONL, dans `/tmp/decisions.jsonl` : `{"lien": …, "fait": "<identifiant court du fait>", "decision": "Q-EV-xx" | "non rattaché", "motif": "<une phrase>"}`.
   Puis `python scripts/tri.py ajouter < /tmp/decisions.jsonl`.
3. **Vérification des faits rattachés.** Pour chaque question à laquelle un fait est rattaché, deux sous-agents distincts (modèle sonnet), sans se consulter, cherchent la source primaire officielle (Journal officiel, Conseil constitutionnel, Assemblée nationale, Insee, agence de notation, etc.) et jugent si le critère de la question est rempli, au mot près. Un comptage produit par une partie prenante n'est jamais une donnée. Chacun ajoute une proposition par `scripts/registre.py registre/propositions.jsonl` (`proposition: true, question, issue, source, agent`) seulement s'il conclut que le critère est rempli, avec la date du fait dans la source.
4. **Résolution.** Si des propositions ont été ajoutées : `python scripts/resolution.py`.
5. **Commit et poussée** dans l'heure (contrôle d'horodatage), message « Tri du AAAA-MM-JJ ».
6. **Rattrapage.** Un titre non trié n'est jamais purgé : un passage manqué est rattrapé au suivant, et chaque fait garde sa date de source. Si le dernier passage date de plus de 7 jours, une ligne est ajoutée à `modele/journal.md` (passage manqué).

En cas d'échec d'une étape : ne pas passer à la suivante, ne rien forcer, consigner l'échec au journal.
