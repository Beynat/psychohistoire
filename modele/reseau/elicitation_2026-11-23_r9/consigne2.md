# Consigne d'élicitation (lot L9, ronde 2)

Même cadre et mêmes règles que /tmp/elic23/consigne.md (avec ID = {ID}). Tu peux lire en plus ta réponse de ronde 1 (/tmp/elic23/{ID}_ronde1.json) et ton retour (/tmp/elic23/retour_{ID}.json : défauts, marginales, sens opposés, réponses anonymisées des deux autres évaluateurs).

Corrige tout défaut. Révise un cas seulement si un argument ou un fait t'y conduit, sinon maintiens-le ; ne converge pas par principe. Écris ta réponse finale dans /tmp/elic23/{ID}.json (justification révisée commençant par « ronde 2 : »), vérifie le JSON, et termine par trois lignes au plus sur ce que tu as changé et pourquoi.

Précision sur les marginales signalées (EV-40c et EV-40f) : elles sont calculées par le réseau avec tes lois et la table actuelle du duel (PV-DUEL), que ce lot ne réélicite pas. Les trois évaluateurs ont le même écart (Mélenchon environ 30 % contre 45 à 48 % d'avis direct ; Glucksmann environ 23 % contre 7 à 10 %) : il vient de la manière dont la table du duel répartit la qualification entre candidats de gauche quand VE-SOND vaut « gauche », pas de tes lois de VE-SOND. Ne modifie pas tes lois pour réduire cet écart ; garde tes avis directs tels que tu les juges.

Explore le retour avec python3 plutôt que de le lire d'un bloc : « defauts », « marginales », les trois cas les plus fréquents (« noeuds »), puis les « sens_opposes » regroupés par issue. Un sens opposé n'est pas un défaut : maintiens ta loi si tu as une raison, et écris-la.
