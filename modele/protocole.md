# Protocole Psychohistoire — version 1.10

Statut : soumis à relecture (relecture 7). Rédigé le 3 octobre 2026, avant toute estimation produite selon ce protocole. Gelé jusqu'au bilan de la phase 1, sauf corrections exigées par une relecture (section 12).
Remplace la version 1.9. Les changements répondent aux relectures 6 et 6 bis et sont justifiés dans `v1.10/reponse_relecture_6.md` et `journal.md`. Le texte est scindé : ce noyau (sections 0 à 9, 12 et 13) et l'annexe `annexe_phase3.md` (sections 10 et 11), gelés et tagués séparément. Toute modification crée une version datée. Le tag Git `protocole-vX.Y` est posé automatiquement au premier commit de chaque version (section 12).

## 0. Pistes et registres

- **Piste exploratoire (v0, v0.2, 3 octobre 2026).** Les probabilités produites avant tout protocole sont figées dans `registre/exploratoire.jsonl`, en ajout seul. Les mises à jour ultérieures de cette piste y sont ajoutées sans réécrire les lignes antérieures. Elles ne servent ni à paramétrer ni à évaluer le modèle du protocole. `data.json` reste l'état vivant de la page, pas un registre.
- **Piste protocole.** Seules les prévisions émises selon ce protocole, après son tag, entrent dans `registre/protocole.jsonl`, en ajout seul.
- **Format d'une ligne de registre :** `question` (identifiant), `emise` (date et heure), `probabilites` (en %), `piste` (et `phase` pour la piste protocole), `origine` (estimation initiale, cycle mensuel, jalon ou fait imprévu, avec sa référence), `donnees` (commit ou état des données gelées). Le champ `emise` est écrit par `scripts/registre.py` à partir de l'horloge système, jamais par un agent, et contrôlé à la poussée (section 12). Une erreur se corrige par une ligne d'erratum, jamais par réécriture.
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
| Lien causal | Arc entre deux nœuds, porté par un mécanisme explicite et un seul sens | Intensité (nulle, faible, forte), renseignée par des jalons (annexe, section 10) |
| Jalon | Fait observable attendu dans une fenêtre datée, le long d'un lien | Question notée ; preuve sur le lien une fois validée la direction de ses mises à jour fantômes (annexe, section 10.6) |
| Moteur exogène | Facteur mondial observé ou coté | Entrée fixe, sans rétroaction |
| Paramètre prédéterminé | Variable quasi certaine sur la période (démographie, calendrier) | Fixé avec sa fourchette, testé en sensibilité |
| Risque extrême | Événement rare (moins de 5 % sur la période) à fort impact | Registre séparé, suivi, non modélisé dans le réseau |

## 3. Phasage

Les phases 2 et 3 sont construites selon le calendrier ; la phase 4 seulement si la phase 3 a battu la phase 1. Si les critères de la section 8.6 échouent, on revient à la phase précédente : c'est ce que « simplifier » veut dire.

| Phase | Date | Contenu | Condition pour passer à la suivante |
| --- | --- | --- | --- |
| 1 | 1er novembre 2026 | Banque de questions, lignes de base, ensemble direct, registre, données arrivées en cours de cycle (section 8.9) | Scripts listés dans `modele/controle/phase1.md` en service |
| 2 | 1er décembre 2026 | Modèle de l'écart de taux (série journalière collectée), moyenne de sondages corrigée de l'erreur historique | Rétro-test publié |
| 3 | 1er janvier 2027 au plus tard | Réseau réduit de 10 à 15 nœuds sur la séquence politique et budgétaire, chaînes de jalons et faits imprévus (annexe phase 3) | Test du jugement passé (section 8.7) et relectures conformes au critère d'arrêt (section 12) |
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
| P2d | Jalons : « J observé dans sa fenêtre » | Descriptif : calibration des jalons, sans décision attachée (annexe, section 10.9) |

Une grappe correspond à une variable source, ou à un lien pour les jalons et les questions conjointes, sur une fenêtre trimestrielle sans chevauchement. L'objectif est d'au moins 40 grappes pour P2b et P2c réunis. La puissance est simulée et publiée avant le premier cycle de chaque phase.

### 8.4 Comparateurs

1. **Persistance** pour les variables : marche aléatoire à la volatilité historique.
2. **Taux de base** pour les événements, sur la période de la question (un statu quo à 0 % rendrait le score logarithmique infini), et **50 %**.
3. **Références externes** sur P1 : prévision communautaire Metaculus ou prix Polymarket. Ce sont les seuls comparateurs extérieurs à la famille de modèles utilisée ; l'écart à ces références, mesuré avant calage, est publié à chaque bilan, même si le pool P1 ne sert pas aux critères d'échec. Si son signe est systématique (test de signe au seuil de 10 %), les estimations de P2 du modèle et de l'ensemble direct sont corrigées du même décalage moyen en log-cotes à l'analyse trimestrielle, avec trace. Les critères de la section 8.6 sont jugés sur les estimations non corrigées.
4. **Ensemble direct** : au moins cinq prévisionnistes IA avec recherche, médiane non extrémisée. Son écart au taux de base est publié à chaque bilan, sans décision attachée : si l'ensemble ne bat pas le taux de base, une victoire du modèle sur l'ensemble prouve peu.
5. **Modèle témoin** : mêmes marginales, nœuds indépendants, sans dépendances.

### 8.5 Scores et tests

- **Scores :** Brier, score logarithmique, décomposition de Murphy, Brier pondéré dans le temps. Ce dernier vaut, pour une question ouverte du jour d'émission t₀ au jour de clôture T, la moyenne sur chaque jour t de (p_t − y)², où p_t est la dernière probabilité inscrite au registre ce jour-là et y l'issue (0 ou 1).
- **Tests :** Diebold-Mariano par grappes, ou test de permutation par grappes s'il y en a moins de 40.

### 8.6 Critères d'échec fixés à l'avance

Évalués à 40 grappes résolues sur P2b et P2c, ou au plus tard au 30 septembre 2027 :
- **Valeur ajoutée.** Si la phase 3 ne bat pas l'ensemble direct (phase 1) sur P2b et P2c, au seuil de 10 %, le modèle structurel est déclaré sans valeur ajoutée et l'on revient à la phase 2.
- **Calibration.** Si l'erreur de calibration dépasse le 90e centile de sa distribution simulée sous calibration parfaite, au même nombre de questions, les probabilités sont recalibrées et la cause est cherchée.
- **Persistance.** Si la persistance (variables) ou le taux de base (événements) bat le modèle sur P2 au seuil de 10 %, le projet est déclaré en échec méthodologique.

Ces critères portent sur les estimations non corrigées du biais commun (section 8.4).

**Calendrier attendu.** Le réseau démarre au plus tard le 1er janvier 2027 ; seules 10 à 15 grappes seront résolues avant le premier tour de la présidentielle. Les 40 grappes devraient être atteintes vers septembre 2027. Le verdict tombera donc après l'élection, et avec une puissance limitée (environ 55 à 68 % pour un écart de Brier de 0,02, selon la simulation de la relecture 3) : le retour par défaut à la phase 2 est probable, même si la structure est bonne.

### 8.7 Tests sur le passé

- **Composantes statistiques :** rétro-test sur 2010-2025.
- **Jugement :** questions ouvertes publiquement avant le 1er juillet 2026 et résolues ensuite. Pas de recherche web : un script constitue, pour chaque question, un dossier figé à partir de captures archivées datées d'avant son ouverture (Internet Archive). Le choix des pages est mécanique : le texte de la question, plus une liste fixe de pages (articles Wikipédia en français et en anglais des entités nommées dans la question, pages d'accueil de franceinfo et du Monde) à la date d'ouverture. Une question dont le dossier ne peut être constitué est écartée. Le test porte sur au moins 50 questions ; s'il y en a moins sur la France, il est élargi à l'Europe, puis au reste du monde. La coupure de chaque modèle est vérifiée par sondage de faits datés. Le résultat fixe le plancher de dispersion (section 4.4).

### 8.8 Résolution des questions

- **Banque d'événements de la phase 1.** Avant le 1er novembre 2026, un fichier `modele/evenements.json` reprend tous les événements et décisions du balayage v1 dotés d'un critère de résolution (écrits dans `modele/v1/fusion.md`), sans sélection par l'agent. Il est commité avant le premier cycle et ne change qu'à l'analyse trimestrielle, par ajout.
- **Qui résout.** Les questions sur des séries sont résolues par script, sur la série collectée. Les questions sur des événements le sont sur une source primaire officielle (Journal officiel, Assemblée nationale, Conseil constitutionnel, ministère), citée avec sa date.
- **Cas ambigu.** Deux agents résolvent indépendamment. S'ils divergent, un troisième tranche. Si le désaccord persiste ou si la source primaire manque 30 jours après l'échéance, la question est annulée pour tous les comparateurs, avec motif.
- **Résolution antérieure à la poussée.** Une prévision dont la question était déjà résolue à la date de poussée de sa ligne de registre (section 12) est annulée, pour le comparateur concerné, avec motif.

### 8.9 Données arrivées en cours de cycle

Dès la phase 1, un fait qui résout une question ou mesure une variable, selon une source primaire officielle ou la collecte (censure votée, candidature déposée, note abaissée, série publiée), est appliqué sans jugement : la question est résolue, et les prévisions qui en dépendent reçoivent de nouvelles lignes de registre (en phase 3, le nœud correspondant est fixé à son issue). La détection passe par la veille et le tri décrits dans l'annexe (section 11.2), limités en phases 1 et 2 à ce seul cas. Un comptage produit par une partie prenante (syndicat, parti, organisateur) n'est jamais une donnée.

## 9. Scénarios

- **Scénarios prospectifs :** combinaisons des deux nœuds en tête du classement, avec leur probabilité.
- **Familles de trajectoires :** trajectoires simulées les plus fréquentes, regroupées par issues.
- **Chemin réel :** tracé sur la carte au fur et à mesure des résolutions.


## 10 et 11. Liens, jalons et faits imprévus

Ces deux sections forment l'annexe `annexe_phase3.md`, qui ne s'applique qu'à partir de la phase 3 (sauf la section 8.9 et le pilote sur la piste exploratoire). En résumé :
- les liens influents sont décomposés en jalons datés et gelés à l'avance, affichés et notés, mais sans effet sur les probabilités tant que la direction de leurs mises à jour fantômes n'est pas validée ;
- les faits imprévus ne déplacent un nœud que s'ils franchissent un seuil d'application.

## 12. Révisions, exécution et gouvernance

- **Cycle mensuel.** Gel des données, génération des questions, prévisions, notation.
- **Analyse trimestrielle.** Révision des paramètres, entrée ou sortie de nœuds, réexamen des révisions ciblées, activation des jalons et estimation des facteurs k (annexe, sections 10.4, 10.6 et 11.4), correction du biais commun (section 8.4). Le tout est tracé.
- **Déclencheurs.**
  - La collecte nocturne, la pose des tags et le contrôle des registres passent par GitHub Actions.
  - Le tri, la routine hebdomadaire, le cycle mensuel et l'analyse trimestrielle passent par des tâches planifiées de Claude, créées après le gel.
- **Rattrapage.** Un passage manqué est rattrapé au passage suivant, en conservant la date des faits. Au-delà de 7 jours de retard, il est déclaré manqué au journal, sans prévision rétroactive.
- **Registres.**
  - Seul `scripts/registre.py` écrit dans les registres ; il fixe l'horodatage à partir de l'horloge système.
  - Un workflow vérifie à chaque poussée que les registres, les journaux de jalons et les décisions de tri (en JSONL, une ligne par décision) ne sont modifiés que par ajout, sans suppression ni renommage de fichier (`--no-renames`). Il vérifie aussi que chaque nouvelle ligne de registre (champ `emise`) et chaque nouvelle définition de jalon (champ `defini_le`) est datée, avec son fuseau horaire, dans les deux heures qui précèdent la poussée. La date de poussée fait foi : une question résolue avant elle est annulée (section 8.8).
  - La branche `main` et les tags `protocole-v*` et `annexe-phase3-v*` sont protégés contre la suppression et la réécriture. Un contrôle obligatoire n'est pas retenu : il imposerait des demandes de fusion et bloquerait la poussée directe de la collecte nocturne et des agents. Le contrôle est donc détectif : un échec est public et se corrige par une ligne d'erratum.
- **Protocole.**
  - Il ne change que par une nouvelle version, numérotée en première ligne et journalisée.
  - Le noyau et l'annexe sont versionnés séparément. Les tags et releases `protocole-vX.Y` et `annexe-phase3-vX.Y` sont créés automatiquement au premier commit de chaque version sur `main`. Le contrôle échoue si un texte change sans nouveau numéro.
  - Le noyau et l'annexe sont gelés jusqu'au bilan de la phase 1, tenu à la première analyse trimestrielle (début février 2027). Pendant le gel, une version n'est possible que pour corriger un défaut relevé en relecture, ou pour retirer une exigence devenue inexécutable, sur décision humaine journalisée. Tout ajout est exclu.
- **Interventions humaines.** Toutes sont tracées.
- **Relecture.** Obligatoire à chaque version. Le critère d'arrêt est de deux relectures consécutives sans défaut bloquant ni important. Le relecteur est de la même famille que les auteurs ; ses relectures sont conduites en sessions séparées, sans accès aux échanges de rédaction.

## 13. Limites assumées

- **Cascades sociales et décisions individuelles.** Le modèle peut dire qu'un terrain est propice, pas dater l'étincelle.
- **Une seule famille de modèles.**
  - Évaluateurs, ensemble direct et relecteur partagent les mêmes biais. Un biais commun déplace le centre des estimations et s'annule dans la comparaison au témoin.
  - Les seuls contrôles extérieurs sont les cotes externes (pool P1, section 8.4) et la résolution des questions. Aucun juge hors famille, humain ou modèle, n'est disponible : les lignes conditionnelles des tables n'ont aucun contrôle extérieur.
  - Aucun humain formé aux probabilités ne relit le protocole.
- **Puissance.** Seuls des écarts nets de performance seront détectables, et le verdict de la phase 3 tombera après la présidentielle. Un petit apport de la structure peut passer inaperçu ; la règle par défaut est alors de simplifier.
- **Jalons et faits imprévus.** Leurs paramètres se vérifient mal individuellement. C'est pourquoi les jalons n'agissent qu'après validation de la direction de leurs mises à jour fantômes, et les faits imprévus seulement au-delà d'un seuil d'application.

## Références

Brier 1950 ; Cameron, Gelbach et Miller 2008 ; Chan et Darwiche 2005 ; Clemen et Winkler 1999 ; Dewar et al. 1993 ; Diebold et Mariano 1995 ; Heckerman et Breese 1996 ; Hemming et al. 2018 ; Kahneman et Lovallo 1993 ; Karger et al. 2024 ; Klein 2007 ; Krippendorff 2004 ; Mellers et al. 2014 ; Murphy 1973 ; Murphy 2002 ; Paleka et al. 2025 ; Pearl 1988 ; Satopää et al. 2014 ; Schwartz 1991.
