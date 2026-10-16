# Consigne d'élicitation (lot L8 : sondages et offre de gauche, ronde 1)

Tu es évaluateur indépendant pour un réseau de prévision sur la France (octobre 2026 à septembre 2028). Nous sommes le 16 octobre 2026.

Fichiers :
- dossier de faits sourcés : /tmp/claude-0/elic16/dossier_L8.md (lis-le en entier ; c'est ta base) ;
- gabarit à remplir, à lire en entier (« lecture », « observations », définitions, parents et leurs états) : /tmp/claude-0/elic16/gabarit_cas.json. Six nœuds : VE-SOND (deuxième place derrière le RN dans les sondages, avec l'état « serré »), PV-ECOLO, PV-SOUTIEN (nouveau : bénéficiaire du soutien des Écologistes), PV-BLOC, PV-GAUCHE, PV-DUEL. Réponse dans /tmp/claude-0/elic16/{ID}.json, même structure, « evaluateur » = "{ID}", « date » renseignée.

Points d'attention :
- VE-SOND est une variable mensuelle : chaque loi est celle du mois SUIVANT sachant l'état du mois précédent (« prec ») et les parents. Pense en persistance d'un mois sur l'autre et compare au taux de base du dossier (fréquence des changements de deuxième place et durée des coude-à-coude dans les cycles passés).
- Un parent daté pas encore tranché (PV-BLOC le 26 mars 2027, PV-SOUTIEN le 31 janvier 2027) est moyenné par le réseau sous sa loi a priori tant qu'il n'est pas connu : ta loi pour « PV-BLOC=les deux » doit valoir pour un mois où l'on sait (ou où les sondages testent surtout) cette configuration.
- PV-SOUTIEN : exclusions déjà appliquées par le réseau (pas de bénéficiaire si PV-ECOLO ≠ « soutien à un autre candidat » ; pas de « pas de soutien » si le soutien est voté). Donne tout de même une loi complète, avec 0 sur les issues exclues.
- PV-DUEL : le nouveau parent PV-SOUTIEN agit surtout sur la qualification à gauche (RN – Glucksmann contre RN – Mélenchon). Jokers vivement conseillés (128 cas) : regroupe les cas qui ont la même loi.

Règles strictes :
- Ne lis aucun autre fichier : ni le dépôt /home/claude/psychohistoire, ni les autres fichiers de /tmp/claude-0/elic16/. Fichiers de travail dans /tmp/claude-0/elic16/travail_{ID}/ seulement.
- Recherches web permises (au plus dix ; sources officielles, instituts, agences, quotidiens nationaux). Pas de marchés de prédiction ni de sites de paris.
- Lois par cas : loi complète (fractions de somme 1), justification d'au moins une phrase (section du dossier, URL, ou « jugement : … »). Jokers permis (voir « lecture »). Pas de multiplicateurs.
- Remplis « direct » : ta probabilité pour chaque question, jugée directement (fraction 0-1, ou loi).
- Vérifie la cohérence : les cas les plus fréquents (« poids_reseau ») doivent, pondérés, donner à peu près ton avis direct (à 5 points près).
- Écris un JSON valide, vérifie-le avec python3 -c "import json;json.load(open('<fichier>'))", et termine par un résumé de cinq lignes au plus.
