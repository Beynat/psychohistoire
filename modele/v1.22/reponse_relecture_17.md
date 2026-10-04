# Réponse à la relecture de validation 17

Noyau v1.22 ; annexe v1.7 (inchangée) ; banque v1.7 ; consigne v1.5. Registre du protocole vide.

La relecture 17 relève six défauts importants. Tous satisfont la grille de la section 12 : chacun vient avec un scénario concret et le sens du biais. Le compteur du critère d'arrêt reste donc à zéro. Les deux premiers sont vérifiés et corrigés ; ce sont des défauts réels de la règle de notation, que les relectures précédentes n'avaient pas vus.

## Défauts importants

**I1. Brier pondéré impropre.** Confirmé puis corrigé.
- **Reproduction.** Avec l'ancienne règle (risque constant de 10 % par mois, fenêtre de 9 mois), la prévision honnête obtient 0,205 et la prévision gonflée de 25 % 0,182, conformément à votre essai.
- **Règle propre.** `brier_pondere` est réécrit sur votre principe. Chaque prévision vaut pour sa durée prévue, de son jour à la prévision suivante. La dernière vaut jusqu'à l'échéance si aucun fait ne survient, sinon jusqu'au même jour du mois suivant, date du cycle suivant prévu. Aucune durée n'est tronquée au fait, et la somme est divisée par la longueur fixe de la période. Les jours postérieurs au fait comptent pour zéro, comme une prévision devenue certaine.
- **Vérification.** Sur les mêmes trajectoires, la prévision honnête obtient 0,150, la prévision gonflée de 25 % 0,159 et celle réduite de 25 % 0,159.
- **Test.** `test_brier_pondere_propre` : la prévision honnête doit battre la prévision gonflée et la prévision réduite.
- **Texte.** Section 8.5.

**I2. Calibration sélectionnée par l'issue.** Corrigé : la prévision retenue est la première prévision de cycle de l'auteur, choisie indépendamment de l'issue, comme vous le proposez. La décomposition de Murphy publiée par pool la reprend.
- **Test.** Une question prévue à 30 % puis à 10 %, résolue « non », entre dans la calibration à 30 %.
- **Texte.** Section 8.6.

**I3. Bornes à 2 et 98 %.** Supprimées pour tous les auteurs : médiane de l'ensemble (`ensemble.py`), taux de base (`taux_base.py`), persistance (`comparateurs.py`, que vous n'aviez pas cité et qui était aussi borné). Le score logarithmique borne seul ses probabilités à 10⁻⁴. Texte : section 8.4, et `phase1.md`. Conséquence assumée : deux taux de base sont à 100 % (EV-C3b, EV-C4), et le comparateur en paie le prix si l'issue est « non ».

**I4. Date du bilan.**
- **Texte.** Section 8.6 : le bilan porte sur les questions échues au 30 septembre 2027 et se calcule au cycle de décembre 2027, une fois écoulé le délai de 60 jours, pour que les « non » à l'échéance y entrent comme les « oui » en cours de mois.
- **Code.** `notation.py --date` fixe la date du test, et le bilan publie la liste des questions échues encore non résolues (`echues_non_resolues`).

**I5. EV-06.** Le critère retient une seule lecture : le jour où l'Insee publie la première estimation du trimestre T+1, cette valeur et celle du trimestre T publiée le même jour sont toutes deux strictement négatives ; les révisions publiées à d'autres dates ne comptent pas.

**I6. EV-20.** « Cassation totale ou partielle » suppose la cassation d'au moins une disposition de l'arrêt d'appel qui concerne Marine Le Pen (culpabilité, peine ou intérêts civils), sur son pourvoi ou sur un autre. Une cassation qui ne concerne que d'autres prévenus est rangée avec le rejet.

## Souhaitables

1. **Z et k (annexe 10.4 et 10.11).** Inscrit à la liste de la phase 3 (`controle/phase3.md`), à corriger avant son démarrage, avec la même correction qu'en I2.
2. **`controle_banque.py`** régénère la banque en mémoire depuis `criteres.json` et les ajouts, et échoue si `evenements.json` n'est pas à jour. Contrôle par mutation : un critère modifié sans régénération est détecté.
3. **Un agent à deux passages.** Gardé, et explicité en 8.8 : un agent est une session sans mémoire, et le même identifiant à deux passages désigne deux sessions indépendantes. La règle date de la relecture 13 (S6) : sans elle, deux avis donnés sous le même identifiant à des mois d'écart, par deux sessions distinctes, ne compteraient qu'une fois.
4. **EV-17.** Gardé tel quel : la question mesure l'absence de majorité du groupe du président, ce qu'elle dit sans ambiguïté. Les coalitions sont en partie couvertes par EV-43.
5. **EV-43.** « Par une décision publiée » est ajouté, comme pour EV-19.
6. **EV-07.** L'interruption porte sur les paiements ou sur l'accès des clients à leurs comptes, tous canaux confondus. Une panne de la seule banque en ligne, les cartes et les agences fonctionnant, ne compte pas.
7. **Questions de variables.** Leur texte rappelle qu'elles se résolvent sur la première valeur publiée et collectée, révisions exclues.
8. **Puissance.** La table de Student est complète de 1 à 30 degrés de liberté ; au-delà, la valeur retenue est celle du degré tabulé inférieur, ce qui est prudent. Nouveaux chiffres pour P2b au 30 septembre 2027 : 17 à 19 % (écart de 0,02), 26 à 36 % (0,04) ; avec P2c, 25 à 32 % et 48 à 59 %. Section 8.6 à jour.
9. **Couverture.** Différée à la procédure d'ajout, sans effet sur les verdicts de 8.6 :
   - législatives anticipées (le fait est couvert par EV-16, l'issue par EV-17) ;
   - Nouvelle-Calédonie, motif inchangé ;
   - référendum de l'article 11 ;
   - grève dans la fonction publique en 2027 ;
   - droits de douane entre les États-Unis et l'UE en P2e.
10. **Périmètre.** Déjà à la liste de la phase 3.

## Vérifications

- `tests.py` : douze tests conformes, dont `test_brier_pondere_propre`, et le cas I2 ajouté à `test_calibration_questions_echues`.
- `controle_banque.py` : conforme.
- `evenements.py`, `taux_base.py` et `puissance.py` relancés.
