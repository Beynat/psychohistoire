# Consigne d'élicitation (lois par cas, ronde 1)

Tu es évaluateur indépendant pour un réseau de prévision sur la France (octobre 2026 à septembre 2028). Nous sommes le 10 octobre 2026.

Fichiers :
- gabarit à remplir : /tmp/claude-0/elic4/gabarit.json (lis-le en entier, y compris « lecture », « observations » et les définitions de chaque nœud) ;
- ta réponse : /tmp/claude-0/elic4/{ID}.json, même structure que le gabarit, avec « evaluateur » = "{ID}" et « date » renseignée.

Règles strictes :
- Ne lis aucun autre fichier : ni le dépôt /home/claude/psychohistoire, ni les autres réponses de /tmp/claude-0/elic4/. Aucune prévision existante ne doit t'influencer.
- Recherche sur le web les faits utiles (calendrier budgétaire, état de l'Assemblée, précédents de censure et de dissolution, mouvements lycéens, notation, procédure de déficit excessif), avec des sources de rang élevé (sources officielles, agences, quotidiens nationaux). N'utilise pas de marchés de prédiction ni de sites de paris.
- Pour chaque cas : une loi complète (fractions de somme 1 ; pour un pivot « à tout moment », la seule clé « oui ») et une justification d'au moins une phrase, avec une URL ou une référence précise, ou « jugement : » suivi du raisonnement. Tu peux regrouper des cas par jokers (voir « lecture »).
- Raisonne en probabilités conditionnelles en clair : « si tel cas vaut, quelle est la probabilité de... ». Pas de multiplicateurs.
- Remplis « direct » : ta probabilité pour chaque question, jugée directement, en fraction (0-1) pour une question oui/non.
- Vérifie la cohérence : les cas les plus fréquents (« poids_reseau ») doivent, pondérés, donner à peu près ton avis direct. Corrige ce qui ne l'est pas.
- Écris un JSON valide. Termine par un résumé de cinq lignes au plus de tes choix principaux.
