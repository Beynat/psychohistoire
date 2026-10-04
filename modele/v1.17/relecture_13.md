# Relecture 13 — noyau v1.16, annexe v1.5

Session neuve, sans accès aux échanges de rédaction. Dépôt cloné le 4 octobre 2026 et lu au commit `acecd1d` (`acecd1d2ffad5963c8a1c8f7a7798d7cd3a6ce3f`). HEAD, le tag `protocole-v1.16` et le tag `annexe-phase3-v1.5` désignent ce même commit. Banque v1.4.

**Verdict.** Les corrections de la relecture 12 sont faites, dans le texte et dans les scripts, à une exception près (S6, résolution des séries). Je les ai vérifiées par exécution, pas sur la foi de la réponse. Un regard neuf fait apparaître un défaut important, limité aux questions de variables : le script résout une question de série sur la valeur présente au premier passage de résolution, qui peut être la moyenne d'un mois incomplet (Brent) ou une valeur déjà révisée (IPCH), alors que le texte gelé dit « première valeur collectée ». Aucun défaut bloquant, un important : le critère d'arrêt n'est pas atteint. Le défaut se corrige sans décision de méthode.

**Ce que j'ai fait.**
- Lecture intégrale : noyau, annexe, relecture 12 et sa réponse, journal, statut, banque, taux de base, sources, tous les scripts de `scripts/`, les trois workflows, les procédures et listes de contrôle, la consigne de l'ensemble. Lecture des relectures 8 à 11 et recherche ciblée dans les relectures 1 à 7 pour ne pas rouvrir un point tranché.
- Comparaison des textes : `git diff protocole-v1.15 protocole-v1.16` pour le noyau, `annexe-phase3-v1.4` contre `v1.5` pour l'annexe.
- Exécution, sur des copies : `tests.py` (six tests conformes), `controle_banque.py` (conforme), `puissance.py`, régénération de `evenements.json` et de `taux_base.json` (identiques aux fichiers du dépôt).
- Simulation de cinq cycles réels (novembre 2026 à mars 2027), puis d'un gel d'avril : gel, questions, comparateurs, dossier anonymisé, cinq prévisionnistes fictifs, vérification, agrégation, propositions, résolution, bilan. Un auteur « modèle » démarre en janvier 2027, avec des lignes de cycle et une mise à jour continue.
- Essais ciblés : ajout à la banque (avec et sans taux de base, avant et après le gel, six ajouts, identifiant en double) ; deux avis du même agent ; erratum de résolution ; annulation à 60 jours ; modification de champs après gel ; tri (caractérisation, étapes, réexamen, scénario S8 de la relecture 12) ; « non » proposé avant l'échéance.
- Workflow de contrôle des registres : code Python extrait du fichier et exécuté localement sur un clone de travail (fichier de cycle modifié ou supprimé, ligne réécrite, ligne antidatée, ajout régulier).
- Tests par mutation : huit corrections de la relecture 12 retirées une à une, pour voir si `tests.py` le détecte.
- Comparaison du test par permutation réel au seuil de Student de la simulation de puissance, sur la banque réelle.

**Limites.**
- Je suis de la même famille de modèles que les auteurs. Mes angles morts sont probablement les leurs.
- Je ne peux pas confirmer les faits postérieurs à ma date de coupure : classes de référence des taux de base, arrêt du 7 juillet 2026, nombre de 326 actes, dates du scrutin, cotes relevées.
- Les workflows n'ont pas tourné sur GitHub : je les ai lus, et j'ai exécuté localement le code de l'un d'eux. Les règles de protection de la branche et des tags, et les tâches planifiées, ne sont pas vérifiables depuis le dépôt.
- Mes simulations utilisent des prévisions et des séries fictives. Elles vérifient la mécanique, pas la qualité des prévisions.
- Lus sans examen approfondi : `collecte/cotes.py`, `collecte/webstat.py`, `scripts/sources.py`, `index.html`, les rapports d'analyse.

## 1. Suivi de la relecture 12

| Point | Avis | Motif |
| --- | --- | --- |
| K1, période commune dans le noyau | Suffisante | La règle est écrite en 8.5 (vérifié par le diff). Sur ma simulation, le modèle démarré en janvier est comparé à l'ensemble sur la période commune : écart nul à prévisions égales. Le test de bout en bout passe par `bilan` et échoue si on retire la règle (mutation détectée). |
| K2, test de 8.6 calculé tel qu'écrit | Suffisante | Seuls les cycles du registre sont lus ; critère sur P2b et P2c ; avec et sans ajouts (13 et 12 grappes sur ma simulation) ; persistance sur P2a, taux de base sur P2b. Réserves mineures : le verdict combiné n'est pas calculé (S9) ; le filtre des cycles n'est couvert par aucun test (S4). |
| K3, instantanés mensuels | Suffisante | Écrit en 8.5. Vérifié : une mise à jour continue du modèle le 15 janvier n'entre pas dans `critere_8_6` et apparaît dans le bilan descriptif. Non couvert par les tests (S4). |
| K4, grappe unique | Suffisante | Champ `acte` sur EV-19, 20, 21, 23, 40a à 40g et 41 ; règle écrite en 8.3. Je reproduis 14 grappes, 90 questions, 12 informatives, dont 10 dans la grappe de la présidentielle. Le texte dit qu'un verdict significatif reste une preuve faible. Réserves : `acte` n'est pas dans le contrôle de la banque (S3) ; non couvert par les tests (S4). |
| K5, faits non judiciaires | Suffisante pour le texte, partielle pour le script | L'annexe distingue mise en cause et fait public vérifié. Vérifié : un recours au 49.3 vérifié par deux agents devient « fait établi ». Mais `tri.py` classe la nature « autre » en « mise en cause » : un appel à la grève finit « retombé » (S5). Descriptif en phases 1 et 2. |
| K6, caractérisation non publiée | Suffisante | Vérifié par exécution : ni nature ni stade proposé dans `data/tri/*.jsonl` ni dans `data/reprise.json`. `actualite.md` est aligné. Reste le champ libre `motif` (S5). |
| S1, convention du Brier | Suffisante | ½ Σ (p − y)² en 8.5 et dans `notation.brier` ; test ajouté, mutation détectée. |
| S2, test écrit | Suffisante | 8.5 décrit la permutation. J'ai comparé les deux tests sur la banque réelle : rejet à 9,7 % (Student) et 10,3 % (permutation) sous l'hypothèse nulle, 32,7 % et 35,1 % pour 0,04. « Les mêmes résultats » est exact à trois points près. |
| S3, ce qui n'est pas figé | Suffisante | Fichiers de cycle : modification et suppression détectées (code du workflow exécuté localement). Pool fixé à la première émission (8.3 et script). Taux de base : modification détectée. Restent quatre champs hors contrôle (S3 ci-dessous) et une tension avec 4.5 (S10). |
| S4, ajouts à la banque | Suffisante | Ajout sans taux de base : `taux_base.py` échoue. Ajout après le gel : non émis dans le cycle, comparateurs sans erreur. Six ajouts et identifiant en double : contrôle non conforme. |
| S5, résolution | Suffisante | Deux avis du même agent ne résolvent pas ; un troisième agent tranche à la majorité ; un seul avis donne l'annulation à 61 jours ; un erratum modifie bien la notation. Réserves : identifiants d'agents (S6), tests (S4). |
| S6, révisions des séries | Insuffisante | Le texte est écrit (8.8). Le script ne l'applique pas : il prend la valeur présente au premier passage de résolution et date le fait de ce passage. Voir L1. |
| S7, identifiants anonymisés | Suffisante | `Q001`… remis aux prévisionnistes, correspondance appliquée par `verifier_reponse.py` et `ensemble.py` (vérifié sur cinq cycles). L'ordre des trois seuils d'une même série reste lisible ; c'est inévitable. |
| S8, tri | Suffisante | Décision inscrite une fois dans `statuts.jsonl` ; deux étapes différentes ne relèvent pas le stade ; votre scénario reste « retombé » le 3, le 11 et le 20 février. |
| S9, banque | Suffisante | EV-09a et b en « survenue », EV-06 clos le 15 août 2028, règle des dépêches reprises en 8.8. |
| S10, puissance | Suffisante | P2c simulé à 10 % ; démarrage tardif écrit en 8.6 et publié. Réserves sur les hypothèses en S7 ci-dessous. |
| S11, biais commun | Suffisante | Correction retirée de 8.4 et de 12. |
| S12, nœuds M | Suffisante | Loi de M, δ et contrainte de centrage écrits en 10.1. La contrainte est bien définie : une équation monotone par ligne. |
| S13, critères de 8.6 | Suffisante pour le texte | Les trois phrases sont écrites. Le critère de calibration reste sans statistique définie et sans script (S2 ci-dessous). |
| S14, version définitive et textes périmés | Suffisante | Règle écrite en 12 ; renvois à `statut.json`. Il reste des mentions périmées dans les listes de contrôle (S12). |
| S15, tests | Partiellement suffisante | Le test de bout en bout existe et tourne. Sur huit corrections retirées par mutation, quatre ne font échouer aucun test, dont deux que sa description dit couvrir (S4). |

## 2. Relecture d'ensemble

### Bloquants

Aucun.

### Importants

**L1. Les questions de variables ne sont pas résolues sur la première valeur collectée, et le Brent l'est sur un mois incomplet.**

- **Constat a, Brent.** `collecte/historique.py` calcule `brent_mensuel` comme la moyenne des cotations quotidiennes disponibles, mois en cours compris. Vérifié sur les données du dépôt : la valeur de septembre 2026 (114,08) est la moyenne de 21 cotations arrêtées au 29 septembre. `resolution.py` résout une question dès que la période figure dans la série. Essai : après le cycle du 1er novembre, j'ajoute trois cotations (2, 3 et 4 novembre) et j'applique la fonction du collecteur ; la série contient « 2026-11 = 132,0 ». Un passage de tri du 6 novembre ajoute deux propositions sur un autre événement et lance `resolution.py`, comme le prévoit la procédure. Résultat : les trois questions « moyenne mensuelle du Brent pour 2026-11 » sont résolues le 6 novembre sur trois jours de cotation. Sans passage de tri, elles le seraient au cycle du 1er décembre, sur un mois encore amputé de ses derniers jours (la source a quelques jours de retard).
- **Constat b, révisions.** Le noyau dit depuis la v1.16 : « résolue sur la première valeur collectée de sa période ; sa date de collecte est la date du fait ». Le script écrit `date_fait = aujourdhui` et lit la série courante, que la collecte réécrit chaque nuit. Rien ne conserve la première valeur ni sa date. Essai : estimation rapide de l'IPCH de novembre collectée le 2 décembre, égale au seuil (3,4, issue « oui ») ; valeur révisée à 3,3 le 17 décembre ; résolution au cycle du 1er janvier. Résultat : issue « non », valeur 3,3, date du fait 1er janvier, source libellée « première valeur collectée ». La série du dépôt contient déjà une estimation rapide (septembre 2026 présent le 4 octobre). Le cas n'est pas marginal : l'estimation rapide paraît en général après l'heure du cycle du 1er, donc la résolution attend le cycle suivant, après la publication définitive.
- **Problème.** Le texte qui sera gelé est contredit par le script. Pour le Brent, 9 des 54 questions de variables de chaque cycle sont résolues sur une grandeur qui n'est pas celle de la question, et l'issue est ensuite verrouillée (« une révision ultérieure ne change pas l'issue »). Pour l'IPCH et l'inflation de l'énergie, l'issue dépend du jour où le script tourne. Ces issues entrent dans P2a, donc dans le critère de persistance, dont la conséquence est l'échec méthodologique. L'erreur ne favorise aucun auteur, mais elle fausse des résultats, et un tiers qui appliquerait la règle écrite n'obtiendrait pas les mêmes issues. C'est le point S6 de la relecture 12, dont seule la moitié « texte » a été traitée.
- **Correction proposée.**
  - Brent : n'écrire un mois dans `brent_mensuel` qu'une fois complet (première cotation du mois suivant présente), ou prendre la série mensuelle de la source.
  - Toutes séries : faire tenir par la collecte un journal en ajout seul des premières valeurs (série, période, valeur, date de collecte), écrit la première fois qu'une période apparaît, et placé sous le contrôle d'ajout seul. `resolution.py` lit ce journal et reprend sa date comme date du fait.
  - Ajouter un test : valeur collectée, puis révisée, puis résolue ; l'issue doit suivre la première valeur.
  - Aucun changement de texte n'est nécessaire.

### Souhaitables

Les deux premiers méritent d'être traités avant le premier cycle.

- **S1. Un « non » prématuré clôt une question, sans retour possible.** Essai : deux agents proposent « non » sur Q-EV-01 le 10 novembre 2026. `resolution.py` résout « non » avec une date du fait au 30 septembre 2028, et la question n'est plus émise (« déjà résolue »). Un erratum corrige une issue mais ne rouvre pas une question. Or l'étape 1 bis dit « chaque constat, quelle que soit l'issue, est ajouté comme proposition » : deux agents qui liraient « constat » au sens courant fermeraient les événements « survenue » non encore produits. Je classe ce point souhaitable parce qu'il suppose une erreur d'agents, alors que L1 se produit en fonctionnement normal ; le garde-fou coûte une ligne. Correction : refuser une issue « non » sur un événement « survenue » avant son échéance ; préciser l'étape 1 bis ; prévoir un erratum qui rouvre.
- **S2. Le critère de calibration de 8.6 n'a ni statistique ni script.** Le texte ne dit pas quelle erreur de calibration (terme de fiabilité de Murphy, autre), sur quelles classes, quel pool, quelle corrélation intra-grappe (la simulation de puissance en emploie deux), ni comment on recalibre. `notation.py` ne calcule que la décomposition de Murphy ; aucune simulation sous calibration parfaite n'existe. Un critère fixé à l'avance dont la mesure reste à choisir laisse une liberté à l'analyste. Conséquence limitée (recalibrer et chercher la cause). Correction : écrire la mesure (par exemple le terme de fiabilité en dix classes, sur les questions binaires de P2b et P2c, prévisions de cycle, ρ = 0,3) et la méthode de recalibration ; scripter la simulation.
- **S3. Quatre champs échappent au contrôle de la banque.** Essai après un gel : retirer `acte` d'EV-21, changer `evenement` d'EV-16a, poser `taux_base_mode: uniforme` sur EV-01, retirer `reference_externe` d'EV-40a. Dans les quatre cas, « Banque conforme ». Les deux premiers déterminent la grappe des questions à venir, le troisième remplace le taux de base par la loi uniforme, ce qui contourne le gel des taux de base. Correction : les ajouter à `CHAMPS` et à la liste de la section 12.
- **S4. Les tests ne protègent pas la moitié des corrections.** Mutations non détectées : dédoublonnage des agents retiré ; filtre des cycles du registre retiré ; instantanés mensuels retirés ; grappe par acte retirée ; annulation à 60 jours retirée. Le test de bout en bout annonce « cycles d'essai ignorés » et « un avis par agent », mais ses propositions (A, A, B, toutes « non ») donnent le même résultat avec ou sans dédoublonnage. Mutations détectées : filtre de pool, période commune, convention du Brier. Ajouter un cas discriminant par règle.
- **S5. Tri.**
  - `tri.py` range la nature « autre » en « mise en cause », alors que l'annexe réserve le stade aux natures pénales, aux manquements et à la vie privée. La procédure (étape 2 bis) ne fait vérifier que la nature « décision ou déclaration publique ». Un fait « autre » est donc publié sous l'étiquette « mise en cause » et finit « retombé ».
  - Un fait public non vérifié reste « fait public non vérifié » sans date de réexamen ; l'annexe le dit contesté, donc en observation.
  - Si un fait porte à la fois une étape judiciaire et « fait public vérifié », le stade retenu dépend de l'ordre de lecture.
  - Les champs libres `motif` et `fait` sont écrits dans le dépôt public par un agent qui ne lit que des titres. Rien ne l'empêche d'y écrire un nom et une qualification. L'écrire dans la consigne de tri.
  - Le contrôle trimestriel (11.2) porte sur « 30 caractérisations (nature proposée, rattachement) », mais la nature proposée n'est plus conservée nulle part. Archiver les propositions hors dépôt, ou faire porter le contrôle sur le type et le rattachement.
- **S6. Identifiants d'agents.** Le dédoublonnage garde la première proposition de chaque valeur du champ `agent`, tous passages confondus. Essai : « agent-1 » propose « oui » en 2026 ; en 2028, « agent-1 » et « agent-2 » proposent « non » ; la question n'est pas résolue. Fixer une convention (identifiant unique par passage) ou dédoublonner par passage.
- **S7. Hypothèses de la puissance.**
  - Les 15 grappes de P2c sont simulées indépendantes. Or la règle de 8.3 range dans une seule grappe toute question liée à la candidature ou au premier tour. Dans un réseau centré sur la séquence politique, beaucoup de questions conjointes y tomberont. Les 47 à 59 % annoncés sont une borne haute ; le dire.
  - Le décompte de P2b (14 grappes, 12 informatives) suppose que le modèle de la phase 3 prévoit toutes les questions de P2b. Le script ne compare que les questions communes, et un réseau de 10 à 15 nœuds n'en couvre qu'une partie. Écrire quelles questions de la banque le modèle doit prévoir, ou dire que le décompte est une borne haute.
  - Le critère de persistance sur P2a ne porte, pour le modèle, que sur l'écart de taux : quatre grappes trimestrielles au plus au 30 septembre 2027. Avec trois grappes, le test exact ne peut pas rejeter (p minimal 12,5 %). Publier cette puissance.
  - `data/puissance.json` ne se reproduit pas à l'identique depuis le code tagué (0,348 publié, 0,32 obtenu pour P2b, δ = 0,04, ρ = 0,1). Les fourchettes du texte restent justes à deux points près. Régénérer le fichier.
  - La butée du 30 septembre 2028 donne 25 grappes et 26 questions informatives (38 à 54 % pour 0,04). Annoncer un bilan final descriptif à cette date.
- **S8. Asymétrie sur les questions cotées.** Depuis la v1.16, une question de P2b calée en phase 3 reste dans le test sur la marginale non calée du modèle. L'ensemble direct, lui, cherche sur le web et peut lire la cote. EV-40 et EV-41 portent une référence externe et pèsent 8 des 12 questions informatives. Le biais va contre le modèle, donc dans le sens de la règle par défaut. L'écrire comme limite, ou interdire aux prévisionnistes les marchés de prédiction sur ces questions.
- **S9. Double bilan.** Le noyau dit qu'un verdict qui diffère avec et sans ajouts est déclaré non concluant, et que les critères de 8.6 sont jugés sur les deux ensembles. `notation.py` publie les deux tests de valeur ajoutée côte à côte sans verdict combiné, et ne fait pas le double calcul pour la persistance.
- **S10. Cohérence du texte.**
  - 4.5 dit « les questions calées vont dans P1 » ; 8.3 dit qu'une question de P2b calée ensuite reste dans P2b. Préciser 4.5.
  - L'en-tête de 8.6 annonce des critères évalués « sur toutes les grappes résolues de P2b et P2c », mais le critère de persistance porte sur les variables (P2a).
  - 8.5 arrête la moyenne la veille du fait « si celle-ci précède l'échéance » ; le script l'arrête aussi la veille quand le fait tombe le jour de l'échéance. Un jour d'écart, identique pour les deux auteurs.
  - Les références gardent des travaux qui ne sont plus cités (Diebold et Mariano, entre autres). La ligne 4 du noyau contient une phrase bancale (« ; ils sont justifiés dans… »).
- **S11. Robustesse des scripts.**
  - `notation.brier` somme sur les issues présentes dans la prévision : une prévision sans la clé de l'issue réalisée est notée 0,5 au lieu de 1. Sommer sur les issues de la question.
  - `questions.py` lit `correspondances_p1.json` hors du gel ; `geler.py` ne vérifie pas que la date passée est celle du jour.
  - La référence externe d'EV-05 subit le plancher de 2 % sur dix issues (Bardella coté 0,55 %, inscrit à 1,9 %). C'est documenté ; à rappeler dans le bilan de P1.
- **S12. Documents périmés.**
  - `phase1.md` : « environ 57 questions et 35 grappes par cycle » (113 et 47 sur ma simulation de novembre) ; « taux de base des 20 questions résolubles » (45) ; consigne « v1.0 » (v1.3). La case « règle de rattrapage testée » n'est pas cochée, alors que la section 3 conditionne la phase 1 à la liste complète.
  - `phase3.md` : report « aligner la ligne de statut », déjà fait.
  - `README.md` : liste des relectures arrêtée à la v1.10.
  - Docstrings : `notation.py` (« somme sur les issues »), `tri.py` (« caractérisation proposée » dans la reprise), `comparateurs.py` (« taux_base: uniforme », et « seule une référence fiable place la question en P1 », ce que le code ne fait pas).
- **S13. Annulation après un cycle manqué.** Si un cycle est manqué, un passage de tri qui lance `resolution.py` plus de 30 jours après une échéance annule toutes les questions sans avis, alors que personne n'a cherché la source. Limiter l'annulation à 30 jours aux questions pour lesquelles une recherche a été consignée.

## 3. Critère d'arrêt

Cette relecture comporte **un défaut important** (L1) et aucun bloquant. Elle n'est **pas** sans défaut bloquant ni important : le compteur reste à zéro.

- L1 se corrige dans la collecte et dans `resolution.py`, sans décision de méthode et sans toucher au texte.
- Puisque le compteur repart de toute façon, la version suivante peut intégrer les souhaitables de texte (S2, S3, S7, S8, S10) sans coût supplémentaire.
- S1 est à traiter avant le premier cycle, quel que soit son classement.

## Ce qui est solide

- La chaîne complète tourne sur cinq cycles simulés avec le code de la v1.16 : gel, questions, comparateurs, dossier anonymisé, ensemble, résolution, bilan, y compris un ajout à la banque et un modèle démarré en cours de route.
- Le test de la section 8.6 est désormais celui du texte : pools, grappes, période commune, instantanés mensuels, double bilan. Je n'ai trouvé aucun écart sur ce chemin.
- La puissance se reproduit (14 grappes, 12 questions informatives, 17 à 19 % et 26 à 35 %), le test par permutation et le seuil de Student concordent, et le texte annonce lui-même un verdict probablement non concluant.
- Les contrôles tiennent quand on les attaque : fichier de cycle modifié, ligne de registre réécrite ou antidatée, critère ou taux de base changé après gel, fichier gelé altéré, ajouts en excès.
- La caractérisation proposée par le tri ne sort plus de la session, et un fait public vérifié n'est plus traité comme une allégation.
- `evenements.json` et `taux_base.json` se régénèrent à l'identique depuis leurs sources.