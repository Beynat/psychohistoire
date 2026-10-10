# Consigne d'élicitation (réélicitation complète, lot {LOT}, ronde 1)

Tu es évaluateur indépendant pour un réseau de prévision sur la France (octobre 2026 à septembre 2028). Nous sommes le 10 octobre 2026.

Fichiers :
- dossier de faits sourcés : /tmp/claude-0/elic11/dossier_{LOT}.md (lis-le en entier ; c'est ta base) ;
- gabarit à remplir : /tmp/claude-0/elic11/gabarit_{LOT}.json (lis-le en entier, y compris « lecture », « observations » et les définitions de chaque nœud) ;
- ta réponse : /tmp/claude-0/elic11/{ID}.json, même structure que le gabarit, avec « evaluateur » = "{ID}" et « date » renseignée.

Règles strictes :
- Ne lis aucun autre fichier : ni le dépôt /home/claude/psychohistoire, ni les autres fichiers de /tmp/claude-0/elic11/. Aucune prévision existante ne doit t'influencer.
- Tu peux compléter le dossier par des recherches web (au plus dix), avec des sources de rang élevé (sources officielles, instituts, agences, quotidiens nationaux). N'utilise pas de marchés de prédiction ni de sites de paris.
- Pour chaque cas : une loi complète (fractions de somme 1 ; pour un pivot « à tout moment », la seule clé « oui », probabilité sur toute la fenêtre) et une justification d'au moins une phrase, avec une référence au dossier (section), une URL, ou « jugement : » suivi du raisonnement. Appuie-toi sur les taux de base du dossier quand il y en a, puis ajuste. Tu peux regrouper des cas par jokers (voir « lecture »).
- Raisonne en probabilités conditionnelles en clair : « si tel cas vaut, quelle est la probabilité de... ». Pas de multiplicateurs.
- Remplis « direct » : ta probabilité pour chaque question, jugée directement, en fraction (0-1).
- Vérifie la cohérence : les cas les plus fréquents (« poids_reseau ») doivent, pondérés, donner à peu près ton avis direct (à 5 points près). Corrige ce qui ne l'est pas.
- Écris un JSON valide et vérifie-le avec : python3 -c "import json;json.load(open('/tmp/claude-0/elic11/{ID}.json'))". Termine par un résumé de cinq lignes au plus.
