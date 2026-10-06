# Réponse à la relecture de validation 21

Noyau v1.26 ; annexe v1.7 (inchangée) ; banque v1.9. Registre du protocole vide.

La relecture 21 relève un défaut bloquant (B1) et deux importants (I1, I2) : le compteur du critère d'arrêt reste à zéro. Les trois sont corrigés. Un défaut trouvé en interne avant le retour de la relecture, sur le rattrapage d'un passage manqué, est corrigé dans la même version (D1).

## B1. Errata de prévision et règle de poussée

Accepté, avec le classement proposé. Corrections :
- **Format.** Une prévision ne peut être qu'annulée, par `{"erratum": true, "objet": {"question", "auteur", "emise"}, "correction": {"annulee": true}, "motif", "piste"}`. `registre.py` exige les trois champs de l'objet et le motif, et refuse toute autre correction d'une prévision.
- **Notation.** `notation.py` applique les errata avant tout calcul, pour chaque ligne visée, et publie les lignes annulées dans `exclues`.
- **Délai.** Un erratum n'a d'effet que s'il est émis au plus tard sept jours après la ligne visée. Sinon il est ignoré et publié, comme un erratum qui ne vise aucune ligne. Le contrôle à la poussée détecte l'anomalie le jour même. Sans délai, un erratum pourrait retirer, une fois l'issue connue, une prévision qui a mal tourné : la correction de B1 créerait alors un biais du type I1.
- **Pas de réémission.** Une ligne annulée n'est pas réémise : pour l'ensemble de la notation, elle compte comme la première prévision du cycle (voir I1). Le cycle est donc retiré pour les deux auteurs, quelle que soit l'issue.
- **Texte.** La section 8.8 remplace « Résolution antérieure à la poussée » par « Émission et poussée » : la date d'émission fait foi, sous réserve du contrôle à la poussée ; une ligne poussée hors fenêtre est annulée par erratum, que sa question ait été résolue ou non entre-temps. Les sections 0 et 12 et le commentaire du workflow sont alignés.
- **Procédure.** `controle/cycle_mensuel.md` et `controle/tri.md` : tout échec du contrôle d'horodatage donne lieu à un erratum d'annulation des lignes en cause dans les sept jours, avec le numéro d'exécution du workflow.
- **Test.** `test_errata_et_unicite_du_cycle` reprend votre essai : modèle à 95 % sur Q-EV-15, erratum, issue « oui » ; le modèle n'est plus noté. Le même erratum émis dix-neuf jours après la ligne est ignoré et publié. `test_registre` vérifie le format.
- **Mutations.** Le test échoue avec l'ancien `notation.py`, sans l'application de l'erratum et sans le délai. `test_registre` échoue avec l'ancien `registre.py`.

## I1. Une seule prévision de cycle par auteur

Accepté. Corrections :
- **Notation.** `notation.py` ne garde que la première ligne de cycle par auteur, question et cycle. Le tri se fait sur toutes les lignes, avant toute exclusion liée au fait ou à une annonce, et les lignes écartées sont publiées (« seconde prévision du cycle … »).
- **Poussée.** Le workflow « Contrôle des registres » signale toute nouvelle ligne qui serait une seconde prévision d'un même cycle. Essayé sur un dépôt jetable : un doublon du cycle 2026-11 est signalé, une ligne du cycle 2026-12 ne l'est pas.
- **Texte.** La section 8.5 pose la règle et son motif.
- **Test.** Votre scénario sur une question : prévisions identiques à 30 %, puis le modèle ajoute une ligne à 1 % le 28 du même cycle, issue « non ». La ligne est écartée et l'écart est nul. Avec l'ancien code, le modèle gagne (t = 1).
- **Test de bout en bout.** Comme vous l'avez relevé, `test_bout_en_bout` étiquetait « cycle 2026-11 » une prévision du 1er décembre et ne passait qu'à la faveur du défaut. Elle est réétiquetée selon son mois.

## I2. EV-35

Accepté. Le nouveau critère vise le premier document publié dans la fenêtre par le ministère de l'Intérieur qui donne le nombre d'actes antimusulmans de 2026, qu'il s'intitule « tendances » ou « bilan annuel ». Il précise que 326 vient du communiqué « Tendances 2025 » du 12 février 2026. Si aucun nombre n'est publié au 31 mars 2027, la question est annulée et non résolue « non » : elle porte sur une hausse, pas sur la date de publication. Banque v1.9 ; la banque n'est pas encore figée.

## D1. Rattrapage d'un passage manqué (audit interne, avant la relecture)

Le test de rattrapage était une condition du premier cycle (`controle/phase1.md`). Simulation sur une copie : gel le 1er, reprise le 5 à la première étape non faite. Trois défauts :
- **Questions perdues.** La tâche passait la date du jour à `questions.py`. Le contrôle des séries périmées (plus de trois jours avant le gel) se calculait donc sur le jour de la reprise. Mesuré : 119 questions pour un passage le jour du gel, 65 pour une reprise quatre jours plus tard, et tout le pool P2a disparaissait sans erreur.
- **Étapes rejouées.** `comparateurs.py` et `ensemble.py` ajoutaient leurs lignes sans vérifier qu'elles étaient déjà au registre : une reprise doublait les 247 lignes des comparateurs.
- **Cycle manqué jamais déclaré.** La tâche ne se déclenchait que du 1er au 7, alors que la déclaration « cycle manqué » n'a lieu qu'après le 7.

Corrections et classement :
- **Code.** `questions.py` retient la date de gel du manifeste quand le cycle est déjà gelé. `comparateurs.py` et `ensemble.py` refusent de rejouer un cycle déjà présent dans le registre cible. Test : `test_rattrapage`, avec contrôle par mutation sur chacun des trois scripts.
- **Texte.** La règle de rattrapage de la section 12 et `controle/cycle_mensuel.md` décrivent la reprise ; la tâche se déclenche du 1er au 8, et le 8 ne fait que la déclaration.
- **Tâche planifiée.** Elle sera alignée sur le texte, avec l'accord de Nathan.
- **Classement.** Souhaitable selon une lecture stricte de la grille : la perte touche tous les auteurs de la même façon, et les doublons des comparateurs étaient identiques, ce que I1 écarte désormais. Il vous est soumis pour que vous jugiez ce classement.

## Souhaitables

- **S1 et S2.** Acceptés, par la procédure d'ajout :
  - fin des fonctions du Premier ministre par décret, quelle qu'en soit la cause ;
  - référendum ;
  - écart OAT-BTP de signe positif ;
  - clause pour une présidentielle anticipée.

  Ils sont inscrits à `controle/phase1.md`, avec les ajouts différés de la passation.
- **S3.** Accepté. Règle générale en section 8.8 : un constat dont la publication manque à l'échéance vaut « non » si le critère exige une publication dans la fenêtre ; la question est annulée sinon, sauf disposition contraire du critère.
- **S4.** Accepté. Le critère d'EV-38 retient d'abord la valeur relevée par la collecte nocturne (API AGSI+) les 2 et 3 février 2027, la capture archivée ne servant qu'à défaut. Le relevé est à écrire avant cette date (`controle/phase1.md`).
- **S5, S6, S7, S12.** Acceptés. Les critères d'EV-13 (ministère, chiffres de la DGAFP, deux agences à défaut), d'EV-17 (groupe comptant le plus de députés du parti ; « oui » s'il n'y en a aucun), d'EV-44 (solde effectif) et d'EV-08 (un exemple qui compte, un qui ne compte pas) sont précisés.
- **S8.** Accepté en partie. Le bilan publie, pour chaque comparaison, le nombre de cycles retirés faute d'être communs et le nombre de questions sans cycle commun. L'émission de l'ensemble le jour du gel est déjà l'objectif de la procédure ; elle dépend de la durée des prévisionnistes.
- **S9.** Reporté à `controle/phase1.md` : la levée d'une annonce par erratum demande un format et du code. Le comportement actuel est symétrique, comme vous le notez.
- **S10.** Reporté : refuser `--essai` pour une étiquette réelle oblige à réétiqueter les essais de presque tous les tests. L'antériorité reste protégée par l'exclusion au jour du fait.
- **S11.** Inscrit à `controle/phase3.md`.

## Vérifications

- `tests.py` : dix-sept tests conformes, dont `test_errata_et_unicite_du_cycle` et `test_rattrapage`.
- `controle_banque.py` : conforme.
- Contrôle du workflow sur un dépôt jetable : conforme.
