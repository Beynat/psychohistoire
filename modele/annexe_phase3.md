# Annexe phase 3 — liens, jalons et faits imprévus — version 1.9

Statut : voir `modele/statut.json` (noyau, section 12). Rédigée le 4 octobre 2026 ; version 1.2 : caractérisation des faits, mesure de reprise et règle d'abandon (sections 11.2 et 11.3), à la demande de Nathan ; version 1.3 : définition de l'étape officielle (section 11.2) ; version 1.4 : réponse à la relecture 11 (stade vérifié, reprise glissante, table de réexamen, affichage) ; version 1.5 : réponse à la relecture 12 (faits établis vérifiés, caractérisation non publiée, décisions de réexamen inscrites, paramètres des nœuds M, centrage de Z) ; version 1.6 : réponse à la relecture 13 (faits publics de toute nature, contrôle du tri, champs libres) ; version 1.7 : rédaction (relecture de suivi 14) ; version 1.8 (10 octobre 2026, v0, feuille de route, étape 2) : moteur de preuve unique et trois classes de preuves (sections 10.4, 10.5 et 11.4) ; version 1.9 (étape 9) : chocs imprévus comme interventions sur des points d'entrée déclarés, intensité par barème (section 11.4). Elle complète `protocole.md` (le noyau) et ne s'applique qu'à partir de la phase 3, sauf le cas b (section 8.9 du noyau) et le pilote sur la piste exploratoire. Elle conserve la numérotation 10 et 11 pour la continuité des renvois. Elle est versionnée et taguée séparément (`annexe-phase3-vX.Y`), et gelée dans les mêmes conditions que le noyau (section 12). Dès la phase 1 servent la veille et le tri (section 11.2) : pour le cas « donnée », avec effet ; pour la caractérisation et la reprise des faits qui concernent une question, à titre descriptif seulement, sans effet sur aucune probabilité.

## 10. Liens causaux et jalons

Un pivot ne bascule pas d'un coup : ce qui y mène passe par des étapes observables. Chaque lien influent est décomposé en une chaîne de jalons datés et fixés à l'avance, comme les indicateurs d'alerte de la planification par hypothèses (Dewar et al. 1993). **Par défaut, les jalons sont affichés et notés, mais n'agissent pas sur les probabilités** ; ils ne deviennent actifs qu'une fois validée la direction de leurs mises à jour fantômes (section 10.6).

### 10.1 Mécanisme et intensité

- **Mécanisme.** Un lien suivi, du nœud A vers le nœud B, porte un mécanisme écrit en une phrase et un seul sens : une issue de A favorise une issue de B.
- **Intensité.** Chaque lien a un nœud caché racine M, indépendant de A, à trois niveaux : nulle, faible, forte. B garde A pour parent et reçoit M comme parent supplémentaire. Quand A prend l'issue concernée et que M n'est pas nul, la cote de l'issue favorisée de B est décalée de δ_faible ou δ_forte en log-cotes, sur le principe de l'indépendance causale (Heckerman et Breese 1996). La loi jointe reste cohérente, et observer un jalon de transmission ne modifie pas la probabilité de A. Le plafond de parents (section 4.2) ne s'applique pas aux nœuds M. La loi a priori de M et les valeurs de δ_faible et δ_forte sont fixées à l'élicitation de la phase 3, avant la définition du premier jalon, par le panel d'élicitation, et journalisées. Contrainte de centrage : ajouter M ne doit pas déplacer P(B | A) ; la table de B est recentrée, en log-cotes, pour que sa marginale sur M égale la table élicitée sans M.
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
| Porte sur | Pour un jalon de transmission : la présence du mécanisme (M non nulle contre nulle) ou sa force (forte contre faible) |
| Vraisemblances | a = P(observé dans la fenêtre si l'hypothèse est vraie) et b = P(observé si elle est fausse). L'hypothèse est A pour un jalon d'état amont, M non nulle (ou M forte, pour un jalon de force) pour un jalon de transmission, l'issue favorisée de B pour un jalon d'état aval. Trois couples (a, b) sont donnés : sachant le jalon précédent de la chaîne observé ; sachant qu'il est manqué ; sachant qu'il n'est pas encore résolu ou qu'il est invalidé (et pour le premier jalon de la chaîne). Pour un jalon de force, on donne en plus c = P(observé si M est nulle) |
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
- **Réduction contre le bruit.** Tous les log-rapports sont multipliés par un facteur k ≤ 1. Tant qu'il n'est pas estimé, k = 0,5, valeur déclarée arbitraire. Il est estimé sur le registre fantôme (section 10.6) par régression logistique de l'issue sur le log-rapport brut, avant réduction, avec la log-cote de la probabilité sans jalons en décalage : le coefficient est k. Le facteur des faits imprévus est estimé séparément (section 11.4). Un facteur n'est estimé qu'à partir de 40 questions résolues, et son estimation est bornée entre 0 et 1. Il n'y a pas de plafond hebdomadaire.
- **Pivots à échéance.** Un événement qui doit survenir avant une date garde sa décroissance propre (taux mensuel, section 7.4), indépendamment des jalons.
- **Moteur unique et trois classes (version 1.8).** Depuis la version 2 des vraisemblances (une probabilité d'observation par issue du pivot), tout jalon, tout fait imprévu et tout pivot tranché est une preuve, appliquée par un seul calcul : chaque trajectoire du réseau est pondérée par le produit des vraisemblances (`scripts/preuves.py`, `scripts/reseau.py`), si bien que l'effet porte sur tout le réseau, vers l'aval comme vers l'amont ; le nombre de trajectoires effectives est publié et, sous 5 %, la combinaison est déclarée trop rare. Classes, fixées avant l'observation : « qui tranche » (jalon équivalent à un état du réseau, ou rapport d'au moins 20 entre la plus forte et la plus faible vraisemblance ; pivot tranché ; fait dont les vraisemblances agrégées atteignent ce rapport) : vraisemblances appliquées sans réduction ni plafond, la probabilité de retournement étant dans la plus faible ; « indice » : réduction par k (et, pour un fait, plafond de la section 11.4) ; « allégation » : aucune mise à jour. Un jalon qui tranche manqué ou en cours est un indice.

### 10.5 Double compte

- **Indicateur exclusif.** Un indicateur ne sert de preuve qu'à un seul jalon et un seul lien. S'il en renseigne plusieurs, son log-rapport est partagé par des poids fixés à l'avance, dont la somme vaut 1.
- **Pas de jalon sur une résolution.** Un indicateur qui tranche un nœud est traité comme une donnée (section 11.3, cas b), jamais comme jalon.
- **État aval.** Un jalon d'état aval agit sur B comme preuve virtuelle, jamais sur le lien.
- **Priorité du jalon.** Quand les jalons sont actifs, un fait prévu comme jalon est traité par le jalon, jamais aussi comme fait imprévu. Tant qu'ils sont inactifs, un jalon indice observé ou manqué est renvoyé à la section 11 comme un fait ordinaire (panel, seuil, plafond) ; ses vraisemblances gelées ne servent qu'au registre fantôme. Un jalon qui tranche observé est une observation : il entre dans les prévisions notées sans réduction (version 1.8). Définir un jalon ne peut donc pas neutraliser un fait décisif.

### 10.6 Activation

- **Par défaut.** Les jalons sont affichés et notés en P2d, sans effet sur les probabilités du réseau.
- **Registre fantôme.** Chaque semaine, un script calcule la probabilité qu'auraient les nœuds si les jalons étaient actifs, avec k courant. Ces probabilités sont enregistrées dans `registre/fantome.jsonl`, en ajout seul ; ce sont aussi celles de l'affichage « indicatif ». Le calcul est entièrement scripté et ne demande aucun travail d'agent.
- **Activation.** Décidée à l'analyse trimestrielle quand la statistique de direction Z (section 10.11), calculée sur le registre fantôme, est significative au seuil unilatéral de 10 %, sur au moins 40 questions résolues.
- **Désactivation.** Même statistique, même seuil et même nombre de questions, calculée sur les probabilités réelles une fois les jalons actifs.

### 10.7 Périmètre et définition

- **Liens suivis.** Les 3 à 5 liens dont la part de variance expliquée sur les pivots principaux est la plus forte (section 4.6), avec au plus 8 jalons par lien.
- **Définition.** Les jalons sont proposés par un agent sur sources primaires. Leurs vraisemblances sont estimées par cinq évaluateurs aveugles en un tour, sur au moins trois modèles différents (section 6.1 du noyau), avec agrégation par moyenne des log-cotes.
- **Gel ex ante.**
  - Un jalon est défini et commité au moins 7 jours avant l'ouverture de sa fenêtre.
  - Son seuil ne doit pas avoir été atteint dans les 30 jours précédant sa définition, faute de quoi il ne renseigne rien.
  - Un jalon ajouté en cours de route ne porte que sur une fenêtre future.
  - Les définitions de jalons (`modele/jalons/definitions.jsonl`) et leurs statuts (`modele/jalons/statuts.jsonl`) sont deux journaux séparés en ajout seul, vérifiés par le contrôle des registres (section 12). La date de définition (`defini_le`, avec fuseau) est fixée par script et contrôlée à la poussée, comme l'horodatage des registres.
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

Chaque jalon est une question : « J est-il observé dans sa fenêtre ? ». Ces questions forment le pool P2d, groupé par lien. Le pool est descriptif : la calibration des jalons y est mesurée et publiée à chaque bilan, mais aucune décision n'y est attachée. Il est exclu des critères de la section 8.6.

### 10.10 Affichage

- **Carte sur axe temporel.** L'axe horizontal est le temps. Les pivots sont placés à leur échéance, les jalons dans leur fenêtre, le long des liens qu'ils renseignent.
- **Deux échelles.** La vue semaine montre les niveaux 1 à 3 et le statut des jalons de la semaine et des deux suivantes. La vue macro ne garde que les niveaux 1 et 2.
- **Sur chaque lien :** intensité, tendance sur 4 semaines, prochain jalon et sa date, avec la mention « indicatif » tant que les jalons ne sont pas actifs. Au survol : ce qui ferait monter ou baisser l'estimation.
- **Chemin réel.** Les jalons observés et les issues résolues sont tracés sur la même carte que les trajectoires prévues.

### 10.11 Critère de direction (commun aux jalons et aux faits imprévus)

- **Statistique.** Pour chaque question résolue i, le terme est sᵢ = dᵢ (yᵢ − pᵢ). Les termes sont sommés par grappe (section 8.3 du noyau) : S_g = Σ_{i ∈ g} sᵢ. La statistique est Z = Σ_g S_g / √(Σ_g S_g²), ce qui tient compte de la corrélation entre questions d'un même lien. Pour chaque question, p est la probabilité sans la couche jugée et d le déplacement cumulé dû à cette couche, mesuré à la clôture de la question : probabilité fantôme moins probabilité sans jalons pour les jalons (section 10.6), probabilité avec moins probabilité sans les mises à jour c et d pour les faits imprévus (section 11.7). y vaut 1 si l'issue s'est réalisée, 0 sinon. Plusieurs mises à jour d'une même question ne comptent donc qu'une fois. Seules comptent les questions dont le déplacement d est d'au moins 0,5 point en valeur absolue.
- **Loi.** Sous l'hypothèse d'une couche sans information, Z suit approximativement une loi normale centrée réduite, quel que soit p, à condition que la probabilité sans la couche soit calibrée. Si elle ne l'est pas, une couche qui corrige un biais uniforme passerait le critère sans apporter d'information sur les liens : la calibration de la probabilité sans la couche est donc publiée avec Z. Avec moins de 15 grappes, la valeur critique est prise dans une loi de Student à (nombre de grappes − 1) degrés de liberté.
- **Décision.** Seuil unilatéral de 10 %, sur au moins 40 questions résolues, pour l'activation comme pour la désactivation.

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

- **Veille.** Chaque nuit, `collect.py` relève sans IA les titres des flux de franceinfo, Le Monde, LCP (Assemblée nationale), Public Sénat, Le Figaro, Libération et Mediapart dans `data/veille.json`. La pluralité des lignes éditoriales sert la mesure de reprise ; elle ne change pas la règle selon laquelle une révélation reste une allégation. Les agences et le Journal officiel n'offrent pas de flux libre ; une décision officielle est vérifiée sur sa source primaire au moment du tri.
- **Conservation.** Un titre non trié n'est jamais purgé. Les titres triés sont conservés 10 jours.
- **Tri.** Au moins trois fois par semaine, un modèle léger :
  - regroupe les titres par fait, en supprimant les doublons ;
  - rattache chaque fait à un jalon attendu, à un nœud ou à rien.

  Il ne juge pas la matérialité : c'est le rôle du panel (section 11.4). Les décisions de tri sont écrites dans un fichier par mois, `data/tri/AAAA-MM.jsonl`, en ajout seul ; la collecte le lit sans le modifier. Chaque ligne porte un seul titre et contient les clés `lien` (adresse du titre, obligatoire), `passage` (date du tri), `fait` (identifiant du fait qui regroupe les titres), `decision` (jalon, nœud ou « non rattaché ») et `motif`.
- **Caractérisation.** Chaque fait rattaché à un nœud ou à une question est caractérisé, avant toute estimation, sur trois axes :
  - **nature**, proposée par l'agent de tri : pénal lié à la fonction ou au mandat (détournement, corruption, financement illégal) ; pénal sans lien avec la fonction ; manquement éthique ou politique non pénal ; vie privée ; décision ou déclaration publique ; autre ;
  - **stade**, aligné sur les étapes officielles ci-dessous : allégation (révélation de presse, accusation, plainte annoncée, saisine ou signalement par un tiers) ; procédure engagée (enquête ouverte par le parquet, information judiciaire, perquisition, procédure ouverte par une autorité de contrôle) ; mise en cause formelle (mise en examen, témoin assisté, renvoi devant une juridiction, levée d'immunité) ; décision (jugement ou arrêt, décision d'une autorité de contrôle, décision de l'intéressé ou de son parti sur sa propre situation) ;
  - **appui** : catégorie de la meilleure source qui établit le fait (`modele/sources.md`) et nature de la preuve publiée (document, témoignages, déclaration de l'intéressé).

  **Mise en cause ou fait établi.** Le stade ne s'applique qu'aux mises en cause (natures pénales, manquements, vie privée). Un fait de nature « décision ou déclaration publique » ou « autre » est un fait public (par exemple un recours à l'article 49.3, un accord entre partis, un appel à la grève) : il est établi quand deux agents l'ont vérifié sur une source de la section 8.8 du noyau (étape « fait public vérifié », inscrite dans `data/tri/etapes.jsonl`) ; établi, il ne va pas en observation et n'est pas soumis à la règle d'abandon, et il est traité selon le tableau de la section 11.3 (cas a à e). Non vérifié, il est contesté : il va en observation et suit la table de réexamen. Les deux axes (étapes d'une mise en cause, vérification d'un fait public) sont distincts.

  **Caractérisation non publiée.** Le dépôt et la page sont publics. La caractérisation proposée par l'agent de tri (nature et stade proposés) sert au travail de la session et n'est pas écrite dans le dépôt ; seuls sont conservés le type (mise en cause ou fait établi), les questions concernées et, pour une étape officielle vérifiée, l'étape, sa source et la nature qu'elle établit (jamais « vie privée »).

  **Stade retenu.** L'agent de tri, qui ne lit que des titres, ne fait que proposer un stade. Le stade retenu est « allégation » par défaut. Un stade supérieur n'est retenu qu'après vérification de la même étape officielle par deux agents distincts, sur une source de résolution du noyau (section 8.8), comme pour le cas « donnée » ; chaque vérification est inscrite en ajout seul dans `data/tri/etapes.jsonl`. Le stade retenu est transmis aux évaluateurs (section 11.4), qui citent une classe de référence de même nature et de même stade. Un fait au stade « allégation » est un fait contesté (section 11.5) : il va en observation (cas f), quelle que soit la réputation du média qui le publie ; la distinction utile est entre allégation et fait établi, pas entre rédactions de référence.
- **Étape officielle.** Acte d'une autorité habilitée à agir sur l'affaire, accompli par cette autorité elle-même, et établi par une source de résolution du noyau (section 8.8) :
  - judiciaire : ouverture d'une enquête par le parquet, perquisition, ouverture d'une information judiciaire, mise en examen ou statut de témoin assisté, renvoi, jugement, arrêt (un appel est l'acte d'une partie, pas une étape) ;
  - administratif ou de contrôle : ouverture d'une procédure ou décision de la HATVP, de la CNCCFP, de la Cour des comptes ou d'un organe de déontologie ; une saisine de ces autorités ou un signalement au parquet par un tiers (adversaire politique, association, élu) n'en est pas une ;
  - parlementaire : levée d'immunité (la création d'une commission d'enquête peut être déclenchée par l'opposition et n'est pas une étape) ;
  - décision de l'intéressé ou de son parti sur sa propre situation : démission, retrait de candidature, suspension, exclusion.

  Ne sont pas des étapes officielles : une nouvelle révélation de presse, une plainte seulement annoncée par le plaignant (elle compte quand le parquet en confirme la réception ou ouvre une enquête), une réaction ou une déclaration d'un tiers. À défaut de publication par l'autorité, l'étape est établie par deux agences de presse concordantes ou par une déclaration de l'intéressé ou de son avocat sur sa propre situation.
- **Reprise.** Pour chaque fait, un script compte, à partir de la veille et des décisions de tri, le nombre de sources distinctes sur les sept premiers jours et sur les sept derniers jours (fenêtre glissante), et le nombre de jours où il apparaît (`data/reprise.json`). L'agent de tri reçoit la liste des faits suivis avec leur identifiant, pour qu'un même fait garde son identifiant d'un passage à l'autre. C'est une mesure descriptive : elle fixe la date de réexamen d'un fait en observation et s'affiche dans le volet actualité, mais n'entre dans aucune probabilité. L'effet d'une affaire sur l'opinion passe par les sondages (section 11.5).
- **Trace.** Toute décision est consignée, y compris « non rattaché », avec son motif.
- **Contrôle du tri.** Chaque trimestre, un second modèle réexamine 60 faits non rattachés tirés au sort, et 30 faits rattachés tirés au sort (type du fait et rattachement, seuls conservés). Plus de 10 % de faux négatifs (borne inférieure de l'intervalle à 80 % au-dessus de 5 %) entraînent une révision de la consigne de tri.
- **Champs libres.** L'identifiant d'un fait et le motif d'une décision de tri sont écrits dans le dépôt public : ils décrivent le rattachement en termes neutres, sans qualification pénale ni nature, et l'identifiant ne contient pas de nom de personne.

### 11.3 Traitements

| Cas | Quand | Traitement |
| --- | --- | --- |
| a. Sans effet | Non rattaché, ou effet jugé nul par le panel | Consigné avec motif |
| b. Donnée | Le fait résout un nœud ou mesure une variable, selon une source primaire officielle ou la collecte | Section 8.9 du noyau, applicable dès la phase 1 |
| c. Évidence | Le fait renseigne un nœud non résolu, par un canal qu'aucune donnée ne mesure | Preuve virtuelle (section 11.4) |
| d. Paramètre | Le fait changerait encore l'enfant si le parent était connu : il modifie une relation, pas la probabilité d'un nœud | En phase 3 : classé en observation (cas f) jusqu'à l'analyse trimestrielle suivante, qui peut réviser les lignes. En phase 4 : révision ciblée des lignes concernées, en un tour, sans montrer la ligne actuelle ; l'écart en log-cotes entre la ligne estimée et la ligne actuelle tient lieu de log-rapport pour le seuil et le plafond |
| e. Hors modèle | Aucun nœud ne correspond | Question ad hoc prévue directement, notée dans un pool séparé. Nœud candidat à l'analyse trimestrielle |
| f. En observation | Fait contesté, ou dont l'effet passe d'abord par une donnée à venir | Aucune mise à jour ; date de réexamen fixée (règle ci-dessous) |

**Réexamen et abandon d'un fait en observation.** La date de réexamen est fixée à l'entrée en observation, à 30 jours ; elle est ramenée à 14 jours au septième jour si au moins cinq sources distinctes ont repris le fait pendant la première semaine. À la date de réexamen :

| Situation | Traitement |
| --- | --- |
| Une étape officielle a été vérifiée depuis l'entrée | L'étape est un fait nouveau, daté et caractérisé, traité selon le tableau ci-dessus (cas c, ou cas b si elle résout une question) ; le fait d'origine est clos |
| Pas d'étape, et la reprise des sept derniers jours est au moins égale à celle des sept premiers | Une seule prolongation de 30 jours ; à son terme, sans étape, classement sans effet (cas a), motif « retombé » |
| Ni l'un ni l'autre | Classement sans effet (cas a), motif « retombé » |

L'effet d'une affaire sur l'opinion n'entre pas dans cette règle : il passe par les sondages (section 11.5), sans attribution causale. Une affaire qui produit au moins deux étapes officielles vérifiées devient candidate à un lien et à ses jalons (section 10), ou à un ajout à la banque (noyau, section 8.8), à l'analyse trimestrielle suivante. La décision de la table est prise une fois, à la date de réexamen, et inscrite en ajout seul dans `data/tri/statuts.jsonl` ; elle n'est pas recalculée ensuite. Un fait classé « retombé » reste clos : il garde son identifiant, et un nouveau titre ne le rouvre pas ; seule une étape officielle vérifiée en fait un fait nouveau. Le statut est calculé par `scripts/tri.py reprise`.

### 11.4 Preuve virtuelle

- **Principe.** Un fait d'évidence est intégré comme preuve virtuelle (Pearl 1988 ; Chan et Darwiche 2005) : un rapport de vraisemblance entre les issues du nœud, propagé vers l'amont et vers l'aval.
- **Conditions.**
  - Un fait par valence : des éléments de sens opposés sont des faits distincts.
  - Le fait est postérieur au gel de la dernière estimation du nœud.
  - Il est rattaché au nœud le plus en amont quand plusieurs nœuds sont concernés.
  - Le rapport est estimé sachant les faits déjà intégrés sur ce nœud, qui sont présentés aux évaluateurs.
- **Estimation.** Cinq évaluateurs aveugles, en un tour, répartis sur au moins trois modèles, reçoivent le fait et sa caractérisation (section 11.2) et estiment P(fait | issue) pour chaque issue, en citant au moins une classe de référence de même nature et de même stade. Agrégation par moyenne des log-rapports.
- **Seuil d'application.** Pas de mise à jour si les évaluateurs divergent de signe, si la moyenne des log-rapports est à moins de deux erreurs types de zéro, ou si le rapport appliqué est compris entre 0,8 et 1,25. Pour ce calcul, la dispersion des log-rapports entre évaluateurs, en log-cotes, ne peut être inférieure au plancher σ_plancher (section 4.4 du noyau) ; l'erreur type est cette dispersion divisée par √n. Un consensus de famille ne passe donc pas pour une preuve. Le fait est alors classé sans effet, avec ce motif.
- **Classe (version 1.8).** Un fait dont la plus faible vraisemblance agrégée vaut au plus le vingtième de la plus forte « tranche » : il est appliqué sans plafond ni réduction. Un fait au stade « allégation » n'a pas d'effet. Les autres sont des indices, soumis au plafond et à la réduction ci-dessous. Décisions consignées dans `modele/reseau/preuves.jsonl` (`scripts/faits.py`).
- **Chocs (version 1.9).** Un fait qui modifie un mécanisme plutôt qu'il ne renseigne sur une issue (affaire visant un candidat ou l'exécutif, attentat) est une intervention, non une preuve : il agit sur un à trois points d'entrée déclarés à l'avance dans la structure (« ports » : intentions de vote RN, popularité, écart de taux, retrait d'un candidat, départ du Premier ministre, vacance), avec une intensité tirée d'un barème par stade calé sur des précédents sourcés (`modele/reseau/bareme_chocs.json`) ; les évaluateurs choisissent seulement les ports, à la majorité. Sur une variable observée chaque mois, l'effet s'éteint à la première observation postérieure (le sondage ou le baromètre l'absorbe, sans double compte) ; sur un pivot, il dure jusqu'à ce que le pivot soit tranché. Une allégation reste sans effet.
- **Plafond.** Rapport brut entre 1/3 et 3, appliqué avant la réduction par k. Un fait jugé très diagnostique peut être porté à sept évaluateurs, avec un plafond de 10.
- **Réduction.** Le rapport appliqué est le rapport plafonné, élevé à la puissance k_faits. k_faits vaut 0,5 tant qu'il n'est pas estimé ; il est estimé comme k (section 10.4), sur tous les avis de panel enregistrés, y compris ceux restés sous le seuil.

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

**Faits visant des personnes nommées.** Le volet actualité est public. Pour un fait au stade « allégation », il affiche le titre et le lien de la source, avec la mention « allégation non vérifiée » ; il n'affiche aucune qualification pénale produite par un agent, seulement le stade retenu et l'étape officielle vérifiée, avec sa source. La nature « vie privée » n'est jamais affichée.

### 11.7 Critère de maintien

La décision repose sur la seule statistique Z de la section 10.11, sur 40 questions résolues au moins. Si Z n'est pas significatif au seuil unilatéral de 10 %, la couche est réduite aux cas b et f. Le test de signe sur la donnée arrivée ensuite (sondage, série) est publié à titre descriptif, sans décision attachée.

### 11.8 Coût

- **Tri :** un passage de modèle léger, trois fois par semaine.
- **Cas c (et d en phase 4) :** cinq évaluateurs sur un seul nœud, sept pour un fait très diagnostique.
- **Plafond :** au plus huit mises à jour c ou d par mois. Au-delà, les faits sont regroupés au cycle mensuel.
