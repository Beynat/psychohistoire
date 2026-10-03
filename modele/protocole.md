# Protocole Psychohistoire — version 1.2

Statut : soumis à relecture (relecture 2). Rédigé le 3 octobre 2026, avant toute estimation produite selon ce protocole.
Remplace la version 1.1 (cahier des charges du projet). Toute modification ultérieure crée une version datée, justifiée dans `journal.md`, et un tag Git.

## 0. Historique et pistes

- **Piste exploratoire (v0, v0.2, 3 octobre 2026).** Probabilités produites avant tout protocole (fichier `data.json`, commits du 3 octobre). Elles sont conservées, gelées et notées dans un registre séparé, `registre_exploratoire`. Elles ne servent ni à paramétrer ni à évaluer le modèle du présent protocole.
- **Piste protocole (à partir de v1.2).** Seules les prévisions émises selon ce protocole, après son tag, entrent dans le registre principal.
- Le balayage v1 (dossier `modele/v1`) est conservé comme matière première ; ses étapes de classement et de sélection sont refaites selon les sections 4 et 5.

## 1. Question centrale et frontières

- **Question.** Quelles trajectoires politiques, économiques et sociales pour la France du 1er novembre 2026 au 30 septembre 2028 ?
- **Système modélisé.** La France (institutions, finances publiques, économie, société), plus deux blocs partiellement endogènes, car la France agit sur eux :
  - la BCE, par sa fonction de réaction aux écarts de taux (instrument anti-fragmentation) ;
  - l'Union européenne, par la procédure budgétaire et les marchés.
- **Environnement exogène.** Énergie, taux mondiaux, États-Unis, Chine, conflits, politique allemande et italienne : distributions externes, sans rétroaction.
- **Hors champ.** Comportements individuels, décisions locales, ce qui ne se mesure pas à l'échelle nationale.

## 2. Objets du modèle

| Objet | Définition | Traitement |
| --- | --- | --- |
| Variable d'état | Grandeur mesurable, série publique primaire | Modèle statistique estimé sur l'historique, pas mensuel |
| Événement | Fait binaire, daté ou non, critère de résolution observable | Nœud du réseau, probabilité mensuelle conditionnelle |
| Décision d'acteur | Choix d'une personne ou d'une institution (dissolution, candidature, retrait, alliance, activation de l'instrument BCE) | Nœud du réseau dont les parents sont les déterminants de la décision (intérêt, contraintes, signaux) |
| Moteur exogène | Facteur mondial | Distribution tirée des marchés ou des agrégateurs, propagée sans rétroaction |
| Paramètre prédéterminé | Élément quasi certain sur 24 mois (tendance démographique, calendrier, dette en hausse) | Fixé, avec sa fourchette ; testé en sensibilité |

## 3. Structure probabiliste

1. **Réseau bayésien dynamique** à pas mensuel (Murphy 2002), sur graphe orienté acyclique au sein d'une tranche. Les dépendances d'une tranche à la suivante passent par les variables d'état et par l'occurrence passée des événements.
2. **Parents.** Au plus trois parents intra-tranche par nœud, plus son propre état au mois précédent. Le graphe est réduit par analyse structurelle (section 5.4).
3. **Tables de probabilités conditionnelles explicites** pour chaque nœud (Pearl 1988). Aucune conversion de notes en rapports de cotes. La méthode d'équilibre des impacts croisés (Weimer-Jehle 2006) n'est plus utilisée pour calculer des probabilités : elle sert seulement, en option, à tester la cohérence qualitative de combinaisons de scénarios.
4. **Incertitude des paramètres.** Chaque ligne de table est une loi de Dirichlet (ou bêta) centrée sur l'agrégat des estimateurs. Sa concentration est fixée par leur dispersion. La simulation tire d'abord un jeu de paramètres, puis des trajectoires : au moins 500 jeux × 100 trajectoires. Chaque sortie est publiée avec un intervalle crédible à 80 %.
5. **Calage sur les références.** Pour un nœud doté d'une cote externe fiable, la marginale du modèle est contrainte à cette cote. La rétropropagation se limite aux nœuds en aval, pour éviter tout double compte des dépendances déjà intégrées par le marché. Les questions correspondantes vont dans le pool P1 (section 7.3).
6. **Sensibilité.** Indices globaux de sensibilité (Saltelli 2008) sur les sorties principales, publiés à chaque version.

## 4. Identification des objets

1. **Matière première.** Balayage v1 (74 moteurs, dossier `modele/v1`).
2. **Compléments obligatoires**, signalés par la relecture 1 :
   - décisions d'acteurs (dissolution, candidatures, alliances, retrait, référendum, vacance présidentielle, décisions du Conseil constitutionnel) ;
   - boucle souverain-banques ;
   - fonction de réaction de la BCE ;
   - politique allemande et italienne ;
   - système médiatique et information.

   Ils sont ajoutés par un agent de balayage dédié, sur sources primaires.
3. **Pré-mortem** (Klein 2007). On imagine qu'en septembre 2028 le modèle a lourdement échoué, puis on écrit pourquoi. Ce travail est confié à au moins un modèle d'une autre famille que celle des agents principaux, par l'intermédiaire de Nathan. Les objets manquants qu'il révèle sont ajoutés.
4. **Stabilité.** Le balayage est refait à un mois d'intervalle, avec les mêmes consignes. On publie le recouvrement entre les deux listes (indice de Jaccard). Un objet absent du second balayage et non retenu par les évaluateurs est signalé fragile.
5. **Sources.** Hiérarchie : séries officielles primaires ; données d'agences ; presse de référence ; le reste est seulement indicatif. Tout niveau courant utilisé pour paramétrer provient d'une source primaire ou de `collect.py`. Toute divergence entre sources est tranchée et consignée avant le paramétrage. La date du scrutin est vérifiée sur le décret de convocation.

## 5. Évaluation et sélection

### 5.1 Évaluateurs

- **Nombre.** Au moins cinq évaluateurs par tâche, dont au moins trois modèles différents de la famille principale (par exemple Opus, Sonnet, Haiku), et un ou deux modèles d'autres familles quand Nathan peut les solliciter.
- **Entrées aveugles.** Fiches d'objets réduites au nom, à la définition, au mécanisme et à la mesure : sans colonne de confiance, sans cote externe, sans regroupement suggéré ni note d'un autre évaluateur. L'ordre est aléatoire et différent pour chaque évaluateur.
- **Aucune posture imposée.** Les rôles « sceptique » ou « historien » sont supprimés : la diversité vient des modèles, pas des consignes.
- **Accord publié.** On publie l'alpha de Krippendorff de chaque échelle. Sous 0,67, l'échelle est jugée non fiable : redéfinition et nouveau passage.

### 5.2 Échelles ancrées

- **Impact conditionnel.** Si l'objet se réalise (événement) ou varie d'un écart-type historique (variable), quel effet sur quatre variables cibles nommées, chacune avec des seuils chiffrés par niveau 1 à 5 :
  - l'écart OAT-Bund, en points de base ;
  - la croissance annuelle, en points ;
  - l'intensité protestataire mensuelle (événements ACLED) ;
  - l'issue de la présidentielle, en points de probabilité pour le favori.

  L'impact retenu est le maximum des quatre. Il est toujours noté en conditionnel, jamais pondéré par la probabilité.
- **Probabilité.** Notée à part pour les événements, sur 24 mois, en pourcentage.
- **Incertitude.** Elle n'est plus notée à l'œil :
  - pour un événement, elle est dérivée de sa probabilité médiane p, par 4 × p × (1 − p) ramené à l'échelle 1 à 5 ;
  - pour une variable, c'est la largeur de l'intervalle à 80 % à 24 mois donné par l'évaluateur, rapportée à la variabilité historique sur 24 mois.

### 5.3 Règle de sélection v1.2 (exhaustive)

| Impact médian | Incertitude | Décision |
| --- | --- | --- |
| ≥ 4 | ≥ 4 | Incertitude critique : axe possible des scénarios |
| ≥ 4 | 3 | Retenu |
| ≥ 4 | ≤ 2, variable | Paramètre prédéterminé, conservé |
| ≥ 4 | ≤ 2, événement | Risque extrême, conservé comme nœud rare |
| 3 | ≥ 3 | Retenu |
| 3 | ≤ 2 | Paramètre prédéterminé, conservé |
| ≤ 2 | ≥ 4 | Déclencheur candidat : conservé si son influence indirecte (5.4) dépasse la médiane |
| ≤ 2 | ≤ 3 | Écarté, réexaminé à chaque analyse trimestrielle |

- **Redondance.** Un objet est fusionné dans sa cible quand au moins trois évaluateurs sur cinq le signalent comme redondant avec elle. Le même traitement s'applique à tous les cas.
- **Cas limites.** Un objet à moins d'un demi-point d'un seuil de décision est testé en sensibilité, avec et sans lui.

### 5.4 Analyse structurelle

On établit une matrice d'influences directes (0 à 3) entre objets retenus, avec le même dispositif d'évaluateurs. On calcule ensuite les influences et dépendances indirectes par puissances de matrice (MICMAC, Godet). Cette analyse sert à trois choses :
- choisir les parents de chaque nœud : les trois influences directes les plus fortes ;
- décider du sort des déclencheurs candidats ;
- repérer les variables relais.

## 6. Paramétrage

1. **Variables d'état.** Modèles estimés et rétro-testés sur l'historique :
   - autorégressif avec chocs d'événements pour l'écart de taux ;
   - agrégation bayésienne des sondages pour les intentions de vote (Linzer 2013) ;
   - modèle de comptage auto-excitant pour l'intensité protestataire, sur données ACLED.
2. **Moteurs exogènes.** Distributions implicites des marchés à terme et options, et cotes d'agrégateurs (Metaculus, Polymarket, Good Judgment Open), relevées à date fixe.
3. **Taux de base.** Au moins deux classes de référence par événement (Kahneman et Lovallo 1993), avec leur fourchette ; la classe retenue est justifiée.
4. **Tables conditionnelles.** Élicitation structurée en deux tours, selon le protocole IDEA (Hemming et al. 2018) :
   - premier tour : estimation indépendante et aveugle ;
   - entre les deux : chaque évaluateur voit les estimations et justifications anonymisées des autres ;
   - second tour : réestimation indépendante.

   Agrégation par moyenne des log-cotes (Clemen et Winkler 1999). La dispersion du second tour fixe la concentration de la loi de Dirichlet.
5. **Contrôles.** Cohérence des tables (sommes, monotonie attendue), et confrontation des marginales calculées aux références externes quand elles existent. Un écart de plus de 15 points est examiné et justifié avant publication.

## 7. Questions, notation et validation

### 7.1 Banque de questions

- **Génération mécanique** à chaque cycle mensuel, à partir de :
  - franchissements de seuils des variables d'état à 1, 2 et 3 mois (par exemple « écart OAT-Bund au-dessus de X pb au dernier jour du mois M ») ;
  - occurrence des événements dans le mois ;
  - issues des pivots.
- **Volume.** Objectif : au moins 50 questions par trimestre, 200 à 300 résolues en 12 mois.
- **Grappes.** Chaque question est rattachée à une grappe (pivot ou variable source). L'erreur est estimée par bootstrap par grappes.

### 7.2 Horodatage et absence de fuite

- Les prévisions d'un cycle sont produites à partir de données arrêtées à une date de gel, puis commitées dans le registre, qui est en ajout seul, avant toute autre recherche.
- Aucune question n'est émise si les données de sa résolution sont déjà publiques à la date de gel.

### 7.3 Pools

- **P1.** Questions dotées d'une cote externe. On y mesure l'écart à la référence, pas la valeur propre du modèle.
- **P2.** Questions sans cote externe, et questions conditionnelles. C'est là que se mesure la valeur propre du modèle.

### 7.4 Comparateurs

1. **Lignes de base naïves :** persistance (rien ne change), 50 % partout, taux de base constant.
2. **Références externes**, sur P1.
3. **Ensemble direct :** au moins cinq prévisionnistes IA indépendants avec recherche documentaire, de familles différentes si possible, médiane extrémisée (Baron et al. 2014). Ils traitent chaque question directement, sans le modèle structurel.
4. **Modèle témoin** sans dépendances : nœuds indépendants, mêmes marginales de base.

### 7.5 Scores et tests

- Score de Brier, score logarithmique, décomposition de Murphy (fiabilité, résolution, incertitude) et Brier pondéré dans le temps.
- Comparaisons par test de Diebold-Mariano adapté aux grappes.
- Puissance attendue publiée à chaque bilan.

### 7.6 Critères d'échec fixés à l'avance

À 200 questions résolues, ou au 30 septembre 2027 au plus tard :
- si le modèle ne bat pas l'ensemble direct sur P2 (différence de Brier non significative au seuil de 10 %), le modèle structurel est déclaré sans valeur ajoutée et simplifié ;
- si l'erreur de calibration attendue dépasse 0,10, les probabilités sont recalibrées par régression logistique et la cause est cherchée ;
- si le modèle fait moins bien que la persistance sur P2, le projet est déclaré en échec méthodologique.

### 7.7 Tests sur le passé

- **Composantes statistiques.** Les modèles de variables d'état sont rétro-testés sur 2010-2025.
- **Jugement des modèles de langage.** Il est testé sur des questions résolues entre juillet et septembre 2026, postérieures à la date de coupure des modèles utilisés. Les agents n'ont accès qu'à des données antérieures à la date de chaque question.
- **Étalon externe.** Participation des mêmes agents à un banc public de prévision (ForecastBench, tournois Metaculus) quand c'est possible.

## 8. Scénarios

Deux sorties distinctes :
- **Scénarios prospectifs** : les combinaisons des deux incertitudes critiques les plus influentes, au sens de Schwartz (1991), avec leur probabilité calculée.
- **Familles de trajectoires** : les trajectoires simulées les plus fréquentes, regroupées par issues.

## 9. Révisions et gouvernance

- **Relevé mensuel.** Met à jour états, moteurs exogènes et événements survenus, sans toucher aux paramètres.
- **Analyse trimestrielle.** Peut réviser les paramètres, avec trace.
- **Protocole.** Ne change que par une version taguée.
- **Interventions humaines.** Toutes sont tracées.
- **Relecture externe.** Obligatoire à chaque version du protocole. Critère d'arrêt : deux relectures consécutives sans défaut bloquant ni important. Au moins une relecture par un modèle d'une autre famille, ou par un prévisionniste humain, avant la mise en production.

## 10. Limites assumées

- Les cascades sociales et les décisions individuelles restent les points les plus faibles : le modèle peut dire qu'un terrain est propice, pas dater l'étincelle.
- L'élicitation, même structurée, reste un jugement.
- Avec 200 à 300 questions par an, seuls des écarts de performance nets seront détectables : de petits apports de la structure pourraient passer inaperçus.

## Références

Baron et al. 2014 ; Brier 1950 ; Clemen et Winkler 1999 ; Diebold et Mariano 1995 ; Gelman et Loken 2013 ; Godet (MICMAC) ; Halawi et al. 2024 ; Hemming et al. 2018 ; Kahneman et Lovallo 1993 ; Karger et al. 2024 ; Klein 2007 ; Krippendorff 2004 ; Linzer 2013 ; Mellers et al. 2014 ; Morgan et Henrion 1990 ; Murphy 1973 ; Murphy 2002 ; Pearl 1988 ; Saltelli et al. 2008 ; Schwartz 1991 ; Wack 1985 ; Weimer-Jehle 2006.
