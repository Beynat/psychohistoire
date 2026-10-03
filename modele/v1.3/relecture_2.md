# Relecture 2 (protocole v1.2, commit d380abf)

Relecteur externe, reçue le 3 octobre 2026. Texte intégral, non modifié.

Je récupère la v1.2 dans le dépôt et je la lis avant de répondre.

**Verdict.** La v1.2 corrige le fond de la relecture 1 : cœur probabiliste cohérent dans son principe, pools séparés, critères d'échec préalables, pistes distinguées. Mais le critère d'échec central ne teste pas ce qu'il prétend tester, et le protocole n'est pas exécutable tel qu'écrit avant le 1er novembre avec les moyens décrits. Il reste donc deux défauts bloquants et six importants, dont plusieurs introduits par les corrections.

J'ai relu le protocole, la réponse, le journal, le README, `data.json` et `collect.py` au commit `d380abf`. Les chiffres de puissance viennent de simulations que j'ai refaites, sous hypothèses indiquées.

## 1. Suivi des points de la relecture 1

| Point | Jugement | Motif |
|---|---|---|
| B1 Puissance | Insuffisante | Le volume est là, pas l'indépendance : voir N1. |
| B2 Circularité | Suffisante sur le principe | Les pools règlent la mesure ; le calage reste indéfini (N3). |
| B3 Cœur probabiliste | Suffisante sur le principe | Tables explicites et incertitude paramétrique ; l'élicitation mensuelle crée un nouveau problème (N4). |
| B4 Antériorité | Insuffisante à ce jour | Aucun tag dans le dépôt, alors que le README dit « version taguée » ; `registre_exploratoire` n'existe pas. |
| I1 Indépendance | Insuffisante | Opus, Sonnet et Haiku sont une même famille ; les modèles externes restent facultatifs. |
| I2 Échelles | Insuffisante | Les « seuils chiffrés par niveau » ne sont pas dans le texte (N5). |
| I3 Règle | Insuffisante | La règle dite exhaustive ne l'est plus avec une incertitude continue (N5). |
| I4 Sources | Suffisante en règle | Non exécutable en l'état : `collect.py` ne collecte que 7 séries et les agents ont essuyé des refus sur HCFP, FMI et Banque de France. |
| I5 Ancrage | Suffisante | Mais le second balayage à un mois contredit le démarrage au 1er novembre (N2). |
| I6 Exhaustivité | Suffisante | Le rejet du modèle multi-agents est bien fondé. |
| I7 Contamination | Insuffisante | Le test sur juillet-septembre 2026 fuit (N6). |
| Ensemble direct | Suffisante, sauf l'extrémisation | Mal fondée pour des modèles corrélés (N7). |
| Variables estimées | Mal fondée en partie | Linzer et ACLED ne conviennent pas tels quels (N2). La référence à Linzer venait de moi. |
| Deux scénarios, scores | Suffisantes | Réserve mineure sur le seuil de calibration (voir améliorations). |
| Étalon externe | Insuffisante | « Quand c'est possible » n'engage à rien. |

## 2. Défauts bloquants

**N1. Le critère d'échec ne teste pas la structure.**
- **Constat.** P2 sera dominé par les questions de seuil sur les variables d'état, générées à 1, 2 et 3 mois. Elles sont résolues par les modèles statistiques, pas par le réseau. Les questions conditionnelles ne se résolvent que si la condition se réalise, donc rarement.
- **Problème.** « Battre l'ensemble direct sur P2 » jugera surtout le modèle autorégressif. De plus, ces questions se chevauchent : 240 questions en 12 grappes valent 36 questions indépendantes si la corrélation intra-grappe est de 0,3. La puissance pour un écart de Brier net (0,02), au seuil de 10 % :

| Découpage de 240 questions | Corrélation 0,1 | Corrélation 0,3 |
|---|---|---|
| 12 grappes de 20 | 52 % | 34 % |
| 60 grappes de 4 | 75 % | 61 % |
| 240 questions indépendantes | 83 % | 83 % |

  Pour un écart faible (0,007), elle reste sous 30 % dans tous les cas. Le bootstrap par grappes est par ailleurs peu fiable sous 30 à 40 grappes (Cameron, Gelbach et Miller 2008).
- **Correction.** Scinder P2 en trois : variables, événements et décisions sans cote, questions structurelles. Juger la structure sur les deux derniers. Remplacer les conditionnelles par des questions conjointes (« A et B avant telle date »), qui se résolvent toujours et dépendent directement des dépendances. Définir la grappe comme une variable source sur une fenêtre de temps sans chevauchement, et viser au moins 40 grappes.

**N2. Le protocole n'est pas exécutable avant le 1er novembre.**
- **Constat.** Sont exigés avant la première prévision : balayage complémentaire, pré-mortem, second balayage à un mois, cinq évaluateurs, matrice d'influences, tables en deux tours, trois modèles statistiques rétro-testés sur 2010-2025, indices de Saltelli, banque de questions, ensemble direct. Sur les données v1, 39 objets sur 74 ont un impact médian d'au moins 3, et la règle les conserve tous.
- **Problème.**
  - La matrice compte environ 1 500 cases et les tables plusieurs centaines de lignes, chacune estimée par cinq évaluateurs en deux tours. Le relais manuel par Nathan vers des modèles externes est impraticable à cette échelle.
  - À ma connaissance, ACLED ne couvre la France que depuis 2020 et demande un compte. Un rétro-test 2010-2025 est impossible et les Gilets jaunes sont hors données. À vérifier.
  - Le modèle de Linzer est conçu pour un scrutin américain par États. Une présidentielle à deux tours avec candidatures incertaines demande un autre modèle, testable sur cinq scrutins au plus.
  - Les chocs d'événements sur l'écart de taux ne sont pas estimables : une dissolution depuis 2010.
- **Conséquence.** Les agents combleront par approximation, ce que le protocole veut éviter.
- **Correction.** Définir une version minimale et la phaser :
  1. ensemble direct et lignes de base, dès novembre ;
  2. modèle statistique de l'écart de taux et agrégateur de sondages simple ;
  3. réseau réduit à 10 ou 15 nœuds sur la séquence politique et budgétaire ;
  4. extension seulement si l'étape 3 bat l'étape 1.

## 3. Défauts importants

**N3. Calage des nœuds cotés indéfini.**
Contraindre la marginale d'un nœud qui a des parents, sans mettre à jour l'amont, rend la loi jointe incohérente : la marginale forcée ne correspond plus aux tables. « Cote fiable » n'est pas défini, et les horizons des marchés diffèrent du pas mensuel. Correction en question ouverte 1.

**N4. Élicitation de probabilités mensuelles.**
- **Constat.** Les tables portent des probabilités mensuelles conditionnelles.
- **Problème.** Une erreur d'un facteur deux, indiscernable au jugement, change tout : 2 % par mois donne 37 % sur 23 mois, 4 % donne 61 %. S'y ajoutent trois lacunes : la discrétisation des variables continues utilisées comme parents, la règle pour casser les cycles quand on prend « les trois influences les plus fortes », et le plafond de trois parents, arbitraire pour la présidentielle.
- **Correction.** Éliciter à l'horizon naturel de l'événement, convertir en taux mensuel, puis contrôler le cumul sur 23 mois. Fixer la discrétisation par quantiles historiques. Renvoyer tout cycle à la tranche suivante.

**N5. Échelles et règle encore incomplètes.**
- Les seuils chiffrés des quatre cibles sont absents : ils seront fixés après coup.
- Prendre le maximum de quatre cibles gonfle les notes. La cible « présidentielle » n'existe plus après mai 2027, et aucune cible ne couvre la gouvernabilité ni l'inflation.
- L'incertitude dérivée est continue, mais la règle ne prévoit que « ≥ 4 », « 3 » et « ≤ 2 » : les valeurs entre 2 et 3 et entre 3 et 4 n'ont pas de ligne.
- Un événement d'impact 3 et de probabilité 5 % devient « paramètre prédéterminé », ce qui n'a pas de sens.
- **Correction.** Publier les seuils dans le protocole. Écrire la règle en intervalles contigus. Distinguer variable et événement sur toutes les lignes.

**N6. Test du jugement sur juillet-septembre 2026.**
- **Problème.** Un agent avec recherche web ne peut pas être limité aux données antérieures : les moteurs remontent des articles postérieurs. Des questions rédigées aujourd'hui sur des faits connus sont biaisées par construction (Paleka et al. 2025). Les dates de coupure varient selon les modèles.
- **Correction.** N'utiliser que des questions ouvertes publiquement avant juillet 2026 (Metaculus, Polymarket). Faire le test sans recherche web, ou sur un corpus figé. Vérifier la coupure de chaque modèle.

**N7. Dispersion sous-estimée et comparateurs mal définis.**
- La concentration des lois de Dirichlet vient de la dispersion du second tour, après convergence entre modèles d'une même famille. Les intervalles à 80 % seront trop étroits.
- Le seuil d'alpha à 0,67 avec « nouveau passage » pousse au consensus. En v1, l'accord élevé était le symptôme, pas la preuve de qualité.
- L'extrémisation suppose des informations privées dispersées (Satopää et al. 2014), ce qui n'est pas le cas ici. Elle peut dégrader le comparateur principal et faire gagner le modèle à tort.
- La persistance est indéfinie. En version 0 ou 1, c'est un adversaire de paille.
- Les seuils des questions mécaniques ne sont pas fixés : trop loin du niveau courant, ils gonflent le volume sans information.
- **Correction.** Utiliser la dispersion du premier tour avec un plancher, calibré sur le test N6. Ne pas extrémiser, sauf paramètre calé au préalable. Prendre pour persistance une marche aléatoire avec volatilité historique, et fixer les seuils des questions à ses quantiles 20, 50 et 80.

**N8. Pièces incohérentes avec le texte.**
- Les prévisions exploratoires sont dites gelées, mais `data.json` reste le fichier vivant des relevés.
- Les « pivots » servent en 7.1 sans être définis en section 2.
- La politique allemande et italienne est exogène « par distributions externes » qui n'existent pas.
- **Correction.** Poser le tag, créer les deux registres en fichiers séparés, définir les pivots.

## 4. Améliorations souhaitables

- Remplacer les indices de Saltelli par une régression des sorties sur les 500 jeux de paramètres : même information, coût nul.
- Avec 100 trajectoires par jeu, le bruit de simulation (5 points) élargit artificiellement les intervalles. Passer à 1 000 ou corriger la variance.
- Une calibration parfaite donne déjà une erreur attendue de 0,067 à 200 questions. Le seuil de 0,10 ne détecte que les écarts grossiers.
- Préciser « simplifié » en 7.6 et le seuil de « moins bien que la persistance ».

## 5. Questions ouvertes

1. **Calage.** Ni l'un ni l'autre. Garder les nœuds dans le réseau et décaler l'ordonnée de leur table, en log-cotes, jusqu'à ce que la marginale calculée égale la cote. Le marché fournit le niveau, le modèle la dépendance, et la loi jointe reste cohérente. Les moteurs sans parent français sont de toute façon des entrées fixes. Exiger un critère de liquidité et le même horizon.
2. **Critère à 200 questions.** Non, pour les raisons de N1. Exprimer le critère en grappes (au moins 40) et publier la puissance avant le premier cycle. La règle par défaut, simplifier si le gain n'est pas démontré, est en revanche la bonne.
3. **Incertitude dérivée.** Préférable à une note à l'œil, car reproductible, avec quatre réserves :
   - la probabilité reste un jugement ;
   - la formule ignore le désaccord entre évaluateurs ;
   - elle ne s'applique pas aux nœuds à plus de deux issues, pour lesquels il faut une entropie normalisée ;
   - elle sature pour les événements récurrents, quasi certains sur 24 mois mais incertains dans leur date.

   Avec un passage linéaire, « ≥ 4 » correspond à une probabilité entre 25 et 75 %, et « ≤ 2 » à moins de 6,7 % ou plus de 93,3 %. Plus simple : classer par impact × √(p(1 − p)), en signalant tout écart interquartile de plus de 20 points.

## 6. Faisabilité

Non, pas telle qu'écrite. Les tâches unitaires sont à la portée d'agents, mais leur nombre, les accès aux données et le relais manuel rendent la dérive certaine. Elle devient exécutable avec la version minimale de N2, une liste de contrôle par étape et des scripts pour tout ce qui est mécanique (questions, scores, agrégation).

Deux remarques de processus :
- La réponse accepte les seize points sans en rejeter aucun, ce qui a alourdi le protocole au-delà de l'objet. Une partie de cette complexité vient de mes propres suggestions ; rejeter avec motif est légitime.
- Le critère d'arrêt repose sur un relecteur de la même famille que les auteurs. La relecture externe prévue en section 9 devrait intervenir avant la mise en production.

## Ce qui est solide

1. La séparation des pistes et des pools, avec l'ensemble direct comme adversaire principal et une règle par défaut qui fait porter la charge de la preuve au modèle.
2. Les tables explicites et le tirage des paramètres, qui rendent la loi jointe cohérente et l'incertitude visible.
3. Les limites sont écrites dans le protocole (section 10) et les limites d'exécution sont reconnues dans la réponse.