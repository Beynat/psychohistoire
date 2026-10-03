# Protocole Psychohistoire — version 1.6

Statut : soumis à relecture (relecture 4). Rédigé le 3 octobre 2026, avant toute estimation produite selon ce protocole. Gelé jusqu'au bilan de la phase 1, sauf corrections exigées par une relecture (section 12).
Remplace la version 1.5. Les changements répondent à la relecture 3 et sont justifiés dans `v1.6/reponse_relecture_3.md` et `journal.md`. Toute modification crée une version datée. Le tag Git `protocole-vX.Y` est posé automatiquement au premier commit de chaque version (section 12).

## 0. Pistes et registres

- **Piste exploratoire (v0, v0.2, 3 octobre 2026).** Les probabilités produites avant tout protocole sont figées dans `registre/exploratoire.jsonl`, en ajout seul. Les mises à jour ultérieures de cette piste y sont ajoutées sans réécrire les lignes antérieures. Elles ne servent ni à paramétrer ni à évaluer le modèle du protocole. `data.json` reste l'état vivant de la page, pas un registre.
- **Piste protocole.** Seules les prévisions émises selon ce protocole, après son tag, entrent dans `registre/protocole.jsonl`, en ajout seul.
- **Format d'une ligne de registre :** `question` (identifiant), `emise` (date et heure), `probabilites` (en %), `piste` (et `phase` pour la piste protocole), `origine` (estimation initiale, cycle mensuel, jalon ou fait imprévu, avec sa référence), `donnees` (commit ou état des données gelées). Une erreur se corrige par une ligne d'erratum, jamais par réécriture.
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
| Lien causal | Arc entre deux nœuds, porté par un mécanisme explicite et un seul sens | Intensité (nulle, faible, forte), renseignée par des jalons (section 10) |
| Jalon | Fait observable attendu dans une fenêtre datée, le long d'un lien | Question notée ; preuve sur le lien une fois sa calibration vérifiée (section 10) |
| Moteur exogène | Facteur mondial observé ou coté | Entrée fixe, sans rétroaction |
| Paramètre prédéterminé | Variable quasi certaine sur la période (démographie, calendrier) | Fixé avec sa fourchette, testé en sensibilité |
| Risque extrême | Événement rare (moins de 5 % sur la période) à fort impact | Registre séparé, suivi, non modélisé dans le réseau |

## 3. Phasage

Chaque phase doit battre la précédente pour que la suivante soit construite. « Simplifier » signifie revenir à la phase précédente.

| Phase | Date | Contenu | Condition pour passer à la suivante |
| --- | --- | --- | --- |
| 1 | 1er novembre 2026 | Banque de questions, lignes de base, ensemble direct, registre, mises à jour événementielles de type « donnée » | Scripts listés dans `modele/controle/phase1.md` en service |
| 2 | 1er décembre 2026 | Modèle de l'écart de taux (série journalière collectée), moyenne de sondages corrigée de l'erreur historique | Rétro-test publié |
| 3 | 1er janvier 2027 au plus tard | Réseau réduit de 10 à 15 nœuds sur la séquence politique et budgétaire, chaînes de jalons sur les 3 à 5 liens les plus influents (affichage et questions, section 10.6), mises à jour sur faits imprévus | Test du jugement passé (section 8.7) et relectures conformes au critère d'arrêt (section 12) |
| 4 | Après le bilan de la phase 3 | Extension du réseau, analyse structurelle complète | La phase 3 bat la phase 1 sur P2b et P2c (section 8.6) |

Avant la phase 3, les chaînes de jalons peuvent être pilotées sur la piste exploratoire, sans effet sur la piste protocole. Chaque phase dispose d'une liste de contrôle dans `modele/controle/`. Tout ce qui est mécanique est scripté : génération des questions, agrégation, notation, puissance.

## 4. Structure probabiliste (phase 3)

1. **Réseau bayésien dynamique** à pas mensuel (Murphy 2002), acyclique au sein d'une tranche. Les dépendances d'une tranche à l'autre passent par les variables d'état et l'occurrence passée des événements.
2. **Parents.** Au plus trois parents intra-tranche par nœud, avec une exception motivée à quatre. Les parents continus sont discrétisés aux quantiles historiques 33 et 67. Si le choix des parents crée un cycle, l'arc le plus faible est renvoyé à la tranche suivante.
3. **Tables de probabilités conditionnelles explicites** (Pearl 1988).
4. **Incertitude des paramètres.** Chaque ligne de table est une loi de Dirichlet centrée sur l'agrégat. Sa concentration est tirée de la dispersion du premier tour d'élicitation, avec un plancher calé sur le test du jugement (section 8.7). Faute d'évaluateurs d'une autre famille, ce plancher n'est jamais inférieur à l'écart observé entre les estimations et les cotes externes du pool P1, mesuré avant calage, une fois celles-ci disponibles. La simulation tire au moins 500 jeux de paramètres, puis 1 000 trajectoires par jeu. Chaque sortie est publiée avec son intervalle crédible à 80 %.
5. **Calage sur les cotes.** Un nœud coté reste dans le réseau. On décale l'ordonnée de sa table, en log-cotes, jusqu'à ce que la marginale calculée égale la cote. La cote est fiable si elle cumule un volume d'au moins 100 000 dollars, un écart entre l'offre et la demande d'au plus 3 points, et porte sur le même événement, résolu à un mois près. Sinon, pas de calage. L'écart entre la marginale non calée et la cote est enregistré avant calage (section 8.4). Les questions calées vont dans P1.
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

- **Effectif.** Au moins cinq évaluateurs, répartis sur au moins trois modèles différents de la famille disponible (par exemple Opus, Sonnet, Haiku). Aucun modèle d'une autre famille n'est disponible : la diversité des évaluateurs reste limitée, ce qui est compensé par le plancher de dispersion (section 4.4) et par la référence externe (section 8.4).
- **Entrées aveugles.** Nom, définition, mécanisme et mesure ; ni cote ni note d'autrui au premier tour. L'ordre est aléatoire et aucune posture n'est imposée.
- **Juge hors famille.** À chaque élicitation de tables, Nathan estime à l'aveugle un échantillon de 10 lignes tirées au sort. Les écarts entre ses estimations et l'agrégat sont publiés ; ils ne modifient pas l'agrégat.
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
- **Questions conjointes** : « A et B avant telle date », pour chaque arc du réseau. Elles se résolvent toujours et dépendent directement des dépendances. Elles appartiennent à la grappe du lien A → B.
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
| P2d | Jalons : « J observé dans sa fenêtre » | Calibration des jalons (section 10.9) |

Une grappe correspond à une variable source, ou à un lien pour les jalons et les questions conjointes, sur une fenêtre trimestrielle sans chevauchement. L'objectif est d'au moins 40 grappes pour P2b et P2c réunis. La puissance est simulée et publiée avant le premier cycle de chaque phase.

### 8.4 Comparateurs

1. **Persistance** : marche aléatoire à la volatilité historique pour les variables, taux de base de la période pour les événements (un statu quo à 0 % rendrait le score logarithmique infini).
2. **Taux de base constant**, et **50 %**.
3. **Références externes** sur P1 : prévision communautaire Metaculus ou prix Polymarket. Ce sont les seuls comparateurs extérieurs à la famille de modèles utilisée ; l'écart à ces références, mesuré avant calage, est publié à chaque bilan, même si le pool P1 ne sert pas aux critères d'échec. Si son signe est systématique (test de signe au seuil de 10 %), les estimations de P2 sont corrigées d'un décalage moyen en log-cotes à l'analyse trimestrielle, avec trace.
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

**Calendrier attendu.** Le réseau démarre au plus tard le 1er janvier 2027 ; seules 10 à 15 grappes seront résolues avant le premier tour de la présidentielle. Les 40 grappes devraient être atteintes vers septembre 2027. Le verdict tombera donc après l'élection, et avec une puissance limitée (environ 55 à 68 % pour un écart de Brier de 0,02, selon la simulation de la relecture 3) : le retour par défaut à la phase 2 est probable, même si la structure est bonne.

### 8.7 Tests sur le passé

- **Composantes statistiques :** rétro-test sur 2010-2025.
- **Jugement :** questions ouvertes publiquement avant le 1er juillet 2026 et résolues ensuite. Pas de recherche web : un script constitue, pour chaque question, un dossier figé à partir de captures archivées datées d'avant son ouverture (Internet Archive). Une question dont le dossier ne peut être constitué est écartée. La coupure de chaque modèle est vérifiée par sondage de faits datés. Le résultat fixe le plancher de dispersion (section 4.4).

## 9. Scénarios

- **Scénarios prospectifs :** combinaisons des deux nœuds en tête du classement, avec leur probabilité.
- **Familles de trajectoires :** trajectoires simulées les plus fréquentes, regroupées par issues.
- **Chemin réel :** tracé sur la carte au fur et à mesure des résolutions.


## 10. Liens causaux et jalons

Un pivot ne bascule pas d'un coup : ce qui y mène passe par des étapes observables. Chaque lien influent est décomposé en une chaîne de jalons datés et fixés à l'avance, comme les indicateurs d'alerte de la planification par hypothèses (Dewar et al. 1993). **Par défaut, les jalons sont affichés et notés, mais n'agissent pas sur les probabilités** ; ils ne deviennent actifs qu'une fois leur calibration vérifiée (section 10.6).

### 10.1 Mécanisme et intensité

- **Mécanisme.** Un lien suivi, du nœud A vers le nœud B, porte un mécanisme écrit en une phrase et un seul sens : une issue de A favorise une issue de B.
- **Intensité.** Chaque lien a un nœud caché racine M, indépendant de A, à trois niveaux : nulle, faible, forte. B garde A pour parent et reçoit M comme parent supplémentaire. Quand A prend l'issue concernée et que M n'est pas nul, la cote de l'issue favorisée de B est décalée de δ_faible ou δ_forte en log-cotes, sur le principe de l'indépendance causale (Heckerman et Breese 1996). La loi jointe reste cohérente, et observer un jalon de transmission ne modifie pas la probabilité de A. Le plafond de parents (section 4.2) ne s'applique pas aux nœuds M.
- **Un seul sens.** Un mécanisme qui peut pousser B dans les deux sens est scindé :
  - si l'orientation dépend d'une décision d'acteur (recul ou non du gouvernement), la décision devient un sous-pivot, nœud de niveau 2 ;
  - sinon (des violences qui radicalisent ou délégitiment un mouvement), le lien est remplacé par deux liens de sens opposés, chacun avec son intensité.

### 10.2 Jalon

| Champ | Contenu |
| --- | --- |
| Lien | Le lien auquel le jalon se rattache, et un seul |
| Observable | Phrase vérifiable sans interprétation |
| Indicateur | Source primaire, mesure et seuil ; collecte automatique quand c'est possible |
| Fenêtre | Date de début et date de fin, ancrées sur le calendrier institutionnel quand il existe, sinon estimées et signalées comme telles |
| Niveau | 1 : pivot ; 2 : jalon structurant ; 3 : jalon fin |
| Type | État amont (renseigne A), transmission (renseigne M), état aval (renseigne B même si A était faux) |
| Rôle | Nécessaire si a ≥ 0,95, sinon favorable |
| Vraisemblances | a = P(observé dans la fenêtre si l'hypothèse est vraie) et b = P(observé si elle est fausse). L'hypothèse est A pour un jalon d'état amont, M non nulle pour un jalon de transmission, l'issue favorisée de B pour un jalon d'état aval. Deux couples (a, b) sont donnés : sachant le jalon précédent de la chaîne observé, et sachant qu'il est manqué |
| Statut | Attendu, en cours, observé, manqué, invalidé |
| Définition | Date de définition et niveau de l'indicateur à cette date ; toute modification est journalisée |

### 10.3 Statuts

| Statut | Condition |
| --- | --- |
| Attendu | Fenêtre non ouverte |
| En cours | Fenêtre ouverte, jalon non observé |
| Observé | Indicateur au seuil dans la fenêtre |
| Manqué | Fenêtre close sans observation |
| Invalidé | Le jalon n'a plus d'objet (gouvernement tombé avant sa fenêtre, par exemple) ; motif journalisé |

### 10.4 Calcul

- **Observé :** rapport a / b.
- **En cours :** rapport (1 − a·F(t)) / (1 − b·F(t)), où F(t) est la part de la fenêtre écoulée, en supposant une date d'observation uniforme dans la fenêtre. Le calcul est fait par script. Il n'y a donc pas de chute à la clôture : la non-observation compte au fur et à mesure.
- **Manqué :** rapport (1 − a) / (1 − b), atteint à la clôture.
- **Réduction contre le bruit.** Tous les log-rapports sont multipliés par un facteur k ≤ 1, calé sur le test du jugement (section 8.7). Il n'y a pas de plafond hebdomadaire.
- **Pivots à échéance.** Un événement qui doit survenir avant une date garde sa décroissance propre (taux mensuel, section 7.4), indépendamment des jalons.

### 10.5 Double compte

- **Indicateur exclusif.** Un indicateur ne sert de preuve qu'à un seul jalon et un seul lien. S'il en renseigne plusieurs, son log-rapport est partagé par des poids fixés à l'avance, dont la somme vaut 1.
- **Pas de jalon sur une résolution.** Un indicateur qui tranche un nœud est traité comme une donnée (section 11.3, cas b), jamais comme jalon.
- **État aval.** Un jalon d'état aval agit sur B comme preuve virtuelle, jamais sur le lien.
- **Priorité du jalon.** Un fait prévu comme jalon est traité par le jalon, jamais aussi comme fait imprévu (section 11).

### 10.6 Activation

- **Par défaut.** Les jalons sont affichés et notés en P2d, sans effet sur les probabilités du réseau.
- **Activation.** Elle est décidée à l'analyse trimestrielle, quand trois conditions sont réunies :
  - au moins 30 jalons sont résolus, tous liens confondus ;
  - leur erreur de calibration est sous le 90e centile de sa distribution simulée sous calibration parfaite ;
  - leur score de Brier bat celui de la fréquence de base des jalons.
- **Exception.** Un lien dont les jalons font moins bien que la fréquence de base reste inactif.
- **Désactivation.** Elle suit la même règle, appliquée à chaque analyse trimestrielle.

### 10.7 Périmètre et définition

- **Liens suivis.** Les 3 à 5 liens dont la part de variance expliquée sur les pivots principaux est la plus forte (section 4.6), avec au plus 8 jalons par lien.
- **Définition.** Les jalons sont proposés par un agent sur sources primaires. Leurs vraisemblances sont estimées par trois évaluateurs aveugles en un tour, sur au moins deux modèles différents, avec agrégation par moyenne des log-cotes.
- **Gel ex ante.**
  - Un jalon est défini et commité au moins 7 jours avant l'ouverture de sa fenêtre.
  - Son seuil ne doit pas avoir été atteint dans les 30 jours précédant sa définition, faute de quoi il ne renseigne rien.
  - Un jalon ajouté en cours de route ne porte que sur une fenêtre future.
  - Le contrôle des registres (section 12) vérifie que les fichiers de jalons ne sont modifiés que par ajout, sauf champs de statut.
- **Révision.** Une fenêtre ne peut être déplacée que si le calendrier institutionnel change (report d'un vote, par exemple), avec la source. Le changement est journalisé.

### 10.8 Routine hebdomadaire

Chaque lundi, par script quand c'est possible :
1. Lister les jalons dont la fenêtre s'ouvre, est en cours ou se ferme, pour la semaine et les deux suivantes.
2. Relever les indicateurs collectés automatiquement.
3. Confronter les faits triés (section 11.2) aux jalons attendus.
4. Mettre à jour les statuts, puis, si les jalons sont actifs, les intensités et la propagation.
5. Journaliser chaque changement (jalon, avant, après) et ajouter les lignes de registre.

Les agents n'interviennent que pour les statuts ambigus (deux évaluateurs ; un troisième en cas de désaccord) et pour la définition de nouveaux jalons.

### 10.9 Questions et notation

Chaque jalon est une question : « J est-il observé dans sa fenêtre ? ». Ces questions forment le pool P2d, groupé par lien. Leur rôle est de mesurer la calibration des jalons (section 10.6), pas d'augmenter la puissance des critères de la section 8.6 : elles en sont exclues.

### 10.10 Affichage

- **Carte sur axe temporel.** L'axe horizontal est le temps. Les pivots sont placés à leur échéance, les jalons dans leur fenêtre, le long des liens qu'ils renseignent.
- **Deux échelles.** La vue semaine montre les niveaux 1 à 3 et le statut des jalons de la semaine et des deux suivantes. La vue macro ne garde que les niveaux 1 et 2.
- **Sur chaque lien :** intensité, tendance sur 4 semaines, prochain jalon et sa date, avec la mention « indicatif » tant que les jalons ne sont pas actifs. Au survol : ce qui ferait monter ou baisser l'estimation.
- **Chemin réel.** Les jalons observés et les issues résolues sont tracés sur la même carte que les trajectoires prévues.

### 10.11 Critère de maintien

Une fois les jalons actifs, on juge la direction de leurs mises à jour : la part de celles qui rapprochent la probabilité de l'issue finalement réalisée, comparée à 50 % par un test de signe. Si cette part n'est pas significativement supérieure à 50 % au seuil de 10 %, à 40 mises à jour, les jalons redeviennent inactifs. Cela ne demande aucune piste parallèle.

## 11. Faits imprévus

Le modèle doit réagir à l'actualité en jours, sans réagir au bruit. Les faits prévus sont traités par les jalons (section 10) ; cette section traite les faits imprévus.

### 11.1 Vitesses

| Couche | Ce qui change | Cadence | Qui |
| --- | --- | --- | --- |
| Données | Séries, sondages, cotes, résolutions | Chaque nuit | `collect.py`, sans IA |
| Jalons | Statuts ; intensités des liens si actifs | Chaque semaine | Script, agents pour les cas ambigus |
| Évidence | Probabilité d'un nœud non résolu, à la lumière d'un fait imprévu | Sous 72 heures | Tri, puis panel |
| Paramètres et structure | Tables, nœuds | Trimestrielle, sauf révision ciblée (cas d) | Analyse complète |

### 11.2 Veille et tri

- **Veille.** Chaque nuit, `collect.py` relève sans IA les titres des flux de franceinfo, Le Monde, LCP (Assemblée nationale) et Public Sénat dans `data/veille.json`. Les agences et le Journal officiel n'offrent pas de flux libre ; une décision officielle est vérifiée sur sa source primaire au moment du tri.
- **Conservation.** Un titre non trié n'est jamais purgé. Les titres triés sont conservés 10 jours.
- **Tri.** Au moins trois fois par semaine, un modèle léger :
  - regroupe les titres par fait, en supprimant les doublons ;
  - rattache chaque fait à un jalon attendu, à un nœud ou à rien.

  Il ne juge pas la matérialité : c'est le rôle du panel (section 11.4). Les décisions de tri sont écrites dans `data/tri.json`, que la collecte ne modifie pas.
- **Trace.** Toute décision est consignée, y compris « non rattaché », avec son motif.
- **Contrôle du tri.** Chaque trimestre, un second modèle réexamine 60 faits non rattachés tirés au sort. Plus de 10 % de faux négatifs (borne inférieure de l'intervalle à 80 % au-dessus de 5 %) entraînent une révision de la consigne de tri.

### 11.3 Traitements

| Cas | Quand | Traitement |
| --- | --- | --- |
| a. Sans effet | Non rattaché, ou effet jugé nul par le panel | Consigné avec motif |
| b. Donnée | Le fait résout un nœud ou mesure une variable, selon une source primaire officielle ou la collecte | Le nœud est fixé à son issue et le réseau propagé. Aucun jugement |
| c. Évidence | Le fait renseigne un nœud non résolu, par un canal qu'aucune donnée ne mesure | Preuve virtuelle (section 11.4) |
| d. Paramètre | Le fait changerait encore l'enfant si le parent était connu : il modifie une relation, pas la probabilité d'un nœud | Révision ciblée des lignes concernées, avec le même plafond, le même seuil d'application et les mêmes garde-fous que le cas c. Les évaluateurs ne voient pas la ligne actuelle au premier tour |
| e. Hors modèle | Aucun nœud ne correspond | Question ad hoc prévue directement, notée dans un pool séparé. Nœud candidat à l'analyse trimestrielle |
| f. En observation | Fait contesté, ou dont l'effet passe d'abord par une donnée à venir | Aucune mise à jour ; date de réexamen fixée |

### 11.4 Preuve virtuelle

- **Principe.** Un fait d'évidence est intégré comme preuve virtuelle (Pearl 1988 ; Chan et Darwiche 2005) : un rapport de vraisemblance entre les issues du nœud, propagé vers l'amont et vers l'aval.
- **Conditions.**
  - Un fait par valence : des éléments de sens opposés sont des faits distincts.
  - Le fait est postérieur au gel de la dernière estimation du nœud.
  - Il est rattaché au nœud le plus en amont quand plusieurs nœuds sont concernés.
  - Le rapport est estimé sachant les faits déjà intégrés sur ce nœud, qui sont présentés aux évaluateurs.
- **Estimation.** Trois évaluateurs aveugles, en un tour, estiment P(fait | issue) pour chaque issue, en citant au moins une classe de référence. Agrégation par moyenne des log-rapports.
- **Seuil d'application.** Pas de mise à jour si les évaluateurs divergent de signe, ou si la moyenne des log-rapports est à moins de deux erreurs types de zéro. Le fait est alors classé sans effet, avec ce motif.
- **Plafond.** Rapport entre 1/3 et 3 avec trois évaluateurs. Un fait jugé très diagnostique peut être porté à cinq évaluateurs, avec un plafond de 10.
- **Réduction.** Le facteur k (section 10.4) s'applique.

### 11.5 Garde-fous

- **Pas de double compte.** Si l'effet d'un fait passe par une variable mesurée (sondages, écart de taux), il n'y a pas de mise à jour sur ce canal : on attend la donnée. Pour un nœud de décision d'acteur, la question posée aux évaluateurs précise « à intentions de vote inchangées », et le nœud a les sondages pour parent.
- **Faits établis.** Un fait contesté reste en observation (cas f).
- **Sources.** Un comptage produit par une partie prenante (syndicat, parti, organisateur) n'est jamais une donnée : c'est au mieux un indice, avec une confiance faible.
- **Revue en différé.** Chaque mise à jour est réexaminée au cycle mensuel suivant, à la lumière des données arrivées.

### 11.6 Trace et affichage

Chaque mise à jour b, c ou d produit de nouvelles lignes de registre pour toutes les questions touchées, horodatées et rattachées au fait. Pour chaque fait, la page montre :
- le traitement et son motif ;
- le nœud touché, avec sa probabilité avant et après ;
- l'effet propagé sur les pivots principaux ;
- la portée maximale : l'écart des pivots principaux entre les issues extrêmes du nœud.

### 11.7 Critère de maintien

On juge la direction des mises à jour c et d : la part de celles qui rapprochent la probabilité de l'issue réalisée, ou de la donnée arrivée ensuite, comparée à 50 % par un test de signe. Si cette part n'est pas significativement supérieure à 50 % au seuil de 10 %, à 40 mises à jour, la couche est réduite aux cas b et f.

### 11.8 Coût

- **Tri :** un passage de modèle léger, trois fois par semaine.
- **Cas c et d :** trois évaluateurs sur un seul nœud, cinq pour un fait très diagnostique.
- **Plafond :** au plus huit mises à jour c ou d par mois. Au-delà, les faits sont regroupés au cycle mensuel.

## 12. Révisions, exécution et gouvernance

- **Cycle mensuel.** Gel des données, génération des questions, prévisions, notation.
- **Analyse trimestrielle.** Révision des paramètres, entrée ou sortie de nœuds, réexamen des révisions ciblées, activation des jalons (section 10.6), correction du biais commun (section 8.4). Le tout est tracé.
- **Déclencheurs.**
  - La collecte nocturne, la pose des tags et le contrôle des registres passent par GitHub Actions.
  - Le tri, la routine hebdomadaire, le cycle mensuel et l'analyse trimestrielle passent par des tâches planifiées de Claude, créées après le gel.
- **Rattrapage.** Un passage manqué est rattrapé au passage suivant, en conservant la date des faits. Au-delà de 7 jours de retard, il est déclaré manqué au journal, sans prévision rétroactive.
- **Registres.** Un workflow vérifie à chaque commit que les registres et les fichiers de jalons ne sont modifiés que par ajout de lignes.
- **Protocole.**
  - Il ne change que par une nouvelle version, numérotée en première ligne et journalisée.
  - Le tag et la release `protocole-vX.Y` sont créés automatiquement au premier commit de la version sur `main`. Le contrôle échoue si le texte change sans nouveau numéro.
  - Après la v1.6, le protocole est gelé jusqu'au bilan de la phase 1 : seules des corrections de défauts relevés en relecture peuvent produire une version.
- **Interventions humaines.** Toutes sont tracées.
- **Relecture.** Obligatoire à chaque version. Le critère d'arrêt est de deux relectures consécutives sans défaut bloquant ni important. Le relecteur est de la même famille que les auteurs ; ses relectures sont conduites en sessions séparées, sans accès aux échanges de rédaction.

## 13. Limites assumées

- **Cascades sociales et décisions individuelles.** Le modèle peut dire qu'un terrain est propice, pas dater l'étincelle.
- **Une seule famille de modèles.**
  - Évaluateurs, ensemble direct et relecteur partagent les mêmes biais. Un biais commun déplace le centre des estimations et s'annule dans la comparaison au témoin.
  - Les seuls contrôles extérieurs sont les cotes du pool P1, l'échantillon estimé par Nathan et la résolution des questions.
  - Aucun humain formé aux probabilités ne relit le protocole.
- **Puissance.** Seuls des écarts nets de performance seront détectables, et le verdict de la phase 3 tombera après la présidentielle. Un petit apport de la structure peut passer inaperçu ; la règle par défaut est alors de simplifier.
- **Jalons et faits imprévus.** Leurs paramètres se vérifient mal individuellement. C'est pourquoi les jalons n'agissent qu'après vérification de leur calibration, et les faits imprévus seulement au-delà d'un seuil d'application.

## Références

Brier 1950 ; Cameron, Gelbach et Miller 2008 ; Chan et Darwiche 2005 ; Clemen et Winkler 1999 ; Dewar et al. 1993 ; Diebold et Mariano 1995 ; Heckerman et Breese 1996 ; Hemming et al. 2018 ; Kahneman et Lovallo 1993 ; Karger et al. 2024 ; Klein 2007 ; Krippendorff 2004 ; Mellers et al. 2014 ; Murphy 1973 ; Murphy 2002 ; Paleka et al. 2025 ; Pearl 1988 ; Satopää et al. 2014 ; Schwartz 1991.
