Je mets à jour le dépôt au tag `protocole-v1.12` et je lis les pièces avant de répondre.

# Relecture 10 — noyau v1.12, banque v1.1

**Verdict.** Les corrections de critères, de nature des événements et de taux de base sont faites, et je les ai vérifiées au tag `protocole-v1.12` (tests conformes, banque à blanc de 112 questions et 51 grappes). La définition de la grappe résolue, demandée en relecture 9, introduit en revanche un biais dans le test central, et la puissance publiée est surestimée d'un facteur deux environ. Aucun défaut bloquant, trois importants : le critère d'arrêt n'est pas atteint.

Limites habituelles : je suis de la même famille de modèles que les auteurs, et je ne peux pas confirmer les faits postérieurs à mi-2026 (classes de référence d'EV-32 et d'EV-45 notamment).

## 1. Suivi de la relecture 9

| Point | Avis | Motif |
| --- | --- | --- |
| H1, nature des événements | Suffisante | Le champ `nature` est présent sur les 49 événements, et `comparateurs.py` ne convertit plus les constats. Un seul classement est contestable (EV-09, voir S1). |
| H2, grappes et puissance | Insuffisante | Le seuil de 40 est retiré, la grappe résolue est définie et le calendrier est réécrit. Mais la définition crée une sélection par l'issue (I1) et la simulation surestime la puissance (I2). |
| H3, banque figée | Insuffisante | Le contrôle détecte bien un critère modifié (testé). Il laisse passer le retrait par le champ d'accessibilité, et ne compare qu'au dernier gel (I3). |
| H4, critères ambigus | Suffisante | EV-C2, EV-28, EV-42, EV-39 et EV-45 sont résolubles. Deux formulations restent à resserrer (S2). |
| Autres critères (EV-36, 43, 40, 08, 13, 23, 17, 20) | Suffisante | Chaque cas limite signalé a désormais une règle. |
| Issues possiblement acquises | Suffisante | EV-32 est réécrit ; les autres passent par l'étape 1 bis. |
| Taux de base EV-45 et EV-32 | Suffisante | Les classes sont explicites et le cas de 1982 est signalé comme discutable. |
| EV-41 et EV-20 | Suffisante | Le biais est connu et écrit. C'est acceptable pour une ligne de base naïve, à rappeler au bilan. |
| Entrées périmées | Suffisante | Le contrôle de cohérence des issues a trouvé un écart réel (EV-20). |
| Date du fait pour « non » | Mal fondée en partie, par ma faute | Ma recommandation était trop générale : elle ne vaut que pour les événements « survenue » (I1, point c). |
| Brier pondéré, section 12, sources | Suffisante | Conforme au code et au texte. |

## 2. Nouveaux défauts

### Bloquants

Aucun.

### Importants

**I1. Le test de la section 8.6 ne note les questions de fenêtre que lorsque l'événement se produit.**

Constat :
- **a. Sélection à la butée.** Au 30 septembre 2027, une question de fenêtre qui se clôt en 2028 (EV-01, 04, 07, 08, C1, C2, 39, 29, 06, 16b, C3b, 09) n'est résolue que si l'événement s'est produit. Elle n'entre donc dans le test que sur l'issue « oui ».
- **b. Dernière prévision.** `notation.py` teste le Brier de la dernière prévision. Pour un « non », c'est celle du dernier cycle, quasi certaine pour tout le monde. Pour un « oui », c'est celle d'avant le fait.
- **c. Date du fait d'un constat.** `resolution.py` fixe la date du fait d'un « non » à la fin de la fenêtre, quelle que soit la nature. Pour un constat négatif publié avant l'échéance (EV-21 sur la liste de mars, EV-35, EV-03), les prévisions émises après la publication sont gardées et notées. Pour un « oui », elles sont exclues.

Problème : dans les trois cas, une probabilité trop haute n'est jamais pénalisée, et une probabilité haute est récompensée quand l'événement arrive. Le test favorise le comparateur le plus alarmiste, sans rapport avec sa qualité.

J'ai simulé 8 grappes à fenêtre longue, avec un prévisionniste A qui donne les probabilités vraies et un B qui les double. B est déclaré meilleur au seuil de 10 % dans 3 %, 10 % et 34 % des cas pour un risque mensuel de 2 %, 3 % et 5 %. A n'est jamais déclaré meilleur. Le point b existait avant la v1.12 et je ne l'avais pas relevé.

Correction proposée :
- À la date du test, n'inclure une question de fenêtre que si son échéance est passée, quelle que soit son issue. Les grappes à fenêtre longue comptent alors par leurs seules questions mensuelles.
- Écrire en 8.5 quel score entre dans le test. Pour les questions de fenêtre, prendre le Brier pondéré dans le temps, déjà calculé, plutôt que la dernière prévision.
- Limiter la règle « date du fait d'un non = fin de fenêtre » aux événements « survenue ». Pour un constat, retenir la date de publication, quelle que soit l'issue, et étendre l'étape 1 bis aux constats négatifs.

**I2. La puissance publiée en 8.6 est surestimée.**

Constat : `puissance.py` donne le même écart (0,02) et la même dispersion (0,12) aux 97 questions. Or 72 d'entre elles sont les questions mensuelles de 8 grappes d'événements rares (9 chacune : EV-01, 04, 07, 08, C1, C2, 39, 29). Deux prévisionnistes à 2 % et 4 % sur un mois diffèrent de 0,002 en Brier, pas de 0,02. Le script compte aussi des mensuelles que `questions.py` n'émet pas : 5 au lieu de 1 pour EV-16a, 4 au lieu de 0 pour EV-42.

Problème : l'information utile vient d'une dizaine de grappes (sept questions isolées, EV-40, EV-16a, EV-42). J'ai refait la simulation avec la même fonction, sur ces 10 grappes et sans P2c :

| Écart de Brier | Publié (18 grappes) | Recalculé (10 grappes) |
| --- | --- | --- |
| 0,02 | 35 à 47 % | 19 à 21 % |
| 0,04 | 70 à 88 % | 36 à 41 % |

Le paragraphe « Calendrier attendu » annonce donc environ le double de la puissance réelle. Un retour à la phase 2 serait lu comme un résultat, alors que le test ne peut presque rien détecter.

Correction proposée :
- Simuler les questions mensuelles avec un écart et une dispersion proportionnés à leur probabilité, ou les exclure du calcul, et aligner le compte sur `questions.py`.
- Réécrire les chiffres du noyau.
- Dire en 8.6 qu'un échec à battre l'ensemble direct à cette puissance est « non concluant », pas « sans valeur ajoutée ». À défaut, assumer explicitement la règle de décision par défaut.

**I3. Le contrôle de la banque laisse passer un retrait et s'efface au gel suivant.**

Constat, sur une copie avec un gel simulé de novembre :
- Passer `source_accessible` à faux sur EV-01 n'est pas détecté. C'est pourtant la façon dont EV-10 a été retiré, et `questions.py` écarte alors l'événement.
- `mensuelle` et `source_resolution` ne sont pas contrôlés non plus.
- Le critère d'EV-39 modifié (500 000 remplacé par 300 000) est bien détecté. Mais après le gel de décembre, le contrôle répond « Banque conforme » : il ne compare qu'au dernier gel, qui contient la modification.

Problème : le noyau interdit tout retrait et toute modification d'une question émise. Le contrôle ne garantit ni l'un ni l'autre dans la durée.

Correction proposée : ajouter `source_accessible`, `mensuelle` et `source_resolution` aux champs figés, et comparer chaque événement au premier gel où il apparaît.

### Souhaitables

- **S1. EV-09 classé « constat ».** Il couvre deux étés. Après un été 2027 sans vigilance rouge, le taux de base reste à 75 % au lieu d'environ 50 %. Le scinder en deux événements (été 2027, été 2028), comme EV-16.
- **S2. Deux formulations.**
  - EV-C2 : « département, région ou collectivité d'outre-mer » peut se lire comme incluant un département métropolitain. Écrire « situé outre-mer ».
  - EV-32 : le critère exige que le ministère « annonce » l'entrée en application. Une suspension qui expire le 10 novembre 2026 sans annonce reste indécise. Écrire « entrent en application pendant la fenêtre ». La réponse dit « visant l'UE » alors que le critère dit « s'appliquent aux exportations vers l'UE » ; le second est le bon.
- **S3. Questions à plusieurs issues dont l'une dépend du temps.** EV-20 (« pas d'arrêt ») et EV-C4 (« pas d'avis ») gardent une répartition fixe. La limite est connue ; l'écrire en 8.4.
- **S4. EV-C3a et EV-C3b.** Leurs fenêtres sont emboîtées, pas disjointes : elles forment deux grappes dépendantes. L'effet est faible, car C3a se clôt avant la phase 3.
- **S5. Gel non vérifié.** `comparateurs.py` lit `modele/taux_base.json` courant, pas la copie gelée. Les empreintes du manifeste ne sont vérifiées par aucun contrôle.
- **S6. Réponse à votre question sur le poids des grappes.** Une grappe à une seule question mensuelle ne pèse pas comme une grappe complète. La statistique somme les écarts, et une grappe à écart quasi nul est neutre dans la permutation des signes. Le test reste valide sous l'hypothèse nulle. Le défaut est celui d'I2 : ces grappes sont comptées dans la puissance sans rien apporter.

## 3. Critère d'arrêt

Cette relecture comporte trois défauts importants et aucun bloquant. Le compteur reste à zéro.

I2 et I3 se corrigent par le script et le texte. I1 demande une décision de méthode sur la composition du test et le score testé, à prendre avant le 1er novembre, puisque `resolution.py` et l'étape 1 bis s'appliquent dès le premier cycle.

## Ce qui est solide

- La distinction entre survenue et constat est appliquée de bout en bout, de la banque au comparateur.
- Le contrôle de cohérence entre taux de base et banque a trouvé seul une erreur réelle.
- Le paragraphe « Calendrier attendu » annonce à l'avance un verdict probablement négatif par défaut. Les chiffres sont à corriger, mais la démarche est la bonne.