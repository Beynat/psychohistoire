# Réponse à la relecture 3 (protocole v1.5 → v1.6)

Relecture : `relecture_3.md`. Protocole révisé : `../protocole.md`.
Légende : **accepté**, **accepté en partie** (avec limite explicite), **rejeté** (avec motif).

## Ligne générale

Le défaut bloquant D1 est corrigé en inversant le défaut, comme le propose le relecteur : les jalons servent d'abord à l'affichage et aux questions du pool P2d. Ils n'agissent sur les probabilités qu'une fois leur calibration vérifiée.

La section 10 est réécrite plus courte. La section 11 reçoit un seuil d'application, ce qui conduit à **annuler MAJ-001** sur la piste exploratoire et à **placer l'affaire Bardella en observation**.

Le protocole est ensuite **gelé** (D11) : seules des corrections exigées par une relecture peuvent produire une nouvelle version avant le bilan de la phase 1.

## Suivi de la relecture 2

| Point | Décision | Correction |
| --- | --- | --- |
| N1 Grappe d'une question conjointe | Accepté | La question « A et B » appartient à la grappe du lien A → B. Section 8.3. |
| N3 Écart aux cotes | Accepté | L'écart se mesure avant calage. Sections 4.5 et 8.4. |
| N6 Dossier figé | Accepté | Le dossier est constitué par script, à partir de captures archivées datées d'avant l'ouverture de chaque question (Internet Archive), sans moteur de recherche. Une question dont le dossier ne peut être constitué est écartée. Section 8.7. |
| N7 Statu quo à 0 % | Accepté | Pour un événement, la persistance est remplacée par le taux de base de la période. Section 8.4. |

## Défaut bloquant

| Point | Décision | Correction |
| --- | --- | --- |
| D1 Formalisme des jalons | Accepté | M devient un nœud racine indépendant de A. B garde A pour parent, et le décalage ne s'applique que si A et M sont vrais. M et I sont fusionnés en une intensité à trois niveaux (nulle, faible, forte). Un type « état aval » est ajouté pour les jalons qui renseignent B même sans A : ils agissent sur B, pas sur le lien. Les vraisemblances sont données selon le statut du jalon précédent (observé ou manqué). **Par défaut, les jalons n'agissent pas sur les probabilités** : ils sont affichés et notés en P2d. Ils ne deviennent actifs, lien par lien, qu'une fois leur calibration marginale vérifiée sur P2d (section 10.6). |

## Défauts importants

| Point | Décision | Correction |
| --- | --- | --- |
| D2 Décroissance, retard, plafond | Accepté | En cours de fenêtre, le rapport (1 − a·F(t)) / (1 − b·F(t)) est calculé par script, F(t) étant la part de fenêtre écoulée. Le statut « en retard » et le plafond hebdomadaire sont supprimés. Contre le bruit, tous les log-rapports sont multipliés par un facteur k ≤ 1, calé sur le test 8.7. Le rôle « nécessaire » est réservé aux jalons de vraisemblance a ≥ 0,95. Section 10.4. |
| D3 Critères de maintien sans puissance | Accepté | Les deux critères (10.11 et 11.7) jugent désormais la direction : la part des mises à jour qui vont vers l'issue réalisée, ou vers la donnée arrivée ensuite, par test de signe. Seuil d'application : pas de mise à jour si les évaluateurs divergent de signe ou si la moyenne des log-rapports est à moins de deux erreurs types de zéro. Il n'y a plus de piste parallèle à tenir. |
| D4 Preuve virtuelle sous-spécifiée | Accepté | Un fait par valence. Rapport estimé sachant les faits déjà intégrés sur le même nœud, qui sont présentés aux évaluateurs. Seuls comptent les faits postérieurs au gel de la dernière estimation du nœud. Rattachement au nœud le plus en amont quand plusieurs nœuds sont concernés. Plafond à 3 avec trois évaluateurs, porté à 10 avec cinq évaluateurs pour un fait très diagnostique. La phrase « un fait plus décisif relève du cas b » est supprimée. Section 11.4. |
| D5 Cas « paramètre » et affaire Bardella | Accepté | Le cas d reçoit le même plafond, le même seuil d'application et les mêmes garde-fous que le cas c. Les évaluateurs ne voient pas la ligne actuelle au premier tour. Un statut « en observation » est ajouté aux traitements. L'affaire Bardella y est placée : le fait est contesté (plainte pour faux) et son effet passe d'abord par les sondages. |
| D6 Une seule famille | Accepté en partie | Accepté : le signe moyen de l'écart aux cotes, mesuré avant calage, est suivi. S'il est systématique (test de signe à 10 %), les estimations de P2 sont corrigées d'un décalage en log-cotes à l'analyse trimestrielle (section 8.4). Accepté sous réserve de l'accord de Nathan : à chaque élicitation de tables, il estime un échantillon tiré au sort de 10 lignes, à l'aveugle, comme seul juge hors famille. Les écarts sont publiés (section 6.1). **Rejeté :** la lecture préalable des sections 10 et 11 par un humain formé aux probabilités. Aucun n'est disponible. Le risque est contenu autrement : les jalons n'agissent pas par défaut (D1) et les faits imprévus passent un seuil d'application (D3). |
| D7 Tri et veille | Accepté | Les flux de `collect.py` et le texte sont alignés : franceinfo, Le Monde, LCP (Assemblée) et Public Sénat. Vie publique, le Journal officiel et les agences ne sont pas accessibles en flux libre ; ils sont retirés du texte. Un titre non trié n'est jamais purgé. Les décisions de tri vont dans un fichier séparé (`data/tri.json`), que la collecte ne modifie pas. Le tri regroupe les titres par fait avant de juger. Le contrôle des faux négatifs porte sur 60 faits par trimestre, ce qui distingue 5 % de 20 %. La matérialité n'est plus une prévision du modèle léger : il ne fait que rattacher le fait, et la matérialité est jugée par le panel. Section 11.2. |
| D8 Moyens d'exécution | Accepté | Déclencheurs décrits : la collecte et le contrôle des registres passent par GitHub Actions ; le tri, la routine hebdomadaire et le cycle mensuel par des tâches planifiées de Claude, créées après le gel. Règle de rattrapage : un passage manqué est rattrapé au suivant, en conservant la date des faits. Au-delà de 7 jours, le passage est déclaré manqué au journal, sans prévision rétroactive. L'ajout seul des registres est vérifié par un workflow. Les scripts de la phase 1 sont listés dans `modele/controle/phase1.md` ; leur existence conditionne le démarrage. L'écart de taux journalier est un prérequis de la phase 2, pas de la phase 1. Section 12. |

## Souhaitables

| Point | Décision | Correction |
| --- | --- | --- |
| D9 Incohérences | Accepté | Le registre étant en ajout seul, les lignes horodatées à 12 h ne sont pas réécrites : une ligne d'erratum les rattache au commit 681502c (14 h 30). Les champs de la section 0 sont alignés sur ceux du registre. Les numéros de section sont corrigés dans le workflow et `collect.py`. La vérification de la date du scrutin sur le décret de convocation est rétablie (section 5.1). |
| D10 Sources partie prenante | Accepté | Un comptage produit par une partie prenante (syndicat, parti, organisateur) n'est jamais une « donnée » : il ne peut être qu'un indice, avec une confiance faible. Une donnée vient d'une source primaire officielle ou de la collecte. Les deux faits sont reclassés. Section 11.5. |
| D11 Rythme des versions | Accepté | Le protocole est gelé après la v1.6 jusqu'au bilan de la phase 1. Seules des corrections de défauts relevés en relecture peuvent produire une version, et la boucle de relecture continue jusqu'au critère d'arrêt. Section 12. |

## Phasage (section 5 de la relecture)

**Accepté.** Le texte dit désormais que le verdict de la phase 3 tombera vraisemblablement après la présidentielle (vers septembre 2027), et que le retour par défaut à la phase 2 est probable même si la structure est bonne. Section 8.6.

## Questions pour la relecture 4

1. Le seuil d'application (signe concordant, moyenne à plus de deux erreurs types) rend-il la couche des faits imprévus presque inerte avec trois évaluateurs ? Faut-il cinq évaluateurs par défaut ?
2. La vérification de calibration qui active les jalons d'un lien (section 10.6) est-elle bien posée, compte tenu du petit nombre de jalons par lien ?
3. Le facteur de réduction k, calé sur le test 8.7, est-il transposable aux jalons, qui ne sont pas des jugements de même nature ?
