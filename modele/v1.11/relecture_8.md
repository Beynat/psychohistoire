Je récupère l'état du dépôt et je lis les pièces de fond et d'exécution avant de rendre la relecture 8.

**Verdict.** Le constat de départ est juste sur un point, l'énergie, et les séries Brent et inflation énergie sont le bon ajout. Mais la proposition s'étend à des sujets internationaux sans canal démontré vers la France, et laisse de côté ce qui décide une présidentielle : qui se qualifie au second tour, l'offre du bloc central, la réponse publique aux prix des carburants et une mobilisation qu'on puisse résoudre. Côté exécution, je relève quatre défauts importants à corriger avant le 1er novembre, aucun bloquant.

J'ai lu les pièces au commit `d9e6661` (noyau et annexe inchangés). Je ne peux pas confirmer par moi-même les faits postérieurs à mi-2026. Je signale donc les incohérences internes, et ce que vos propres séries collectées permettent de trancher.

## 1. Fond

### 1.1 Périmètre

**La prémisse est à nuancer.** Vos propres chiffres disent que l'international ne pèse sur le vote que par les prix : la défense n'est prioritaire que pour 15 % des électeurs, le pouvoir d'achat pour plus de la moitié. Le périmètre doit suivre ce constat.

**Ce qui manque, par ordre d'importance :**
- **Qualification au second tour.** C'est l'incertitude centrale (Philippe, Mélenchon ou Glucksmann face au RN), et aucun événement ne la porte. Polymarket cote déjà « qui accède au second tour ».
- **Candidature du bloc central.** Philippe et Attal sont-ils tous deux sur la liste officielle ? Le rapport dit ce sujet « déjà dans le modèle » : il n'est que dans la piste exploratoire, pas dans la banque.
- **Réponse publique au choc.** Une remise générale ou une baisse de taxe sur les carburants, publiée au Journal officiel, agit à la fois sur les prix, le déficit et le vote. Rien ne la suit.
- **Mobilisation résoluble.** EV-11, EV-12 et EV-14 ne sont pas émis faute de source, alors que le canal « énergie, puis mobilisation » est celui que vous jugez décisif. Deux critères résolubles : une journée à plus de 500 000 manifestants selon le ministère de l'Intérieur, ou la part de stations en rupture d'après les données ouvertes des prix des carburants.
- **Après l'élection.** Seize des vingt-trois mois de l'horizon suivent le scrutin et sont peu couverts : nomination à Matignon, cible de déficit du premier budget, sort de la réforme des retraites suspendue jusqu'en 2028.
- **Confiance des ménages (Insee, mensuelle).** C'est la série qui relie le mieux prix et vote.

**À retirer ou ne pas ajouter :** EV-32, EV-37, EV-33, EV-31, EV-34 (motifs ci-dessous).

### 1.2 Événements EV-18 à EV-38

| Événement | Résoluble sans ambiguïté ? | Information | Avis |
|---|---|---|---|
| EV-18 Écologistes | Oui, si l'on ajoute une issue « autre ou vote non tenu » | Moyenne | Garder |
| EV-19 Fragmentation | Oui, en comptant les candidats soutenus par décision publiée d'un parti listé | Bonne | Garder |
| EV-20 Cassation Le Pen | Oui ; ajouter l'issue « désistement » | Forte | Garder |
| EV-21 Le Pen candidate | Oui | Forte | Garder |
| EV-22 Philippe | Non : aucune source officielle ne publie une mise en examen | Faible (rare) | Garder seulement avec un repli sur deux agences de presse |
| EV-23 Participation | Oui | Descriptive | Garder |
| EV-24, EV-25 Enjeux | Pas encore : série et périodicité non confirmées | Bonne | Garder une fois la série confirmée ; viser « dernière vague publiée avant le 31 mars » |
| EV-26 Niveau du RN | Non : « hypothèse principale » indéfinie, date de vague inconnue | — | Remplacer par la série de sondages de la phase 2 |
| EV-27 Ormuz | Non : « accord écrit prévoyant la réouverture » est flou, et le protocole du 17 juin pourrait déjà y répondre | Redondant avec le Brent | Retirer, ou reprendre le critère exact d'un marché coté |
| EV-28 Cessez-le-feu | Partiellement : « déclaré rompu » est ambigu | Moyenne | Garder, aligné sur le critère d'un marché coté |
| EV-29 Troupes | Non : « annonce le déploiement » confond intention et envoi | Forte si elle survient | Résoudre sur l'information du Parlement au titre de l'article 35 de la Constitution |
| EV-30 Midterms | Oui | Faible pour la France ; cotée | Retirer, ou garder comme simple référence externe |
| EV-31 Turnberry | Oui | Faible, lointaine | Retirer |
| EV-32 Terres rares | Ambigu ; résolu neuf jours après le premier cycle, peut-être déjà acquis | Nulle | Retirer |
| EV-33 UE-Israël | Oui | Faible effet en France | Retirer |
| EV-34 Actes antisémites | Oui | Quasi certaine : environ 529 actes au premier semestre contre un seuil de 1 320 | Retirer |
| EV-35 Actes antimusulmans | Oui | Pile ou face sur une mesure bruitée | Retirer ou garder seule |
| EV-36 Crédits de défense | Non si la loi de finances 2028 n'est pas votée à temps | Bonne (signal du nouvel exécutif) | Résoudre sur le projet de loi déposé |
| EV-37 Frontex | Oui | Sans effet démontré, résolue en 2028 | Retirer |
| EV-38 Gaz | Oui | Bonne | Garder |

Bilan : onze événements à garder ou corriger, dix à retirer ou remplacer, six à ajouter (section 1.1).

### 1.3 Réécriture d'EV-05

Je recommande des issues par candidat plutôt que par bloc :

> « Personne proclamée élue par le Conseil constitutionnel à l'issue de l'élection de 2027. Issues : Marine Le Pen ; autre candidat investi par le RN ; Édouard Philippe ; Gabriel Attal ; Jean-Luc Mélenchon ; candidat investi par le PS ou Place publique ; Bruno Retailleau ; autre. Échéance : proclamation des résultats. »

- Les blocs se déduisent ensuite d'une table candidat → bloc, fixée maintenant.
- Les issues actuelles se chevauchent (« droite LR ou autre » et « autre »).
- Le critère doit perdre ses cotes et ses sondages du 3 octobre.
- Polymarket cote chaque candidat, et votre collecte marque ces marchés fiables. EV-05 doit donc passer dans le pool P1 : il est aujourd'hui en P2b, là où se mesure la valeur propre du modèle, et le fichier des correspondances est vide.

## 2. Méthode

### 2.1 Fiabilité des sources

- **Compatibilité avec la section 8.8 : non.** Le noyau n'admet qu'une source primaire officielle. La règle d'usage 1 admet aussi un institut ou une partie prenante nommés par le critère. EV-18, EV-24, EV-25 et EV-38 seraient annulés sous le noyau actuel, et EV-01 se résout déjà sur des agences privées. Il faut inscrire au noyau cette seule règle, avec un repli sur deux agences de presse quand aucune autorité ne publie l'acte. Le reste (classement, indicateur) peut rester hors noyau.
- **Compatibilité avec la section 8.9 : oui.**
- **Le classement se fait par domaine, alors que la fiabilité dépend de l'affirmation.** La chronologie de la guerre d'Iran repose sur une note de la bibliothèque de la Chambre des communes, classée « primaire officielle » par la règle de suffixe. C'est une synthèse secondaire. Même défaut pour `un.org` (chiffres venus du ministère de la Santé de Gaza) et `gov.cn`. Règle à ajouter : une source n'est primaire que pour ses propres actes et données.
- **Le critère « média d'État étranger » est mal posé.** « Financé par un État hors de l'UE » classerait la BBC avec RT, et votre fichier classe la RTS suisse en média de référence. Le bon critère est l'indépendance éditoriale garantie par un statut.
- **L'indicateur compte les sources citées, pas les sources lues.** 26 adresses sur 158 sont marquées non lues, bloquées ou non utilisées, dont 15 de rang 1 à 3. Trois des quatre sources officielles du rapport de campagne n'ont pas été ouvertes. Il faut les exclure, et mesurer plutôt la part des faits chiffrés appuyés par une source lue de rang 1 à 3.
- **Deux typologies coexistent.** Le rapport international classe AGSI+ en partie prenante et RFE/RL en média de référence ; le fichier dit l'inverse.

### 2.2 Règle d'ajout à chaque cycle

L'argument « tous les comparateurs répondent aux mêmes questions » ne couvre pas trois biais :
- **Choix des questions.** En phase 3, ceux qui construisent le réseau pourraient ajouter des questions là où il est fort, ce qui fausserait le critère 8.6.
- **Taux de base contaminé.** Un événement ajouté parce qu'il devient probable reçoit un taux de base estimé par des agents qui connaissent l'actualité. Ce n'est plus une ligne de base naïve.
- **Saillance.** Les ajouts suivent l'actualité et multiplient les grappes corrélées.

Encadrement proposé :
- ajouts proposés par un agent sans accès au registre ni aux prévisions ;
- cinq ajouts au plus par cycle, chacun avec critère, source et motif, dans un fichier en ajout seul contrôlé à la poussée ;
- bilans publiés avec et sans les questions ajoutées après le premier cycle, le critère 8.6 étant jugé sur les deux ;
- le gros de la correction fait maintenant, tant que le registre du protocole est vide.

C'est un ajout au noyau, donc une nouvelle exception au gel : à écrire comme telle.

### 2.3 Moteurs internationaux en nœuds racines

Acceptable avec quatre réserves :
- Le plafond est de 10 à 15 nœuds : quatre racines en prennent un tiers. Deux suffisent, le Brent en terciles et le cessez-le-feu en Ukraine.
- « Guerre au Moyen-Orient » et « énergie » ne sont pas deux racines : l'une cause l'autre.
- « Relation transatlantique » n'est pas mesurable, donc pas un nœud.
- Le lien Brent → inflation énergie s'estime sur l'historique dès la phase 2, mieux que par une table élicitée.

L'envoi de troupes est une décision française, pas un moteur exogène.

## 3. Nouveaux défauts d'exécution

Aucun bloquant.

### Importants

**G1. Les critères remis aux prévisionnistes contiennent des cotes, des sondages et des taux de base.**
- **Constat.** Le champ `critere` recopie le balayage mot pour mot : cotes Polymarket du 3 octobre (EV-05, EV-16), « taux de base (calcul de B) » (EV-10, EV-15), remarques de fusion (EV-17). Le champ `source_resolution` d'EV-10 contient des chiffres, pas une source.
- **Problème.** Le comparateur principal est ancré, à chaque cycle, sur des chiffres périmés. La recopie sans sélection venait de ma relecture 4 : elle a eu cet effet de bord.
- **Correction.** Séparer `critere` (seul transmis) et `contexte`. Nettoyer avant le premier cycle.

**G2. Une prévision émise après le fait est notée.**
- **Constat.** `notation.py` exclut une prévision postérieure à l'enregistrement de la résolution, pas à la date du fait. Le cycle peut tourner jusqu'au 7 avec un gel daté du 1er, et les prévisionnistes cherchent sur le web.
- **Problème.** Un prévisionniste lancé le 5 voit un événement survenu le 3 et répond 98 % à la question « survenu dans le mois ». Les comparateurs figés sont désavantagés.
- **Correction.** Champ `date_fait` obligatoire dans les propositions ; exclusion si l'émission est postérieure ; gel daté du jour réel d'exécution.

**G3. Critères non résolubles dans la banque actuelle.**
- EV-07 : la liste des opérateurs d'importance vitale est classifiée.
- EV-10 : aucune source ne publie le nombre d'établissements bloqués.
- Les avis des cinq prévisionnistes de l'essai vont de 12 à 80 % sur EV-16b et de 18 à 85 % sur EV-C1 : ils ne lisent pas le même critère.
- **Correction.** Retirer ou réécrire ces critères ; traiter toute dispersion de plus de 40 points comme un signal d'ambiguïté.

**G4. Règle de résolution du noyau trop étroite** (section 2.1) : à corriger avant d'émettre une question résolue par un institut.

### Souhaitables

- **Taux de base d'EV-05.** Le comparateur donne 3,7 % au RN, parce qu'il n'a jamais gagné. Battre ce comparateur ne prouvera rien : prendre la cote de marché ou une répartition uniforme.
- **Grappes.** La question de fenêtre d'un événement et ses questions mensuelles sont dans des grappes différentes, alors qu'elles sont corrélées. Dix questions mensuelles sur vingt-neuf portent sur des événements rares où tout le monde répond 2 à 5 %. Elles gonflent le compte des 40 grappes sans rien apporter. Une grappe par événement serait plus juste.
- **Registre d'essai.** Ses 904 lignes portent `piste: protocole`.
- **Liste de contrôle.** « Workflow de contrôle actif » et « rattrapage testé » ne sont pas cochés.
- **Séries.** Brent et inflation énergie sont collectés mais absents de `VARIABLES` : aucune question n'est encore générée.
- **Date du second tour.** `second_tour_a_verifier` reste ouvert, alors que le rapport cite info.gouv.fr pour les 18 avril et 2 mai.

### Affirmations douteuses ou contradictoires

- **Ormuz.** Le balayage v1 disait les flux « revenus au niveau d'avant-guerre » (HNGN, 2 octobre). Le rapport dit 132 transits par semaine contre 130 par jour avant la guerre. Votre série EIA tranche : 114 $ en septembre contre 78 $ en février. La mention v1 est fausse ou périmée.
- **Date du blocage.** « Fin mars » (Wikipédia) dans un rapport, immédiatement après le 28 février dans l'autre.
- **Écart OAT-Bund.** Marqué « non vérifié », alors que votre série quotidienne le confirme : 103 à 111 pb fin septembre, 124 pb le 1er octobre.
- **Inflation énergie à 21,2 %.** Étiquetée « Insee » dans le rapport de campagne, « non vérifiée dans le texte Insee » dans l'autre.
- **Instruction du Havre.** Elle ne repose que sur Wikipédia, donc « non vérifiée » selon votre règle 2. La désignation d'un juge « en 2026 » me paraît tardive, de mémoire plutôt 2025 : à vérifier.
- **Vigipirate.** Le niveau « urgence attentat » n'est pas continu depuis Arras : il a été abaissé en janvier 2024 puis relevé en mars 2024.
- **Déjà signalés par les rapports et à lever :** l'approbation de Trump (31 % ou 37 à 39 %), le Premier ministre britannique, l'adoption définitive de la programmation militaire, le nombre de candidats à la primaire.

## Ce qui est solide

1. Les deux rapports typent leurs sources et listent ce qui n'a pas pu être vérifié.
2. L'essai planifié a trouvé et corrigé de vrais défauts (ancrage quotidien de l'écart, vérification des réponses, événements déjà survenus).
3. Les séries d'énergie sont collectées sur sources primaires et tranchent déjà deux doutes des rapports.