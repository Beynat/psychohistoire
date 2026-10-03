Je lis d'abord les pièces du dépôt, puis je rends la relecture au format demandé.

Je relance l'accès au dépôt pour lire les pièces avant de rédiger la relecture.

**Verdict.** Le protocole emprunte les bons outils (taux de base, questions datées, score de Brier, modèle témoin), mais son cœur probabiliste est mal fondé et son dispositif de validation ne pourra pas dire, en 24 mois, si le modèle vaut quelque chose. Les pièces montrent en outre que l'indépendance des évaluateurs est largement fictive et que la règle de sélection a été appliquée avec des écarts au texte. En l'état, les sorties seraient des probabilités d'apparence rigoureuse dont ni la cohérence interne ni la valeur ajoutée par rapport aux marchés ne seraient démontrables.

J'ai lu les huit fichiers de `modele/v1`, `data.json` et l'historique Git, et recalculé les médianes (aucune erreur). Je n'ai pas vérifié les faits postérieurs à mi-2026 cités dans les balayages : la relecture porte sur la méthode.

## Défauts bloquants

**B1. Validation sans puissance statistique.**
- **Constat.** Le modèle produit une dizaine d'événements, dont la plupart dépendent d'un seul fait (la présidentielle) ou ne se résolvent qu'en 2028. Rien ne garantit donc d'atteindre 20 résolutions indépendantes.
- **Problème.** À 20 prévisions, une fréquence observée de 70 % a un intervalle à 95 % de ±20 points : la calibration n'est pas mesurable. J'ai simulé la comparaison des Brier sur questions indépendantes (hypothèse optimiste) :

| Comparaison | N = 20 | N = 100 | N = 400 |
|---|---|---|---|
| Bon modèle contre « 50 % partout » | 48 % | 92 % | 100 % |
| Contre un taux de base constant | 27 % | 64 % | 99 % |
| Contre un modèle proche (cas du témoin sans impacts croisés) | 8 % | 14 % | 26 % |

  L'apport des impacts croisés est donc indétectable (Brier 1950 ; Murphy 1973 ; Diebold et Mariano 1995).
- **Correction.** Dériver des variables d'état 50 à 100 questions courtes (1 à 3 mois) par trimestre, par franchissement de seuil. Regrouper les questions par pivot pour le calcul d'erreur. Fixer à l'avance le critère d'échec du modèle. Objectif : 200 à 300 résolutions en 12 mois.

**B2. Circularité entre paramétrage et référence.**
- **Constat.** Les moteurs exogènes et plusieurs événements sont paramétrés sur Polymarket et Metaculus, puis le modèle est comparé à ces mêmes références.
- **Problème.** Sur ces questions, le modèle ne mesure que la qualité des marchés. De plus, une cote de marché intègre déjà les dépendances : lui appliquer des impacts croisés compte deux fois la même information.
- **Correction.** Noter séparément les questions avec et sans cote externe. La valeur propre du modèle se lit sur les secondes et sur les questions conditionnelles.

**B3. Cœur probabiliste incohérent.**
- **Constat.** La matrice notée de −3 à +3 est convertie en rapports de cotes, contrôlée par la méthode de Weimer-Jehle, puis simulée.
- **Problème.** La méthode de Weimer-Jehle (2006) est un test de cohérence qualitatif entre états, pas un calcul de probabilités. La conversion en rapports de cotes relève de Gordon et Hayward (1968), est arbitraire et ne garantit pas une loi jointe cohérente. Les taux de base historiques contiennent déjà l'effet moyen des causes. Enfin, 10 000 trajectoires éliminent le bruit d'échantillonnage, pas l'incertitude sur les paramètres, qui domine (Morgan et Henrion 1990).
- **Correction.** Garder un graphe orienté réduit avec tables de probabilités conditionnelles explicites (Pearl 1988), ce que fait déjà la v0.2. Caler les marginales sur les références. Tirer aussi les paramètres dans la simulation et publier la sensibilité.

**B4. Antériorité du protocole non vérifiable.**
- **Constat.** Le texte du protocole n'est pas dans le dépôt. Les commits v0 et v0.2 (13h28 et 14h30 le 3 octobre) contiennent déjà des probabilités sur les mêmes objets : RN 44 %, Moody's 30 %, écart à 150 pb 35 à 40 %. Trois prévisions y sont « révisées » le jour de leur émission. Tout le protocole v1 est commité 52 minutes plus tard.
- **Problème.** La mention « rédigé avant toute estimation » est inexacte à l'échelle du projet, et les choix de méthode restent ajustables après coup (Gelman et Loken 2013).
- **Correction.** Commiter le protocole et le taguer. Tenir un registre de questions en ajout seul. Déclarer la v0.2 comme piste séparée, notée à part.

## Défauts importants

**I1. Indépendance fictive des évaluateurs.**
- **Constat.** Les 14 redondances signalées reprennent toutes les regroupements suggérés en section 6 de `fusion.md`. Les trois évaluateurs emploient la même formule (« grandeur quasi comptable »). L'accord est très élevé (alpha de Krippendorff de 0,85 sur l'impact et 0,74 sur l'incertitude). Ils ont lu le même document, avec colonne « confiance » et cotes de marché. Pourtant 20 décisions garder/écarter sur 74 dépendent de l'évaluateur, et l'évaluateur 2 seul en changerait 11.
- **Problème.** La médiane de trois tirages corrélés ne réduit aucun biais. Le même dispositif est prévu pour la matrice.
- **Correction.** Utiliser des modèles de familles différentes (Schoenegger et al. 2024). Fournir des entrées aveugles : sans section 6, sans colonne « confiance », sans cotes, dans un ordre aléatoire. Passer à cinq évaluateurs ou plus et publier l'alpha. Les rôles « sceptique » ou « historien » d'un même modèle ne créent pas de diversité.

**I2. Échelles non ancrées.**
- **Constat.** L'évaluateur 2 note l'impact en espérance (conflit Russie-OTAN à 3, « pèse peu en espérance »), les deux autres en conditionnel (5). L'incertitude est confondue avec la probabilité (« environ 12 % », donc 2). 172 notes d'impact sur 222 valent 2 ou 3, et la note d'incertitude 5 n'apparaît que deux fois.
- **Problème.** Les médianes agrègent des grandeurs différentes.
- **Correction.** Définir l'impact comme l'effet conditionnel sur des variables cibles nommées, en unités. Définir l'incertitude comme la largeur d'un intervalle à 80 % rapportée à l'historique.

**I3. Règle de sélection appliquée avec des écarts.**
- **Constat.** Le cas « impact ≥ 4 et incertitude 3 » (croissance du PIB, guerre au Moyen-Orient) n'existe pas dans le protocole transmis ; il apparaît dans `selection.md`. Les redondances signalées par les trois évaluateurs sont traitées de trois façons : fusion (EV-03), maintien (EV-06, EV-12), écart (EX-08). Des moteurs d'impact 3 sont écartés pour « impact faible » alors que c'est leur faible incertitude qui les exclut : BCE, chômage, zone euro, crédits de défense.
- **Problème.** Un élément prédéterminé appartient à la structure du modèle (Wack 1985). Écarter la BCE alors que l'écart OAT-Bund est la variable la mieux classée retire son principal mécanisme, l'instrument anti-fragmentation.
- **Correction.** Publier une version 1.2 de la règle. Conserver les prédéterminés comme paramètres. Compléter par une analyse structurelle influence/dépendance (Godet). Garder les cas limites en test de sensibilité.

**I4. Sources secondaires et incohérences non levées.**
- **Constat.** Le HCFP, la Cour des comptes, le rapport de stabilité financière et le FMI sont lus via des reprises. Des niveaux courants viennent de TechTimes, HNGN, IndexBox, echosplus.com et Wikipédia. L'agent B signale lui-même des résumés Polymarket incohérents. Les quatre divergences de la section 7 (écart à 82 ou 111 pb, premier tour le 11 ou le 18 avril) n'ont pas été tranchées avant le classement.
- **Correction.** Établir une liste de sources primaires et de séries brutes, en étendant `collect.py`. Lever toutes les divergences avant le paramétrage, la date du scrutin sur le décret de convocation.

**I5. Ancrage sur le 3 octobre et taux de base fragiles.**
- **Constat.** Plusieurs moteurs sont des faits d'actualité : mouvement lycéen, grève du 29 septembre, « gouvernement Lecornu ». Des taux de base reposent sur deux à quatre cas récents (« 1 censure sur 4 budgets », alors qu'une seule censure avait abouti entre 1958 et 2024).
- **Correction.** Donner pour chaque événement plusieurs classes de référence avec fourchette (Kahneman et Lovallo 1993). Refaire le balayage à un mois et mesurer sa stabilité.

**I6. Exhaustivité et délimitation.**
- **Constat.** L'agent A est à 16 moteurs économiques sur 38, contre 3 politiques. L'agent C n'a traité que les trous vus par l'agent de fusion, et 3 de ses 14 moteurs sont retenus, contre 30 sur 60 pour A et B.
- **Manques.** Les décisions d'acteurs : candidatures et alliances, pourvoi de Marine Le Pen, pourtant présents en v0.2 ; vacance ou démission présidentielle ; référendum ; Conseil constitutionnel. La boucle souverain-banques. La politique allemande et italienne. Le système médiatique.
- **Problème.** Le modèle n'a pas d'acteurs, alors qu'une dissolution est la décision d'une personne. L'hypothèse « sans rétroaction de la France » est fausse pour la BCE et la zone euro, ce que la fusion note sans en tirer de conséquence.
- **Correction.** Confier une contre-expertise à un modèle différent, par pré-mortem (Klein 2007). Ajouter un module d'acteurs. Rendre la BCE et l'UE endogènes.

**I7. Biais propres aux modèles de langage et contamination.**
- **Constat.** Le refus de toute validation sur le passé est trop large. Le risque réel de fuite se situe au relevé hebdomadaire, quand un agent connecté au web met à jour un état après le fait.
- **Problème.** La contamination ne touche que les jugements du modèle de langage. La dynamique des variables d'état et les taux de base se testent sur l'historique. Les jugements se testent sur la période postérieure à la date de coupure du modèle (Halawi et al. 2024 ; ForecastBench, Karger et al. 2024). S'y ajoutent le repli vers 50 % et les chiffres ronds, la préférence pour les récits cohérents et les sources citées sans avoir été ouvertes.
- **Correction.** Horodater chaque prévision avant toute recherche web. Rétro-tester les composantes statistiques.

## Améliorations souhaitables

- **Témoin manquant.** Ajouter une prévision directe, question par question, par un ensemble de modèles hétérogènes avec recherche documentaire. C'est l'état de l'art à bas coût (quelques euros par question), et le modèle structurel doit le battre.
- **Variables d'état.** Remplacer la « dynamique simple » par des modèles estimés : autorégressif pour l'écart de taux, agrégation de sondages pour la présidentielle (Linzer 2013). Quelques jours de travail, testable sur le passé.
- **Scénarios.** Les familles de trajectoires les plus fréquentes ne sont pas des scénarios au sens de la prospective, qui couvrent les incertitudes critiques (Schwartz 1991). Publier les deux.
- **Scores.** Ajouter le score logarithmique, la décomposition de Murphy et un Brier pondéré dans le temps comme au Good Judgment Project (Mellers et al. 2014 ; Tetlock et Gardner 2015).
- **Étalon externe.** Soumettre les mêmes agents à Metaculus ou ForecastBench : gratuit, et des centaines de résolutions en quelques mois.

## Ce qui est solide

1. Les critères de résolution sont observables et datés, avec des lignes de base et un modèle témoin prévus dès le départ.
2. La traçabilité est réelle : les agents déclarent ce qu'ils n'ont pas pu ouvrir, et la fusion liste ses incohérences et ses trous.
3. Les relevés, les paramètres et le protocole sont séparés, et les interventions humaines sont tracées.

Une réserve sur cette relecture : je suis un modèle de langage, probablement proche de ceux qui ont produit les pièces, donc susceptible de partager leurs angles morts. Une relecture par un modèle d'une autre famille ou par un prévisionniste humain serait un vrai complément.