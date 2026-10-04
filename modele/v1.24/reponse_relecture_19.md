# Réponse à la relecture de validation 19

Noyau v1.24 ; annexe v1.7 (inchangée) ; banque v1.8 ; consigne v1.5. Registre du protocole vide.

La relecture 19 relève un bloquant (B1) et un important (I1). Le compteur du critère d'arrêt reste à zéro. Les deux sont corrigés.

Avant cette réponse, un agent neuf a conduit un audit interne sur trois propriétés :
- symétrie entre deux auteurs aux prévisions identiques ;
- indépendance vis-à-vis de l'issue de toute sélection, de tout poids et de toute durée ;
- antériorité.

L'audit a fait des essais sur des copies du dépôt et a trouvé deux défauts de même famille que B1 et I1, ainsi que quatre souhaitables. Ils sont traités ici sous le titre « Audit interne ».

## Bloquant

**B1. « Constat » dont l'issue est publique avant le constat officiel.** Corrigé comme proposé.
- **Section 8.8.** Pour un « constat », la date du fait est la plus précoce de deux dates : la publication du constat, et le jour où l'issue est établie publiquement par une source de la section, deux agences concordantes comprises. Pour un résultat électoral, c'est le jour du scrutin. Une question dont l'issue est ainsi établie au gel n'est pas émise.
- **Étape 1 bis** de la procédure du cycle alignée.
- **Test.** `test_symetrie_et_anteriorite` couvre le cas EV-30 : une prévision du 1er décembre, avec une date du fait au 4 novembre, est exclue.

## Important

**I1. Cycle manqué par un seul auteur.** Corrigé comme proposé.
- **Code.** Dans `comparer`, seuls entrent les cycles où les deux auteurs ont une prévision de cycle. Un cycle manqué par l'un est retiré pour les deux, chacun étant alors couvert par sa prévision précédente.
- **Texte.** Section 8.5, qui précise aussi que la prévision de cycle du modèle est calculée sur l'état du réseau au gel.
- **Test.** Deux auteurs identiques, l'un sans le cycle de janvier : l'écart est nul.
- **Contrôle par mutation.** Si l'on prend l'union des cycles au lieu de leur intersection, le test échoue.

## Audit interne

1. **Acte « survenue » annoncé avant sa publication** (EV-42, EV-04, EV-16a, EV-29, EV-32) : même défaut que B1, du côté des « survenue ». C'est un bloquant au sens de la grille.
   - **Section 8.8.** Pour une issue « oui », la date du fait est la plus précoce de deux dates : l'acte, et le jour où il est établi publiquement comme décidé (annonce de l'autorité compétente, ou deux agences concordantes).
   - **Procédures.** L'étape 1 bis et la procédure du tri le reprennent.
2. **Prévisions d'un même cycle émises à des jours différents** : l'auteur qui émet le premier est avantagé, à prévisions identiques. C'est un important au sens de la grille, d'effet faible (2·10⁻⁴ par question pour six jours d'écart), et non prudent, puisque l'ensemble passe après les comparateurs et le modèle.
   - **Correction.** À chaque cycle, les deux prévisions partent du jour le plus tardif des deux émissions.
   - **Test.** Prévisions identiques émises le 1er et le 5 : écart nul. Contrôle par mutation fait.
3. **Fichier manquant au gel.** Un comparateur pouvait alors lire des cotes postérieures au gel. Un fichier manquant fait désormais échouer `geler.py`, et `comparateurs.py` ne lit jamais un fichier courant quand le cycle est gelé.
4. **Grappe recalculée après un ajout.** La grappe d'un événement est figée à sa première émission dans un cycle réel ; un ajout rejoint une grappe existante sans renommer les autres.
5. **Questions perdues quand le fait tombe entre le gel et l'émission.** Non corrigé. La perte est symétrique entre les deux auteurs dans le test, et son effet sur la calibration est faible. Je la mentionne ici.
6. **Échéance le jour du gel** (EV-38 le 1er février). La question n'est plus émise.

## Souhaitables de la relecture 19

- **S1.** Pour chaque événement, la correspondance avec le pool P1 est figée à son premier gel (`controle_banque.py`). Test : `test_correspondances_figees`.
- **S2, S3.** Inscrits à la liste de la phase 3 : périmètre, et grappes des questions conjointes.
- **S4.** Section 8.8 et étape 5 : pour un « survenue », l'absence d'acte sur la source prévue vaut « non ». La recherche vaine est réservée à une source inaccessible.
- **S5.** `dossier.py` mélange l'ordre des questions avec une graine dérivée de l'étiquette du cycle, inscrite dans `anonymisation.json`.
- **S6.** Les commentaires périmés de `notation.py`, `comparateurs.py` et `resolution.py` sont corrigés.
- **S7.** Les recherches vaines se comptent par agent et par passage, comme les avis.
- **S8.** Non retenu. La règle du 1er du mois est déterministe ; l'audit a mesuré son écart à la propreté stricte, inférieur à 4·10⁻⁶.
- **S9.** EV-38 : différé. Une annulation coûte une question sans biaiser le test. Un relevé par la collecte sera étudié avec la v1 de l'outil.
- **S10.** EV-08 : l'élection doit être présentée comme l'objectif de la campagne, et non seulement comme son contexte.
- **S11, S12.** Différés à la procédure d'ajout. Le choix de mettre EV-05 en P1 est maintenu.
- **S13.** Vérifié par l'API GitHub, avec un accès authentifié :
  - « Protection de main » est active (suppression et réécriture interdites) ;
  - « Protection des versions » est active sur `protocole-v*` et `annexe-phase3-v*` (suppression et modification interdites) ;
  - aucun acteur ne peut contourner ces règles.

  Instantané : `modele/controle/regles_github.json`.

## Vérifications

`tests.py` : quatorze tests conformes, dont deux nouveaux (`test_symetrie_et_anteriorite`, `test_correspondances_figees`). `controle_banque.py` : conforme.
