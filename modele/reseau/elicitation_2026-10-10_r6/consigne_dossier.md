# Consigne : dossier de faits pour une élicitation (lot {LOT})

Tu prépares le dossier de faits remis à trois évaluateurs indépendants qui vont fixer les tables de probabilités d'un réseau de prévision sur la France (octobre 2026 à septembre 2028). Nous sommes le 10 octobre 2026. Tu ne donnes AUCUNE probabilité ni aucun avis sur ce qui va arriver : seulement des faits datés et sourcés, des précédents et des taux de base historiques (fréquences observées, avec leur classe de référence et leur décompte).

Nœuds du lot (définitions, états, parents) : /tmp/claude-0/elic11/noeuds_{LOT}.json. Le dossier doit couvrir, pour chaque nœud, ce qui sert à juger la loi de ses états selon l'état de ses parents : situation actuelle, calendrier, acteurs et positions déclarées, précédents comparables, taux de base.

Tu peux lire, dans le dépôt /home/claude/psychohistoire : modele/sources.md (méthode de fiabilité des sources, à appliquer), modele/sources.json, modele/reseau/dossiers/ (dossiers existants à reprendre et mettre à jour plutôt qu'à refaire : {BASE}), modele/reseau/calendrier.json, data/etat/ (séries observées). Tu ne lis RIEN d'autre du dépôt : ni modele/reseau/tables_v0.json, ni registre/, ni data/cycles/, ni modele/reseau/elicitation*, ni modele/reseau/rapports/, ni modele/reseau/sensibilite.json.

Recherche sur le web (au plus 25 recherches ; pas de marchés de prédiction ni de sites de paris). Chaque fait chiffré ou daté porte sa source (URL, date de publication) et son rang (PO, I, MR, S, W, ME, MEE, PP selon modele/sources.md) ; un fait appuyé seulement par S, W, ME, MEE ou PP est marqué « non vérifié ». Une source n'est primaire que pour ses propres actes. Pas de faits de vie privée.

Écris le dossier en Markdown dans /tmp/claude-0/elic11/dossier_{LOT}.md : titre « Dossier de faits : <thème> (état au 10 octobre 2026) », une section par nœud ou groupe de nœuds, une section finale « Incertitudes et points non trouvés ». Style factuel, phrases courtes, pas de prévision. Termine par un résumé de cinq lignes au plus.
