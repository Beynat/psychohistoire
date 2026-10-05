# Réponse à la relecture de suivi 20

Noyau v1.25 ; annexe v1.7 (inchangée) ; banque v1.8. Registre du protocole vide.

La relecture 20 est une relecture de suivi : elle ne compte pas pour le critère d'arrêt, qui reste à zéro. Elle juge B1, I1 et la plupart des points de l'audit suffisants. Elle relève un défaut important introduit (N1) et un souhaitable (N2). Comme convenu avant chaque relecture de validation, un audit interne, conduit par un agent neuf, a éprouvé les corrections. Il a trouvé un défaut important lié à N1 (D1) et un défaut souhaitable lié à N2 (D2).

## N1 et D1. Annonce d'un acte

N1 est corrigé selon votre proposition.
- **Section 8.8.** Est « décidé » un acte adopté, signé ou notifié par l'autorité compétente, dont seules la publication ou l'entrée en vigueur restent à venir ; une intention ne suffit pas. L'annonce fixe la date du fait d'un « oui », mais ne résout pas la question. La question n'est résolue « oui » que lorsque l'acte remplit le critère dans la fenêtre, et la date de l'annonce ne vaut que si cet acte est celui qui a été annoncé. Une annonce sans acte laisse l'issue « non ».
- **Section 8.2.** Une question dont l'acte a été annoncé comme décidé avant le gel n'est pas émise.
- **Code.** Les annonces sont consignées dans `registre/annonces.jsonl`, en ajout seul et sous contrôle d'horodatage ; `registre.py` refuse un identifiant qui n'est pas un événement de la banque. `questions.py` n'émet pas une question dont l'annonce, datée au plus tard du gel, a été consignée par deux agents ou à deux passages. `resolution.py` ne lit pas ce journal.
- **Procédures.** L'étape 1 bis et la procédure du tri sont alignées.

D1, relevé par l'audit, est corrigé dans le même mouvement. Avec N1 seul, les prévisions émises après une annonce n'étaient exclues que si l'annonce se vérifiait, puisqu'elle fixait alors la date du fait. Elles restaient notées si l'annonce échouait. Le sens du biais est déterminé : le modèle, calculé au gel, était favorisé.
- **Correction.** `notation.py` coupe chaque question au jour de la première annonce consignée pour son événement, quelle que soit l'issue, et même si un seul agent l'a consignée. Section 8.8.
- **Test.** Annonce le 2 novembre, ensemble émis le 4, issue « non » : la prévision de l'ensemble est exclue. Avec le contrôle par mutation (sans la coupure), le test échoue.

## N2 et D2. Grappe d'un ajout

N2 est corrigé selon votre proposition : un ajout prend la grappe figée d'un événement déjà émis.

D2, relevé par l'audit, en précise la règle. L'ajout cherche d'abord parmi les événements dont la fenêtre chevauche directement la sienne, puis seulement dans le reste de sa composante. Sans cela, un ajout emboîté dans EV-15b rejoignait la grappe d'EV-15 dès qu'un ajout antérieur avait relié les deux.

Un ajout qui relie plusieurs grappes figées garde la première, et le fait est consigné parmi les questions écartées, sans écarter la question.

Tests :
- EV-15d, emboîté dans EV-15b, rejoint EV-15b ;
- EV-15e relie EV-15 et EV-15b, et la liaison est consignée ;
- EV-15g, emboîté dans EV-15b seul, rejoint EV-15b.

Contrôle par mutation fait.

## Autres remarques

- **Audit 3.** Les replis de `questions.py` et de `lire_serie` sur les fichiers courants ne sont plus atteignables quand le gel est complet, et le gel échoue désormais s'il est incomplet. Ils restent pour les cycles à blanc.
- **Audit 5.** Accepté : la perte sélectionne bien sur l'issue, dans un sens non déterminé. Les questions concernées figurent déjà dans la liste `exclues` du bilan, avec leur motif.
- **S1.** Deux trous, souhaitables, sont inscrits à la liste de la phase 1 pour le prochain bilan : questions mensuelles d'un événement déjà en P1, et questions de variable.
- **S5.** Retrait de votre point noté ; le mélange de l'ordre est gardé.
- **S13.** L'instantané a été relevé par l'API avec un accès authentifié, depuis la session de rédaction. Il reste une déclaration pour un relecteur sans accès.

## Vérifications

`tests.py` : quinze tests conformes, dont `test_annonces_et_grappes_d_ajout`. `controle_banque.py` : conforme.
