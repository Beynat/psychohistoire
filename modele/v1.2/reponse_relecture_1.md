# Réponse à la relecture 1 (protocole v1.1 → v1.2)

Relecture : `relecture_1.md`. Protocole révisé : `../protocole.md`.
Légende : **accepté**, **accepté en partie** (avec limite explicite), **rejeté** (avec motif).

## Défauts bloquants

| Point | Décision | Correction dans la v1.2 |
| --- | --- | --- |
| B1. Puissance statistique | Accepté | La banque de questions est générée mécaniquement à partir des seuils des variables d'état, à 1, 2 et 3 mois, plus les événements et les pivots. Objectif : 50 questions par trimestre et 200 à 300 résolues en 12 mois. Les questions sont rattachées à des grappes, avec bootstrap par grappes. Les critères d'échec sont fixés à l'avance. La puissance attendue est publiée à chaque bilan. Sections 7.1, 7.5 et 7.6. |
| B2. Circularité paramétrage-référence | Accepté | Deux pools : P1 avec cote externe, où l'on mesure seulement l'écart à la référence ; P2 sans cote et conditionnelles, où se mesure la valeur propre du modèle. Les nœuds cotés sont calés sur la référence, avec une propagation limitée à l'aval pour éviter le double compte. Sections 3.5 et 7.3. |
| B3. Cœur probabiliste | Accepté | Réseau bayésien dynamique mensuel avec tables de probabilités conditionnelles explicites. La conversion des notes en rapports de cotes est supprimée. La méthode de Weimer-Jehle est ramenée à un test qualitatif optionnel. L'incertitude des paramètres est tirée selon des lois de Dirichlet, au moins 500 jeux × 100 trajectoires, avec une analyse de sensibilité globale publiée. Section 3. |
| B4. Antériorité du protocole | Accepté | Le protocole est versionné dans le dépôt et tagué avant toute estimation. La v0 et la v0.2 sont déclarées piste exploratoire, gelées et notées dans un registre séparé. Le registre principal est en ajout seul. Les horizons démarrent le 1er novembre 2026, après validation de la méthode. Section 0. |

## Défauts importants

| Point | Décision | Correction et limite |
| --- | --- | --- |
| I1. Indépendance des évaluateurs | Accepté en partie | Au moins cinq évaluateurs, entrées aveugles (sans confiance, sans cotes, sans regroupements suggérés), ordre aléatoire, aucune posture imposée, alpha de Krippendorff publié avec un seuil à 0,67. **Limite :** l'environnement d'exécution ne donne accès qu'à des modèles d'une même famille. La diversité entre familles dépend de Nathan, qui soumet manuellement un ou deux évaluateurs externes aux étapes clés. Section 5.1. |
| I2. Échelles non ancrées | Accepté | L'impact est conditionnel, mesuré sur quatre variables cibles chiffrées, en prenant le maximum. La probabilité est notée à part. L'incertitude est dérivée (4 × p × (1 − p) pour les événements ; largeur d'intervalle à 80 % rapportée à l'historique pour les variables). Section 5.2. |
| I3. Règle appliquée avec écarts | Accepté | Règle v1.2 exhaustive, couvrant toutes les combinaisons. Les éléments prédéterminés sont conservés comme paramètres. Les redondances suivent un traitement unique (trois évaluateurs sur cinq). Cas limites testés en sensibilité. Analyse structurelle MICMAC. Sections 5.3 et 5.4. La BCE est réintégrée et devient endogène par sa fonction de réaction (section 1). |
| I4. Sources secondaires et incohérences | Accepté | Hiérarchie des sources. Les niveaux de paramétrage viennent uniquement de sources primaires ou de `collect.py`, qui sera étendu. Les divergences sont tranchées et consignées avant le paramétrage ; la date du scrutin est vérifiée sur le décret. Section 4.5. |
| I5. Ancrage sur l'actualité et taux de base fragiles | Accepté | Au moins deux classes de référence par événement, avec fourchette. Balayage refait à un mois d'intervalle, avec mesure de stabilité (indice de Jaccard). Sections 4.4 et 6.3. |
| I6. Exhaustivité et délimitation | Accepté en partie | Nouvelle catégorie « décision d'acteur » (dissolution, candidatures, alliances, référendum, vacance, Conseil constitutionnel, instrument de la BCE), modélisée comme nœud dont les parents sont ses déterminants. Ajouts : boucle souverain-banques, politique allemande et italienne, médias. Pré-mortem par un modèle d'une autre famille. BCE et UE partiellement endogènes. **Limite :** un modèle multi-agents complet est écarté pour la v1.2, faute de validation possible à cette échelle ; les décisions d'acteurs restent des nœuds probabilistes. Sections 1, 2, 4.2 et 4.3. |
| I7. Contamination et biais des modèles de langage | Accepté | Gel des données et commit des prévisions avant toute autre recherche. Composantes statistiques rétro-testées sur 2010-2025. Jugement testé sur des questions résolues entre juillet et septembre 2026, postérieures à la date de coupure, avec des données antérieures à chaque question. L'interdiction générale de toute validation sur le passé est levée. Sections 7.2 et 7.7. |

## Améliorations souhaitables

| Point | Décision | Correction |
| --- | --- | --- |
| Témoin par ensemble direct | Accepté | Au moins cinq prévisionnistes IA avec recherche, médiane extrémisée. C'est le comparateur principal du critère d'échec. Sections 7.4 et 7.6. |
| Variables d'état estimées | Accepté | Modèle autorégressif avec chocs pour l'écart de taux, agrégation bayésienne des sondages, modèle de comptage auto-excitant pour la contestation, tous rétro-testés. Section 6.1. |
| Deux types de scénarios | Accepté | Scénarios prospectifs sur les deux incertitudes critiques, et familles de trajectoires. Section 8. |
| Scores | Accepté | Score logarithmique, décomposition de Murphy, Brier pondéré dans le temps. Section 7.5. |
| Étalon externe | Accepté | ForecastBench ou tournois Metaculus, quand c'est possible. Section 7.7. |

## Questions ouvertes pour la relecture 2

1. Le calage des nœuds cotés (section 3.5) suffit-il à éviter le double compte, ou faut-il exclure ces nœuds du réseau et les traiter comme entrées fixes ?
2. Le critère d'échec à 200 questions (section 7.6) est-il réaliste compte tenu de la corrélation entre questions d'une même grappe ?
3. La dérivation de l'incertitude par 4 × p × (1 − p) est-elle préférable à une note directe pour la sélection des incertitudes critiques ?
