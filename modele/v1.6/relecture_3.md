# Relecture 3 (protocole v1.5, tag protocole-v1.5)

Relecteur externe, reçue le 3 octobre 2026. Texte intégral, non modifié.

Je récupère la v1.5 au tag indiqué et je lis les pièces avant de rendre la relecture 3.

**Verdict.** Les phases 1 et 2 sont saines et peuvent démarrer : le phasage, les pools et les trois rejets règlent l'essentiel de la relecture 2. Les sections 10 et 11 réintroduisent en revanche la complexité que le phasage venait de retirer : le formalisme des jalons produit des mises à jour fausses dans des cas courants, et les deux critères de maintien n'ont aucune puissance. Je compte un défaut bloquant, limité à l'action des jalons sur les probabilités, et sept importants.

J'ai lu le protocole au tag `protocole-v1.5`, l'exemple, la réponse, le journal, les registres, `collect.py`, le workflow et MAJ-001 dans `data.json`. Cette relecture est faite dans la même session que les deux précédentes : je juge en partie mes propres propositions (calage, score de classement).

## 1. Suivi de la relecture 2

| Point | Jugement | Motif |
|---|---|---|
| N1 Critère d'échec | Suffisante dans sa conception | Reste un problème de calendrier (section 5). La grappe d'une question conjointe « A et B » n'est pas définie. |
| N2 Exécutabilité | Suffisante pour les phases 1 à 3 | Annulée en partie par les sections 10 et 11 (D1, D8). |
| N3 Calage | Suffisante | Préciser que l'écart aux cotes se mesure avant calage, sinon il est nul par construction. |
| N4 Élicitation | Suffisante | |
| N5 Échelles | Suffisante | Les seuils sont publiés et le classement est continu. |
| N6 Test du jugement | Suffisante en principe | Le dossier figé reste à constituer sans fuite : qui le monte, et comment ? |
| N7 Dispersion, comparateurs | Suffisante | Le « statu quo » pour un événement vaut 0 % : score logarithmique infini. Prendre le taux de base. |
| N8 Pièces | Insuffisante sur des détails | Voir D9. |
| Améliorations | Suffisantes | |
| Questions ouvertes | Suffisantes | |

Les trois rejets sont fondés : l'étalon externe remplacé par la comparaison sur P1, l'analyse indirecte inutile à 15 nœuds, le second balayage sorti des préalables de la phase 1.

## 2. Section 10 : jalons

- **Paramétrisation.** Le décalage en log-cotes est correct et la loi jointe reste cohérente. Le statut de M ne l'est pas : le texte en fait un nœud enfant de A qui « remplace A », l'exemple le traite comme une hypothèse indépendante de A (D1).
- **Surcompte.** Les vraisemblances conditionnelles à la chaîne ne suffisent pas : l'exemple donne une seule valeur par jalon, qui suppose les précédents observés. Après un jalon manqué, les valeurs suivantes ne sont plus valides (D1).
- **Retard et plafond.** Ni l'un ni l'autre n'est défendable (D2).
- **Gel à 7 jours.** Il empêche la définition après coup, pas la définition en cours de route sur une tendance déjà visible. Le jalon J1 de l'exemple fixe un seuil de 500 établissements alors que 564 étaient relevés le 2 octobre, avec une fenêtre ouverte deux jours après sa définition. Rien ne vérifie non plus l'ajout seul.
- **Pool P2d.** Il n'ajoute pas de puissance : 3 à 5 grappes par trimestre, et des jalons corrélés par construction. Le texte dit à la fois qu'il augmente les grappes du critère 8.6 et qu'il est jugé à part. Son vrai intérêt est de tester la calibration des jalons.
- **Sous-pivot.** Insuffisant : beaucoup de mécanismes à double sens ne passent par aucune décision d'acteur. MAJ-001 en est un cas (les violences radicalisent ou délégitiment).

## 3. Section 11 : faits imprévus

- **Preuve virtuelle.** C'est le bon formalisme, à deux conditions absentes du texte :
  - le fait ne doit renseigner que ce nœud, sinon il faut l'attacher au nœud le plus en amont ;
  - le rapport doit être estimé sachant les faits déjà intégrés sur ce nœud. Le code multiplie aujourd'hui les rapports successifs sans condition, alors que trois faits en cinq jours portent sur le même mouvement.
- **Plafond.** Défendable comme garde-fou contre la surconfiance, arbitraire dans sa valeur. « Un fait plus décisif relève du cas b » est faux : un fait peut être très diagnostique sans résoudre le nœud.
- **Évidence ou paramètre.** La frontière devient opérante avec ce test : si le parent était connu, le fait changerait-il encore l'enfant ? L'affaire Bardella le passe, mais son classement enfreint deux garde-fous du protocole (D5).
- **Double compte.** La règle suffit si la question précise « à intentions de vote inchangées » et si le nœud de décision a les sondages pour parent. Ce n'est pas écrit.
- **Critère 11.7.** Puissance nulle (D3).
- **Tri.** Trois biais :
  - le tri se fait sur les titres seuls, donc suit la saillance médiatique et ne voit jamais les non-événements ;
  - la matérialité est une prévision confiée au modèle le plus faible ;
  - le contrôle sur 20 faits ne distingue pas 5 % de 25 % de faux négatifs.

  Le code ne lit que cinq flux de deux titres, sans agence, Vie publique ni Journal officiel, contrairement au texte.

## 4. MAJ-001

- **Consigne.** Mal posée : le « fait » réunit incendies et concessions, de valences opposées. Les évaluateurs raisonnent sur ce que le fait annonce, pas sur sa vraisemblance sous chaque issue.
- **Agrégation.** La moyenne des log-rapports est la bonne. Le défaut est d'appliquer un résultat indiscernable de 1 : la moyenne est à 0,8 erreur type de zéro, et les trois avis donnent 32, 39 et 47 %.
- **Seuil.** Le seuil de 3 points filtre la portée possible au tri, pas la mise à jour réalisée. Un déplacement de 3,5 points avec désaccord de signe est du bruit enregistré.
- **Antériorité.** L'estimation de base, datée du même jour, a été faite avec recherche web : le fait y était sans doute déjà intégré.

## 5. Phasage

Non. Le réseau démarre au plus tard le 1er janvier ; un trimestre donne 10 à 15 grappes avant le premier tour. La séquence budgétaire, la plus riche en résolutions, sera passée. La présidentielle résout ensuite beaucoup de questions d'un seul tirage.

| Grappes résolues | Écart de Brier net (0,02) | Écart fort (0,04) |
|---|---|---|
| 12 à 15 | 29 à 43 % | 58 à 82 % |
| 25 | 44 à 54 % | 82 à 94 % |
| 40 | 55 à 68 % | 94 à 99 % |

Simulation de ma part, au seuil de 10 %, six questions par grappe, corrélation de 0,1 à 0,3. Les 40 grappes arrivent vers septembre 2027. Le verdict tombera donc après l'élection, et le retour par défaut à la phase 2 est probable même si la structure est bonne. C'est acceptable si c'est écrit.

## 6. Nouveaux défauts

### Bloquant

**D1. Le formalisme des jalons produit des mises à jour fausses.**
- **Constat.**
  - Le statut de M est contradictoire entre le texte et l'exemple.
  - Les jalons J5 (première partie rejetée) et J6 (motion déposée avec des signataires PS) annoncent la censure quelle que soit la mobilisation. Classés « transmission », ils n'agissent que si A est vrai.
  - Quatre paramètres (probabilité, deux décalages, part de l'intensité forte) décrivent un seul écart observable. M et I ne sont jamais observés.
- **Problème.**
  - Si M est enfant de A, observer un jalon de transmission augmente mécaniquement la probabilité de la mobilisation.
  - Un précurseur de B sans mobilisation est ignoré.
  - Le recalibrage trimestriel de a et b est impossible : seule la fréquence marginale d'un jalon est observable, une fois.
- **Correction.**
  - Faire de M un nœud racine indépendant de A ; B garde A pour parent et le décalage s'applique si A et M sont vrais.
  - Ajouter un type « état aval », pour tout jalon qui renseignerait B même si A était faux.
  - Fusionner M et I en une intensité à trois niveaux (nulle, faible, forte).
  - Donner les vraisemblances selon le statut du jalon précédent.
  - Inverser le défaut : les jalons servent d'abord à l'affichage et au pool P2d, et n'agissent sur les probabilités qu'une fois leur calibration marginale vérifiée.

### Importants

**D2. Absence de décroissance, retard et plafond.**
- **Constat.** Un lien ne bouge pas pendant la fenêtre, puis chute à la clôture : 0,50, puis 0,31, puis 0,17 dans l'exemple.
- **Problème.** La non-observation en cours de fenêtre est une information. À mi-fenêtre sans J2, le calcul correct donne déjà 0,40. Une baisse prévisible à l'avance est une erreur de calibration. Le plafond hebdomadaire avec report publie sciemment une probabilité périmée, et l'étiquette « nécessaire », qui en exempte, est attribuée à des jalons de vraisemblance 0,85.
- **Correction.** Calculer par script le rapport (1 − a·F(t)) / (1 − b·F(t)), où F(t) est la part de fenêtre écoulée. Supprimer le statut « en retard » et le plafond. Contre le bruit, réduire tous les log-rapports d'un facteur fixe calé sur le test 8.7.

**D3. Critères de maintien 10.10 et 11.7 sans puissance.**
- **Constat.** Une mise à jour juste de quelques points améliore le Brier d'environ 0,001 par question.
- **Problème.** Ma simulation donne une puissance de 12 à 20 % avec 70 mises à jour, soit presque le taux de fausse alarme. Les deux couches seront retirées quel que soit leur mérite. Chaque critère impose en plus une piste parallèle à tenir.
- **Correction.** Juger la direction : la part des mises à jour qui vont vers l'issue réalisée ou vers la donnée arrivée ensuite, par test de signe. Fixer un seuil d'application : pas de mise à jour si les évaluateurs divergent de signe ou si la moyenne est à moins de deux erreurs types de zéro.

**D4. Preuve virtuelle sous-spécifiée.** Constat et problème en sections 3 et 4. Correction :
- un fait par valence ;
- un rapport estimé sachant les faits déjà intégrés ;
- des faits postérieurs au gel de la dernière estimation ;
- un rattachement au nœud amont quand plusieurs nœuds sont concernés ;
- un plafond relevé à 10 avec cinq évaluateurs pour les faits très diagnostiques.

**D5. Cas « paramètre » sans plafond, et affaire Bardella.**
- **Constat.** Le cas c est plafonné à 3, le cas d ne l'est pas, et ses évaluateurs voient la ligne actuelle. L'affaire Bardella est classée d et « intégrée », alors que le fait est contesté (plainte pour faux) et que le motif renvoie son effet aux sondages.
- **Problème.** L'asymétrie pousse à classer en d. Le classement Bardella contredit les règles « faits établis » et « on attend la donnée » : il devait rester en observation.
- **Correction.** Appliquer au cas d le même plafond et les mêmes garde-fous. Ajouter le statut « en observation » au tableau des traitements.

**D6. Une seule famille : compensations partielles.**
- **Constat.** Le plancher de dispersion élargit les intervalles. L'ensemble direct et le modèle partagent la même famille.
- **Problème.** Un biais commun déplace le centre, pas la largeur, et s'annule dans la comparaison 8.6. Le critère d'arrêt repose désormais sur moi seul.
- **Correction.** Mesurer le signe moyen de l'écart aux cotes avant calage, et corriger les estimations de P2 s'il est systématique. Faire estimer par Nathan un échantillon tracé de lignes, comme seul juge hors famille. Faire lire les sections 10 et 11 par un humain formé aux probabilités avant qu'elles n'agissent.

**D7. Tri et veille.** Constat et problème en section 3. Trois points de code s'y ajoutent :
- le fichier de veille est tronqué à 400 titres par date, ce qui peut supprimer des titres non triés entre deux passages ;
- l'agent de tri et la collecte nocturne écrivent le même fichier ;
- rien ne dédoublonne un même fait repris par plusieurs titres.

Correction : aligner les flux sur le texte, ne jamais purger un titre non trié, séparer le fichier des décisions de tri.

**D8. Moyens d'exécution non décrits.**
- **Constat.** Le protocole prévoit une routine le lundi, un tri trois fois par semaine et un cycle mensuel. `modele/controle/` n'existe pas, aucun script de génération, de notation ou de puissance n'est au dépôt, et la collecte ne fournit qu'un écart de taux mensuel alors que le modèle demande du journalier.
- **Problème.** Rien ne dit qui lance les agents ni ce qui se passe quand un passage manque.
- **Correction.** Décrire le déclencheur et la règle de rattrapage. Faire vérifier l'ajout seul des registres par le workflow.

### Souhaitables

**D9. Incohérences de pièces.**
- Les lignes du registre exploratoire sont horodatées à 12 h, avant le premier commit (13 h 28).
- Les champs du registre diffèrent de la section 0.
- Le workflow et `collect.py` citent d'anciens numéros de section.
- La vérification de la date du scrutin sur le décret a disparu, alors que la section 5.2 retient le 2 mai.

**D10. Sources de la piste exploratoire.** Deux faits traités comme « donnée » ou « évidence » viennent de France Épargne et de la CGT, partie prenante pour un comptage de manifestants.

**D11. Rythme des versions.** Les versions 1.3 à 1.5 ont été publiées en 21 minutes, et les sections 10 et 11 font la moitié du texte. Geler le protocole jusqu'au bilan de la phase 1.

## 7. Faisabilité

- **Phase 1 au 1er novembre : oui**, si les scripts, l'écart de taux journalier et le déclencheur des agents sont en place (D8). C'est quatre semaines de travail mécanique.
- **Phases 2 et 3 : oui**, à la taille prévue.
- **Sections 10 et 11 agissant sur les probabilités : non en l'état.** Trop de jugements hebdomadaires reposent sur des paramètres non vérifiables, et quatre pistes parallèles sont à tenir. En affichage et en questions P2d, elles sont exécutables dès maintenant.

## Ce qui est solide

1. Le phasage conditionnel, avec retour à la phase précédente par défaut, et les trois rejets motivés.
2. L'idée des jalons datés et gelés à l'avance : ce sont de bonnes questions de prévision, vérifiables chaque semaine, et un bon outil de lecture.
3. La trace : registres séparés, tags automatiques, décisions de tri consignées avec motif, y compris « sans effet ».