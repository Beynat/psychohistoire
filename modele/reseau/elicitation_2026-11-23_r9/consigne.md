# Consigne d'élicitation (lot L9 : persistance de VE-SOND, ronde 1)

Tu es évaluateur indépendant pour un réseau de prévision sur la France (octobre 2026 à septembre 2028). Nous sommes le 23 novembre 2026.

Fichiers :
- dossier de faits sourcés : /tmp/elic23/dossier_L9.md (lis-le en entier ; c'est ta base) ;
- gabarit à remplir, à lire en entier (« lecture », « observations », définition, parents et leurs états) : /tmp/elic23/gabarit_cas.json. Un seul nœud : VE-SOND (deuxième place derrière le RN dans les intentions de vote : centre, serré, gauche, droite). Réponse dans /tmp/elic23/{ID}.json, même structure, « evaluateur » = "{ID}", « date » renseignée.

Points d'attention :
- VE-SOND est une variable mensuelle : chaque loi est celle du mois SUIVANT sachant l'état du mois précédent (« prec ») et les parents. Le réseau enchaîne ces lois de mois en mois jusqu'au premier tour (18 avril 2027) : juge la persistance d'un mois sur l'autre ET celle qu'elle implique à quatre ou cinq mois, en la comparant aux taux de base du dossier (section 2).
- Un parent daté pas encore tranché (PV-BLOC le 26 mars 2027, PV-SOUTIEN le 31 janvier 2027) est moyenné par le réseau sous sa loi a priori tant qu'il n'est pas connu : ta loi pour « PV-BLOC=les deux » doit valoir pour un mois où l'on sait (ou où les sondages testent surtout) cette configuration.
- Jokers vivement conseillés (192 cas) : regroupe les cas qui ont la même loi.

Règles strictes :
- Ne lis aucun autre fichier : ni le dépôt /home/claude/psychohistoire, ni les autres fichiers de /tmp/elic23/. Fichiers de travail dans /tmp/elic23/travail_{ID}/ seulement.
- Recherches web permises (au plus dix ; sources officielles, instituts, agences, quotidiens nationaux). Pas de marchés de prédiction ni de sites de paris.
- Lois par cas : loi complète (fractions de somme 1), justification d'au moins une phrase (section du dossier, URL, ou « jugement : … »). Jokers permis (voir « lecture »). Pas de multiplicateurs.
- Remplis « direct » : ta probabilité pour chaque question indiquée (EV-40b, EV-40c, EV-40f : qualification de Philippe, de Mélenchon, de Glucksmann au second tour), jugée directement (fraction 0-1).
- Vérifie la cohérence : avec tes lois, les cas les plus fréquents (« poids_reseau ») doivent rester plausibles au regard de ton avis direct ; le contrôle automatique compare la marginale impliquée par tes lois (avec la table actuelle du duel) à ton avis direct.
- Écris un JSON valide, vérifie-le avec python3 -c "import json;json.load(open('<fichier>'))", et termine par un résumé de cinq lignes au plus.
