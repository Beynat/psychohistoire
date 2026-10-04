# Relecture 12 — noyau v1.15, annexe v1.4, banque v1.2

Session neuve, sans accès aux échanges de rédaction. Dépôt lu au commit `41d0478` (tags `protocole-v1.15` et `annexe-phase3-v1.4`).

**Verdict.** Les corrections de la relecture 11 sont faites dans les scripts, mais la plus importante (J1) n'est pas écrite dans le noyau, contrairement à ce que dit la réponse. Un regard neuf fait apparaître cinq autres défauts importants : le script de notation ne calcule pas le test de la section 8.6 tel qu'il est écrit, et le test lui-même garde deux biais de construction. Aucun défaut bloquant, six importants : le critère d'arrêt n'est pas atteint.

**Ce que j'ai fait.** Lecture intégrale des pièces listées. Exécution de `tests.py` (cinq tests conformes) et de `controle_banque.py`. Simulation de cinq cycles réels (novembre 2026 à mars 2027) sur une copie, avec gels, comparateurs, propositions, résolutions et bilan. Reproduction de la puissance (19 grappes, 90 questions, 12 informatives ; 20 à 24 % pour 0,02). Essais ciblés sur les ajouts, le tri et la résolution.

**Limites.** Je suis de la même famille de modèles que les auteurs. Je ne peux pas confirmer les faits postérieurs à mi-2026 (classes de référence, arrêt du 7 juillet 2026, chiffre de 326 actes). Les workflows sont lus, pas exécutés ; les règles de protection de GitHub ne sont pas vérifiables depuis le dépôt.

## 1. Suivi de la relecture 11

| Point | Avis | Motif |
| --- | --- | --- |
| J1, période commune | Insuffisante | Le script est correct : sur ma simulation, la phase 3 démarrée en janvier est comparée à l'ensemble sur la période commune. Mais la section 8.5 n'a pas changé entre les tags v1.14 et v1.15 : la règle n'y figure pas, alors que la réponse dit « règle écrite en 8.5 ». Voir K1. |
| J2, stade vérifié | Suffisante sur les quatre points demandés | Stade « allégation » par défaut, vérification par deux agents, listes alignées, contrôle trimestriel étendu. La correction a un effet de bord sur les faits non judiciaires (K5) et un écart mineur dans le script (S8). |
| S1, gel et statut | Suffisante | Dates relatives à P, règle du compteur écrite, contrôle du statut vérifié (un gel réel avec statut non définitif fait échouer le contrôle). Restent des dates périmées dans les listes de contrôle (S14). |
| S2, reprise | Suffisante | `faits_suivis` transmis, fenêtres de sept jours, seuil unique, description corrigée. |
| S3, règle d'abandon | Suffisante pour le texte, insuffisante pour le script | La table est claire. `tri.py reprise` recalcule le statut chaque jour sans mémoire : un fait passe de « retombé » à « prolongé » puis de nouveau à « retombé » (S8). |
| S4, actes de l'autorité | Suffisante en partie | Saisines et signalements par un tiers sont exclus. La création d'une commission d'enquête reste une étape, alors que la relecture 11 la citait comme acte déclenchable par un adversaire (droit de tirage). |
| S5, gels immuables | Suffisante | Lu dans le workflow : tout fichier sous `gel/` modifié ou supprimé fait échouer le contrôle. Non exécuté. |
| S6, étape 1 bis | Suffisante | |
| S7, noyau 8.9 | Suffisante | |
| S8, verdict non concluant | Suffisante | Écart moyen, intervalle et puissance recalculée sont dans le bilan. Réserve d'échelle (S1 ci-dessous). |
| S9, affichage public | Insuffisante | La règle porte sur le volet actualité, mais la caractérisation est écrite dans des fichiers publics du dépôt. Voir K6. |

## 2. Relecture d'ensemble

### Bloquants

Aucun.

### Importants

**K1. La période commune du Brier pondéré n'est pas dans le noyau.**

- **Constat.** `git diff protocole-v1.14 protocole-v1.15 -- modele/protocole.md` ne touche pas la section 8.5. Elle définit toujours le score « du jour d'émission t₀ au jour de clôture T », par auteur.
- **Problème.** Le texte gelé décrit la statistique que la relecture 11 a jugée biaisée. La correction ne vit que dans `notation.py`, qui n'est pas gelé : un changement de script la retirerait sans enfreindre le protocole. Le test `test_brier_periode_commune` ne couvre que la fonction, pas le chemin de `bilan`.
- **Correction proposée.** Ajouter en 8.5 : « Pour une comparaison entre deux auteurs, la moyenne court du plus tardif de leurs deux premiers jours de prévision à la veille du fait ou à l'échéance. » Ajouter un test de bout en bout sur un registre fictif.

**K2. `notation.py` ne calcule pas le test de la section 8.6.**

- **Constat**, sur ma simulation de cinq cycles :
  - **Cycles d'essai lus comme des cycles réels.** `toutes_les_questions()` parcourt `data/cycles/*/questions.json` et garde la première définition de chaque identifiant. Les dossiers d'essai `2026-10` et `2026-10-planifie` passent avant `2026-11`. Résultat : 18 questions de fenêtre reçoivent la grappe de l'essai. Pour les sept événements à questions mensuelles déjà présents à l'essai (EV-01, 04, 07, 08, 16a, C1, C2), la fenêtre et les mensuelles sont séparées : `Q-EV-08` porte `EV-08-2028-T3`, ses mensuelles `EV-08`. `Q-EV-05` est en P2b avec les cinq issues par bloc de l'ancienne banque, au lieu de P1 et dix issues.
  - **Pas de filtre de pool.** La comparaison porte sur toutes les questions communes. Le verdict « modèle contre ensemble direct » de ma simulation compte 14 grappes dont celles de P2e, que la section 8.3 exclut. P2a et P1 y entreraient aussi.
  - **Pas de double bilan.** Le jugement « avec et sans les questions ajoutées » (section 8.8) n'est pas calculé.
- **Problème.** La question de fenêtre et ses mensuelles sont séparées en deux grappes, ce que la section 8.3 interdit : des questions corrélées comptent comme indépendantes. Le verdict affiché n'est pas celui du protocole. Aucun test ne l'aurait détecté.
- **Correction proposée.** Ne lire que les cycles réels (même règle que `controle_banque.py`), ou prendre pool et grappe dans `evenements.json` gelé. Calculer le test par pool (P2b et P2c pour la valeur ajoutée ; P2a contre la persistance ; P2b contre le taux de base), avec et sans ajouts. Ajouter le test de bout en bout de K1.

**K3. Le modèle est mis à jour en continu, l'ensemble direct une fois par mois.**

- **Constat.** En phase 3, le modèle reçoit de nouvelles lignes de registre entre deux cycles : données en cours de cycle (8.9), faits imprévus sous 72 heures (11.1, 11.6), jalons chaque semaine s'ils sont actifs (10.8). L'ensemble direct n'est interrogé qu'au cycle mensuel. Le score testé est une moyenne journalière.
- **Problème.** C'est le même type d'artefact que J1. À jugement égal, le prévisionniste rafraîchi le plus souvent gagne sur un Brier pondéré dans le temps. Le verdict « la phase 3 fait mieux » peut donc venir de la cadence, pas de la structure, alors que la section 8.3 dit que P2b juge « structure et jugement » et que ce verdict ouvre la phase 4 (extension du réseau). Le modèle témoin, qui isolerait la structure, n'entre dans aucun critère de 8.6.
- **Correction proposée.** Au choix, à écrire en 8.6 :
  - juger le test sur les seules prévisions de cycle du modèle (lignes d'origine « cycle mensuel », figées entre deux cycles), et publier la version continue à titre descriptif ;
  - ou assumer que le test compare deux systèmes, cadence comprise, et ajouter la comparaison au témoin pour dire ce qui revient à la structure.

**K4. Les grappes informatives du test ne sont pas indépendantes.**

- **Constat.** Sur les 12 questions informatives de P2b, 10 se résolvent au premier tour du 18 avril 2027 ou sur la liste des candidats : EV-19, EV-20, EV-21, EV-23, EV-40 (cinq questions), EV-41. Elles forment six grappes. Trois dépendent directement de la candidature de Marine Le Pen (EV-20, EV-21, EV-40a).
- **Problème.** Le test par permutation de signes suppose des grappes indépendantes. Un prévisionniste qui se trompe sur cette candidature perd sur plusieurs grappes à la fois. J'ai ajouté à votre simulation un choc commun aux six grappes : la fausse alarme unilatérale passe de 9 % à 13 %, 16 % et 18 % pour une corrélation de 0,2, 0,4 et 0,6. Le risque global annoncé de 20 % serait donc de 26 à 36 %. L'hypothèse de corrélation est la mienne ; l'ordre de grandeur suffit. Avec une puissance de 20 à 25 %, un verdict « fait mieux » serait presque aussi souvent faux que vrai.
- **Correction proposée.** Fusionner ces six grappes en une grappe « premier tour 2027 » (la fausse alarme revient à 9 %, la puissance pour 0,04 tombe à 20-30 %), ou garder les grappes et écrire en 8.6 le risque réel simulé avec dépendance. Dans les deux cas, dire qu'un verdict significatif reste une preuve faible.

**K5. Annexe : le stade par défaut bloque les faits non judiciaires.**

- **Constat.** La section 11.2 caractérise « chaque fait rattaché à un nœud ou à une question ». Le stade retenu est « allégation » par défaut ; un fait à ce stade est « contesté » et va en observation (cas f). Un stade supérieur exige une étape officielle, et la liste des étapes ne couvre que les affaires : actes judiciaires, autorités de contrôle, commission d'enquête, décision de l'intéressé sur sa propre situation.
- **Problème.** Un fait public établi qui n'est pas une affaire (annonce d'un recours au 49.3, accord entre deux partis, appel à la grève, déclaration de candidature) n'a aucune étape possible. Lu à la lettre, il reste « allégation », attend 30 jours et finit « retombé ». La couche des faits imprévus (cas c) serait réduite aux affaires judiciaires, à l'opposé de l'objet de la section 11. C'est un effet de bord de la correction de J2. L'annexe sera gelée avant la phase 3, sans ajout possible.
- **Correction proposée.** Limiter l'axe « stade » aux natures pénale, éthique et vie privée. Pour « décision ou déclaration publique » et « autre », écrire que le fait est établi quand deux agents l'ont vérifié sur une source de la section 8.8, et contesté sinon.

**K6. La caractérisation produite par le modèle léger est publiée dans le dépôt.**

- **Constat.** La section 11.6 interdit d'afficher une qualification pénale produite par un agent, et la nature « vie privée ». Or `tri.py ajouter` écrit `caracterisation` (nature, stade proposé) dans `data/tri/AAAA-MM.jsonl`, et `tri.py reprise` la recopie dans `data/reprise.json` (`caracterisation_proposee`), avec l'identifiant du fait et le lien du titre. Le dépôt est public et servi par GitHub Pages : ces fichiers ont une adresse publique. `modele/interface/actualite.md` demande encore d'afficher « nature, stade, appui ». La tâche de tri est planifiée trois fois par semaine et n'est pas conditionnée au statut du protocole.
- **Problème.** La règle acceptée en 11.6 est contournée par les données. Une qualification pénale non vérifiée, tirée d'un titre, visant une personne nommée, sera publiée dès le premier fait caractérisé par le tri. Je ne suis pas juriste, mais c'est le risque que la relecture 11 signalait (présomption d'innocence, vie privée), et il pèse sur vous personnellement. Ce défaut ne touche pas la validité des prévisions ; je le classe important pour cette raison.
- **Correction proposée.** Ne pas écrire la nature ni le stade proposé dans le dépôt public : les garder hors dépôt (ou dans un dépôt privé), et ne publier que le stade retenu et l'étape vérifiée avec sa source. Aligner `actualite.md` sur 11.6.

### Souhaitables

- **S1. Échelle du Brier.** `notation.brier` somme sur les issues : pour une question binaire, il vaut 2(p − y)², le double de la formule de 8.5. Le verdict n'en dépend pas, mais l'écart moyen publié se lit à côté d'une puissance exprimée « pour un écart de 0,02 ». Fixer une seule convention.
- **S2. Trois tests pour un seul.** Le noyau annonce Diebold-Mariano, ou une permutation sous 40 grappes ; `notation.py` permute toujours ; `puissance.py` utilise un seuil de Student. Écrire en 8.5 le test réellement utilisé.
- **S3. Ce qui n'est pas figé.**
  - `data/cycles/<cycle>/questions.json` n'est ni dans le manifeste ni sous contrôle. J'ai modifié les seuils des variables et les grappes d'un cycle émis : « Banque conforme ». Or le seuil d'une question de variable n'existe que là.
  - Le pool effectif vient de `correspondances_p1.json`, modifiable d'un cycle à l'autre, alors que le pool de la banque est figé. La section 4.5 dit que les questions calées « vont dans P1 » : dire si une question de P2b calée en phase 3 quitte le test, et comment. EV-40 et EV-41 portent une référence externe et pèsent 6 des 12 questions informatives.
  - Les taux de base peuvent changer entre deux cycles ; ils servent au critère de persistance.
- **S4. Ajouts à la banque.** Essai avec un ajout : `questions.py` émet la question, puis `comparateurs.py` échoue (`KeyError`) car le taux de base n'est pas dans le fichier gelé. Le gel étant fait, la correction est impossible sans enfreindre le contrôle. La procédure (étape 0) ne dit pas de relancer `taux_base.py`. Le champ `taux_base` de l'ajout entre en collision avec le drapeau `taux_base: uniforme`.
- **S5. `resolution.py`.**
  - Deux propositions du même agent résolvent la question (« deux agents concordants ») : exiger deux valeurs distinctes du champ `agent`.
  - Avec un seul avis, ou deux avis divergents sans troisième, la question n'est ni résolue ni annulée, même 60 jours après l'échéance.
  - Une ligne d'erratum dans `resolutions.jsonl` fait échouer le script (`KeyError`), et `notation.py` l'ignore. Le noyau dit qu'une erreur se corrige par erratum, mais rien ne permet de corriger une résolution fausse dans la notation.
- **S6. Révisions des séries.** Une question de variable est résolue sur la valeur présente dans la série au premier passage du script. Le chômage et l'IPCH sont révisés, et les seuils sont arrondis à 0,1 : une révision d'un dixième inverse l'issue. Écrire quelle publication fait foi (la première collectée) et conserver sa date.
- **S7. Identifiants transmis aux prévisionnistes.** `dossier.py` transmet l'identifiant, qui contient le quantile (`…-q20`, `-q50`, `-q80`). L'ensemble direct peut en déduire la probabilité du comparateur de persistance, alors que la section 8.8 exclut de transmettre un taux de base. Anonymiser les identifiants remis.
- **S8. `tri.py`.**
  - Le statut d'un fait est recalculé chaque jour. Essai : « retombé » le 3 février, « prolongé » le 11 après deux titres, « retombé » le 20. La table de 11.3 décide une fois, à la date de réexamen. Inscrire la décision en ajout seul.
  - Le stade est relevé si deux agents vérifient deux étapes différentes du même stade (une perquisition pour l'un, une commission d'enquête pour l'autre). L'annexe exige la même étape.
  - Un fait « retombé » sort de `faits_suivis` : un nouveau titre recrée un fait et rouvre 30 jours, ce qui contourne la prolongation unique.
  - « Appel » figure parmi les étapes judiciaires de l'annexe mais c'est un acte d'une partie, absent du script.
- **S9. Banque.**
  - EV-09a et b sont classés « constat », alors qu'une vigilance rouge peut survenir à tout moment de l'été : le taux de base reste à 50 % jusqu'au 15 septembre. « Survenue » donnerait la décroissance voulue.
  - EV-06 : la première estimation du deuxième trimestre 2028 paraît vers le 30 juillet, pour une fenêtre close le 31. Reculer la fin de fenêtre de deux semaines.
  - Plusieurs critères s'appuient sur « deux agences concordantes », que les agents ne lisent qu'à travers des reprises. Dire si une dépêche reprise par un média de référence compte.
- **S10. Puissance.**
  - Les 15 grappes de P2c sont simulées à l'échelle 1, soit une probabilité de 50 %. Une conjonction « A et B » est plus rare : à 10 %, la puissance pour 0,04 tombe de 74-84 % à 55-65 %.
  - La butée du 30 septembre 2027 est fixe, mais P glisse avec les relectures. Phase 3 au 1er avril 2027 : 10 questions informatives, 19 % et 33 %. Au 1er mai : une seule, 14 % et 19 %, soit le niveau du seuil. Écrire qu'au-delà d'une date de démarrage, le test est déclaré non concluant d'avance.
- **S11. Correction du biais commun (8.4, point 3).** Le test de signe n'a ni unité ni polarité définies. Dans P1, les dix issues d'EV-05 viennent d'un même marché et leurs écarts se compensent par construction. Le signe sur « oui » dépend de la formulation de la question. Définir l'unité (une issue par marché indépendant) et un effectif minimal, ou retirer la correction.
- **S12. Annexe 10.1.** La loi a priori de M et les valeurs de δ_faible et δ_forte ne sont fixées nulle part (seul l'exemple de la v1.4 en donne). Ajouter M à un nœud B dont la table contient déjà l'effet de A déplace P(B | A), sauf à recentrer : écrire la contrainte.
- **S13. Critères de 8.6.**
  - La calibration est comparée à une simulation « au même nombre de questions », donc à questions indépendantes : simuler par grappes.
  - « Échec méthodologique » n'a pas de conséquence écrite.
  - La statistique Z de 10.11 n'est centrée que si la probabilité sans la couche est calibrée ; sinon elle valide une couche qui corrige un biais uniforme. À mentionner.
- **S14. Version définitive et textes périmés.**
  - Dire quel texte devient définitif : celui lu par la seconde relecture propre, sans modification ultérieure. Sinon la correction de ses souhaitables gèle un texte non relu.
  - La ligne 3 du noyau dit « pas encore définitif » : elle sera fausse dans la version définitive, et la corriger crée une version. La remplacer par un renvoi à `statut.json`.
  - Périmés : en-tête de l'annexe (« soumise à relecture avec le noyau v1.13 »), motif de `statut.json` (relecture 10), `phase1.md` (dates fixes, « 21 événements », « 61 à 79 % à 40 grappes », règle de rattrapage non testée), `phase3.md` (1er janvier 2027), `README.md` (« l'historique Git de `data.json` fait foi », contraire à la section 0).
- **S15. Tests.** `tests.py` ne couvre ni `resolution.py`, ni `comparateurs.py`, ni `questions.py`, ni `tri.py`, ni `controle_banque.py`. Un test de bout en bout sur un cycle fictif aurait trouvé K2, S4 et S5.

## 3. Critère d'arrêt

Cette relecture comporte **six défauts importants** (K1 à K6) et aucun bloquant. Elle n'est **pas** sans défaut bloquant ni important : le compteur reste à zéro.

- K1, K2 et K6 se corrigent sans décision de fond.
- K3 et K4 demandent une décision de méthode sur le test de la section 8.6.
- K5 demande une phrase dans l'annexe.

Un premier cycle au 1er novembre 2026 n'est plus possible avec deux relectures propres à obtenir. Chaque mois de décalage retire de la substance au test (S10).

## Ce qui est solide

- La chaîne gel, questions, comparateurs, résolution et bilan tourne de bout en bout sur cinq cycles simulés, et le contrôle du statut bloque bien un gel prématuré.
- La puissance est publiée à l'avance, se reproduit, et le texte annonce lui-même un verdict probablement non concluant.
- La distinction entre allégation et étape officielle vérifiée est nette pour les affaires, et la reprise n'entre dans aucune probabilité.
- Seul le critère est transmis aux prévisionnistes, à l'exception du quantile dans l'identifiant (S7).