Bonjour,

Merci pour la relecture 2. Voici la version 1.5 du protocole (la 1.3 répond à votre relecture ; la 1.4 ajoute une section ; la 1.5 retire le recours à un modèle d'une autre famille, indisponible), pour une troisième relecture, dans le même cadre que les précédentes : critique scientifique, exhaustive et sans complaisance.

Dépôt : https://github.com/Beynat/psychohistoire, tag `protocole-v1.5`.

Pièces à lire :
- `modele/protocole.md` : le protocole v1.5 ;
- `modele/v1.4/exemple_lien_mobilisation_budget.md` : un exemple complet de chaîne de jalons, aux valeurs illustratives ;
- `modele/v1.3/reponse_relecture_2.md` : la réponse point par point à votre relecture 2, avec trois rejets motivés ;
- `modele/journal.md` ;
- `registre/` : les registres en ajout seul ;
- `collecte/collect.py` : le collecteur, auquel s'ajoute désormais la veille d'actualité ;
- `.github/workflows/version-protocole.yml` : la pose automatique du tag de chaque version ;
- `index.html` et `data.json`, onglet Actualité : la première mise à jour événementielle réelle (MAJ-001), sur la piste exploratoire.

Quatre changements de fond :
1. **Protocole phasé (section 3).** Chaque phase n'est construite que si la précédente est battue : ensemble direct au 1er novembre, puis modèles statistiques, puis réseau de 10 à 15 nœuds au 1er janvier 2027 au plus tard.
2. **Section 10, nouvelle et non relue : liens causaux et chaînes de jalons.** Chaque lien influent porte un mécanisme caché, avec une probabilité et une intensité distinctes. Il est décomposé en jalons observables, datés et gelés à l'avance, de niveau 2 ou 3, nécessaires ou favorables. Un jalon observé renforce le lien ; un jalon manqué dans sa fenêtre l'affaiblit, sans décroissance liée au seul temps. Plafond hebdomadaire pour les jalons favorables, routine hebdomadaire, pool de questions P2d, carte sur axe temporel.
3. **Section 11, nouvelle et non relue : mises à jour sur faits imprévus.**
   - Une veille gratuite, sans IA, relève chaque nuit les titres de la presse.
   - Un modèle léger les trie au moins trois fois par semaine.
   - Chaque fait reçoit l'un de cinq traitements : sans effet, donnée, évidence, paramètre, hors modèle.
   - Les faits d'évidence sont intégrés comme preuve virtuelle, avec un rapport de vraisemblance plafonné entre 1/3 et 3.
   - Garde-fous : pas de double compte avec les données, mise à jour sur faits établis seulement, revue en différé.
   - Un critère préalable décide si la couche est maintenue.
4. **Une seule famille de modèles (v1.5).** Aucun modèle performant d'une autre famille n'est accessible. Les exigences correspondantes sont retirées et compensées : plancher de dispersion, écart publié aux cotes externes, pré-mortem par deux agents puis lecture humaine, limite explicite (section 13). Ces compensations sont-elles suffisantes, et que faudrait-il ajouter ?

Je vous demande, dans l'ordre :
1. **Suivi de la relecture 2.** Pour chaque point (N1 à N8, améliorations, questions ouvertes), dites si la correction est suffisante, insuffisante ou mal fondée, avec motif. Jugez aussi les trois rejets.
2. **Examen de la section 10 (jalons).**
   - Le nœud caché « mécanisme actif » et le décalage d'intensité en log-cotes (indépendance causale) sont-ils une paramétrisation correcte, et la loi jointe reste-t-elle cohérente ?
   - Les vraisemblances conditionnelles à la chaîne suffisent-elles à éviter le surcompte entre jalons d'un même lien ?
   - Les règles « en retard » (racine du rapport de manque) et le plafond hebdomadaire hors jalons nécessaires sont-ils défendables ?
   - Le gel ex ante à 7 jours empêche-t-il réellement la définition de jalons après coup ?
   - Le pool P2d augmente-t-il la puissance, ou ajoute-t-il surtout des questions corrélées ?
   - La règle qui transforme une décision à double sens en sous-pivot est-elle suffisante ?
3. **Examen de la section 11 (faits imprévus).**
   - La preuve virtuelle est-elle le bon formalisme pour un fait qui renseigne un nœud sans l'observer ?
   - Le plafond du rapport de vraisemblance est-il justifié, ou arbitraire ?
   - La frontière entre « évidence » et « paramètre » est-elle opérante ? L'affaire Bardella, classée « paramètre », vous semble-t-elle bien classée ?
   - La règle de non-double-compte est-elle suffisante quand un fait agit à la fois par l'opinion, mesurée par les sondages, et par une décision d'acteur, non mesurée ?
   - Le critère de maintien (11.7) a-t-il une puissance suffisante, compte tenu du petit nombre de mises à jour attendues ?
   - Quels biais introduit un tri par un modèle léger : faux négatifs, saillance médiatique, sources limitées à deux titres de presse ?
4. **Examen de MAJ-001.**
   - Les trois évaluateurs ont donné R = 0,85, 1,15 et 1,6 : la consigne était-elle bien posée ? L'agrégation par moyenne géométrique est-elle adaptée à des avis de sens opposé ?
   - Le seuil de matérialité de 3 points est-il cohérent avec une mise à jour qui déplace le nœud d'environ 3,5 points ?
5. **Phasage.** Laisse-t-il assez de questions résolues avant la présidentielle d'avril 2027 pour juger la phase 3 ?
6. **Nouveaux défauts.** Classez-les en bloquants, importants et souhaitables, avec constat, problème et correction proposée, comme dans vos relectures précédentes.
7. **Faisabilité.** Le protocole v1.5 est-il exécutable par des agents IA, avec les moyens décrits, à partir du 1er novembre ?

Le critère d'arrêt du processus est deux relectures consécutives sans défaut bloquant ni important. Rejeter une de nos décisions avec motif est bienvenu.

Merci.
