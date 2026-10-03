# Protocole Psychohistoire — version 1.4

Statut : soumis à relecture (relecture 3). Rédigé le 3 octobre 2026, avant toute estimation produite selon ce protocole.
Remplace la version 1.3. Ajout de la section 10 (liens causaux et jalons) ; les changements sont justifiés dans `journal.md`. Toute modification crée une version datée. Le tag Git `protocole-vX.Y` est posé automatiquement au premier commit de chaque version (section 12).

## 0. Pistes et registres

- **Piste exploratoire (v0, v0.2, 3 octobre 2026).** Les probabilités produites avant tout protocole sont figées dans `registre/exploratoire.jsonl`, en ajout seul. Les mises à jour ultérieures de cette piste y sont ajoutées sans réécrire les lignes antérieures. Elles ne servent ni à paramétrer ni à évaluer le modèle du protocole. `data.json` reste l'état vivant de la page, pas un registre.
- **Piste protocole.** Seules les prévisions émises selon ce protocole, après son tag, entrent dans `registre/protocole.jsonl`, en ajout seul.
- **Format d'une ligne de registre :** identifiant de question, date et heure d'émission, probabilités, phase, origine (cycle mensuel ou mise à jour événementielle, avec sa référence), commit des données gelées.
- **Matière première :** le balayage v1 (`modele/v1`), conservé tel quel.

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
| Lien causal | Arc entre deux nœuds, porté par un mécanisme explicite | Probabilité et intensité, renseignées par des jalons (section 10) |
| Jalon | Fait observable attendu dans une fenêtre datée, le long d'un lien | Preuve sur le mécanisme du lien (section 10) |
| Moteur exogène | Facteur mondial observé ou coté | Entrée fixe, sans rétroaction |
| Paramètre prédéterminé | Variable quasi certaine sur la période (démographie, calendrier) | Fixé avec sa fourchette, testé en sensibilité |
| Risque extrême | Événement rare (moins de 5 % sur la période) à fort impact | Registre séparé, suivi, non modélisé dans le réseau |

## 3. Phasage

Chaque phase doit battre la précédente pour que la suivante soit construite. « Simplifier » signifie revenir à la phase précédente.

| Phase | Date | Contenu | Condition pour passer à la suivante |
| --- | --- | --- | --- |
| 1 | 1er novembre 2026 | Banque de questions, lignes de base, ensemble direct, registre, mises à jour événementielles de type « donnée » | Scripts de génération, de notation et de puissance en service |
| 2 | 1er décembre 2026 | Modèle de l'écart de taux, moyenne de sondages corrigée de l'erreur historique | Rétro-test publié |
| 3 | 1er janvier 2027 au plus tard | Réseau réduit de 10 à 15 nœuds sur la séquence politique et budgétaire, chaînes de jalons sur les 3 à 5 liens les plus influents, mises à jour événementielles complètes | Relecture par une autre famille de modèles (section 12) |
| 4 | Après le bilan de la phase 3 | Extension du réseau, analyse structurelle complète | La phase 3 bat la phase 1 sur P2b et P2c (section 8.6) |

Avant la phase 3, les chaînes de jalons peuvent être pilotées sur la piste exploratoire, sans effet sur la piste protocole. Chaque phase dispose d'une liste de contrôle dans `modele/controle/`. Tout ce qui est mécanique est scripté : génération des questions, agrégation, notation, puissance.

## 4. Structure probabiliste (phase 3)

1. **Réseau bayésien dynamique** à pas mensuel (Murphy 2002), acyclique au sein d'une tranche. Les dépendances d'une tranche à l'autre passent par les variables d'état et l'occurrence passée des événements.
2. **Parents.** Au plus trois parents intra-tranche par nœud, avec une exception motivée à quatre. Les parents continus sont discrétisés aux quantiles historiques 33 et 67. Si le choix des parents crée un cycle, l'arc le plus faible est renvoyé à la tranche suivante.
3. **Tables de probabilités conditionnelles explicites** (Pearl 1988).
4. **Incertitude des paramètres.** Chaque ligne de table est une loi de Dirichlet centrée sur l'agrégat. Sa concentration est tirée de la dispersion du premier tour d'élicitation, avec un plancher calé sur le test du jugement (section 8.7). La simulation tire au moins 500 jeux de paramètres, puis 1 000 trajectoires par jeu. Chaque sortie est publiée avec son intervalle crédible à 80 %.
5. **Calage sur les cotes.** Un nœud coté reste dans le réseau. On décale l'ordonnée de sa table, en log-cotes, jusqu'à ce que la marginale calculée égale la cote. La cote est fiable si elle cumule un volume d'au moins 100 000 dollars, un écart entre l'offre et la demande d'au plus 3 points, et porte sur le même événement, résolu à un mois près. Sinon, pas de calage. Les questions calées vont dans P1.
6. **Sensibilité.** Régression des sorties principales sur les jeux de paramètres tirés : part de variance expliquée par ligne de table. Publiée à chaque version.

## 5. Identification et sélection

### 5.1 Identification

1. Balayage v1 complété des décisions d'acteurs, de la boucle souverain-banques et de la fonction de réaction de la BCE.
2. Pré-mortem (Klein 2007) par un modèle d'une autre famille, relayé par Nathan.
3. Second balayage à un mois d'intervalle, avant la phase 3. Le recouvrement est publié (indice de Jaccard).
4. Hiérarchie des sources : séries officielles primaires, puis données d'agences, puis presse de référence. Tout niveau de paramétrage vient d'une source primaire ou de `collect.py`. Les divergences sont tranchées et consignées.

### 5.2 Cibles et seuils d'impact

L'impact d'un objet est l'effet, s'il se réalise (ou varie d'un écart-type historique), sur chacune des cinq cibles. On retient le niveau le plus haut atteint.

| Niveau | Écart OAT-Bund, variation à 3 mois | Croissance annuelle | Inflation annuelle | Gouvernabilité : probabilité de chute du gouvernement ou de dissolution à 12 mois | Issue politique : probabilité du favori |
| --- | --- | --- | --- | --- | --- |
| 1 | < 10 pb | < 0,1 pt | < 0,1 pt | < 2 pts | < 2 pts |
| 2 | 10 à 25 pb | 0,1 à 0,3 pt | 0,1 à 0,3 pt | 2 à 5 pts | 2 à 5 pts |
| 3 | 25 à 50 pb | 0,3 à 0,6 pt | 0,3 à 0,7 pt | 5 à 10 pts | 5 à 10 pts |
| 4 | 50 à 100 pb | 0,6 à 1,2 pt | 0,7 à 1,5 pt | 10 à 20 pts | 10 à 20 pts |
| 5 | > 100 pb | > 1,2 pt | > 1,5 pt | > 20 pts | > 20 pts |

L'issue politique désigne la présidentielle jusqu'au 2 mai 2027, puis la majorité absolue à l'Assemblée.

### 5.3 Classement

- **Score.** Impact médian × incertitude normalisée. L'incertitude vaut 2√(p(1 − p)) pour un nœud binaire, et l'entropie normalisée au-delà de deux issues. p est la probabilité de survenue dans la fenêtre de la phase, ce qui couvre les événements récurrents.
- **Sélection.** On retient les N premiers (10 à 15 en phase 3), à condition que chaque cible soit couverte par au moins un nœud. Les deux premiers forment les axes des scénarios prospectifs.
- **Signalements.** Un écart interquartile de probabilité supérieur à 20 points entre évaluateurs est signalé. Un objet à moins de 5 % du score du N-ième est testé en sensibilité.
- **Redondance.** Un objet est fusionné dans sa cible quand au moins trois évaluateurs sur cinq le signalent comme redondant.

### 5.4 Risques extrêmes

Les événements de probabilité inférieure à 5 % sur la période et d'impact au moins égal à 4 forment un registre séparé. Ils sont suivis par la veille (section 11), sans nœud dans le réseau. Si la probabilité d'un risque extrême dépasse 5 %, son entrée dans le réseau est proposée lors de l'analyse trimestrielle.

## 6. Évaluateurs

### 6.1 Composition et règles

- **Effectif.** Au moins cinq évaluateurs, dont au moins trois modèles différents de la famille principale. Un évaluateur d'une autre famille reçoit l'ensemble des tables, en un message par tour, relayé par Nathan.
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
- **Contrôles.** Sommes et monotonie. Un écart de plus de 15 points à une référence externe est examiné et justifié avant publication.

## 8. Questions, notation et validation

### 8.1 Banque de questions

- **Variables d'état** : seuils aux quantiles 20, 50 et 80 de la marche aléatoire, à 1, 2 et 3 mois.
- **Événements et décisions** : survenue dans le mois ou avant l'échéance.
- **Questions conjointes** : « A et B avant telle date », pour chaque arc du réseau. Elles se résolvent toujours et dépendent directement des dépendances.
- **Génération** par script à chaque cycle mensuel.

### 8.2 Horodatage

Les données sont gelées à une date, puis les prévisions sont commitées avant toute autre recherche. Aucune question n'est émise si sa résolution est déjà publique.

### 8.3 Pools et grappes

| Pool | Contenu | Ce qui y est jugé |
| --- | --- | --- |
| P1 | Questions avec cote externe fiable | Écart à la référence |
| P2a | Variables d'état sans cote | Modèles statistiques |
| P2b | Événements et décisions sans cote | Structure et jugement |
| P2c | Questions conjointes | Dépendances |
| P2d | Jalons : « J observé dans sa fenêtre » | Chaînes de jalons (section 10.8) |

Une grappe correspond à une variable source, ou à un lien pour les jalons, sur une fenêtre trimestrielle sans chevauchement. L'objectif est d'au moins 40 grappes pour P2b et P2c réunis. La puissance est simulée et publiée avant le premier cycle de chaque phase.

### 8.4 Comparateurs

1. **Persistance** : marche aléatoire à la volatilité historique pour les variables, statu quo pour les événements.
2. **Taux de base constant**, et **50 %**.
3. **Références externes** sur P1 : prévision communautaire Metaculus ou prix Polymarket.
4. **Ensemble direct** : au moins cinq prévisionnistes IA avec recherche, médiane non extrémisée.
5. **Modèle témoin** : mêmes marginales, nœuds indépendants, sans dépendances.

### 8.5 Scores et tests

- **Scores :** Brier, score logarithmique, décomposition de Murphy, Brier pondéré dans le temps.
- **Tests :** Diebold-Mariano par grappes, ou test de permutation par grappes s'il y en a moins de 40.

### 8.6 Critères d'échec fixés à l'avance

Évalués à 40 grappes résolues sur P2b et P2c, ou au plus tard au 30 septembre 2027 :
- **Valeur ajoutée.** Si la phase 3 ne bat pas l'ensemble direct (phase 1) sur P2b et P2c, au seuil de 10 %, le modèle structurel est déclaré sans valeur ajoutée et l'on revient à la phase 2.
- **Calibration.** Si l'erreur de calibration dépasse le 90e centile de sa distribution simulée sous calibration parfaite, au même nombre de questions, les probabilités sont recalibrées et la cause est cherchée.
- **Persistance.** Si la persistance bat le modèle sur P2 au seuil de 10 %, le projet est déclaré en échec méthodologique.

### 8.7 Tests sur le passé

- **Composantes statistiques :** rétro-test sur 2010-2025.
- **Jugement :** questions ouvertes publiquement avant le 1er juillet 2026 et résolues ensuite. Pas de recherche web : un dossier documentaire est figé à la date d'ouverture de chaque question. La coupure de chaque modèle est vérifiée par sondage de faits datés. Le résultat fixe le plancher de dispersion (section 4.4).

## 9. Scénarios

- **Scénarios prospectifs :** combinaisons des deux nœuds en tête du classement, avec leur probabilité.
- **Familles de trajectoires :** trajectoires simulées les plus fréquentes, regroupées par issues.
- **Chemin réel :** tracé sur la carte au fur et à mesure des résolutions.

## 10. Liens causaux et jalons

Un pivot ne bascule pas d'un coup : ce qui y mène passe par des étapes observables. Chaque lien influent est décomposé en une chaîne de jalons datés, fixés à l'avance, comme les indicateurs d'alerte de la planification par hypothèses (Dewar et al. 1993) ou le chemin critique d'un chantier. Un jalon qui se produit renforce le lien ; un jalon attendu qui ne se produit pas l'affaiblit.

### 10.1 Mécanisme, probabilité et intensité

- **Mécanisme.** Chaque lien suivi, du nœud A vers le nœud B, porte un mécanisme écrit en une phrase et un sens : une issue de A favorise une issue de B.
- **Probabilité du lien.** C'est la probabilité qu'un nœud caché M (« mécanisme actif ») soit vrai quand A prend l'issue concernée. Si M est faux, A n'agit pas sur B par ce canal.
- **Intensité.** Elle est représentée par un second nœud caché I, à deux niveaux (faible, forte). Quand M est vrai, la cote de l'issue favorisée de B est décalée de δ_I en log-cotes. Les valeurs δ_faible et δ_forte sont fixées à l'élicitation.
- **Effet sur la table de B.** Les lignes de B deviennent une fonction de leur base et des décalages des liens actifs, sur le principe de l'indépendance causale (Heckerman et Breese 1996). La loi jointe reste cohérente, et la probabilité et l'intensité du lien sont deux paramètres distincts : un signal faible abaisse l'intensité sans toucher nécessairement la probabilité. M et I remplacent A parmi les parents de B ; le plafond de parents (section 4.2) s'applique aux nœuds observables, pas à ces nœuds cachés.
- **Un seul sens par lien.** Un mécanisme qui peut pousser B dans un sens ou dans l'autre selon une décision d'acteur (par exemple, recul ou non du gouvernement) n'est pas un lien : la décision devient un sous-pivot, nœud de niveau 2, et le lien est scindé en deux.

### 10.2 Jalon

| Champ | Contenu |
| --- | --- |
| Lien | Le lien auquel le jalon se rattache, et un seul |
| Observable | Phrase vérifiable sans interprétation |
| Indicateur | Source, mesure et seuil ; collecte automatique quand c'est possible |
| Fenêtre | Date de début et date de fin, ancrées sur le calendrier institutionnel quand il existe (source primaire, section 5.1), sinon estimées et signalées comme telles |
| Niveau | 1 : pivot ; 2 : jalon structurant ; 3 : jalon fin |
| Type | État (renseigne le nœud amont lui-même) ou transmission (renseigne le mécanisme) |
| Rôle | Nécessaire au mécanisme, ou seulement favorable |
| Porte sur | La probabilité du lien (M) ou son intensité (I) |
| Vraisemblances | a = P(observé dans la fenêtre si M ou I vrai) et b = P(observé si faux), estimées sachant les jalons antérieurs de la même chaîne |
| Statut | Attendu, observé, en retard, manqué, invalidé |
| Définition | Date de définition ; toute modification est journalisée |

Un jalon de type état est une preuve sur le nœud amont, traitée comme une preuve virtuelle (section 11.4) avec ses vraisemblances fixées à l'avance. Un jalon de transmission est une preuve sur M ou I.

### 10.3 Statuts

| Statut | Condition | Effet |
| --- | --- | --- |
| Attendu | Fenêtre non close, jalon non observé | Aucun |
| Observé | Indicateur au-dessus du seuil dans la fenêtre | Rapport a / b |
| En retard | Fenêtre close depuis moins de 7 jours | Racine carrée du rapport de manque |
| Manqué | Fenêtre close depuis 7 jours ou plus | Rapport (1 − a) / (1 − b), qui remplace le retard |
| Invalidé | Le jalon n'a plus d'objet (par exemple, gouvernement tombé avant sa fenêtre) | Aucun ; motif journalisé |

- **Pas de décroissance liée au temps pour un lien.** Sans jalon attendu dans la fenêtre écoulée, l'estimation du lien ne bouge pas.
- **Les pivots à échéance gardent leur décroissance.** Un événement qui doit survenir avant une date perd de la probabilité à mesure que la fenêtre restante se réduit ; c'est son taux mensuel (section 7.4), distinct des liens.

### 10.4 Mise à jour

1. **Chaîne ordonnée.** Les vraisemblances d'un jalon sont estimées sachant les jalons antérieurs de la chaîne. On ne multiplie pas des rapports estimés indépendamment pour des jalons qui s'impliquent l'un l'autre.
2. **Plafond hebdomadaire.** Pour les jalons favorables, la somme des |log rapport| appliqués à un même lien est plafonnée à log 2 par semaine. Le reliquat est reporté sur les semaines suivantes. Les jalons nécessaires et les résolutions de nœuds ne sont pas plafonnés : ce sont des informations structurantes, et les retarder fausserait le registre.
3. **Recalibrage.** L'analyse trimestrielle compare les fréquences observées des jalons à leurs vraisemblances a et b, et les révise avec trace.

### 10.5 Double compte

- **Indicateur exclusif.** Un indicateur ne sert de preuve qu'à un seul lien. S'il en renseigne plusieurs, son log-rapport est partagé par des poids fixés à l'avance, dont la somme vaut 1.
- **Pas de jalon sur une résolution.** Un indicateur qui tranche un nœud (par exemple, une journée à plus de 500 000 manifestants qui résout la mobilisation) ne peut pas servir de jalon d'intensité ou de transmission.
- **Priorité du jalon.** Un fait prévu comme jalon est traité par le jalon, jamais aussi par la couche des faits imprévus (section 11).

### 10.6 Périmètre et définition

- **Liens suivis.** Les 3 à 5 liens dont la part de variance expliquée sur les pivots principaux est la plus forte (section 4.6), avec au plus 8 jalons par lien.
- **Définition.** Les jalons sont proposés par un agent sur sources primaires. Leurs vraisemblances a et b sont estimées par trois évaluateurs aveugles en un tour, plus un évaluateur d'une autre famille. Agrégation par moyenne des log-cotes.
- **Gel ex ante.** Un jalon est défini et commité au moins 7 jours avant l'ouverture de sa fenêtre. Un jalon ajouté en cours de route ne porte que sur une fenêtre future ; un jalon défini après les faits est interdit.
- **Révision.** Une fenêtre ne peut être déplacée que si le calendrier institutionnel change (report d'un vote, par exemple), avec la source. Le changement est journalisé.

### 10.7 Routine hebdomadaire

Chaque lundi, par script quand c'est possible :
1. Lister les jalons dont la fenêtre s'ouvre, se ferme ou est en cours, pour la semaine et les deux suivantes.
2. Relever les indicateurs collectés automatiquement.
3. Confronter la veille (section 11.2) aux jalons attendus. Le tri commence par cette liste fermée, puis seulement traite les faits imprévus.
4. Mettre à jour les statuts, puis les paramètres des liens, puis propager.
5. Journaliser chaque mise à jour (jalon déclencheur, avant, après) et ajouter les lignes de registre.

Les agents n'interviennent que pour les statuts ambigus (deux évaluateurs ; un troisième en cas de désaccord) et pour la définition de nouveaux jalons.

### 10.8 Questions et notation

- Chaque jalon est une question : « J est-il observé dans sa fenêtre ? ». Sa probabilité est calculée par le réseau. Ces questions forment le pool P2d, groupé par lien.
- Les jalons donnent des questions résolues chaque semaine, ce qui augmente le nombre de grappes disponibles pour les critères de la section 8.6. Ils restent jugés à part de P2b et P2c, pour ne pas mêler la qualité des jalons et celle de la structure.

### 10.9 Affichage

- **Carte sur axe temporel.** L'axe horizontal est le temps. Les pivots sont placés à leur échéance, les jalons dans leur fenêtre, le long des liens qu'ils renseignent.
- **Deux échelles.** La vue semaine montre les niveaux 1 à 3 et le statut des jalons de la semaine et des deux suivantes. La vue macro ne garde que les niveaux 1 et 2.
- **Sur chaque lien :** probabilité, intensité, tendance sur 4 semaines, prochain jalon et sa date. Au survol, ce qui ferait monter ou baisser l'estimation, c'est-à-dire les rapports des prochains jalons s'ils sont observés ou manqués.
- **Chemin réel.** Les jalons observés et les issues résolues sont tracés sur la même carte que les trajectoires prévues.

### 10.10 Critère de maintien

Les chaînes de jalons sont comparées à la même piste sans jalons (faits imprévus seuls), par le Brier pondéré dans le temps sur P2b et P2c. Si elles ne font pas mieux au bilan de la phase 3, au seuil de 10 %, elles sont conservées pour l'affichage et la lecture des enjeux, mais n'agissent plus sur les probabilités.

## 11. Faits imprévus : mises à jour événementielles

Le modèle doit réagir à l'actualité en jours, pas en mois, sans réagir au bruit. Les faits prévus sont traités par les jalons (section 10) ; cette section traite les faits imprévus.

### 11.1 Trois vitesses

| Couche | Ce qui change | Cadence | Qui |
| --- | --- | --- | --- |
| Données | Séries, sondages, cotes | Chaque nuit | `collect.py`, sans IA |
| Jalons | Statut des jalons, probabilité et intensité des liens | Chaque semaine | Script, agents pour les cas ambigus (section 10.7) |
| Évidence | Probabilité d'un nœud non résolu, à la lumière d'un fait imprévu | Sous 72 heures | Tri, puis panel réduit |
| Paramètres et structure | Tables, nœuds | Trimestrielle, sauf révision ciblée (11.3, cas d) | Analyse complète |

### 11.2 Veille et tri

- **Veille.** Chaque nuit, `collect.py` relève les titres de flux publics (agences, presse de référence, Vie publique, Journal officiel) dans `data/veille.json`, gratuitement et sans IA.
- **Tri.** Au moins trois fois par semaine, un modèle léger passe sur les nouveaux titres avec la liste des jalons attendus, puis celle des nœuds et leurs définitions. Un fait qui correspond à un jalon est renvoyé à la section 10. Pour chaque autre fait, il décide du rattachement (nœud ou aucun) et de la matérialité : le fait peut-il déplacer un nœud d'au moins 3 points ?
- **Trace.** Toute décision est consignée, y compris « sans effet », avec son motif.
- **Contrôle du tri.** Chaque mois, un second modèle réexamine un échantillon aléatoire de 20 faits classés sans effet. Si plus de 10 % sont de faux négatifs, le seuil de matérialité est abaissé.

### 11.3 Cinq traitements

| Cas | Quand | Traitement |
| --- | --- | --- |
| a. Sans effet | Non rattaché, ou sous le seuil | Consigné avec motif |
| b. Donnée | Le fait résout un nœud ou mesure une variable (censure votée, candidature déposée, note abaissée) | Le nœud est fixé à son issue et le réseau propagé. Aucun jugement. Possible dès la phase 1 |
| c. Évidence | Le fait renseigne un nœud non résolu, par un canal qu'aucune donnée ne mesure | Preuve virtuelle (11.4) |
| d. Paramètre | Le fait change une relation conditionnelle, et non la probabilité d'un nœud | Révision ciblée des seules lignes concernées. Les évaluateurs voient la ligne actuelle et le fait. Au plus deux révisions par nœud et par trimestre, toutes réexaminées à l'analyse trimestrielle |
| e. Hors modèle | Aucun nœud ne correspond | Question ad hoc prévue directement, notée dans un pool séparé. Nœud candidat à l'analyse trimestrielle |

### 11.4 Preuve virtuelle

- **Principe.** Un fait d'évidence n'est pas une observation du nœud. Il est intégré comme preuve virtuelle (Pearl 1988 ; Chan et Darwiche 2005) : un rapport de vraisemblance entre les issues du nœud, qui se propage de façon cohérente vers l'amont et vers l'aval.
- **Estimation.** Trois évaluateurs aveugles, en un tour, répondent à la question « à quel point ce fait est-il plus probable si l'issue est A que si elle est B ? ». Agrégation par moyenne des log-rapports.
- **Taux de base.** Chaque estimation cite au moins une classe de référence, par exemple l'effet des scandales touchant un chef de parti.
- **Plafond.** Le rapport de vraisemblance est compris entre 1/3 et 3 par fait. Un fait plus décisif relève du cas b.

### 11.5 Garde-fous

- **Pas de double compte.** Si l'effet d'un fait passe par une variable mesurée (sondages, écart de taux), il n'y a pas de mise à jour d'évidence sur ce canal : on attend la donnée.
- **Faits établis.** On met à jour sur des faits établis (authentification, décision, vote), pas sur des réactions ou des rumeurs. Un fait contesté reste en observation, avec une date de réexamen.
- **Revue en différé.** Chaque mise à jour est réexaminée au cycle mensuel suivant, à la lumière des données arrivées.

### 11.6 Trace et affichage

Chaque mise à jour b, c ou d produit de nouvelles lignes de registre pour toutes les questions touchées, horodatées et rattachées au fait. Pour chaque fait, la page montre :
- le traitement et son motif ;
- le nœud touché, avec sa probabilité avant et après ;
- l'effet propagé sur les pivots principaux ;
- la portée maximale, c'est-à-dire l'écart des pivots principaux entre les issues extrêmes du nœud.

### 11.7 Critère de maintien

La couche est comparée à la même piste sans mises à jour événementielles (cycles mensuels seuls), par le Brier pondéré dans le temps sur les questions touchées. Si elle ne fait pas mieux au bilan de la phase 3, au seuil de 10 %, elle est réduite au cas b.

### 11.8 Coût

- **Tri :** un passage de modèle léger, trois fois par semaine.
- **Cas c et d :** trois évaluateurs sur un seul nœud.
- **Plafond :** au plus huit mises à jour c ou d par mois. Au-delà, les faits sont regroupés au cycle mensuel.

## 12. Révisions et gouvernance

- **Cycle mensuel.** Gel des données, génération des questions, prévisions, notation.
- **Analyse trimestrielle.** Révision des paramètres, entrée ou sortie de nœuds, réexamen des révisions ciblées. Le tout est tracé.
- **Protocole.** Il ne change que par une nouvelle version, numérotée en première ligne et journalisée. Le tag et la release `protocole-vX.Y` sont créés automatiquement par GitHub Actions au premier commit de la version sur `main` (`.github/workflows/version-protocole.yml`). Le contrôle échoue si le texte change sans nouveau numéro.
- **Routine hebdomadaire.** Jalons (section 10.7).
- **Interventions humaines.** Toutes sont tracées.
- **Relecture.** Obligatoire à chaque version. Critère d'arrêt : deux relectures consécutives sans défaut bloquant ni important. La mise en production de la phase 3 exige en plus une relecture par un modèle d'une autre famille ou par un prévisionniste humain.

## 13. Limites assumées

- **Cascades sociales et décisions individuelles.** Le modèle peut dire qu'un terrain est propice, pas dater l'étincelle.
- **Élicitation.** Même structurée, elle reste un jugement, et des modèles d'une même famille partagent leurs biais.
- **Puissance.** Seuls des écarts nets de performance seront détectables. Un petit apport de la structure peut passer inaperçu, et la règle par défaut est alors de simplifier.
- **Couche événementielle.** Elle juge vite, donc avec moins de recul. Ses erreurs sont mesurées (section 11.7), pas supposées nulles.
- **Jalons.** Leur qualité dépend de fenêtres bien posées : une fenêtre trop étroite transforme un simple retard en échec du mécanisme. Le recalibrage trimestriel (section 10.4) et le critère de maintien (section 10.10) en mesurent le coût.

## Références

Brier 1950 ; Cameron, Gelbach et Miller 2008 ; Chan et Darwiche 2005 ; Clemen et Winkler 1999 ; Dewar et al. 1993 ; Diebold et Mariano 1995 ; Heckerman et Breese 1996 ; Hemming et al. 2018 ; Kahneman et Lovallo 1993 ; Karger et al. 2024 ; Klein 2007 ; Krippendorff 2004 ; Mellers et al. 2014 ; Murphy 1973 ; Murphy 2002 ; Paleka et al. 2025 ; Pearl 1988 ; Satopää et al. 2014 ; Schwartz 1991.
