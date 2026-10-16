# Consigne d'élicitation (lot L8, ronde 2)

Même cadre et mêmes règles que /tmp/claude-0/elic16/consigne.md (avec ID = {ID}). Tu peux lire en plus ta réponse de ronde 1 (/tmp/claude-0/elic16/{ID}_ronde1.json) et ton retour (/tmp/claude-0/elic16/retour_{ID}.json : défauts, marginales, sens opposés, réponses anonymisées des deux autres évaluateurs).

Corrige tout défaut. Révise un cas seulement si un argument ou un fait t'y conduit, sinon maintiens-le ; ne converge pas par principe. Écris ta réponse finale dans /tmp/claude-0/elic16/{ID}.json (justification révisée commençant par « ronde 2 : »), vérifie le JSON, et termine par trois lignes au plus sur ce que tu as changé et pourquoi.

Précision : les marginales signalées sont calculées par le réseau avec tes lois et les tables actuelles des autres nœuds.

Le retour est volumineux (environ 900 ko : les sens opposés sont listés cas par cas pour VE-SOND et PV-DUEL). Explore-le avec python3 plutôt que de le lire d'un bloc : commence par « defauts », « marginales », les trois cas les plus fréquents de chaque nœud (« noeuds »), puis regroupe les « sens_opposes » par nœud et par issue pour voir sur quels mouvements tu t'écartes des deux autres. Un sens opposé n'est pas un défaut : maintiens ta loi si tu as une raison, et écris-la.
EV-23 passe par une table de mesure élicitée dans un autre lot : un écart de marginale sur EV-23 ne se corrige pas en modifiant tes lois de nœuds.
