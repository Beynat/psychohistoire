# Relecture de validation 19 — noyau v1.23, annexe phase 3 v1.7, banque v1.7

Relecteur : Claude Opus 5.5, session neuve, sans accès aux échanges de rédaction (noyau, section 12). Date : 4 octobre 2026.
Objet : tag `protocole-v1.23` (76ea08f) et tag `annexe-phase3-v1.7` (2de1b04), banque `criteres.json` v1.7, scripts et workflows à ce commit. Les relectures antérieures n'ont pas été prises pour acquises.

## Synthèse

| Classe | Nombre | Défauts |
| --- | --- | --- |
| Bloquant | 1 | B1 : prévisions notées sur des questions « constat » dont l'issue est publique avant le constat officiel |
| Important | 1 | I1 : un cycle manqué par un seul auteur avantage l'autre dans le test de valeur ajoutée |
| Souhaitable | 13 | S1 à S13 |

Si ces classements sont confirmés, le compteur du critère d'arrêt reste à zéro. Les deux corrections sont courtes et n'exigent pas de refonte.

## 1. Méthode

Le protocole permet de conclure ce qu'il annonce, à condition de lire ses annonces comme il les formule lui-même : un test faible, dont l'issue la plus probable est « non concluant », avec une règle par défaut prudente. Les choix principaux tiennent :

- le Brier pondéré à poids indépendants de l'issue (durée prévue, longueur fixe, jours postérieurs au fait à zéro) est propre ; je l'ai vérifié par simulation, y compris avec des cycles manqués par l'auteur noté ;
- les questions entrent dans le test à leur échéance, quelle que soit l'issue, ce qui neutralise la sélection par les survenues ;
- la période commune, le réseau entièrement non calé, l'interdiction des marchés à l'ensemble et le contrôle des adresses ferment les fuites de cotes identifiées ;
- la calibration sur la première prévision de cycle est indépendante de l'issue ; la référence par copule intra-grappe est cohérente avec le test ;
- les chiffres de puissance du texte (17 à 19 % et 26 à 36 % sur P2b, 25 à 32 % et 48 à 59 % avec P2c, 28 grappes et 27 questions informatives au bilan final, une seule question informative pour un démarrage en mai) correspondent à `data/puissance.json`.

Restent deux défauts qui touchent ce que le protocole protège en priorité : l'antériorité (B1) et la symétrie de la comparaison (I1). Les limites déjà déclarées (dépendance entre grappes, critère de persistance presque inopérant sur P2a, une seule famille de modèles) ne sont pas recomptées comme défauts.

## 2. Défauts bloquants

### B1 — Questions « constat » : une prévision émise alors que l'issue est publique, mais avant le constat officiel, est notée

**Texte et code.** Noyau 8.8 : pour un événement « constat », la date du fait est « la date de publication du constat » ; seule est annulée une prévision émise le jour du fait ou après. Procédure du cycle, étape 1 bis : une question « constat » n'est retirée que si « le constat est déjà publié ». `notation.py`, lignes 170-171 : l'exclusion porte sur `emise` ≥ `date_fait` et sur `emise` > échéance ; `resolution.py`, fonction `df` : `date_fait` est la date portée par les avis, donc celle du constat.

**Scénario.** EV-30 (Chambre des représentants, P2e). Le scrutin a lieu le 3 novembre 2026 ; la majorité est donnée par les agences dans les jours qui suivent, mais le critère exige « les résultats certifiés », et les certifications des États s'étalent jusqu'à début ou mi-décembre. Au cycle du 1er décembre 2026 (et à celui de novembre s'il est rattrapé après le 3, ce que la règle du 1er au 7 permet), l'étape 1 bis ne trouve pas de constat publié : la question est émise, l'ensemble prévoit l'issue connue à 99 % (la consigne l'invite à signaler la question comme « déjà résolue », sans effet sur la notation), le taux de base reste figé, et la ligne est notée puisque sa date d'émission précède la date de certification. Même mécanisme pour EV-05 (P1) si le cycle de mai 2027 est exécuté le 2 mai après la fermeture des bureaux : l'échéance est le jour du scrutin, une prévision de ce jour-là est acceptée, la proclamation vient plusieurs jours après. Les questions du premier tour (EV-23, EV-40) n'y échappent que parce qu'aucun jour de cycle ne tombe entre le 18 avril et la proclamation. Tout ajout futur de nature « constat » (8.8) hérite du défaut. EV-20 en est une variante : si l'arrêt de cassation tombe en janvier, une lecture de « date de publication du constat » comme le 31 mars laisserait noter les cycles de février et mars ; l'étape 1 bis rattrape probablement ce cas, mais le texte ne le garantit pas.

**Effet.** Issue connue avant la prévision pour ces questions : la calibration publiée de P2e et l'écart publié sur P1 sont faussés en faveur des auteurs qui suivent l'actualité, contre le taux de base. Aucun verdict de la section 8.6 n'est touché aujourd'hui, puisque P1 et P2e en sont exclus ; d'où une portée limitée. La grille classe toutefois l'antériorité en bloquant sans condition de pool, et je ne vois pas de lecture raisonnable de « issue connue » qui exclue une majorité annoncée par les agences depuis plusieurs semaines.

**Correction proposée.**
- Noyau 8.8, « Date du fait » : « Pour un événement « constat », c'est la plus précoce de deux dates : la publication du constat, et le jour où l'issue est établie publiquement par une source de la section 8.8, deux agences concordantes comprises. Pour un résultat électoral, c'est le jour du scrutin. »
- Procédure, étape 1 bis : vérifier aussi si l'issue est déjà établie publiquement au sens de cette règle ; si oui, la question n'est pas émise.
- Code : rien à changer dans `notation.py` si `date_fait` suit la règle ; ajouter à `tests.py` un cas EV-30 (prévision du 1er décembre, date du fait au 4 novembre, prévision exclue).

## 3. Défauts importants

### I1 — Un cycle manqué par un seul auteur avantage l'autre dans le test de valeur ajoutée

**Texte et code.** Noyau 8.5 : « un cycle manqué avant le fait est couvert par la prévision précédente » ; 8.6 : test sur les instantanés mensuels. Procédure du cycle, étape 4 : après un second échec d'un prévisionniste, « le cycle passe sans ensemble direct » ; `ensemble.py` s'arrête aussi s'il manque des prévisionnistes conformes. `notation.py`, `comparer`, lignes 229-245 : les lignes de cycle de chaque auteur sont filtrées séparément ; rien n'exige que les deux auteurs aient prévu au même cycle. La propreté vérifiée par `test_brier_pondere_propre` porte sur un auteur seul ; elle montre précisément qu'un cycle manqué coûte à celui qui le manque.

**Scénario.** L'ensemble échoue au cycle d'avril 2027. Pour les questions du premier tour (une seule grappe, environ la moitié du poids informatif de P2b selon le texte), l'ensemble est noté du 1er au 18 avril sur sa prévision de mars, le modèle sur sa prévision d'avril. Simulation (variable latente en marche aléatoire, issue au bout de quatre mois, deux prévisionnistes honnêtes et également informés) : manquer le dernier cycle avant l'issue coûte en moyenne 0,013 de Brier pondéré par question, soit l'ordre de l'écart que le test cherche à détecter (0,02). Sur des événements rares à risque constant, le même effet existe mais reste faible (environ 0,0002 par question et par cycle manqué).

**Sens du biais.** Vers « la phase 3 fait mieux », c'est-à-dire une valeur ajoutée démontrée à tort : sens non prudent. Le cas symétrique (le modèle manque un cycle) pousse vers « moins bien », dont la conséquence est celle de la règle par défaut ; c'est le chemin de l'ensemble, prévu explicitement par la procédure, qui fait le défaut. Un effet de même sens, plus faible, naît si la prévision de cycle du modèle est émise plusieurs jours après le gel avec les mises à jour continues intégrées : rien dans le texte ne fixe sa date par rapport à celle de l'ensemble.

**Correction proposée.**
- Noyau 8.6 (instantanés) : « Pour chaque question, le test ne retient que les cycles où les deux auteurs ont une prévision de cycle ; un cycle manqué par l'un est retiré pour les deux, chacun étant alors couvert par sa prévision de cycle précédente. La prévision de cycle du modèle est calculée sur l'état du réseau au gel. »
- Code, dans `comparer`, après le filtrage des lignes de cycle :

```python
cyc = lambda l: re.match(r"cycle ([^\s,]+)", str(l.get("origine", ""))).group(1)
communs = {cyc(l) for l in ls} & {cyc(l) for l in lo}
ls = [l for l in ls if cyc(l) in communs]
lo = [l for l in lo if cyc(l) in communs]
```

  avec un test : deux auteurs identiques, l'un manque un cycle, l'écart doit être nul.

## 4. Défauts souhaitables

- **S1. Pool des nouvelles questions modifiable sans contrôle.** `correspondances_p1.json` est saisi à la main, gelé par cycle mais non contrôlé : d'un cycle à l'autre, les questions mensuelles d'un événement peuvent passer de P2b à P1, donc sortir du test de 8.6, sans trace autre que Git. Je l'ai vérifié sur une copie (critère modifié après un gel : détecté ; correspondance ajoutée : non détectée). Proposer : correspondance fixée par événement au premier gel et ajoutée aux champs de `controle_banque.py`, ou dérivée par script du drapeau de fiabilité de `cotes.json`.
- **S2. Périmètre du modèle : règle non implémentée.** Le texte (8.6) note sur le taux de base une question du périmètre sans prévision du modèle ; `notation.py` l'écarte. Ce n'est pas un biais démontré (l'omission se décide sans connaître l'issue), mais l'écart texte-code doit être levé avant la phase 3.
- **S3. Questions conjointes dans la grappe du lien.** Une question « A et B » est corrélée aux questions de A et de B, rangées dans d'autres grappes : la dépendance entre grappes, déjà déclarée, augmente dans les deux sens. Proposer de ranger la question conjointe dans la grappe de A, ou de fusionner les grappes de A, de B et du lien, comme pour la règle de l'acte.
- **S4. Résolution « non » d'un événement « survenue ».** La procédure (étape 5) prévoit une proposition sans issue quand l'agent « ne trouve pas la source ». Pour un événement qui ne s'est pas produit, l'absence d'acte est la réponse ; si deux agents la consignent comme recherche vaine, la question est annulée à 30 jours, et les annulations portent alors sur les seules issues « non ». Préciser : « Pour un événement « survenue », l'absence d'acte répondant au critère, après recherche sur la source prévue, vaut « non » ; la proposition sans issue est réservée à une source inaccessible. »
- **S5. Ordre des questions remises à l'ensemble.** `dossier.py` anonymise les identifiants mais garde l'ordre de la banque : les trois seuils d'une même série et d'un même horizon se suivent, par ordre croissant, ce qui révèle le seuil médian, donc la probabilité du comparateur de persistance. Mélanger l'ordre par une graine journalisée.
- **S6. Commentaires périmés.** `comparateurs.py` annonce encore des probabilités bornées entre 2 et 98 % ; `notation.py` décrit encore le Brier pondéré comme « arrêté la veille du fait » (lignes 9 et 175) et la calibration sur la « dernière prévision de cycle » (ligne 207) ; la docstring de `resolution.py` annule « si aucune proposition n'existe 30 jours après l'échéance ». Le code suit le texte ; les commentaires non.
- **S7. Recherches vaines.** Le texte compte deux passages du même identifiant comme deux agents ; `resolution.py` compte les recherches vaines par identifiant seul. Aligner l'un sur l'autre.
- **S8. Fin de durée au « 1er du mois qui suit le fait ».** La règle suppose des cycles le 1er. Avec un cycle rattrapé entre le 2 et le 7, la durée de la dernière prévision dépend légèrement de la date du fait. Écart faible, sans sens démontré ; formuler « jusqu'à la date du cycle suivant le fait ».
- **S9. EV-38 (stocks de gaz).** La résolution dépend d'une capture archivée d'une page dynamique d'AGSI+, que l'Internet Archive restitue souvent sans données ; à défaut, la question sera annulée, ce qui coûte une question du test sans le biaiser. Faire relever la valeur par la collecte le 3 février 2027 et la geler.
- **S10. EV-08 (ingérence).** « Désigne expressément l'élection présidentielle de 2027 comme sa cible » laisse place à deux lectures quand un rapport de VIGINUM décrit une campagne « dans le contexte » de l'élection. Préciser : le texte doit présenter l'élection comme l'objectif de la campagne, pas seulement comme son contexte.
- **S11. Couverture de la banque.** Manquent, pour la période : le résultat de législatives anticipées en 2027 (dissolution probable après la présidentielle ; une question sur la majorité absolue à l'issue du scrutin, échue avant le 30 septembre 2027, ajouterait une question informative là où il n'y en a que 12) ; les élections régionales et départementales de mars 2028 ; une variable de croissance du PIB, alors que la croissance est l'une des cinq cibles (section 5.2) et n'a qu'EV-06 ; le taux directeur de la BCE, bloc déclaré partiellement endogène ; les États-Unis après décembre 2026 (droits de douane UE-États-Unis).
- **S12. Puissance et vainqueur de la présidentielle.** EV-05 est en P1 et sort du test, alors que le modèle et l'ensemble y sont tous deux notés sans cote. Une question binaire en P2b (victoire d'un candidat du RN, par exemple) donnerait au test sa question la plus informative. À arbitrer, puisque le choix de P1 est délibéré.
- **S13. Protection des tags et de `main`.** Je n'ai pas pu vérifier les ensembles de règles GitHub (accès API refusé à cette session) ; le texte s'appuie sur eux pour l'intégrité.

## 5. Fond : couverture et critères

La banque couvre bien la séquence qui comptera d'ici septembre 2028 : stabilité gouvernementale (censure en trois fenêtres, dissolution avant et après le second tour), présidentielle (pourvoi, candidatures, nombre de candidats de gauche, participation, qualifications, vainqueur), finances publiques (note, procédure de déficit excessif, loi de finances 2027, déficit 2027, budget 2028, crédits de défense), économie (récession, six variables), société et sécurité (mobilisation, grève, terrorisme, outre-mer, cyberattaque, ingérence, retraites), Europe (cadre financier, Mercosur, gaz, BCE) et international en descriptif (Ukraine, États-Unis, Chine, Proche-Orient). Les manques sont listés en S11.

Les critères sont dans l'ensemble résolubles sans ambiguïté, sur des sources primaires qui publient leurs propres actes (Journal officiel, Assemblée nationale, Conseil constitutionnel, Insee, Conseil de l'UE, BCE, Météo-France). J'ai relu les 55 critères ; deux appellent une précision (EV-08, S10 ; EV-38, S9), et la date du fait des événements « constat » relève de B1. Les dates de la présidentielle (18 avril et 2 mai 2027) sont confirmées par recherche web. Les autres prémisses datées (arrêt du 7 juillet 2026, 326 actes antimusulmans en 2025, vote des Écologistes) sont postérieures à ma coupure et n'ont pas été revérifiées.

## 6. Conformité du code au texte

Exécutés à ce commit :
- `python scripts/tests.py` : 12 tests passés ;
- `python scripts/controle_banque.py` : banque conforme ;
- sur une copie : gel d'un cycle 2026-11 puis modification d'un critère (détectée) et d'une correspondance P1 (non détectée, S1) ;
- simulations du Brier pondéré : propreté pour un auteur seul confirmée ; écart entre deux auteurs dont l'un manque un cycle (I1).

Lus et confrontés au texte : `notation.py`, `resolution.py`, `questions.py`, `comparateurs.py`, `ensemble.py`, `verifier_reponse.py`, `dossier.py`, `evenements.py`, `geler.py`, `registre.py`, `controle_banque.py`, `premieres_valeurs.py`, `commun.py`, l'en-tête de `puissance.py`, les trois workflows, les procédures du cycle mensuel, de la phase 1 et du tri, la consigne de l'ensemble, `sources.md`. Conformes au texte, hors les points relevés : règle du Brier pondéré, période commune, exclusion des prévisions émises le jour du fait, questions échues quelle que soit l'issue, calibration sur la première prévision de cycle, bilans avec et sans ajouts, retrait de chaque grappe, puissance recalculée, gel de la banque et des taux de base, contrôle d'ajout seul et d'horodatage, plafond des ajouts, ancrage quotidien, péremption de la collecte à trois jours, première valeur collectée pour les séries, errata et réouvertures.

## 7. Non vérifié

- La protection effective des tags et de `main`, et l'historique d'exécution des workflows sur GitHub (S13).
- `puissance.py` n'a pas été relancé : j'ai comparé le texte à `data/puissance.json` et lu la méthode.
- `scripts/tri.py`, `taux_base.py`, `sources.py`, `collecte/*.py` et `index.html` n'ont pas été lus en détail ; la collecte n'a pas été exécutée (réseau limité).
- Les taux de base (`modele/taux_base/`) n'ont pas été recalculés ; leurs classes de référence n'ont pas été contrôlées une à une.
- L'annexe a été relue pour sa cohérence et son effet possible sur la section 8.6, sans simulation de ses règles (jalons, preuve virtuelle, statistique Z), qui relèvent de la phase 3.
- Les faits postérieurs à juin 2026 cités dans la banque, sauf les dates de la présidentielle.