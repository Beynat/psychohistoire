# Consigne d'élicitation (tables de mesure, lot L6, ronde {RONDE})

Tu es évaluateur indépendant pour un réseau de prévision sur la France (octobre 2026 à septembre 2028). Nous sommes le 10 octobre 2026.

Une table de mesure relie l'état de nœuds du réseau à une question de la banque. Exemple : « si la mobilisation sociale du mois est forte, probabilité qu'une journée de grève dépasse 18 % dans la fonction publique de l'État ». Tu donnes ces probabilités conditionnelles, entrée par entrée.

Fichiers :
- gabarit : /tmp/claude-0/elic11/gabarit_L6.json (lis-le en entier : critère et fenêtre de chaque question, nœuds lus, entrées à remplir, entrées fixes déjà déterminées par le critère) ;
- dossiers de faits sourcés (lis les sections utiles) : /tmp/claude-0/elic11/dossier_L1.md (mobilisations : EV-13, EV-51), dossier_L2.md (gouvernement : EV-49), dossier_L3.md (pourvoi : EV-20), dossier_L4.md (candidats, vainqueur : EV-05, EV-45), dossier_L5.md (majorité, dissolution : EV-17, EV-43) ;
- ta réponse : /tmp/claude-0/elic11/{ID}.json, même structure que le gabarit, avec « evaluateur » = "{ID}", « date » renseignée, chaque « table » remplie (pourcentage de 0 à 100, ou loi en % de somme 100) et chaque « justifications » remplie (au moins une phrase : section du dossier, URL, ou « jugement : … »).
{RONDE2}
Règles strictes :
- Ne lis aucun autre fichier : ni le dépôt /home/claude/psychohistoire, ni les autres fichiers de /tmp/claude-0/elic11/. Fichiers de travail éventuels dans /tmp/claude-0/elic11/travail_{ID}/ seulement.
- Recherches web permises (au plus dix ; sources officielles, instituts, agences, quotidiens nationaux ; par exemple programmes des candidats sur l'âge de départ, taux de grévistes historiques de la fonction publique d'État, interpellations lors de journées de mobilisation). Pas de marchés de prédiction ni de sites de paris.
- Remplis « direct » : ta probabilité pour chaque question, jugée directement (fraction 0-1, ou loi pour EV-05 et EV-20).
- Écris un JSON valide, vérifie-le avec python3 -c "import json;json.load(open('/tmp/claude-0/elic11/{ID}.json'))", et termine par un résumé de cinq lignes au plus.
