# Relecture de validation 21 — protocole v1.25, annexe v1.7

Relecteur : Claude (Opus 5.5), session neuve, sans accès aux échanges de rédaction. Date : 5 octobre 2026.
Objet relu : tag `protocole-v1.25` (commit 8cf999d, tête de `main`) ; tag `annexe-phase3-v1.7` (commit 2de1b04, texte de l'annexe identique à la tête). Les relectures précédentes n'ont pas été lues.

## Verdict

Un défaut bloquant, deux défauts importants, douze souhaitables. Le compteur du critère d'arrêt reste à zéro.

Les tests passent (`scripts/tests.py`, 15 tests) et `scripts/controle_banque.py` conclut « Banque conforme ». Les chiffres de puissance du noyau (section 8.6) correspondent à `data/puissance.json`.

## Défaut bloquant

### B1. Les errata sur les prévisions n'ont aucun effet sur la notation ; la règle « résolution antérieure à la poussée » n'est pas appliquée

Texte. Section 0 : une erreur se corrige par une ligne d'erratum. Section 12 : le contrôle des registres est détectif, « un échec est public et se corrige par une ligne d'erratum ». Section 8.8 : une prévision dont la question était déjà résolue à la date de poussée de sa ligne est annulée.

Code. `scripts/notation.py` lit toutes les lignes portant `probabilites` et ignore toute ligne d'erratum du registre des prévisions ; seul le registre des résolutions applique des errata (`resolution.resolutions_effectives`). Aucun format d'erratum de prévision n'est défini. La date de poussée n'est enregistrée nulle part : la notation ne connaît que `emise`, la date du fait et la date d'enregistrement de la résolution.

Scénario. Une ligne est écrite par `registre.py` le jour J (champ `emise` exact), puis la poussée échoue ou est différée ; le fait survient à J+1 ; la ligne, modifiable localement tant qu'elle n'est pas poussée, l'est à J+2. Le workflow signale l'horodatage hors fenêtre. La ligne d'erratum prescrite est écrite, mais la notation garde la prévision, puisque `emise` précède la date du fait. Essai sur une copie : une prévision du modèle à 95 % sur Q-EV-15, puis un erratum d'annulation, puis une résolution « oui » ; la prévision est notée (écart moyen 0,64 en faveur du modèle).

Classement. Atteinte à l'intégrité des registres : la seule correction prévue pour une anomalie détectée n'existe pas dans le code. Le défaut ne joue qu'après une poussée tardive, que le workflow détecte ; si la réponse le reclasse pour ce motif, elle doit au moins montrer que la correction est appliquée.

Correction proposée.
- Définir l'erratum de prévision : `{"erratum": true, "objet": {"question", "auteur", "emise"}, "correction": {"annulee": true}, "motif"}`, accepté par `registre.py`.
- L'appliquer dans `notation.py` avant tout calcul, pour tous les auteurs concernés, et le compter dans les exclusions publiées.
- Inscrire dans la procédure : tout échec d'horodatage du workflow donne lieu à un erratum d'annulation des lignes en cause.
- Test discriminant : la ligne annulée n'est plus notée ; contrôle par mutation (sans l'application de l'erratum, le test échoue).
- Reformuler la règle de la section 8.8 sur ce que le code peut vérifier : la date d'émission fait foi, sous réserve du contrôle de poussée ; une ligne poussée hors fenêtre est annulée par erratum.

## Défauts importants

### I1. Une seconde prévision de cycle d'un même auteur remplace la première selon l'issue

Code. `notation.comparer` garde toutes les lignes d'origine « cycle X » d'un auteur. La date de départ commune du cycle est calculée sur la dernière émission de chaque auteur (`d_s[c]`, qui écrase les précédentes), et toutes les lignes du cycle sont recalées à cette date : la dernière ligne remplace donc la première sur tout le cycle. Or une ligne émise le jour du fait ou après est exclue en amont. La ligne qui compte dépend ainsi de l'issue : si le fait survient avant la seconde ligne, la première compte ; sinon, la seconde. Rien n'interdit deux lignes de cycle par auteur, question et cycle : ni `registre.py`, ni le workflow, ni le texte de la section 8.5.

Scénario. En phase 3, l'étape du modèle est relancée en cours de mois (reprise après incident, dans la fenêtre de rattrapage ou au-delà) sur l'état courant du réseau, qui intègre les faits imprévus postérieurs au gel, au lieu de l'état au gel. Sur une question de fenêtre ou une question mensuelle d'événement rare, la seconde ligne est plus basse quand rien ne s'est produit. Elle compte seule quand l'issue est « non » ; elle est écartée quand le fait l'a précédée.

Essai sur une copie. 11 questions mensuelles de P2b, prévisions identiques des deux auteurs à 30 % (modèle le 1er, ensemble le 3), un tiers d'issues « oui » avec un fait le 10 ; le modèle ajoute une ligne « cycle 2026-11 » à 1 % le 28. Sans la seconde ligne : écart nul, non concluant. Avec : « le modèle bat l'ensemble », p = 0,008, écart moyen 0,057 par question.

Sens du biais : en faveur de l'auteur qui émet la seconde ligne. Pour le modèle, c'est le sens opposé à la prudence. La propriété « aucune sélection ne dépend de l'issue » n'est pas respectée.

Correction proposée.
- Dans `notation.py`, ne garder que la première ligne de cycle par auteur, question et cycle ; publier les lignes écartées.
- Ajouter un contrôle à la poussée qui signale une seconde ligne de cycle.
- Préciser la section 8.5 en conséquence.

Essai fait sur une copie : la correction (douze lignes, au tri des lignes dans `bilan`) annule l'effet ; les 15 tests passent après une retouche de `test_bout_en_bout`. Ce test étiquette « cycle 2026-11 » une prévision du 1er décembre, et ne passait qu'à la faveur du défaut ; je l'ai réétiqueté « cycle 2026-12 ». Mutation : le code actuel avec le scénario ci-dessus donne le verdict biaisé.

### I2. EV-35 : deux publications peuvent prétendre au « bilan annuel 2026 »

Critère. « Le bilan annuel 2026 des actes antireligieux publié par le ministère de l'Intérieur fait état de plus de 326 actes antimusulmans (nombre de 2025). »

Fait vérifié. Le chiffre de 326 vient du communiqué « Actes antireligieux – Tendances 2025 » du 12 février 2026. Le ministère y précise que ces données ne constituent pas une statistique institutionnelle, et annonce qu'un bilan annuel sera publié pour la première fois en 2026.

Scénario. Début 2027, le ministère publie à la fois des « tendances 2026 » (en février, comme en 2026) et un « bilan annuel » au sens propre, à une autre date et peut-être selon une autre méthode. Deux lectures raisonnables s'opposent :
- le bilan visé est le communiqué de tendances, comparable au 326 ;
- c'est le nouveau bilan annuel. S'il paraît après le 31 mars 2027, une lecture donne « non » (rien n'est publié dans la fenêtre), l'autre « oui » s'il dépasse 326.

L'issue est contestable, ce qui relève du défaut important (section 12).

Correction proposée. Nommer le document (« le communiqué du ministère de l'Intérieur présentant les chiffres des actes antimusulmans de 2026, tendances ou bilan, le premier publié »), dire que 326 vient des tendances 2025, et fixer l'issue si rien n'est publié au 31 mars 2027 (« non », ou annulation). La banque n'est pas encore figée : la correction est possible sans procédure d'ajout.

## Souhaitables

S1. Couverture de la gouvernabilité. La cible « chute du gouvernement » (section 5.2) n'est couverte que par la censure (EV-15, 15b, 15c). En 2025, les deux chutes sont passées par d'autres voies : refus de la confiance (article 49, alinéa 1, gouvernement Bayrou, 8 septembre 2025) et démission du Premier ministre (Lecornu, 6 octobre 2025). À ajouter : la fin des fonctions du Premier ministre, constatée par un décret au Journal officiel, quelle qu'en soit la cause, par fenêtres comme EV-15.

S2. Couverture, autres sujets.
- Référendum (article 11 ou 89) organisé ou décrété après mai 2027 : une promesse de campagne plausible, à fort impact.
- Clause pour une présidentielle anticipée : les fenêtres de EV-15b, EV-16a et EV-43 à 45 sont ancrées sur le 2 mai 2027, ce qui reste résoluble mais change le sens des questions.
- Écart OAT-BTP italien de signe positif : la France a déjà emprunté plus cher que l'Italie en 2025 ; la série est collectée (`webstat_ecart_IT_DE_pb`).

Les ajouts différés déjà listés dans la passation sont pertinents.

S3. Constat sans publication à l'échéance. La section 8.8 dit que l'absence d'acte vaut « non » pour un événement « survenue », mais ne dit rien d'un « constat » dont la publication attendue manque à l'échéance (EV-03, EV-35, EV-38). Une règle générale éviterait les ambiguïtés du type I2 : « non » si le critère exige une publication dans la fenêtre, annulation sinon.

S4. EV-38 (stocks de gaz). La résolution dépend d'une capture archivée de la page d'AGSI+, qui est une application dynamique ; je n'ai pas pu vérifier que les captures contiennent la donnée. Plus sûr : relever la valeur du 1er février 2027 par la collecte nocturne (API AGSI+) les 2 et 3 février 2027, en ajout seul, comme les premières valeurs.

S5. EV-13. Le taux de grévistes est communiqué par le ministère chargé de la fonction publique (chiffres de la DGAFP), en général le jour même, sans page de publication stable « lue 30 jours après ». Nommer cette source et admettre deux agences concordantes.

S6. EV-17. Cas non couverts : députés du parti du président répartis entre plusieurs groupes, ou trop peu nombreux pour former un groupe. Préciser : « groupe comptant le plus de députés de ce parti ; s'il n'y en a pas, la réponse est oui ».

S7. EV-44. Écrire « solde public effectif » : l'article liminaire présente aussi les soldes structurel et conjoncturel.

S8. Fait survenu entre l'émission du modèle et celle de l'ensemble. La ligne de l'ensemble est exclue, et le cycle est retiré pour les deux auteurs (question mensuelle : question entière retirée). Cette sélection dépend de l'issue : seules des questions « oui » sont retirées. Elle est appliquée aux deux auteurs et son sens n'est pas déterminé ; l'effet est faible si l'écart d'émission reste de quelques jours. Publier le nombre de cycles et de questions ainsi retirés, et viser une émission de l'ensemble le jour du gel.

S9. Annonces. Une annonce consignée par deux agents retire la question de toute émission future, sans terme, même si l'acte annoncé échoue (l'issue reste alors ouverte jusqu'à l'échéance, sans prévision). La notation coupe dès la première annonce d'un seul agent. C'est symétrique, mais à documenter, avec une levée possible de l'annonce par erratum.

S10. `geler.py --essai` accepte une étiquette réelle (AAAA-MM) avec n'importe quelle date, donc un gel antidaté. La notation protège l'antériorité (exclusion au jour du fait), mais la section 8.8 dit que le gel est daté du jour réel. Refuser `--essai` pour une étiquette AAAA-MM postérieure ou égale à 2026-11, et adapter les tests (étiquettes d'essai nommées autrement).

S11. Règles de la phase 3 non codées dans la notation : notation du modèle sur le taux de base pour une question du périmètre sans prévision (déjà dans `controle/phase3.md`) ; verdict « non concluant d'avance » si la phase 3 démarre après le 1er avril 2027 (section 8.6), à coder plutôt qu'à déclarer.

S12. EV-08. « Présente expressément l'élection comme l'objectif » reste une appréciation sur des rapports de VIGINUM souvent prudents. Ajouter un exemple de formulation qui compte et un qui ne compte pas.

## Réponses aux questions posées

Méthode. Hors B1 et I1, le protocole peut conclure ce qu'il annonce, et il le dit avec mesure. Le Brier pondéré est propre (vérifié par `test_brier_pondere_propre` et par lecture du code), le test par grappes a le bon niveau sous l'hypothèse nulle, et la calibration repose sur une prévision choisie indépendamment de l'issue. L'antériorité est tenue par l'exclusion au jour du fait et par les annonces. L'asymétrie d'information joue contre le modèle : l'ensemble cherche sur le web après le gel, le modèle est figé au gel et noté non calé. La puissance est faible et publiée comme telle ; un verdict non concluant est l'issue la plus probable, et la règle par défaut est cohérente avec ce constat.

Fond. La banque couvre bien la séquence politique et budgétaire 2026-2028 et les principaux canaux économiques. Les lacunes notables sont la chute du gouvernement hors censure (S1) et le référendum (S2). Les critères sont dans l'ensemble résolubles sur des sources primaires. Seul EV-35 est contestable au sens de la grille ; EV-38, EV-13 et EV-17 présentent des risques moindres.

Conformité du code au texte. Les écarts relevés sont B1 (errata, règle de poussée), I1 (unicité de la prévision de cycle, non écrite), S10 (date du gel) et S11 (règles de la phase 3). Le reste des points contrôlés est conforme : gel sans repli sur un fichier courant, grappes figées, exclusions au jour du fait et à la première annonce, cycles communs et départ commun, calibration sur les questions échues, verdicts avec et sans ajouts.

## Non vérifié

- Scripts de collecte (`collecte/*.py`), dont le calcul du Brent mensuel sur mois complet ; `scripts/tri.py` lu en partie ; `scripts/taux_base.py` et le contenu des taux de base (`modele/taux_base/`) ; `scripts/sources.py` et `modele/sources.json`.
- Simulation de `scripts/puissance.py` non relancée (seuls les chiffres publiés ont été comparés au texte).
- Exécution réelle des workflows GitHub et état actuel des règles de protection : pas d'accès authentifié.
- Contenu des captures archivées d'AGSI+ (S4) ; existence d'un bilan annuel 2025 publié par le ministère de l'Intérieur depuis février 2026 (I2).
- Annexe de la phase 3 : lue, non éprouvée, faute de scripts.
- Interface (`index.html`, volet actualité) et piste exploratoire.