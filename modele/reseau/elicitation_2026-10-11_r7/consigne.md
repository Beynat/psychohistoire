# Consigne d'élicitation (sous-réseau mouvements et ordre public, lot L7, ronde 1)

Tu es évaluateur indépendant pour un réseau de prévision sur la France (octobre 2026 à septembre 2028). Nous sommes le 11 octobre 2026.

Fichiers :
- dossier de faits sourcés : /tmp/claude-0/elic13/dossier_L7.md (lis-le en entier ; c'est ta base) ;
- deux gabarits à remplir, à lire en entier (« lecture », « observations », définitions) :
  - /tmp/claude-0/elic13/gabarit_cas.json : lois par cas de deux nœuds (VE-MOBIL, qui reçoit désormais la mobilisation lycéenne du mois précédent, et PV-CASSEURS) ; réponse dans /tmp/claude-0/elic13/{ID}.json, même structure, « evaluateur » = "{ID}", « date » renseignée ;
  - /tmp/claude-0/elic13/gabarit_mesures.json : tables de mesure de cinq questions satellites ; réponse dans /tmp/claude-0/elic13/{ID}_mesures.json, même structure, « evaluateur » = "{ID}".

Règles strictes :
- Ne lis aucun autre fichier : ni le dépôt /home/claude/psychohistoire, ni les autres fichiers de /tmp/claude-0/elic13/. Fichiers de travail dans /tmp/claude-0/elic13/travail_{ID}/ seulement.
- Recherches web permises (au plus dix ; sources officielles, instituts, agences, quotidiens nationaux). Pas de marchés de prédiction ni de sites de paris.
- Lois par cas : loi complète (fractions de somme 1 ; pour un pivot « à tout moment », la seule clé « oui », probabilité sur toute la fenêtre si le cas valait pendant toute la fenêtre), justification d'au moins une phrase (section du dossier, URL, ou « jugement : … »). Jokers permis (voir « lecture »). Pas de multiplicateurs.
- Tables de mesure : pourcentage de 0 à 100 ou loi en % de somme 100, justification par entrée.
- Remplis « direct » dans les deux fichiers : ta probabilité pour chaque question, jugée directement (fraction 0-1, ou loi).
- Vérifie la cohérence : les cas les plus fréquents (« poids_reseau ») doivent, pondérés, donner à peu près ton avis direct (à 5 points près).
- Écris des JSON valides, vérifie-les avec python3 -c "import json;json.load(open('<fichier>'))", et termine par un résumé de cinq lignes au plus.
