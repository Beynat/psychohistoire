**Verdict : six défauts importants, aucun bloquant.** La relecture ne compte donc pas comme relecture propre et le compteur reste à zéro. Les deux défauts de méthode les plus sérieux (I1 et I2) touchent la notation elle-même, dans le texte comme dans le code, et se renforcent l'un l'autre en faveur du modèle.

J'ai relu le tag `protocole-v1.21` ; l'annexe est inchangée depuis `annexe-phase3-v1.7`, et la v1.21 ne change que la grille de classement. `tests.py` (11 tests) et `controle_banque.py` passent. J'ai relancé `puissance.py` sur une copie : les chiffres de la section 8.6 sont reproduits, aux écarts de simulation près. Les essais ci-dessous appellent directement `brier_pondere` et `test_calibration` de `notation.py`.

## Défauts importants

**I1. Le Brier pondéré dans le temps n'est pas une règle propre pour les questions de fenêtre de nature « survenue ».**
- **Défaut.** La moyenne quotidienne s'arrête la veille du fait (section 8.5, `fin_brier`). Le poids relatif de chaque instantané mensuel dépend donc de l'issue.
- **Essai.** Un prévisionniste honnête (risque constant, fenêtre de 9 mois, 10 % par mois) obtient 0,203. Le même prévisionniste qui gonfle ses probabilités de 25 % obtient 0,180. L'optimum se situe vers 1,25 à 1,5 fois la vraie probabilité. L'écart (0,023) dépasse l'écart de 0,02 que le test doit détecter.
- **Scénario et sens.** Le comparateur « taux de base » applique exactement un risque constant. Tout auteur plus haut que lui sur les fenêtres le bat sans aucune information. Le critère « le taux de base bat le modèle » est donc biaisé en faveur du modèle, ce qui masque un échec méthodologique : c'est le sens non prudent. Sur la valeur ajoutée, le biais favorise l'auteur le plus haut, donc le modèle après la recalibration décrite en I2.
- **Correction.** Pondérer chaque instantané de cycle par sa durée prévue (jusqu'au cycle suivant ou à l'échéance), sans la tronquer au fait. Diviser par la longueur fixe de la période commune. J'ai vérifié par simulation que cette variante est propre : la prévision honnête y est optimale. Les questions mensuelles et celles de nature « constat » ne sont pas touchées.

**I2. Le critère de calibration sélectionne la prévision selon l'issue.**
- **Défaut.** « La dernière prévision de cycle avant sa résolution » vaut, pour une fenêtre résolue « oui », la prévision du mois de l'événement. Pour une fenêtre résolue « non », c'est la dernière, devenue faible. Toutes les classes au-dessus de 0,2 ne contiennent alors que des « oui ».
- **Essai.** Sur 30 questions de fenêtre de 12 mois, un prévisionniste parfaitement calibré reçoit le verdict « recalibrer » dans 94 % des cas, contre 10 % attendus.
- **Scénario et sens.** La recalibration logistique, appliquée au seul modèle, relève ses probabilités. Avec I1, ce relèvement est récompensé dans le test de valeur ajoutée comme dans celui du taux de base.
- **Correction.** Retenir pour chaque question une prévision choisie indépendamment de l'issue, par exemple la première prévision de cycle du modèle. Avec cette variante, le taux de verdict « recalibrer » tombe à 9,5 %. À défaut, prendre tous les instantanés en tirant y une seule fois par question dans la loi nulle. Prendre tous les instantanés sans ce correctif donne encore 41 % de verdicts « recalibrer ».

**I3. Bornes à 2 et 98 % appliquées à certains auteurs seulement.**
- **Défaut.** `ensemble.py` borne l'ensemble direct à 2 et 98 % sans base dans le texte, qui prévoit une médiane non extrémisée. Le comparateur « taux de base » est borné de même. Le modèle ne l'est pas.
- **Scénario et sens.** Sur les nombreuses questions mensuelles d'événements rares (vraie probabilité de 0,5 %), l'auteur borné perd environ 0,0002 de Brier par question, toujours dans le même sens. L'effet est faible par question mais systématique, en faveur du modèle, sur la valeur ajoutée comme sur le taux de base.
- **Correction.** Supprimer ces bornes. `log_score` borne déjà à 10⁻⁴, ce qui suffit pour le score logarithmique. À défaut, appliquer la même borne à tous les auteurs.

**I4. Date de calcul du bilan de la section 8.6.**
- **Défaut.** « Évalués au 30 septembre 2027 » ne fixe pas quand le bilan est calculé, et `notation.py` ne prend pas de date en paramètre.
- **Scénario et sens.** Lancé le 30 septembre, le bilan inclut les questions mensuelles de septembre résolues « oui » en cours de mois par le tri. Il exclut celles qui ne seront résolues « non » qu'à l'étape 5 du cycle d'octobre. C'est exactement la sélection que la section 8.5 veut éviter, et elle favorise l'auteur le plus alarmiste. L'effet est faible, car il ne porte que sur un mois de questions.
- **Correction.** Calculer le bilan au cycle de novembre 2027, sur les questions échues au 30 septembre. Ajouter un argument de date à `notation.py`.

**I5. EV-06 (récession technique) : « en première estimation » se lit de deux façons.**
- **Lecture A.** On prend la première estimation de chacun des deux trimestres.
- **Lecture B.** On prend la publication de la première estimation du second trimestre, où le premier apparaît déjà révisé.
- **Scénario.** Le trimestre 1 est publié à −0,1 puis révisé à 0,0 ; le trimestre 2 sort à −0,2. La lecture A donne « oui », la lecture B donne « non ».
- **Correction.** Écrire par exemple : « la première estimation du trimestre T+1 et la valeur du trimestre T publiée le même jour sont toutes deux strictement négatives ». La formulation inverse convient aussi, pourvu qu'une seule lecture reste possible.

**I6. EV-20 (pourvoi de Marine Le Pen) : « une cassation, même obtenue sur un autre pourvoi ».**
- **Défaut.** Il y a treize pourvois : douze condamnés et le Parlement européen, partie civile, mais pas le parquet général.
- **Scénario.** Le pourvoi de Marine Le Pen est rejeté, mais l'arrêt casse partiellement pour un coprévenu. Une lecture range ce cas en « cassation », l'autre en « rejet ».
- **Correction.** Écrire « cassation d'une disposition de l'arrêt qui concerne Marine Le Pen (culpabilité, peine ou intérêts civils) ».

## Souhaitables

1. **Statistique Z et facteur k (annexe 10.4 et 10.11).** Elles mesurent p et d « à la clôture de la question », ce qui produit la même sélection selon l'issue qu'en I2. Le risque est une activation à tort d'une couche qui relève les probabilités. La correction est la même. C'est une procédure de phase 3, d'où le classement.
2. **`controle_banque.py`.** Il compare `evenements.json` au gel, et non `criteres.json` comme le dit la section 12. Une modification de `criteres.json` non régénérée passe le contrôle. Les questions sortent du gel, donc l'intégrité tient, mais il faut régénérer en mémoire et comparer.
3. **Résolution (section 8.8).** Le même agent à deux passages vaut deux avis, ce qui contredit « deux agents résolvent indépendamment ». Mieux vaut exiger deux agents distincts.
4. **EV-17.** « Le groupe du parti du président » ignore les coalitions de groupes. Avec un président RN, une majorité RN plus UDR donne « sans majorité ». Ce n'est pas ambigu, mais probablement pas l'intention.
5. **EV-43.** « Investi ou soutenu » sans exiger de décision publiée, contrairement à EV-19.
6. **EV-07.** « Ayant interrompu […] un établissement bancaire » est vague : une panne de la banque en ligne seule compte-t-elle ?
7. **Questions de variables.** Le texte remis à l'ensemble ne dit pas qu'elles se résolvent sur la première valeur collectée, révisions exclues.
8. **Puissance.** La simulation utilise le seuil de Student, alors que le test réel est une permutation. Le tableau `T10` arrondit aussi 16 degrés de liberté à 19 (1,328 au lieu de 1,337). Sans effet notable.
9. **Couverture.**
   - Aucune question sur l'issue de législatives anticipées, alors que la majorité absolue est une cible (section 5.2) ; seul EV-17 l'approche.
   - Rien sur l'avenir institutionnel de la Nouvelle-Calédonie, seulement les troubles d'ordre public, ni sur un référendum de l'article 11 après 2027.
   - EV-13 (grève dans la fonction publique) s'arrête fin 2026.
   - P2e devient très mince après 2027 : EV-30 se résout en 2026, et rien ne couvre les droits de douane entre les États-Unis et l'UE.
   - Le reste couvre bien la séquence budgétaire, électorale et financière.
10. **Substitution par le taux de base (« Périmètre », section 8.6).** Elle n'est pas encore codée ; c'est déjà inscrit dans la liste de contrôle de la phase 3.

## Faits vérifiés

Les dates de la présidentielle (18 avril et 2 mai 2027) sont confirmées. Pour l'arrêt d'appel du 7 juillet 2026, une source indique que le parquet général ne s'est pas pourvu. Elle annonce aussi un arrêt de la Cour de cassation « début avril 2027 au plus tard », donc peut-être après le 31 mars : l'issue « pas d'arrêt » est réaliste.

## Non vérifié

- La protection effective des tags et de la branche `main`, et l'historique d'exécution des workflows : je n'ai pas d'accès authentifié au dépôt.
- `collecte/` au-delà du Brent et `cotes.py` ; la suite de `tri.py` (reprise et statuts).
- Les fichiers de taux de base, classe par classe.
- Plusieurs faits cités par les critères : 326 actes antimusulmans en 2025, annuité 2028 de la LPM, génération 1970 hors suspension de la réforme des retraites.
- Le test du jugement passé (section 8.7) et les scripts de phase 3, qui n'existent pas encore.
- Les relectures antérieures, que je n'ai pas consultées comme demandé.

Mes scripts d'essai (I1, I2) sont dans un dossier temporaire ; je peux les verser dans `scripts/tests.py` comme tests de non-régression, ou rédiger cette relecture au format des fichiers `modele/v1.*/`.

Sources :
- [Présidentielle 2027 : les dates du premier et du second tour fixées (LCP)](https://lcp.fr/actualites/presidentielle-2027-les-dates-du-premier-et-du-second-tour-fixees-438582)
- [Pourvoi de Marine Le Pen : mémoires et calendrier (Kohen Avocats)](https://kohenavocats.com/marine-le-pen-pourvoi-cassation-memoires-15-octobre-arret-avant-avril-2027)
- [Décision de la cour d'appel de Paris du 7 juillet 2026](https://www.cours-appel.justice.fr/sites/default/files/2026-07/20260707%20-%20CA%20Paris%20-%20CP.pdf)