# Réponse à la relecture 8

Noyau v1.11, annexe v1.1 inchangée. Méthode des sources v1.1. Banque d'événements réécrite : `modele/banque/criteres.json`. Toutes les corrections sont faites avant le premier cycle, tant que le registre du protocole est vide.

## 1. Fond

### 1.1 Périmètre

Accepté, avec une décision de Nathan sur l'international (voir plus bas).

| Manque relevé | Traitement |
| --- | --- |
| Qualification au second tour | EV-40a à g : une question par candidat (Le Pen, Philippe, Mélenchon, Lisnard, Attal, Glucksmann, Retailleau), une seule grappe. Référence externe : marché Polymarket « who will advance to the 2nd round », aujourd'hui non fiable (volume) ; publié, sans calage |
| Candidatures du bloc central | EV-41 : Philippe et Attal sur la liste officielle (quatre issues), référence externe Polymarket non fiable |
| Réponse publique au choc des prix | EV-42 : remise générale ou baisse d'accise sur les carburants publiée au Journal officiel avant le premier tour ; une aide ciblée ne compte pas |
| Mobilisation résoluble | EV-39 : une journée à plus de 500 000 manifestants selon le ministère de l'Intérieur, sur toute la période, avec questions mensuelles. Remplace EV-12 |
| Après l'élection | EV-43 cohabitation au 30 septembre 2028 ; EV-44 déficit 2028 inscrit dans la loi de finances (trois issues, dont l'absence de loi au 31 janvier 2028) ; EV-45 âge légal sous 64 ans pour la génération 1968 au 30 septembre 2028 |
| Confiance des ménages | Série Insee (identifiant 001587668) collectée et ajoutée aux variables, avec le Brent et l'inflation énergie |

**International.** Le correcteur proposait de retirer EV-30 à EV-34 et EV-37. Nathan a décidé de garder un indicateur par grand sujet mondial, dans un pool descriptif P2e sans décision attachée (noyau, section 8.3) : EV-28 cessez-le-feu en Ukraine, EV-30 Chambre des représentants (États-Unis), EV-32 contrôles chinois sur les terres rares (critère réécrit : état au 31 mars 2027, et non prolongation avant le 10 novembre), EV-33 suspension de l'accord UE-Israël (Proche-Orient). Retirés : EV-27, EV-31, EV-34, EV-37. L'énergie passe par les séries et EV-38 ; EV-29 et EV-36 restent en P2b, car ce sont des décisions françaises.

### 1.2 Événements EV-18 à EV-38

| Événement | Traitement |
| --- | --- |
| EV-18 | Issue « autre ou vote non tenu » ajoutée |
| EV-19 | Candidats soutenus « par une décision publiée » d'un parti listé |
| EV-20 | Issue « désistement » ajoutée |
| EV-21, EV-23, EV-38 | Gardés |
| EV-22 | Non retenu |
| EV-24, EV-25 | Non retenus tant que la série n'est pas confirmée ; candidats à un ajout encadré (section 8.8) |
| EV-26 | Non retenu, renvoyé à la série de sondages de la phase 2 |
| EV-27 | Retiré |
| EV-28 | « Déclaré rompu » supprimé : annonce par les deux gouvernements d'un cessez-le-feu général ou d'un accord de paix. Pas de marché coté trouvé dans la collecte pour aligner le critère |
| EV-29 | Résolu sur l'information du Parlement au titre de l'article 35, alinéa 2 |
| EV-30 | Gardé comme indicateur des États-Unis (P2e) |
| EV-31, EV-34, EV-37 | Retirés |
| EV-32, EV-33 | Gardés en P2e (décision de Nathan) |
| EV-35 | Gardé seul, en P2b |
| EV-36 | Résolu sur le projet de loi de finances déposé, comparé à l'annuité de la programmation en vigueur (plus de chiffre à vérifier) |

### 1.3 EV-05

Accepté. Issues par personne : Marine Le Pen, Jordan Bardella, Édouard Philippe, Gabriel Attal, Jean-Luc Mélenchon, David Lisnard, Bruno Retailleau, Raphaël Glucksmann, François Hollande, autre. Lisnard et Hollande sont ajoutés à la liste proposée parce que le marché les cote à 12 % et 4 %. La table personne → bloc est fixée dans le même fichier. Le critère ne contient plus ni cote ni sondage. EV-05 passe en P1 : le marché « Next French Presidential Election » est fiable (volume et écart), et `scripts/comparateurs.py` inscrit désormais la référence externe gelée au registre. Son taux de base est la loi uniforme (souhaitable « taux de base d'EV-05 »).

## 2. Méthode

### 2.1 Fiabilité des sources

- **Section 8.8.** Accepté : la règle de résolution est inscrite au noyau (source primaire pour ses propres actes ; institut si le critère le nomme ; partie prenante pour sa propre décision si le critère le prévoit ; à défaut d'autorité, deux agences de presse concordantes). EV-01 se résout sur le communiqué de l'agence, acte propre de celle-ci.
- **Primaire pour ses seuls actes.** Accepté : règle 1 bis de `modele/sources.md`. La bibliothèque de la Chambre des communes est reclassée en source secondaire.
- **Média d'État.** Accepté : le critère devient l'absence de statut garantissant l'indépendance éditoriale. BBC, RTS et France 24 sont MR ; Al Jazeera reste MEE ; RFE/RL passe en MR, à vérifier.
- **Sources lues.** Accepté : les adresses marquées non lues, bloquées ou inaccessibles sont exclues, et l'indicateur principal devient la part des faits étiquetés de rang 1 à 3 quand le document étiquette ses faits. La détection automatique trouve 18 adresses non lues sur les deux rapports, contre 26 relevées par le correcteur : elle dépend des mentions du rapport.
- **Typologie.** Accepté : une seule typologie, celle de `modele/sources.md` ; table de conversion pour les deux rapports existants. AGSI+ reste I, RFE/RL passe en MR.

### 2.2 Règle d'ajout

Accepté avec l'encadrement proposé, inscrit à la section 8.8 comme exception au gel (section 12) : cinq ajouts au plus par cycle, avant le gel, dans un fichier en ajout seul contrôlé à la poussée (`modele/banque/ajouts.jsonl`, champ `ajoute_le`) ; proposition par un agent sans accès aux registres ni aux prévisions, ou par décision humaine journalisée ; taux de base sur classe historique, sans recherche d'actualité ; aucun retrait ni modification d'une question émise ; bilans avec et sans les ajouts, verdict non concluant s'ils divergent.

### 2.3 Moteurs internationaux en nœuds racines

Accepté, sans changement de texte : la liste des nœuds est fixée à l'élicitation de la phase 3. Deux racines au plus : le Brent en terciles et le cessez-le-feu en Ukraine. La relation transatlantique n'est pas un nœud ; l'envoi de troupes est une décision française. Le lien Brent → inflation énergie sera estimé sur l'historique dès la phase 2.

## 3. Défauts d'exécution

- **G1.** Corrigé. Les critères sont dans `modele/banque/criteres.json` ; le texte du balayage v1 est conservé dans `contexte_v1`, jamais transmis. Le champ `source_resolution` ne contient plus que des sources.
- **G2.** Corrigé. `date_fait` est obligatoire dans les propositions (`scripts/registre.py`), reportée dans la résolution (`scripts/resolution.py`) ; `scripts/notation.py` exclut une prévision émise le jour du fait ou après ; le gel est daté du jour réel d'exécution (procédure du cycle et noyau, section 8.8). Tests ajoutés.
- **G3.** EV-07 réécrit sur des services nommés ; EV-10 retiré (non résoluble) ; EV-16a et b et EV-C1 réécrits sans le texte de fusion, qui expliquait probablement la dispersion. Une dispersion de plus de 40 points entre prévisionnistes est signalée comme critère possiblement ambigu (procédure du cycle, étape 4). EV-09 ne garde que la vigilance rouge canicule ; EV-17 est jugé sur la composition des groupes au 30 septembre 2028.
- **G4.** Corrigé avec 2.1.

**Souhaitables.**
- Taux de base d'EV-05 : loi uniforme.
- Grappes : une par événement (`scripts/questions.py`, noyau section 8.3). Banque d'essai : 111 questions, 49 grappes.
- Registre d'essai : `registre/README.md` précise que le fichier fait foi, pas le champ `piste`.
- Liste de contrôle : workflow coché (passé sur les poussées du 4 octobre) ; le test de rattrapage reste à faire.
- Séries : Brent, inflation énergie et confiance des ménages ajoutés à `VARIABLES`.
- Date du second tour : 18 avril et 2 mai 2027, confirmés sur info.gouv.fr.
- Report de la relecture 7 : en-tête du noyau aligné.

**Affirmations douteuses.**
- **Ormuz.** La mention du balayage v1 est périmée ; elle reste dans `modele/v1`, conservé tel quel, et n'est plus transmise.
- **Écart OAT-Bund.** Confirmé par la série quotidienne collectée (103 à 111 pb fin septembre, 124 pb le 1er octobre).
- **Inflation énergie.** L'Insee (IPC) et Eurostat (IPCH, 20,9 %) mesurent deux indices différents ; seule la série Eurostat est collectée.
- **Instruction du Havre et Vigipirate.** Non utilisés : EV-22 n'est pas retenu, et Vigipirate n'entre dans aucun critère.

## 4. Taux de base

Trois groupes d'agents ont estimé les événements nouveaux ou réécrits (`modele/taux_base/groupe_*_r8.json`). Ces estimations remplacent les anciennes pour EV-07, EV-09 et EV-17.

**Point à trancher.** Pour EV-45, les sources secondaires divergent sur l'effet de la suspension de la réforme de 2023 après le 1er janvier 2028 : maintien du barème modifié (63 ans et 9 mois pour la génération 1968), ou retour automatique au calendrier de 2023 (64 ans). Le statu quo, donc le taux de base, s'inverse selon la lecture. L'article L161-17-2 sera vérifié sur Légifrance avant le premier cycle ; le critère reste valable dans les deux cas.
