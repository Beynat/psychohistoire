# Relecture de suivi 22 — protocole v1.26, annexe v1.7

Relecteur : Claude (Opus 5.5), même session que la relecture de validation 21. Date : 6 octobre 2026.
Objet : tag `protocole-v1.26` (commit 07be526). Annexe inchangée (`annexe-phase3-v1.7`).
Relecture de suivi : elle vérifie les corrections et ne compte pas pour le critère d'arrêt.

## Verdict

- I1 est corrigé.
- B1 n'est corrigé qu'en partie : le délai de l'erratum est compté depuis l'émission de la ligne, non depuis sa poussée (N1, bloquant).
- I2 est corrigé sur le point relevé, mais le nouveau critère d'EV-35 ouvre une autre lecture : un chiffre partiel de l'année (N2, important).
- D1 est corrigé. Le classement en souhaitable est fondé.
- Deux souhaitables nouveaux (N3, N4).

Les 17 tests passent et `scripts/controle_banque.py` conclut « Banque conforme ».

## Points à vérifier

### 1. B1 (errata de prévision)

Ce qui est conforme :
- Format : `registre.py` exige les trois champs de l'objet et le motif, et n'admet que `{"annulee": true}`.
- Application : `notation.annulations` est appelée avant tout calcul ; les lignes annulées et les errata ignorés sont publiés.
- Textes : sections 0, 8.8 (« Émission et poussée ») et 12, et les deux procédures, sont alignés entre eux.

Le délai pose deux problèmes, décrits en N1 (bloquant) et au point 5.

### 2. I1 (unicité de la prévision de cycle)

Conforme :
- Le tri garde la première ligne de cycle par auteur, question et cycle, sur toutes les lignes, avant les exclusions liées au fait et aux annonces.
- Une ligne annulée bloque la réémission du cycle, et ce cycle est alors retiré pour les deux auteurs.
- Le workflow signale une seconde ligne de cycle parmi les lignes nouvelles. La logique est lue, non exécutée sur GitHub.
- Le texte de la section 8.5 correspond au code.

Je n'y vois pas de défaut introduit.

### 3. I2 (EV-35)

La double lecture « tendances » ou « bilan annuel » est levée, et l'annulation faute de publication est cohérente avec la nouvelle règle générale des constats (section 8.8). Le critère ouvre cependant une autre lecture : voir N2.

### 4. D1 (rattrapage)

Conforme :
- `questions.py` reprend la date de gel du manifeste (essai : « Date de gel du manifeste retenue : 2026-11-01 (et non 2026-11-05) »).
- `comparateurs.py` et `ensemble.py` refusent de rejouer un cycle déjà au registre.
- La section 12 et la procédure décrivent la reprise.
- Il reste à aligner la tâche planifiée (du 1er au 8), ce que la réponse renvoie à l'accord de Nathan.

Classement : souhaitable, d'accord. La perte des questions de P2a touche tous les auteurs de la même façon et ne fait que réduire la puissance. Les doublons des comparateurs étaient identiques, et I1 les écarte désormais. Aucun cycle n'était rendu inexécutable.

Reste un défaut voisin, non corrigé : N3.

### 5. Défauts introduits

- Unicité du cycle : aucune sélection ne dépend de l'issue (la première ligne est retenue quelle que soit la date du fait).
- Ligne annulée comptée comme première du cycle : le retrait du cycle pour les deux auteurs est symétrique. La sélection, elle, n'est neutre que si la décision d'annuler ne dépend pas de l'issue.
- Or, dans le délai de sept jours, rien dans le code ne relie l'erratum à un échec du contrôle d'horodatage :
  - `registre.py` n'exige pas le champ `controle`, que la procédure demande ;
  - la notation ne vérifie aucun lien avec un échec.

Essai sur une copie :
- Q-EV-15 : modèle à 5 % le 1er, ensemble à 40 % le 2, fait « oui » le 4. Sans erratum, l'ensemble gagne (écart −0,26 sur la question).
- Avec un erratum du modèle émis le 5, donc après le fait, la question sort de la comparaison.

En usage conforme (annulation après un échec du contrôle, quelle que soit l'issue), le sens du biais n'est pas déterminé : je le classe en souhaitable. Mais la condition qui rend l'annulation neutre est seulement procédurale. La correction proposée pour N1 la rend vérifiable et règle les deux points.

## Défauts nouveaux

### N1. Bloquant — une ligne poussée plus de sept jours après son émission ne peut plus être annulée

Texte. Section 8.8 : « une ligne poussée hors de la fenêtre de ce contrôle est annulée par un erratum […] que sa question ait été résolue ou non entre-temps ».

Code. `annulations` ignore tout erratum émis plus de sept jours après le champ `emise` de la ligne visée. L'erratum ne peut être écrit qu'une fois l'anomalie détectée, c'est-à-dire à la poussée. Pour une ligne poussée plus de sept jours après son émission, aucun erratum valable n'est donc possible.

Scénario. Une ligne du modèle est écrite le 1er à 95 %. La poussée échoue, ou le commit reste dans un clone local. Le fait survient le 10. La ligne, modifiable localement jusque-là, est poussée le 12. Le workflow la signale, et l'erratum est écrit le 12, comme le prévoit la procédure. Il est ignoré (« émis plus de 7 jours après la ligne ») et la prévision est notée : écart de +0,17 en faveur du modèle sur la question (essai sur une copie).

C'est le scénario de B1, avec un retard plus long. Le motif du délai est juste (empêcher le retrait discrétionnaire d'une prévision perdante), mais son point de départ est faux : il doit courir depuis la détection, pas depuis l'émission.

Correction proposée : rendre l'annulation mécanique.
- Le workflow « Contrôle des registres » inscrit chaque ligne hors fenêtre dans un journal en ajout seul, par exemple `registre/controles.jsonl` : question, auteur, `emise`, numéro d'exécution, date de détection. Il lui faut `contents: write`. Une poussée faite avec `GITHUB_TOKEN` ne redéclenche pas le workflow ; l'ajout seul de ce journal se contrôle dans le workflow lui-même, comme pour `premieres_valeurs.jsonl`.
- `notation.py` annule toutes les lignes inscrites dans ce journal, sans erratum ni délai.
- Un erratum manuel n'est accepté que pour une ligne inscrite au journal. Cela règle aussi le point 5 : plus aucune annulation ne dépend d'une décision prise après l'issue.
- Si l'écriture par le workflow est écartée, solution de repli :
  - exiger `controle` dans `registre.py` ;
  - compter le délai depuis le premier commit de `main` qui contient la ligne (date du commit de fusion sur le dépôt, lue par l'API) ;
  - publier, pour chaque annulation, le numéro d'exécution et l'écart de Brier retiré.
- Test : ligne poussée douze jours après son émission, fait entre les deux ; elle doit être annulée.

### N2. Important — EV-35 : un chiffre partiel de 2026 peut être pris pour « le nombre d'actes recensés en 2026 »

Critère. « Le premier document publié pendant la fenêtre par le ministère de l'Intérieur qui donne le nombre d'actes antimusulmans recensés en 2026 […] fait état de plus de 326 actes. »

La fenêtre s'ouvre le 3 octobre 2026. Le ministère communique couramment des chiffres en cours d'année (par exemple ceux des cinq premiers mois de 2025, en juin 2025, dont je cite la date de mémoire, sans l'avoir vérifiée).

Scénario. En novembre 2026, un communiqué ou une réponse ministérielle donne « 280 actes antimusulmans depuis le 1er janvier ». Deux lectures raisonnables s'opposent :
- c'est le premier document de la fenêtre qui donne un nombre d'actes recensés en 2026 : issue « non », constatée en novembre ;
- le critère vise l'année entière : on attend les tendances de février 2027, qui peuvent dépasser 326, donc « oui ».

L'issue est contestable.

Correction proposée : « le nombre d'actes antimusulmans recensés sur l'ensemble de l'année 2026 ; un chiffre portant sur une partie de l'année ne compte pas ». La banque n'est pas figée.

## Souhaitables

N3. À la reprise d'un cycle, une question résolue après le gel est retirée de la banque. `questions.py` écarte « déjà résolue » toute question présente dans `resolutions_effectives`, sans regarder la date du fait. À une reprise le 5, un événement survenu le 3 fait disparaître la question de fenêtre et la question mensuelle du cycle, pour tous les auteurs. Essai : Q-EV-07 résolue « oui », fait le 3, et la banque passe de 119 à 117 questions.
- Cette sélection ne retire que des « oui ». Elle est symétrique entre auteurs et son sens n'est pas déterminé.
- Elle contredit la section 8.2, qui vise une résolution publique au gel.
- Correction : ne retenir que les résolutions dont la date du fait est antérieure au gel, comme le fait déjà le filtre des annonces (`date_annonce <= gel`).

N4. `annulations` compare des jours entiers (`.days > 7`) : un erratum émis à 7 jours et 23 heures passe. C'est sans effet si N1 est corrigé comme proposé.

## Non vérifié

- Exécution du workflow sur GitHub, notamment le signalement d'une seconde ligne de cycle : logique lue seulement.
- Alignement de la tâche planifiée du cycle (du 1er au 8).
- Les nouveaux tests ont été exécutés, mais je n'ai pas refait les mutations annoncées par la réponse.
- Critères d'EV-08, EV-13, EV-17, EV-38 et EV-44 : lus, sans ambiguïté nouvelle relevée. Le relevé AGSI+ par la collecte n'existe pas encore (inscrit à `controle/phase1.md`).
- Données de collecte et de tri modifiées entre les deux tags (`data/`) : non relues.