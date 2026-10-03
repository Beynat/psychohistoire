# Protocole Psychohistoire — version 1.3

Statut : soumis à relecture (relecture 3). Rédigé le 3 octobre 2026, avant toute estimation produite selon ce protocole.
Remplace la version 1.2. Les changements sont justifiés dans `v1.3/reponse_relecture_2.md` et `journal.md`. Toute modification ultérieure crée une version datée et un tag Git.

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
| Moteur exogène | Facteur mondial observé ou coté | Entrée fixe, sans rétroaction |
| Paramètre prédéterminé | Variable quasi certaine sur la période (démographie, calendrier) | Fixé avec sa fourchette, testé en sensibilité |
| Risque extrême | Événement rare (moins de 5 % sur la période) à fort impact | Registre séparé, suivi, non modélisé dans le réseau |

## 3. Phasage

Chaque phase doit battre la précédente pour que la suivante soit construite. « Simplifier » signifie revenir à la phase précédente.

| Phase | Date | Contenu | Condition pour passer à la suivante |
| --- | --- | --- | --- |
| 1 | 1er novembre 2026 | Banque de questions, lignes de base, ensemble direct, registre, mises à jour événementielles de type « donnée » | Scripts de génération, de notation et de puissance en service |
| 2 | 1er décembre 2026 | Modèle de l'écart de taux, moyenne de sondages corrigée de l'erreur historique | Rétro-test publié |
| 3 | 1er janvier 2027 au plus tard | Réseau réduit de 10 à 15 nœuds sur la séquence politique et budgétaire, mises à jour événementielles complètes | Relecture par une autre famille de modèles (section 11) |
| 4 | Après le bilan de la phase 3 | Extension du réseau, analyse structurelle complète | La phase 3 bat la phase 1 sur P2b et P2c (section 8.6) |

Chaque phase dispose d'une liste de contrôle dans `modele/controle/`. Tout ce qui est mécanique est scripté : génération des questions, agrégation, notation, puissance.

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

Les événements de probabilité inférieure à 5 % sur la période et d'impact au moins égal à 4 forment un registre séparé. Ils sont suivis par la veille (section 10), sans nœud dans le réseau. Si la probabilité d'un risque extrême dépasse 5 %, son entrée dans le réseau est proposée lors de l'analyse trimestrielle.

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

Une grappe correspond à une variable source sur une fenêtre trimestrielle sans chevauchement. L'objectif est d'au moins 40 grappes pour P2b et P2c réunis. La puissance est simulée et publiée avant le premier cycle de chaque phase.

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

## 10. Mises à jour événementielles

Le modèle doit réagir à l'actualité en jours, pas en mois, sans réagir au bruit.

### 10.1 Trois vitesses

| Couche | Ce qui change | Cadence | Qui |
| --- | --- | --- | --- |
| Données | Séries, sondages, cotes | Chaque nuit | `collect.py`, sans IA |
| Évidence | Probabilité d'un nœud non résolu, à la lumière d'un fait | Sous 72 heures | Tri, puis panel réduit |
| Paramètres et structure | Tables, nœuds | Trimestrielle, sauf révision ciblée (10.3, cas d) | Analyse complète |

### 10.2 Veille et tri

- **Veille.** Chaque nuit, `collect.py` relève les titres de flux publics (agences, presse de référence, Vie publique, Journal officiel) dans `data/veille.json`, gratuitement et sans IA.
- **Tri.** Au moins trois fois par semaine, un modèle léger passe sur les nouveaux titres avec la liste des nœuds et leurs définitions. Pour chaque fait, il décide du rattachement (nœud ou aucun) et de la matérialité : le fait peut-il déplacer un nœud d'au moins 3 points ?
- **Trace.** Toute décision est consignée, y compris « sans effet », avec son motif.
- **Contrôle du tri.** Chaque mois, un second modèle réexamine un échantillon aléatoire de 20 faits classés sans effet. Si plus de 10 % sont de faux négatifs, le seuil de matérialité est abaissé.

### 10.3 Cinq traitements

| Cas | Quand | Traitement |
| --- | --- | --- |
| a. Sans effet | Non rattaché, ou sous le seuil | Consigné avec motif |
| b. Donnée | Le fait résout un nœud ou mesure une variable (censure votée, candidature déposée, note abaissée) | Le nœud est fixé à son issue et le réseau propagé. Aucun jugement. Possible dès la phase 1 |
| c. Évidence | Le fait renseigne un nœud non résolu, par un canal qu'aucune donnée ne mesure | Preuve virtuelle (10.4) |
| d. Paramètre | Le fait change une relation conditionnelle, et non la probabilité d'un nœud | Révision ciblée des seules lignes concernées. Les évaluateurs voient la ligne actuelle et le fait. Au plus deux révisions par nœud et par trimestre, toutes réexaminées à l'analyse trimestrielle |
| e. Hors modèle | Aucun nœud ne correspond | Question ad hoc prévue directement, notée dans un pool séparé. Nœud candidat à l'analyse trimestrielle |

### 10.4 Preuve virtuelle

- **Principe.** Un fait d'évidence n'est pas une observation du nœud. Il est intégré comme preuve virtuelle (Pearl 1988 ; Chan et Darwiche 2005) : un rapport de vraisemblance entre les issues du nœud, qui se propage de façon cohérente vers l'amont et vers l'aval.
- **Estimation.** Trois évaluateurs aveugles, en un tour, répondent à la question « à quel point ce fait est-il plus probable si l'issue est A que si elle est B ? ». Agrégation par moyenne des log-rapports.
- **Taux de base.** Chaque estimation cite au moins une classe de référence, par exemple l'effet des scandales touchant un chef de parti.
- **Plafond.** Le rapport de vraisemblance est compris entre 1/3 et 3 par fait. Un fait plus décisif relève du cas b.

### 10.5 Garde-fous

- **Pas de double compte.** Si l'effet d'un fait passe par une variable mesurée (sondages, écart de taux), il n'y a pas de mise à jour d'évidence sur ce canal : on attend la donnée.
- **Faits établis.** On met à jour sur des faits établis (authentification, décision, vote), pas sur des réactions ou des rumeurs. Un fait contesté reste en observation, avec une date de réexamen.
- **Revue en différé.** Chaque mise à jour est réexaminée au cycle mensuel suivant, à la lumière des données arrivées.

### 10.6 Trace et affichage

Chaque mise à jour b, c ou d produit de nouvelles lignes de registre pour toutes les questions touchées, horodatées et rattachées au fait. Pour chaque fait, la page montre :
- le traitement et son motif ;
- le nœud touché, avec sa probabilité avant et après ;
- l'effet propagé sur les pivots principaux ;
- la portée maximale, c'est-à-dire l'écart des pivots principaux entre les issues extrêmes du nœud.

### 10.7 Critère de maintien

La couche est comparée à la même piste sans mises à jour événementielles (cycles mensuels seuls), par le Brier pondéré dans le temps sur les questions touchées. Si elle ne fait pas mieux au bilan de la phase 3, au seuil de 10 %, elle est réduite au cas b.

### 10.8 Coût

- **Tri :** un passage de modèle léger, trois fois par semaine.
- **Cas c et d :** trois évaluateurs sur un seul nœud.
- **Plafond :** au plus huit mises à jour c ou d par mois. Au-delà, les faits sont regroupés au cycle mensuel.

## 11. Révisions et gouvernance

- **Cycle mensuel.** Gel des données, génération des questions, prévisions, notation.
- **Analyse trimestrielle.** Révision des paramètres, entrée ou sortie de nœuds, réexamen des révisions ciblées. Le tout est tracé.
- **Protocole.** Il ne change que par une version taguée.
- **Interventions humaines.** Toutes sont tracées.
- **Relecture.** Obligatoire à chaque version. Critère d'arrêt : deux relectures consécutives sans défaut bloquant ni important. La mise en production de la phase 3 exige en plus une relecture par un modèle d'une autre famille ou par un prévisionniste humain.

## 12. Limites assumées

- **Cascades sociales et décisions individuelles.** Le modèle peut dire qu'un terrain est propice, pas dater l'étincelle.
- **Élicitation.** Même structurée, elle reste un jugement, et des modèles d'une même famille partagent leurs biais.
- **Puissance.** Seuls des écarts nets de performance seront détectables. Un petit apport de la structure peut passer inaperçu, et la règle par défaut est alors de simplifier.
- **Couche événementielle.** Elle juge vite, donc avec moins de recul. Ses erreurs sont mesurées (section 10.7), pas supposées nulles.

## Références

Brier 1950 ; Cameron, Gelbach et Miller 2008 ; Chan et Darwiche 2005 ; Clemen et Winkler 1999 ; Diebold et Mariano 1995 ; Hemming et al. 2018 ; Kahneman et Lovallo 1993 ; Karger et al. 2024 ; Klein 2007 ; Krippendorff 2004 ; Mellers et al. 2014 ; Murphy 1973 ; Murphy 2002 ; Paleka et al. 2025 ; Pearl 1988 ; Satopää et al. 2014 ; Schwartz 1991.
