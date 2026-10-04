# Relecture de validation 15 — noyau v1.18, annexe phase 3 v1.7

Relecteur : Claude Opus 5.5, session neuve, sans accès aux échanges de rédaction (relectures précédentes non lues). Date : 4 octobre 2026. Objet relu : tags `protocole-v1.18` et `annexe-phase3-v1.7` (commit 2de1b04), banque v1.4, `sources.md` v1.1, consigne v1.4, procédures de `modele/controle/`, `scripts/`, `.github/workflows/`.

## Verdict

Aucun défaut bloquant. Trois défauts importants (I1 à I3) : la relecture ne remplit donc pas le critère d'arrêt. Quatorze souhaitables.

Sur le fond de la question 1 : le protocole peut conclure ce qu'il annonce, au sens où il l'annonce. Le dispositif d'antériorité (gel, registre horodaté par script, banque figée et contrôlée, instantanés mensuels, période commune, questions échues quelle que soit l'issue, test par grappes) est cohérent et correctement scripté pour le test de valeur ajoutée. La puissance est faible et le texte le dit honnêtement : sur P2b seul, 16 à 19 % pour un écart de Brier de 0,02, 26 à 32 % pour 0,04 ; le verdict le plus probable est « non concluant », et la règle par défaut est assumée. Les défauts relevés portent sur le critère de calibration (biais de sélection), sur l'usage des cotes par le modèle (biais possible en sa faveur dans le test principal) et sur la couverture de la gouvernabilité.

## Vérifications effectuées

- `python scripts/tests.py` : 8 tests passés. `python scripts/controle_banque.py` : banque conforme.
- Test exact par permutation des signes contre seuil de Student, sur les 14 grappes réelles de P2b au 30 septembre 2027 (3 000 tirages, mêmes hypothèses que `puissance.py`) : taux de rejet sous δ = 0 de 0,098 (exact) et 0,091 (Student) ; 0,178 et 0,166 pour δ = 0,02 ; 0,274 et 0,246 pour 0,04. L'affirmation de 8.5 (« mêmes résultats ») tient, le test exact étant un peu plus puissant ; les puissances publiées sont donc légèrement prudentes.
- Répartition du poids informatif (somme des échelles 4p(1 − p)) par grappe de P2b au 30 septembre 2027 : la grappe « présidentielle 2027, premier tour » porte 9,0 sur 17,3, soit 52 %, et 10 des 12 questions informatives. Le test de 2027 repose donc pour moitié sur une seule grappe (voir S2).
- Mutation du contrôle de la banque après un gel réel simulé : une modification du critère est détectée, celle du nom de l'événement ne l'est pas (S7).
- Démonstration de I1 sur une copie du dépôt (ci-dessous).
- Prémisses de critères vérifiées sur sources : 326 actes antimusulmans en 2025, bilan du ministère de l'Intérieur publié le 12 février 2026 (EV-35) ; arrêt de la cour d'appel de Paris du 7 juillet 2026 et pourvoi annoncé par Marine Le Pen (EV-20) ; vote des adhérents des Écologistes du 10 au 13 décembre 2026 entre candidature autonome et soutien externe (EV-18) ; suspension de la réforme de 2023 limitée aux générations 1964 à 1968 (EV-45).

## Défauts importants

### I1. Critère de calibration : sélection des issues « oui » précoces (méthode et code)

**Constat.** Le critère de calibration (8.6) porte sur « les questions binaires de P2b et P2c, prévisions de cycle ». Dans `notation.py`, la liste `cal` retient toute question résolue, sans le filtre d'échéance appliqué au test de valeur ajoutée (`comparer`). Au 30 septembre 2027, une question de fenêtre longue (échéance 2028-09-30) entre dans la mesure si l'événement est survenu, et n'y entre pas s'il ne l'est pas encore. C'est exactement le biais que 8.5 écarte pour le score testé (« seules les survenues seraient notées »), mais 8.5 ne vise que le Brier pondéré : le texte ne couvre pas la calibration, et le code ne la protège pas.

**Démonstration.** Copie du dépôt, banque du cycle 2026-11 : 13 questions de fenêtre P2b à échéance 2028-09-30 (EV-01, EV-04, EV-07, EV-08, EV-16b, EV-17, EV-C1, EV-C2, EV-C3b, EV-39, EV-29, EV-43, EV-45), toutes prévues à 20 %. Trois résolues « oui » le 15 mars 2027, les dix autres encore ouvertes. `bilan(..., '2027-09-30')` : la calibration retient 3 questions, les trois « oui ».

**Effet.** Les fréquences observées par classe sont gonflées vers 1 : le critère tend à conclure à une sous-confiance qui n'existe pas, et déclenche une recalibration logistique appliquée aux prévisions suivantes. Les événements rares à fenêtre longue (EV-07, EV-C2, EV-29) pèsent le plus : quand ils surviennent, ils entrent seuls.

**Correction proposée.** Texte, 8.6, critère de calibration : « sur les questions binaires de P2b et P2c dont l'échéance est passée à la date du test, quelle que soit leur issue (section 8.5), dernière prévision de cycle ; avec et sans les questions ajoutées ». Code : ajouter `qs[qid]["echeance"] <= aujourdhui` au filtre de `cal`, et calculer la calibration sur les deux ensembles (avec et sans ajouts), comme les autres critères. Ajouter un test discriminant (le cas ci-dessus doit donner 0 question retenue).

### I2. Cotes et « marginale non calée » : le modèle peut utiliser une information interdite à l'ensemble (méthode)

**Constat.** 4.5 et 8.3 notent une question de P2b sur « sa marginale non calée, enregistrée avant calage ». Le texte ne dit pas si c'est la marginale du réseau sans aucun calage, ou celle du nœud avant son propre calage, les autres nœuds étant calés. Dans le second cas, un nœud de P2b dont un parent est calé sur une cote reçoit l'information du marché par propagation. De même, 7.4 fait examiner tout écart de plus de 15 points à une référence externe avant publication : si la table est retouchée après cet examen, la cote entre dans le modèle avant tout calage. Or l'ensemble direct n'a pas le droit de consulter les marchés (consigne v1.4). Le paragraphe « Limite connue (questions cotées) » de 8.6, qui conclut qu'une question cotée « ne favorise aucun des deux », n'est vrai que pour le nœud coté lui-même.

**Effet.** Biais en faveur du modèle dans le test de valeur ajoutée, attribué à tort à la structure, c'est-à-dire dans le sens contraire de la règle par défaut. Son ampleur dépend des nœuds calés (le relevé Polymarket compte 232 marchés France, dont la présidentielle, le maintien du Premier ministre, le budget, la convocation d'élections) et n'est pas connue avant la construction du réseau : c'est la raison de la fixer maintenant.

**Correction proposée.** 4.5 : « Les prévisions notées en P2b et P2c sont celles du réseau entièrement non calé : aucun nœud calé, aucune ligne de table modifiée à la suite d'une comparaison à une cote. Elles sont enregistrées à chaque cycle avant tout calage ; les sorties calées sont publiées à part. » 7.4 : préciser que l'écart à une cote est consigné et justifié, sans retouche de la table utilisée pour la notation.

### I3. Gouvernabilité non couverte après 2026 (fond)

**Constat.** La gouvernabilité est l'une des cinq cibles (5.2 : « probabilité de chute du gouvernement ou de dissolution à 12 mois »), et 5.3 exige qu'elle soit couverte par au moins un nœud. Dans la banque, la chute du gouvernement n'est mesurée que par EV-15 (censure avant le 31 décembre 2026). De janvier 2027 à septembre 2028, soit 21 des 23 mois de l'horizon, seule la dissolution (EV-16a, EV-16b) est suivie. Les périodes les plus exposées ne le sont pas : de janvier à mai 2027 (exécution d'un budget contesté, campagne) et après les législatives éventuelles de 2027 (Assemblée sans majorité). Le marché « Lecornu out as French PM » du relevé Polymarket montre que la question est jugée pertinente à l'extérieur.

**Effet.** Un nœud central du réseau de la phase 3 (« séquence politique et budgétaire ») n'aurait aucune question notée au-delà de 2026, alors qu'il serait parmi les plus informatifs du test de 2027 (probabilité intermédiaire, donc échelle 4p(1 − p) élevée). Ajoutée plus tard comme « ajout », la question serait analysée à part (bilan avec et sans ajouts) et pourrait rendre le verdict non concluant par divergence.

**Correction proposée.** Avant le premier gel, dans `criteres.json` (et non dans `ajouts.jsonl`) : deux sous-questions de censure, sur le modèle d'EV-15 et d'EV-16 — « L'Assemblée nationale adopte une motion de censure contre le gouvernement (article 49, alinéa 2 ou 3, de la Constitution) entre le 1er janvier 2027 et le 2 mai 2027 », puis « entre le 3 mai 2027 et le 30 septembre 2028 » ; nature « survenue », questions mensuelles, source Assemblée nationale (scrutins). La censure est préférable à la démission du Premier ministre, qui obligerait à exclure les démissions d'usage après la présidentielle et les législatives. Taux de base sur classe de référence (motions adoptées depuis 1958, puis depuis 2022), et puissance recalculée.

## Souhaitables

**S1. Fuite par la recherche web de l'ensemble.** Le dépôt et la page sont publics et contiendront les probabilités du modèle ; la consigne interdit de les consulter, mais rien ne le contrôle. Demander dans le fichier de réponse la liste des adresses consultées (ce que `sources.md` prévoit déjà) et faire refuser par `verifier_reponse.py` toute adresse du dépôt ou de la page. La contamination rapprocherait l'ensemble du modèle, donc pousserait vers « non concluant » : sens prudent, d'où le classement.

**S2. Procédure de la phase 3, à écrire avant son démarrage.** (a) Ordre et aveuglement : les évaluateurs et l'opérateur du réseau ne voient pas les prévisions de l'ensemble sur les questions ouvertes, symétriquement à l'interdit fait à l'ensemble. (b) Périmètre : une question prévue une fois par le modèle reste dans le test même si son nœud sort du réseau (c'est déjà le cas, par report, pour les questions de fenêtre ; les questions mensuelles futures d'un nœud retiré, elles, disparaissent du test, ce qui laisse au modèle le choix de ses questions). (c) Publier avec le verdict une analyse en retirant chaque grappe tour à tour, au minimum la grappe de la présidentielle, qui porte 52 % du poids informatif.

**S3. Critère de persistance : qui est « le modèle » dans le code.** `notation.py` compare la persistance et le taux de base à la référence, l'ensemble direct par défaut. Pour juger le modèle, il faut lancer `--reference modèle`, ce qui inverse aussi le sens du test de valeur ajoutée. Prévoir un mode « bilan 8.6 » qui calcule les trois critères pour le modèle en une fois. Mentionner la multiplicité (deux pools, deux ensembles de questions) dans la phrase sur la preuve faible.

**S4. Calibration : définition de la mesure.** Écrire « dernière prévision de cycle avant résolution » (c'est ce que fait le code) au lieu de « prévisions de cycle ». Le calcul avec et sans ajouts manque (voir I1).

**S5. Ancrage quotidien de l'écart de taux et du Brent.** Le pas de la marche aléatoire est compté en mois entre le mois de la dernière observation quotidienne et le mois cible ; à l'horizon 1, on applique la dispersion d'une variation de moyennes mensuelles (de l'ordre de 2N/3 en variance pour une marche aléatoire) à l'écart entre un point quotidien et la moyenne du mois suivant (de l'ordre de N/3). Le comparateur de persistance est alors trop large, d'environ √2 en écart-type à l'horizon 1, ce qui facilite le critère de persistance sur P2a. Estimer la distribution sur la série quotidienne (point du jour J → moyenne du mois cible), ou documenter l'approximation.

**S6. Section 8.2 pour les séries.** Une question de variable n'est écartée que si la valeur est déjà dans la série collectée. Si la collecte a échoué quelques jours autour d'une publication (les étapes sont en `continue-on-error`), une question peut être émise alors que sa valeur est publique, et l'ensemble, qui cherche sur le web, peut la trouver. Faire inscrire par `geler.py` la date de dernière collecte réussie de chaque série et faire refuser par `questions.py` une série non collectée depuis plus de trois jours.

**S7. Champs figés.** `controle_banque.py` ne fige pas `nom` ni `sous_question`, qui entrent dans le texte remis aux prévisionnistes. Les ajouter à `CHAMPS` (et à la liste du noyau, section 12).

**S8. Section 8.7 : coupure des modèles.** Écrire la conséquence du sondage : si la coupure vérifiée d'un évaluateur est postérieure au 1er juillet 2026, les questions résolues avant cette coupure sont écartées pour tous.

**S9. Section 8.8 : deux règles d'annulation à 30 jours.** « Cas ambigu » annule si la source primaire manque 30 jours après l'échéance ; « Délais » exige pour cela deux recherches vaines consignées. Aligner le premier sur le second.

**S10. Grappes à fenêtres emboîtées.** EV-C3a (accord avant fin 2026) implique EV-C3b (accord avant septembre 2028) : ce sont deux grappes alors que les issues sont liées. Règle : fenêtres disjointes, grappes distinctes ; fenêtres emboîtées, même grappe. Sans effet sur le test de 2027 (EV-C3a échoit avant la phase 3).

**S11. Précisions de critères.**
- EV-19 : depuis la scission de 2022, deux organisations se réclament du NPA (NPA-l'Anticapitaliste, NPA-Révolutionnaires). Nommer celle(s) qui comptent ; une unité d'écart change l'issue.
- EV-20 : si le parquet général s'est aussi pourvu, l'arrêt peut statuer sur plusieurs pourvois. Écrire « dispositif de l'arrêt de la Cour de cassation statuant sur le pourvoi de Marine Le Pen ; une cassation, même obtenue sur un autre pourvoi, est rangée en « cassation totale ou partielle » ».
- EV-07 : les communiqués officiels donnent rarement la durée d'interruption ; admettre la durée établie par le communiqué de l'opérateur concerné ou par deux agences.
- EV-08 : préciser qu'une mise en garde sur un risque pour l'élection ne suffit pas ; il faut une campagne attribuée et visant l'élection.
- EV-38 : AGSI+ révise ses données ; fixer la date de lecture (valeur affichée le 3 février 2027, par exemple).
- EV-42 : préciser si le superéthanol E85 entre dans « les essences ».
- EV-13 : fixer la date de lecture de « la dernière valeur publiée » (par exemple 30 jours après la journée).
- EV-45 : préciser « version en vigueur le 30 septembre 2028 » (une disposition votée à effet différé ne compte pas).

**S12. Couverture, hors gouvernabilité.** (a) P2e : trois des quatre indicateurs internationaux échoient au plus tard le 30 juin 2027, l'Ukraine le 30 septembre 2027 ; de mi-2027 à septembre 2028, plus aucun indicateur. Prévoir une seconde série pour la seconde moitié de l'horizon. (b) La BCE est un bloc partiellement endogène (section 1) sans aucune question notée : une question « activation de l'instrument de protection de la transmission en faveur de la France » (source BCE, survenue) donnerait une prise. (c) Nouvelle-Calédonie : EV-C2 ne couvre que l'ordre public, pas l'issue institutionnelle ; à examiner si une consultation reste au calendrier. Le reste de la France est bien couvert : finances publiques (note, procédure de déficit, lois de finances, déficits 2027 et 2028), présidentielle (candidatures, qualifications, participation), société, sécurité, énergie.

**S13. Documents de contrôle périmés.** `controle/phase1.md` donne une puissance de 17 à 19 % et 26 à 35 % (noyau : 16 à 19 %, 26 à 32 %) ; `controle/cycle_mensuel.md`, étape 4, cite la consigne v1.3 (en vigueur : v1.4, qui interdit les marchés).

**S14. Texte des questions mensuelles.** Elles portent sur la période du gel à la fin du mois, alors que le texte dit « au cours du mois ». Sans effet grâce à l'étape 1 bis, mais à aligner.

## Non vérifié

- Réglages GitHub (rulesets sur `main` et les tags, secret `WEBSTAT_KEY`) et exécution réelle des workflows : lus, pas observés en fonctionnement.
- Existence et réglage des tâches planifiées (tri, cycle mensuel).
- Scripts de collecte (`collecte/*.py`) au-delà de la règle du Brent mensuel et du seuil de fiabilité des cotes ; exactitude des séries historiques.
- Contenu et qualité des taux de base (`modele/taux_base/`), classement `sources.json`, correspondance exacte des marchés Polymarket cités en `reference_externe`.
- Balayage v1, analyses d'octobre 2026, page publiée, interface.
- Éléments de la phase 3 non encore écrits (jalons, registre fantôme, statistique Z, test du jugement passé) : jugés sur le texte seulement.
- Relectures précédentes et leurs réponses : non lues, conformément à la demande.