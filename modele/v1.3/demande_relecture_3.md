Bonjour,

Merci pour la relecture 2. Voici la version 1.3 du protocole, pour une troisième relecture, dans le même cadre que les précédentes : critique scientifique, exhaustive et sans complaisance.

Dépôt : https://github.com/Beynat/psychohistoire, commit a6bb6ee.

Pièces à lire :
- `modele/protocole.md` : le protocole v1.3 ;
- `modele/v1.3/reponse_relecture_2.md` : la réponse point par point à votre relecture 2, avec trois rejets motivés ;
- `modele/journal.md` ;
- `registre/` : les registres en ajout seul ;
- `collecte/collect.py` : le collecteur, auquel s'ajoute désormais la veille d'actualité ;
- `index.html` et `data.json`, onglet Actualité : la première mise à jour événementielle réelle (MAJ-001), sur la piste exploratoire.

Deux changements de fond :
1. **Protocole phasé (section 3).** Chaque phase n'est construite que si la précédente est battue : ensemble direct au 1er novembre, puis modèles statistiques, puis réseau de 10 à 15 nœuds au 1er janvier 2027 au plus tard.
2. **Section 10, nouvelle et non relue : mises à jour événementielles.**
   - Une veille gratuite, sans IA, relève chaque nuit les titres de la presse.
   - Un modèle léger les trie au moins trois fois par semaine.
   - Chaque fait reçoit l'un de cinq traitements : sans effet, donnée, évidence, paramètre, hors modèle.
   - Les faits d'évidence sont intégrés comme preuve virtuelle, avec un rapport de vraisemblance plafonné entre 1/3 et 3.
   - Garde-fous : pas de double compte avec les données, mise à jour sur faits établis seulement, revue en différé.
   - Un critère préalable décide si la couche est maintenue.

Je vous demande, dans l'ordre :
1. **Suivi de la relecture 2.** Pour chaque point (N1 à N8, améliorations, questions ouvertes), dites si la correction est suffisante, insuffisante ou mal fondée, avec motif. Jugez aussi les trois rejets.
2. **Examen de la section 10.**
   - La preuve virtuelle est-elle le bon formalisme pour un fait qui renseigne un nœud sans l'observer ?
   - Le plafond du rapport de vraisemblance est-il justifié, ou arbitraire ?
   - La frontière entre « évidence » et « paramètre » est-elle opérante ? L'affaire Bardella, classée « paramètre », vous semble-t-elle bien classée ?
   - La règle de non-double-compte est-elle suffisante quand un fait agit à la fois par l'opinion, mesurée par les sondages, et par une décision d'acteur, non mesurée ?
   - Le critère de maintien (10.7) a-t-il une puissance suffisante, compte tenu du petit nombre de mises à jour attendues ?
   - Quels biais introduit un tri par un modèle léger : faux négatifs, saillance médiatique, sources limitées à deux titres de presse ?
3. **Examen de MAJ-001.**
   - Les trois évaluateurs ont donné R = 0,85, 1,15 et 1,6 : la consigne était-elle bien posée ? L'agrégation par moyenne géométrique est-elle adaptée à des avis de sens opposé ?
   - Le seuil de matérialité de 3 points est-il cohérent avec une mise à jour qui déplace le nœud d'environ 3,5 points ?
4. **Phasage.** Laisse-t-il assez de questions résolues avant la présidentielle d'avril 2027 pour juger la phase 3 ?
5. **Nouveaux défauts.** Classez-les en bloquants, importants et souhaitables, avec constat, problème et correction proposée, comme dans vos relectures précédentes.
6. **Faisabilité.** Le protocole v1.3 est-il exécutable par des agents IA, avec les moyens décrits, à partir du 1er novembre ?

Le critère d'arrêt du processus est deux relectures consécutives sans défaut bloquant ni important. Rejeter une de nos décisions avec motif est bienvenu.

Merci.
