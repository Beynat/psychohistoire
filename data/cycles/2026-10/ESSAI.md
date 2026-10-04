# Cycle à blanc

Ce dossier est un essai de la chaîne complète sur la piste exploratoire (4 octobre 2026), avant le premier cycle réel du 1er novembre. Ses prévisions vont dans registre/essai.jsonl et ne comptent pas au registre du protocole.

## Bilan du cycle à blanc

**La chaîne complète a fonctionné.** Elle a enchaîné le gel (14 fichiers), la génération de 57 questions en 32 grappes, les comparateurs (114 lignes), cinq prévisionnistes indépendants sur trois modèles, l'agrégation (342 lignes) et le contrôle d'horodatage à la poussée. La notation a été vérifiée sur une copie jetable du dépôt, avec des résolutions fictives : scores par pool, décomposition de Murphy et tests par grappes s'exécutent sans erreur.

**Coût mesuré.** Les cinq prévisionnistes ont consommé environ 600 000 jetons au total, soit de 100 000 à 145 000 chacun, en 30 secondes à 4 minutes. Le reste de la chaîne est scripté, sans IA.

**Problèmes trouvés et corrections**

| Problème | Correction |
| --- | --- |
| Deux prévisionnistes sur cinq ont très peu cherché (0 et 3 recherches web). L'un a déduit ses probabilités de la structure des seuils. | Consigne v1.1 : au moins 10 recherches, déclarées dans le fichier et vérifiées par `scripts/ensemble.py`. Un prévisionniste en dessous est relancé. |
| Les seuils de l'écart de taux sont calés sur la dernière moyenne mensuelle publiée par la BCE (août, 82 pb). L'écart quotidien dépassait 100 pb fin septembre : les cinq prévisionnistes le signalent et répondent « oui » à 74-97 %. | Le texte de chaque question donne désormais la dernière valeur publiée et sa période. La vraie correction est une série quotidienne de l'OAT, accessible par l'API Webstat de la Banque de France (gratuite, sur compte). |
| La question sur l'extension du mouvement lycéen était déjà probablement résolue avant le gel : des universités étaient bloquées dès le 1er octobre. | Nouvelle étape 1 bis du cycle : deux agents vérifient avant chaque gel si un événement ouvert s'est déjà produit. La résolution est alors prononcée avant émission (`scripts/resolution.py`). |
| La question mensuelle sur l'élection d'un président sans majorité absolue n'a pas de sens : ce critère se juge à l'issue de législatives. | Pas de question mensuelle pour cet événement (`scripts/evenements.py`). |

Les prévisions de ce cycle sont dans `registre/essai.jsonl`. Elles ne comptent pas.

**Mise à jour du 4 octobre 2026.** Le problème de l'écart de taux est résolu. L'OAT quotidienne est désormais collectée par Webstat, et les seuils partent du dernier niveau quotidien corrigé du décalage avec la série BCE. Dans un test pour un gel au 1er novembre, le seuil médian de novembre passe de 82 à 118 pb.
