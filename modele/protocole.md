# Protocole Psychohistoire — version 1.26

Statut : voir `modele/statut.json` (section 12). Rédigé le 3 octobre 2026, avant toute estimation produite selon ce protocole.
Remplace la version 1.25. Les changements répondent à la relecture de validation 21 (`v1.26/reponse_relecture_21.md`) ; l'historique des versions et de leurs motifs est dans `journal.md`. Le texte est scindé : ce noyau (sections 0 à 9, 12 et 13) et l'annexe `annexe_phase3.md` (sections 10 et 11), gelés et tagués séparément. Toute modification crée une version datée. Le tag Git `protocole-vX.Y` est posé automatiquement au premier commit de chaque version (section 12).

## 0. Pistes et registres

- **Piste exploratoire (v0, v0.2, 3 octobre 2026).** Les probabilités produites avant tout protocole sont figées dans `registre/exploratoire.jsonl`, en ajout seul. Les mises à jour ultérieures de cette piste y sont ajoutées sans réécrire les lignes antérieures. Elles ne servent ni à paramétrer ni à évaluer le modèle du protocole. `data.json` reste l'état vivant de la page, pas un registre.
- **Piste protocole.** Seules les prévisions émises selon ce protocole, après son tag, entrent dans `registre/protocole.jsonl`, en ajout seul.
- **Format d'une ligne de registre :** `question` (identifiant), `emise` (date et heure), `probabilites` (en %), `piste` (et `phase` pour la piste protocole), `origine` (estimation initiale, cycle mensuel, jalon ou fait imprévu, avec sa référence), `donnees` (commit ou état des données gelées). Le champ `emise` est écrit par `scripts/registre.py` à partir de l'horloge système, jamais par un agent, et contrôlé à la poussée (section 12). Une erreur se corrige par une ligne d'erratum, jamais par réécriture. Une prévision ne peut être qu'annulée, par un erratum `{erratum, objet: {question, auteur, emise}, correction: {annulee: true}, motif, piste}` émis au plus tard sept jours après la ligne visée ; la notation l'applique avant tout calcul et publie les lignes annulées, ainsi que les errata ignorés (tardifs ou sans ligne visée).
- **Matière première :** le balayage v1 (`modele/v1`), conservé tel quel. Les critères de résolution qui en sont tirés sont réécrits dans `modele/banque/criteres.json` (section 8.8).

## 1. Question centrale et frontières

- **Question.** Quelles trajectoires politiques, économiques et sociales pour la France du 1er novembre 2026 au 30 septembre 2028 ?
- **Système modélisé.** La France (institutions, finances publiques, économie, société), plus deux blocs partiellement endogènes : la BCE, par sa fonction de réaction aux écarts de taux ; l'Union européenne, par la procédure budgétaire.
- **Environnement exogène.** Il n'entre que par des séries observées ou cotées : prix de l'énergie, taux mondiaux et Bund, écart de taux italien, cotes des marchés sur les événements mondiaux. Aucune distribution n'est inventée pour un acteur étranger.
- **Hors champ.** Comportements individuels, décisions locales.

## 2. Objets du modèle

| Objet | Définition | Traitement |
| --- | --- | --- |
| Variable d'état | Grandeur mesurable, série publique primaire | Modèle statistique simple (section 7.1) |
| Événement | Fait binaire, critère de résolution observable | Nœud du réseau |
| Décision d'acteur | Choix d'une personne ou d'une institution (dissolution, candidature, alliance, instrument de la BCE) | Nœud dont les parents sont les déterminants de la décision |
| Pivot | Événement ou décision dont l'issue change d'au moins deux niveaux (section 5.2) la distribution d'une variable cible | Nœud principal, affiché comme moment pivot |
| Lien causal | Arc entre deux nœuds, porté par un mécanisme explicite et un seul sens | Intensité (nulle, faible, forte), renseignée par des jalons (annexe, section 10) |
| Jalon | Fait observable attendu dans une fenêtre datée, le long d'un lien | Question notée ; preuve sur le lien une fois validée la direction de ses mises à jour fantômes (annexe, section 10.6) |
| Moteur exogène | Facteur mondial observé ou coté | Entrée fixe, sans rétroaction |
| Paramètre prédéterminé | Variable quasi certaine sur la période (démographie, calendrier) | Fixé avec sa fourchette, testé en sensibilité |
| Risque extrême | Événement rare (moins de 5 % sur la période) à fort impact | Registre séparé, suivi, non modélisé dans le réseau |

## 3. Phasage

Les phases 2 et 3 sont construites selon le calendrier ; la phase 4 seulement si la phase 3 a battu la phase 1. Si les critères de la section 8.6 échouent, on revient à la phase précédente : c'est ce que « simplifier » veut dire.

| Phase | Date | Contenu | Condition pour passer à la suivante |
| --- | --- | --- | --- |
| 1 | Premier cycle (P), le 1er du mois qui suit la première version définitive (section 12), au plus tôt le 1er novembre 2026 | Banque de questions, lignes de base, ensemble direct, registre, données arrivées en cours de cycle (section 8.9) | Scripts listés dans `modele/controle/phase1.md` en service |
| 2 | P + 1 mois | Modèle de l'écart de taux (série journalière collectée), moyenne de sondages corrigée de l'erreur historique | Rétro-test publié |
| 3 | P + 2 mois au plus tard | Réseau réduit de 10 à 15 nœuds sur la séquence politique et budgétaire, chaînes de jalons et faits imprévus (annexe phase 3) | Test du jugement passé (section 8.7) et relectures conformes au critère d'arrêt (section 12) |
| 4 | Après le bilan de la phase 3 | Extension du réseau, analyse structurelle complète | La phase 3 bat la phase 1 sur P2b et P2c (section 8.6) |

Avant la phase 3, les chaînes de jalons peuvent être pilotées sur la piste exploratoire, sans effet sur la piste protocole. Chaque phase dispose d'une liste de contrôle dans `modele/controle/`. Tout ce qui est mécanique est scripté : génération des questions, agrégation, notation, puissance.

## 4. Structure probabiliste (phase 3)

1. **Réseau bayésien dynamique** à pas mensuel (Murphy 2002), acyclique au sein d'une tranche. Les dépendances d'une tranche à l'autre passent par les variables d'état et l'occurrence passée des événements.
2. **Parents.** Au plus trois parents intra-tranche par nœud, avec une exception motivée à quatre. Les parents continus sont discrétisés aux quantiles historiques 33 et 67. Si le choix des parents crée un cycle, l'arc le plus faible est renvoyé à la tranche suivante.
3. **Tables de probabilités conditionnelles explicites** (Pearl 1988).
4. **Incertitude des paramètres.** Chaque ligne de table est une loi de Dirichlet centrée sur l'agrégat. Sa concentration est tirée de la dispersion du premier tour d'élicitation, exprimée en log-cotes, qui ne peut être inférieure à un plancher σ_plancher. Celui-ci vaut le plus grand de trois termes :
   - 0,3 en log-cotes ;
   - la dispersion moyenne entre évaluateurs observée au test du jugement (section 8.7), divisée par la pente β de la recalibration logistique estimée sur ce test lorsque β < 1 (surconfiance) ;
   - l'écart-type, en log-cotes, de l'écart entre les estimations et les cotes externes du pool P1, mesuré avant calage, une fois celles-ci disponibles.

   Le même plancher sert au seuil d'application des faits imprévus (annexe, section 11.4).

   **Passage à la concentration.** Pour une ligne d'issue modale p̂ et de dispersion retenue σ (la plus grande de la dispersion observée et de σ_plancher), la concentration α₀ de la loi de Dirichlet est la solution de ψ₁(α₀ p̂) + ψ₁(α₀ (1 − p̂)) = σ², où ψ₁ est la fonction trigamma : c'est la variance de la log-cote de l'issue modale sous la loi bêta marginale. Elle est calculée par script. La simulation tire au moins 500 jeux de paramètres, puis 1 000 trajectoires par jeu. Chaque sortie est publiée avec son intervalle crédible à 80 %.
5. **Calage sur les cotes.** Un nœud coté reste dans le réseau. On décale l'ordonnée de sa table, en log-cotes, jusqu'à ce que la marginale calculée égale la cote. La cote est fiable si elle cumule un volume d'au moins 100 000 dollars, un écart entre l'offre et la demande d'au plus 3 points, et porte sur le même événement, résolu à un mois près. Sinon, pas de calage. L'écart entre la marginale non calée et la cote est enregistré avant calage (section 8.4). Les questions calées vont dans P1, sauf une question déjà émise dans un autre pool : elle y reste, sur sa marginale non calée (section 8.3). **Prévisions notées.** Les prévisions du modèle notées en P2a, P2b et P2c sont celles du réseau entièrement non calé : aucun nœud calé, aucune ligne de table modifiée à la suite d'une comparaison à une cote, de sorte qu'aucune cote n'y entre par propagation. Elles sont enregistrées à chaque cycle avant tout calage ; les sorties calées sont publiées à part et ne sont pas notées dans ces pools.
6. **Sensibilité.** Régression des sorties principales sur les jeux de paramètres tirés : part de variance expliquée par ligne de table. Publiée à chaque version.

## 5. Identification et sélection

### 5.1 Identification

1. Balayage v1 complété des décisions d'acteurs, de la boucle souverain-banques et de la fonction de réaction de la BCE.
2. Pré-mortem (Klein 2007) par deux agents distincts, sans accès au balayage, puis lu par Nathan, qui peut ajouter des objets avec trace.
3. Second balayage à un mois d'intervalle, avant la phase 3. Le recouvrement est publié (indice de Jaccard).
4. Hiérarchie des sources : séries officielles primaires, puis données d'agences, puis presse de référence. Tout niveau de paramétrage vient d'une source primaire ou de `collect.py`. Les divergences sont tranchées et consignées. Les dates de scrutin sont vérifiées sur le décret de convocation dès sa publication.

### 5.2 Cibles et seuils d'impact

L'impact d'un objet est l'effet, s'il se réalise (ou varie d'un écart-type historique), sur chacune des cinq cibles. On retient le niveau le plus haut atteint.

| Niveau | Écart OAT-Bund, variation à 3 mois | Croissance annuelle | Inflation annuelle | Gouvernabilité : probabilité de chute du gouvernement ou de dissolution à 12 mois | Issue politique : probabilité du favori |
| --- | --- | --- | --- | --- | --- |
| 1 | < 10 pb | < 0,1 pt | < 0,1 pt | < 2 pts | < 2 pts |
| 2 | 10 à 25 pb | 0,1 à 0,3 pt | 0,1 à 0,3 pt | 2 à 5 pts | 2 à 5 pts |
| 3 | 25 à 50 pb | 0,3 à 0,6 pt | 0,3 à 0,7 pt | 5 à 10 pts | 5 à 10 pts |
| 4 | 50 à 100 pb | 0,6 à 1,2 pt | 0,7 à 1,5 pt | 10 à 20 pts | 10 à 20 pts |
| 5 | > 100 pb | > 1,2 pt | > 1,5 pt | > 20 pts | > 20 pts |

L'issue politique désigne la présidentielle jusqu'à son second tour, puis la majorité absolue à l'Assemblée.

### 5.3 Classement

- **Score.** Impact médian × incertitude normalisée. L'incertitude vaut 2√(p(1 − p)) pour un nœud binaire, et l'entropie normalisée au-delà de deux issues. p est la probabilité de survenue dans la fenêtre de la phase, ce qui couvre les événements récurrents.
- **Sélection.** On retient les N premiers (10 à 15 en phase 3), à condition que chaque cible soit couverte par au moins un nœud. Les deux premiers forment les axes des scénarios prospectifs.
- **Signalements.** Un écart interquartile de probabilité supérieur à 20 points entre évaluateurs est signalé. Un objet à moins de 5 % du score du N-ième est testé en sensibilité.
- **Redondance.** Un objet est fusionné dans sa cible quand au moins trois évaluateurs sur cinq le signalent comme redondant.

### 5.4 Risques extrêmes

Les événements de probabilité inférieure à 5 % sur la période et d'impact au moins égal à 4 forment un registre séparé. Ils sont suivis par la veille (annexe, section 11.2), sans nœud dans le réseau. Si la probabilité d'un risque extrême dépasse 5 %, son entrée dans le réseau est proposée lors de l'analyse trimestrielle.

## 6. Évaluateurs

### 6.1 Composition et règles

- **Effectif.** Au moins cinq évaluateurs, répartis sur au moins trois modèles différents de la famille disponible (par exemple Opus, Sonnet, Haiku). Aucun modèle d'une autre famille n'est disponible : la diversité des évaluateurs reste limitée, ce qui est compensé par le plancher de dispersion (section 4.4) et par la référence externe (section 8.4).
- **Entrées aveugles.** Nom, définition, mécanisme et mesure ; ni cote ni note d'autrui au premier tour. L'ordre est aléatoire et aucune posture n'est imposée.
- **Accord.** L'alpha de Krippendorff est publié. On ne refait pas de passage pour l'améliorer : un accord faible élargit les lois de Dirichlet. Un accord élevé n'est pas une preuve de qualité.

## 7. Paramétrage

### 7.1 Variables d'état

- **Écart OAT-Bund.** Marche aléatoire puis autorégressif d'ordre 1, estimés sur données journalières 2010-2025 ; on retient celui qui gagne en rétro-test. Pas de chocs d'événements estimés, faute d'historique : les événements agissent par les nœuds du réseau.
- **Intentions de vote.** Moyenne pondérée des sondages récents. L'incertitude est fixée par l'erreur historique des sondages à horizon égal (présidentielles 2002 à 2022).
- **Mobilisation sociale.** Nœud événement (journée nationale au-dessus d'un seuil, selon les chiffres du ministère de l'Intérieur), avec taux de base. Pas de modèle de comptage.

### 7.2 Moteurs exogènes

Cotes et prix relevés à date fixe, par `collect.py` quand c'est possible.

### 7.3 Taux de base

Au moins deux classes de référence par nœud (Kahneman et Lovallo 1993), avec leur fourchette.

### 7.4 Tables conditionnelles

- **Horizon.** L'élicitation se fait à l'horizon naturel de l'événement (par exemple, censure avant le 31 décembre), puis la valeur est convertie en taux mensuel. Le cumul sur la période est présenté aux évaluateurs avant validation.
- **Deux tours IDEA** (Hemming et al. 2018), avec agrégation par moyenne des log-cotes (Clemen et Winkler 1999).
- **Contrôles.** Sommes et monotonie. Un écart de plus de 15 points à une référence externe (cote ou prévision communautaire) est consigné et justifié avant publication, sans retouche de la table utilisée pour la notation (section 4.5) : la comparaison à une cote ne modifie que les sorties calées.

## 8. Questions, notation et validation

### 8.1 Banque de questions

- **Variables d'état** : seuils aux quantiles 20, 50 et 80 de la marche aléatoire, à 1, 2 et 3 mois.
- **Événements et décisions** : survenue avant l'échéance (question de fenêtre) ou entre la date du gel et la fin du mois (question mensuelle, dont le texte donne ces deux dates).
- **Questions conjointes** : « A et B avant telle date », pour chaque arc du réseau. Elles se résolvent toujours et dépendent directement des dépendances. Elles appartiennent à la grappe du lien A → B.
- **Génération** par script à chaque cycle mensuel.

### 8.2 Horodatage

Les données sont gelées à une date, puis les prévisions sont commitées avant toute autre recherche. Aucune question n'est émise si sa résolution est déjà publique, ni si son échéance tombe le jour du gel, ni si son acte a été annoncé comme décidé avant le gel (section 8.8 ; deux agents ou deux passages l'ont consigné). Tous les fichiers gelés doivent exister : un fichier manquant fait échouer le gel, et aucun script ne lit alors un fichier courant à sa place. La grappe d'un événement est fixée à sa première émission. Pour une variable, la collecte inscrit la date de sa dernière collecte réussie (`data/historique/_collecte.json`, gelée avec le cycle) ; une série, ou sa série quotidienne d'ancrage, qui n'a pas été collectée dans les trois jours précédant le gel ne donne lieu à aucune question ce cycle, car une publication a pu échapper à la collecte.

### 8.3 Pools et grappes

| Pool | Contenu | Ce qui y est jugé |
| --- | --- | --- |
| P1 | Questions avec cote externe fiable | Écart à la référence |
| P2a | Variables d'état sans cote | Modèles statistiques |
| P2b | Événements et décisions sans cote | Structure et jugement |
| P2c | Questions conjointes | Dépendances |
| P2d | Jalons : « J observé dans sa fenêtre » | Descriptif : calibration des jalons, sans décision attachée (annexe, section 10.9) |
| P2e | Indicateurs internationaux : un événement par grand sujet mondial (Ukraine, États-Unis, Chine, Proche-Orient) | Descriptif : calibration publiée, sans décision attachée ; exclu des critères de la section 8.6 |

Une grappe correspond à une variable source sur une fenêtre trimestrielle sans chevauchement ; à un événement, dont la question de fenêtre et les questions mensuelles forment une seule grappe (deux sous-questions à fenêtres disjointes, comme la dissolution avant et après le second tour, forment deux grappes ; des sous-questions à fenêtres qui se chevauchent ou s'emboîtent, comme l'accord sur le cadre financier avant fin 2026 et avant septembre 2028, n'en forment qu'une) ; ou à un lien pour les jalons et les questions conjointes. Les questions tranchées par un même acte officiel ou liées à la même candidature (pourvoi de Marine Le Pen, liste des candidats et résultats du premier tour de 2027) forment une seule grappe, quel que soit leur événement.

**Pool d'une question.** Il est fixé à sa première émission et ne change plus. En phase 3, une question de P2b dont le nœud est ensuite calé sur une cote (section 4.5) reste dans P2b pour les tests de la section 8.6, sur la marginale du réseau entièrement non calé (section 4.5), enregistrée avant tout calage ; la valeur calée est publiée à part.

**Grappe résolue.** Une grappe entre dans les tests dès qu'une de ses questions est résolue ; elle y contribue par la somme des écarts de score sur ses questions résolues à la date du test. La puissance est simulée sur la banque réelle (nombre de questions de chaque grappe) et publiée avant le premier cycle de chaque phase (`data/puissance.json`). 
### 8.4 Comparateurs

1. **Persistance** pour les variables : marche aléatoire à la volatilité historique. Quand le niveau de départ est un point quotidien (ancrage d'une série mensuelle publiée tard sur son équivalent quotidien), la loi utilisée, pour les seuils comme pour ce comparateur, est celle de l'écart historique entre un point quotidien pris au même jour du mois et la moyenne du mois cible, et non celle d'une variation de moyennes mensuelles.
2. **Taux de base** pour les événements, sur la période de la question (un statu quo à 0 % rendrait le score logarithmique infini), et **50 %**. Chaque événement a une nature déclarée : « survenue » (il peut se produire à tout moment de sa fenêtre ; le taux est ramené à la fenêtre restante par un risque constant) ou « constat » (l'issue est constatée à une date fixe ; le taux n'est pas converti). Limite connue : pour une question à plusieurs issues dont l'une dépend du temps restant (« pas d'arrêt », « pas d'avis »), la répartition du taux de base reste fixe. Pour un événement sans classe de référence pertinente (le vainqueur d'une élection dont un candidat n'a jamais gagné), la loi uniforme tient lieu de taux de base.
3. **Références externes** sur P1 : prévision communautaire Metaculus ou prix Polymarket. Ce sont les seuls comparateurs extérieurs à la famille de modèles utilisée ; l'écart à ces références, mesuré avant calage, est publié à chaque bilan, même si le pool P1 ne sert pas aux critères d'échec. Aucune correction des estimations n'en est tirée : avec un seul marché fiable, dont les issues se compensent par construction, un test de signe n'aurait ni unité ni effectif définis (relecture 12).
4. **Ensemble direct** : au moins cinq prévisionnistes IA avec recherche, médiane non extrémisée et non bornée. Aucune prévision notée n'est bornée, quel que soit l'auteur (comparateurs, ensemble, modèle) : une borne propre à certains auteurs les pénaliserait sur les événements rares. Le score logarithmique borne seul ses probabilités à 10⁻⁴. Son écart au taux de base est publié à chaque bilan, sans décision attachée : si l'ensemble ne bat pas le taux de base, une victoire du modèle sur l'ensemble prouve peu.
5. **Modèle témoin** : mêmes marginales, nœuds indépendants, sans dépendances.

### 8.5 Scores et tests

- **Scores :** Brier, score logarithmique, décomposition de Murphy, Brier pondéré dans le temps. Ce dernier vaut, pour une question de la période t₀ à l'échéance T, la somme sur les prévisions de leur Brier multiplié par leur durée prévue, divisée par la longueur fixe T − t₀ + 1 jours. La durée prévue d'une prévision va de son jour au jour de la prévision suivante ; pour la dernière, jusqu'à l'échéance si aucun fait ne survient dans la fenêtre, et sinon jusqu'au 1er du mois qui suit le fait (cycle prévu suivant le fait) : un cycle manqué avant le fait est couvert par la prévision précédente, comme sans fait, et ne vaut pas une prévision certaine. Elle n'est jamais tronquée au fait ; les jours postérieurs au fait comptent pour zéro, comme une prévision devenue certaine. Le poids d'une prévision ne dépend donc pas de l'issue, et la règle est propre : une moyenne arrêtée la veille du fait, divisée par le nombre de jours comptés, récompensait les probabilités gonflées sur les questions de fenêtre (relecture 17, vérifié par simulation dans `test_brier_pondere_propre`). Les prévisions émises le jour du fait ou après sont exclues (section 8.8). Pour une question à prévision unique (variable), le Brier pondéré vaut à peu près le Brier simple multiplié par la part de la période couverte jusqu'à la collecte de la valeur ; les horizons longs pèsent donc moins dans les sommes par grappe. Le facteur ne dépend pas de l'issue et s'applique de même aux deux auteurs.
- **Convention.** Le Brier d'une question est ½ Σ_k (p_k − y_k)², sur ses issues ; pour une question binaire, il vaut (p − y)². Les écarts de la section 8.6 (0,02 ; 0,04) sont dans cette unité.
- **Score testé.** Les tests de la section 8.6 portent sur le Brier pondéré dans le temps, pour toutes les questions, calculé pour chaque comparaison sur la période commune aux deux auteurs : du plus tardif de leurs premiers jours de prévision à l'échéance, selon la règle ci-dessus. Le test compare des instantanés mensuels : seules les prévisions inscrites aux cycles mensuels entrent dans le test, et, pour chaque question, seulement les cycles où les deux auteurs ont une prévision de cycle ; un cycle manqué par l'un est retiré pour les deux, chacun étant alors couvert par sa prévision de cycle précédente ; le nombre de cycles et de questions ainsi retirés est publié. Un auteur n'a qu'une prévision par question et par cycle : la première émise. Une seconde ligne du même cycle est écartée de toute notation, publiée, et signalée à la poussée ; une ligne annulée par erratum n'est pas réémise, et le cycle est alors retiré pour les deux auteurs. Sinon la seconde ligne remplacerait la première, mais seulement si le fait ne l'a pas précédée : la ligne notée dépendrait de l'issue. À chaque cycle, les deux prévisions partent du même jour, le plus tardif de leurs deux jours d'émission, pour qu'émettre le premier ne donne aucun avantage. La prévision de cycle du modèle est calculée sur l'état du réseau au gel ; l'apport des mises à jour continues de la phase 3 (jalons, faits imprévus) est mesuré à part et publié sans décision. N'y entrent, à la date du test, que les questions dont l'échéance est passée, quelle que soit leur issue : une question de fenêtre résolue « oui » avant son échéance attend son échéance, faute de quoi seules les survenues seraient notées et la prévision la plus alarmiste serait favorisée.
- **Test :** permutation des signes des sommes d'écarts par grappe (exacte jusqu'à 16 grappes, 20 000 tirages au-delà), seuil unilatéral de 10 % dans chaque sens. La simulation de puissance emploie le seuil de Student correspondant, qui donne les mêmes résultats.

### 8.6 Critères d'échec fixés à l'avance

Évalués sur les questions échues au 30 septembre 2027, quelle que soit leur issue, des pools indiqués pour chaque critère, avec et sans les questions ajoutées après le premier cycle. Le bilan est calculé au cycle de décembre 2027 (`scripts/notation.py --date 2027-09-30`), une fois écoulé le délai de résolution et d'annulation de 60 jours, pour que les questions résolues « non » à leur échéance y entrent comme celles résolues « oui » en cours de mois ; les questions échues encore ouvertes sont publiées avec le bilan :
- **Valeur ajoutée.** Comparaison de la phase 3 à l'ensemble direct (phase 1) sur les seuls pools P2b et P2c, au seuil unilatéral de 10 % dans chaque sens. Trois verdicts : la phase 3 fait mieux (valeur ajoutée démontrée) ; elle fait moins bien (sans valeur ajoutée, retour à la phase 2) ; ni l'un ni l'autre (non concluant). Un verdict non concluant n'est pas un résultat négatif : il est publié comme tel, avec l'écart moyen par question, son intervalle à 80 % (rééchantillonnage des grappes) et la puissance recalculée sur les grappes réellement présentes à la date du test. Deux tests unilatéraux à 10 % donnent un risque global de 20 % de conclure à tort dans un sens ou dans l'autre. La règle de décision par défaut s'applique alors (section 13) : on revient à la phase 2, la plus simple, pour la suite du projet.
- **Calibration.** Mesure : terme de fiabilité de la décomposition de Murphy, en dix classes de probabilité, sur les questions binaires de P2b et P2c dont l'échéance est passée à la date du test, quelle que soit leur issue (section 8.5 : une question de fenêtre résolue « oui » avant son échéance n'entre pas seule), avec pour chaque question la première prévision de cycle de l'auteur, choisie indépendamment de l'issue (la dernière avant résolution dépend de l'issue pour une question de fenêtre) ; calculée avec et sans les questions ajoutées. Référence : sa distribution sous calibration parfaite, simulée avec les mêmes questions et les mêmes grappes (copule gaussienne, corrélation intra-grappe ρ = 0,3 ; `scripts/notation.py`). Au-delà du 90e centile, les probabilités sont recalibrées par une régression logistique en log-cotes estimée sur les questions résolues et appliquée aux prévisions suivantes, avec trace, et la cause est cherchée.
- **Persistance.** Si la persistance bat le modèle sur les variables (P2a) ou si le taux de base le bat sur les événements (P2b), au seuil de 10 %, le projet est déclaré en échec méthodologique : il le publie, cesse de présenter les probabilités du modèle comme des prévisions, et ne poursuit jusqu'à la fin de l'horizon qu'avec l'ensemble direct et les comparateurs.

Pour un verdict significatif, la dépendance entre grappes (une même campagne électorale, une même conjoncture) fait du seuil nominal une borne optimiste, et la multiplicité des tests (valeur ajoutée, persistance sur P2a, taux de base sur P2b, chacun avec et sans ajouts) accroît le risque qu'un d'eux conclue à tort : un tel verdict reste une preuve faible et est publié comme tel. Les trois critères sont calculés pour le modèle en une fois par `scripts/notation.py` (rubrique `bilan_8_6_modele` du bilan), quel que soit l'auteur de référence demandé.

**Conduite de la phase 3, fixée avant son démarrage.**
- **Aveuglement.** Les évaluateurs et l'opérateur du réseau ne consultent pas les prévisions de l'ensemble direct sur les questions encore ouvertes, comme l'ensemble ne consulte pas celles du modèle. Ils travaillent sur une copie du dépôt dont sont retirés `registre/`, `data/cycles/*/ensemble/`, `data/bilans/`, `data.json` et `index.html`. Il leur est interdit de consulter le dépôt public et sa page ; ils listent les adresses consultées, contrôlées comme celles de l'ensemble (`scripts/verifier_reponse.py`).
- **Périmètre.** La liste des événements couverts par le modèle est publiée au démarrage de la phase 3 et ne se réduit pas. Un nœud retiré du réseau continue d'être prévu par sa dernière table ; une question d'un événement du périmètre sans prévision du modèle est notée, pour le modèle, sur le taux de base. Le modèle ne choisit donc pas ses questions après coup.
- **Sensibilité.** Le verdict est publié avec le même test refait en retirant chaque grappe tour à tour (`sans_chaque_grappe` dans le bilan) ; la grappe de la présidentielle porte à elle seule environ la moitié du poids informatif de P2b en 2027. Si la phase 3 démarre après le 1er avril 2027, il ne reste presque plus de question informative dans P2b avant la butée (une seule pour un démarrage en mai) : le test de valeur ajoutée est alors déclaré non concluant d'avance.

**Calendrier attendu.** Le réseau démarre au plus tard deux mois après le premier cycle, soit le 1er janvier 2027 si le premier cycle a lieu le 1er novembre 2026 ; la simulation ci-dessous retient cette date. Sur la banque réelle, en ne comptant que les questions émises après son démarrage et échues au 30 septembre 2027, P2b fournit 17 grappes (les questions de la candidature et du premier tour de la présidentielle n'en forment qu'une) et 105 questions, dont 12 seulement sont informatives : les autres sont des questions mensuelles sur des événements rares, où deux prévisions ne diffèrent presque pas en Brier. La puissance simulée (`data/puissance.json`, σ = 0,12 ; écart et dispersion de chaque question proportionnés à 4p(1 − p)) est, pour P2b seul, de 17 à 19 % pour un écart de Brier de 0,02 et de 26 à 36 % pour 0,04. Avec 15 grappes de P2c (questions conjointes simulées à 10 %), elle passerait à 25 à 32 % et 48 à 59 %. Le test ne peut donc détecter qu'un écart net, porté surtout par les questions conjointes de la phase 3 ; un verdict non concluant est le cas le plus probable. Ces chiffres sont des bornes hautes : la simulation suppose que le modèle prévoit toutes les questions de P2b, alors qu'un réseau de 10 à 15 nœuds n'en couvrira qu'une partie (le test ne porte que sur les questions communes), et que les grappes de P2c sont indépendantes, alors que beaucoup de questions conjointes tomberont dans la grappe de la présidentielle. Le critère de persistance sur P2a ne porte, pour le modèle, que sur l'écart de taux : quatre grappes trimestrielles au plus, avec lesquelles le test exact ne peut presque pas rejeter ; sa puissance est publiée (`data/puissance.json` : avec trois grappes, le test ne peut pas rejeter). Un bilan final, descriptif, est publié au 30 septembre 2028 (28 grappes de P2b, 27 questions informatives).

**Limite connue (questions cotées et fuites).** Les prévisionnistes de l'ensemble direct n'ont pas le droit de consulter les marchés de prédiction ni le dépôt du projet ; ils listent les adresses consultées, et une réponse qui en cite une interdite est rejetée par script (consigne v1.5, `scripts/verifier_reponse.py`). Le modèle est noté sur le réseau entièrement non calé (section 4.5) : aucune cote n'y entre, ni directement ni par propagation d'un nœud parent. Une question cotée ne favorise donc aucun des deux, sauf fuite de la cote dans la presse ou adresse non déclarée, qui jouent contre le modèle et dans le sens de la règle par défaut.

### 8.7 Tests sur le passé

- **Composantes statistiques :** rétro-test sur 2010-2025.
- **Jugement :** questions ouvertes publiquement avant le 1er juillet 2026 et résolues ensuite. Pas de recherche web : un script constitue, pour chaque question, un dossier figé à partir de captures archivées datées d'avant son ouverture (Internet Archive). Le choix des pages est mécanique : le texte de la question, plus une liste fixe de pages (articles Wikipédia en français et en anglais des entités nommées dans la question, pages d'accueil de franceinfo et du Monde) à la date d'ouverture. Une question dont le dossier ne peut être constitué est écartée. Le test porte sur au moins 50 questions ; s'il y en a moins sur la France, il est élargi à l'Europe, puis au reste du monde. La coupure de chaque modèle est vérifiée par sondage de faits datés. Si la coupure vérifiée d'un évaluateur est postérieure au 1er juillet 2026, les questions résolues avant cette coupure sont écartées du test pour tous les évaluateurs. Le résultat fixe le plancher de dispersion (section 4.4).

### 8.8 Résolution des questions

- **Banque d'événements de la phase 1.** Elle est fixée avant le premier cycle dans `modele/banque/criteres.json`, d'où `scripts/evenements.py` tire `modele/evenements.json`. Elle comprend les événements du balayage v1 dotés d'un critère, avec un critère réécrit à la relecture 8 (le texte d'origine est conservé dans le champ `contexte_v1`), et les ajouts de la relecture 8. Seuls le nom, la sous-question et le critère sont transmis aux prévisionnistes : ni cote, ni sondage, ni taux de base ; les identifiants des questions leur sont remis anonymisés, l'identifiant d'une question de variable contenant le quantile de son seuil.
- **Ajouts en cours de phase.** Exception au gel (section 12), encadrée ainsi :
  - au plus cinq ajouts par cycle, inscrits avant le gel du cycle dans `modele/banque/ajouts.jsonl`, en ajout seul, avec des identifiants nouveaux ; le plafond, l'unicité et l'ajout seul sont contrôlés à la poussée (`scripts/controle_banque.py`) ;
  - chacun porte un critère, une source de résolution et un motif ; il est proposé par un agent sans accès aux registres ni aux prévisions, ou par une décision humaine journalisée ;
  - son taux de base est estimé sur une classe de référence historique, sans recherche d'actualité ;
  - aucun retrait d'événement, aucune modification du critère d'une question émise ;
  - les bilans sont publiés avec et sans les questions ajoutées après le premier cycle ; les critères de la section 8.6 sont jugés sur les deux ensembles, et un verdict qui diffère de l'un à l'autre est déclaré non concluant, avec motif.
- **Qui résout.** Les questions sur des séries sont résolues par script, sur la série collectée. Les questions sur des événements le sont, avec la date de la source :
  - sur une source primaire officielle (Journal officiel, Assemblée nationale, Conseil constitutionnel, ministère, juridiction, institution européenne), qui ne l'est que pour ses propres actes et données ;
  - sur un institut, seulement si le critère le nomme ;
  - sur une partie prenante, seulement pour sa propre décision et si le critère le prévoit (vote interne d'un parti) ;
  - à défaut de toute autorité qui publie l'acte, sur deux agences de presse concordantes (AFP, Reuters, AP).
  La méthode de classement des sources est dans `modele/sources.md`.
- **Séries.** Une question de variable est résolue sur la première valeur collectée de sa période, inscrite par la collecte, en ajout seul, dans `data/premieres_valeurs.jsonl` (contrôlé dans le workflow de collecte lui-même, dont les poussées ne déclenchent pas le contrôle des registres) ; sa date de collecte est la date du fait. Une révision ultérieure de la série ne change pas l'issue. Une moyenne mensuelle calculée à partir de données quotidiennes (Brent) n'est écrite qu'une fois le mois complet.
- **Délais et errata.** Une question sans résolution concordante 60 jours après son échéance, alors qu'au moins un avis ou une recherche a été consigné, est annulée ; à 30 jours, elle ne l'est que si deux recherches vaines (propositions sans issue) ont été consignées par des agents ou à des passages distincts. Pour un événement « survenue », l'absence d'acte répondant au critère, constatée après l'échéance sur la source prévue, vaut « non » : la recherche vaine est réservée à une source inaccessible. Une question sans aucune recherche consignée reste ouverte et est signalée au cycle suivant. Une résolution erronée se corrige par une ligne d'erratum dans le registre des résolutions, appliquée à la notation ; un erratum peut rouvrir une question close à tort, et les propositions émises avant lui ne comptent plus. Deux propositions ne valent deux avis que si elles viennent de deux agents distincts, ou du même identifiant d'agent à deux passages distincts : un agent est une session sans mémoire, et le même identifiant à deux passages désigne deux sessions indépendantes. Une proposition « non » émise avant l'échéance d'un événement « survenue » est ignorée, même après l'échéance : l'événement pouvait encore survenir. Une dépêche d'agence reprise intégralement et attribuée par un média de référence compte comme cette agence. Pour un événement « constat » dont la publication attendue manque à l'échéance, l'issue est « non » si le critère exige une publication dans la fenêtre, et la question est annulée sinon, sauf disposition contraire du critère.
- **Date du fait.** Toute proposition de résolution porte la date du fait. Pour un événement « survenue » d'issue « oui », c'est la plus précoce de deux dates : l'acte, et le jour où cet acte a été annoncé comme décidé. « Décidé » s'entend d'un acte adopté, signé ou notifié par l'autorité compétente, dont seules la publication ou l'entrée en vigueur restent à venir ; une intention ne suffit pas. L'annonce fixe la date du fait, elle ne résout pas la question : celle-ci n'est résolue « oui » que lorsque l'acte remplit le critère dans la fenêtre, et une annonce sans acte dans la fenêtre laisse l'issue « non ». Les annonces sont consignées, en ajout seul, dans `registre/annonces.jsonl`, sous l'identifiant de l'événement ; quelle que soit l'issue, les prévisions d'une question émises le jour de la première annonce consignée ou après sont exclues, comme celles émises le jour du fait ou après. D'issue « non », c'est la fin de la fenêtre ; pour un événement « constat », c'est la plus précoce de deux dates, quelle que soit l'issue : la publication du constat, et le jour où l'issue est établie publiquement par une source de cette section, deux agences concordantes comprises. Pour un résultat électoral, c'est le jour du scrutin. Une question dont l'issue est ainsi établie au gel n'est pas émise (section 8.2). Une prévision émise le jour du fait ou après est annulée pour son auteur. Le gel d'un cycle est daté du jour réel de son exécution.
- **Cas ambigu.** Deux agents résolvent indépendamment. S'ils divergent, un troisième tranche. Si le désaccord persiste, la question est annulée pour tous les comparateurs, avec motif. L'absence de source primaire suit la règle des délais ci-dessus : annulation à 30 jours si deux recherches vaines ont été consignées, à 60 jours sinon.
- **Émission et poussée.** La date d'émission (`emise`) fait foi, sous réserve du contrôle à la poussée (section 12) : une ligne poussée hors de la fenêtre de ce contrôle est annulée par un erratum (section 0), pour l'auteur concerné, avec motif, que sa question ait été résolue ou non entre-temps.

### 8.9 Données arrivées en cours de cycle

Dès la phase 1, un fait qui résout une question ou mesure une variable, selon une source primaire officielle ou la collecte (censure votée, candidature déposée, note abaissée, série publiée), est appliqué sans jugement : la question est résolue, et les prévisions qui en dépendent reçoivent de nouvelles lignes de registre (en phase 3, le nœud correspondant est fixé à son issue). La détection passe par la veille et le tri décrits dans l'annexe (section 11.2). En phases 1 et 2, le tri n'agit sur les probabilités que dans ce cas ; il caractérise aussi les faits qui concernent une question et mesure leur reprise, à titre descriptif seulement (affichage, sans effet sur aucune probabilité). Un comptage produit par une partie prenante (syndicat, parti, organisateur) n'est jamais une donnée.

## 9. Scénarios

- **Scénarios prospectifs :** combinaisons des deux nœuds en tête du classement, avec leur probabilité.
- **Familles de trajectoires :** trajectoires simulées les plus fréquentes, regroupées par issues.
- **Chemin réel :** tracé sur la carte au fur et à mesure des résolutions.


## 10 et 11. Liens, jalons et faits imprévus

Ces deux sections forment l'annexe `annexe_phase3.md`, qui ne s'applique qu'à partir de la phase 3, sauf la section 8.9, l'usage descriptif de la caractérisation et de la reprise des faits dès la phase 1, et le pilote sur la piste exploratoire. En résumé :
- les liens influents sont décomposés en jalons datés et gelés à l'avance, affichés et notés, mais sans effet sur les probabilités tant que la direction de leurs mises à jour fantômes n'est pas validée ;
- les faits imprévus ne déplacent un nœud que s'ils franchissent un seuil d'application.

## 12. Révisions, exécution et gouvernance

- **Cycle mensuel.** Gel des données, génération des questions, prévisions, notation.
- **Analyse trimestrielle.** Révision des paramètres, entrée ou sortie de nœuds, réexamen des révisions ciblées, activation des jalons et estimation des facteurs k (annexe, sections 10.4, 10.6 et 11.4). Le tout est tracé.
- **Déclencheurs.**
  - La collecte nocturne, la pose des tags et le contrôle des registres passent par GitHub Actions.
  - Le tri, la routine hebdomadaire, le cycle mensuel et l'analyse trimestrielle passent par des tâches planifiées de Claude, créées après le gel.
- **Rattrapage.** Un passage manqué est rattrapé au passage suivant, en conservant la date des faits. Le cycle mensuel reprend à la première étape non faite : le gel n'est jamais refait, les questions sont générées à la date du gel inscrite au manifeste, et une étape dont les lignes sont déjà au registre n'est pas rejouée (contrôlé par `questions.py`, `comparateurs.py` et `ensemble.py`). Au-delà de 7 jours de retard, il est déclaré manqué au journal, sans prévision rétroactive : la tâche du cycle se déclenche du 1er au 8 du mois, et le 8 ne fait que cette déclaration.
- **Registres.**
  - Seul `scripts/registre.py` écrit dans les registres ; il fixe l'horodatage à partir de l'horloge système.
  - Un workflow vérifie à chaque poussée que les registres, les journaux de jalons et les décisions de tri (en JSONL, une ligne par décision) ne sont modifiés que par ajout, sans suppression ni renommage de fichier (`--no-renames`). Il vérifie aussi que chaque nouvelle ligne de registre (champ `emise`) et chaque nouvelle définition de jalon (champ `defini_le`) est datée, avec son fuseau horaire, dans les deux heures qui précèdent la poussée. Une ligne hors de cette fenêtre est annulée par erratum (sections 0 et 8.8) ; le workflow signale aussi une seconde prévision d'un même cycle (section 8.5).
  - La branche `main` et les tags `protocole-v*` et `annexe-phase3-v*` sont protégés contre la suppression et la réécriture. Un contrôle obligatoire n'est pas retenu : il imposerait des demandes de fusion et bloquerait la poussée directe de la collecte nocturne et des agents. Le contrôle est donc détectif : un échec est public et se corrige par une ligne d'erratum.
- **Protocole.**
  - Il ne change que par une nouvelle version, numérotée en première ligne et journalisée.
  - Le noyau et l'annexe sont versionnés séparément. Les tags et releases `protocole-vX.Y` et `annexe-phase3-vX.Y` sont créés automatiquement au premier commit de chaque version sur `main`. Le contrôle échoue si un texte change sans nouveau numéro.
  - **Version définitive.** Tant que le processus de relecture n'a pas abouti, le protocole évolue librement, par versions datées et journalisées. La première version définitive est la première qui satisfait le critère d'arrêt (deux relectures consécutives sans défaut bloquant ni important) ; le passage de `modele/statut.json` à « définitif » est une décision humaine (Nathan), journalisée. Le texte définitif est celui qu'a lu la seconde relecture propre, sans modification ultérieure ; les souhaitables de cette relecture vont à la version suivante, après le bilan de la phase 1. Le contrôle de la banque échoue si un gel d'un cycle réel existe alors que le statut n'est pas définitif. Aucun cycle de la piste protocole n'est exécuté avant elle : le premier cycle est décalé au mois suivant si besoin.
  - Le noyau et l'annexe sont gelés de la première version définitive au bilan de la phase 1, tenu à la première analyse trimestrielle après le premier cycle. Pendant le gel, une version n'est possible que pour corriger un défaut relevé en relecture, ou pour retirer une exigence devenue inexécutable, sur décision humaine journalisée. Tout ajout au texte est exclu. Les ajouts d'événements à la banque, encadrés par la section 8.8, sont la seule exception ; ils ne modifient pas le texte. La banque (`modele/banque/criteres.json`) est figée au premier gel d'un cycle réel : à chaque poussée, un contrôle échoue si le critère, les issues, la fenêtre, la nature, le pool, l'accessibilité, les questions mensuelles, la source de résolution, l'acte, l'événement de rattachement, le mode de taux de base, la référence externe, le nom ou la sous-question d'un événement diffère de sa valeur au premier gel où il apparaît, ou si l'empreinte d'un fichier gelé diffère de celle de son manifeste.
- **Interventions humaines.** Toutes sont tracées.
- **Relecture.** Obligatoire à chaque version. Le critère d'arrêt est de deux relectures consécutives sans défaut bloquant ni important. Le compteur repart de zéro après une relecture qui relève un défaut bloquant ou important ; la correction de souhaitables, ou un changement de texte relu par la relecture suivante, ne le remet pas à zéro si cette relecture est elle-même sans défaut bloquant ni important. Le relecteur est de la même famille que les auteurs. Deux sortes de relectures : une relecture de suivi, dans la session courante du relecteur, vérifie seulement les corrections et ne compte pas pour le critère d'arrêt ; une relecture de validation, complète, est conduite en session neuve, sans accès aux échanges de rédaction. Seules les relectures de validation comptent pour le critère d'arrêt. Un défaut bloquant ou important relevé par une relecture de suivi est corrigé, puis relu par la relecture de validation suivante, qui seule fait foi pour le compteur.
- **Classement des défauts.** Il s'apprécie sur l'effet, non sur l'intérêt de la remarque :
  - **bloquant** : compromet l'antériorité ou l'intégrité des registres (prévision modifiable après coup, issue connue avant la prévision), ou empêche l'exécution d'un cycle ;
  - **important** : biaise de façon systématique, dans un sens déterminé, un verdict de la section 8.6 (valeur ajoutée, persistance, taux de base, calibration), ou rend l'issue d'une question indéterminable ou contestable entre deux lectures raisonnables du critère. Le relecteur décrit le scénario concret et le sens du biais ;
  - **souhaitable** : tout le reste, notamment la couverture de la banque, une précision de critère sans ambiguïté avérée, la rédaction, la robustesse sans biais démontré, la procédure des phases ultérieures, et un biais qui joue dans le sens prudent (vers « non concluant » ou la règle par défaut).

  Un défaut présenté comme important sans scénario ni sens de biais est traité comme souhaitable. La réponse peut reclasser un défaut, avec motif ; la relecture suivante juge le reclassement.

## 13. Limites assumées

- **Cascades sociales et décisions individuelles.** Le modèle peut dire qu'un terrain est propice, pas dater l'étincelle.
- **Une seule famille de modèles.**
  - Évaluateurs, ensemble direct et relecteur partagent les mêmes biais. Un biais commun déplace le centre des estimations et s'annule dans la comparaison au témoin.
  - Les seuls contrôles extérieurs sont les cotes externes (pool P1, section 8.4) et la résolution des questions. Aucun juge hors famille, humain ou modèle, n'est disponible : les lignes conditionnelles des tables n'ont aucun contrôle extérieur.
  - Aucun humain formé aux probabilités ne relit le protocole.
- **Puissance.** Seuls des écarts nets de performance seront détectables, et le verdict de la phase 3 tombera après la présidentielle. Un petit apport de la structure peut passer inaperçu ; la règle par défaut est alors de simplifier.
- **Jalons et faits imprévus.** Leurs paramètres se vérifient mal individuellement. C'est pourquoi les jalons n'agissent qu'après validation de la direction de leurs mises à jour fantômes, et les faits imprévus seulement au-delà d'un seuil d'application.

## Références

Brier 1950 ; Cameron, Gelbach et Miller 2008 ; Chan et Darwiche 2005 ; Clemen et Winkler 1999 ; Dewar et al. 1993 ; Heckerman et Breese 1996 ; Hemming et al. 2018 ; Kahneman et Lovallo 1993 ; Karger et al. 2024 ; Klein 2007 ; Krippendorff 2004 ; Mellers et al. 2014 ; Murphy 1973 ; Murphy 2002 ; Paleka et al. 2025 ; Pearl 1988 ; Satopää et al. 2014 ; Schwartz 1991.
