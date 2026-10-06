# Réponse à la relecture de suivi 22

Noyau v1.27 ; annexe v1.7 (inchangée) ; banque v1.10. Registre du protocole vide.

La relecture 22 est une relecture de suivi : elle ne compte pas pour le critère d'arrêt, qui reste à zéro. Elle juge I1 et D1 corrigés, et le classement de D1 fondé. Elle relève un défaut bloquant (N1), un important (N2) et deux souhaitables (N3, N4).

La correction de N1 rend l'annulation mécanique. Trois audits internes successifs, chacun conduit par un agent neuf, l'ont éprouvée ; chacun a trouvé des défauts dans la correction précédente, tous corrigés ci-dessous. Nathan a fixé le modèle de menace à cette occasion (section 12, « Limites du contrôle »).

## N1. Annulation d'une ligne poussée en retard

Accepté, avec votre correction principale : l'annulation est mécanique.

**Journal des contrôles.**
- Le contrôle à la poussée inscrit chaque ligne de registre poussée hors de sa fenêtre dans un journal en ajout seul.
- La ligne est désignée par l'empreinte SHA-256 de sa ligne brute, et non par (question, auteur, emise) : une copie forgée ne peut pas annuler une ligne régulière.
- Le journal vit sur une branche à part, `controles`, que seul le workflow écrit.
- Toute lecture des registres écarte une ligne inscrite (`commun.lire_jsonl`) : prévisions, mais aussi annonces, propositions et résolutions.
- Un erratum n'a d'effet que pour une ligne inscrite. Il n'y a plus ni délai ni décision prise après l'issue, ce qui règle aussi N4 et votre point 5.

**Contrôle de la plage.** La logique est passée du workflow à `scripts/controle_registres.py`, testé.
- Il contrôle tous les commits de `main` depuis le repère « contrôlé jusqu'à » le plus avancé du journal. Les commits poussés sans contrôle complet (« [skip ci] », jeton de workflow, exécution annulée ou interrompue) sont donc contrôlés à la poussée suivante.
- Chaque ligne est jugée à l'heure de la poussée qui l'a apportée, lue dans l'activité du dépôt.

**Ce que le contrôle inscrit ou signale de plus :**
- les lignes sans fuseau, avec un autre décalage que celui de Paris, illisibles ou dont un champ n'a pas le type attendu, toutes inscrites ;
- une copie à l'identique d'une ligne présente, signalée mais non inscrite ;
- une modification de `data/premieres_valeurs.jsonl` par un autre commit que la collecte, signalée ;
- une poussée directe sur la branche du journal, signalée ;
- une branche du journal absente ou recréée, qui est une erreur et jamais un journal vide.

**Robustesse :**
- lecture en octets, découpée sur le seul saut de ligne (U+2028 et retour chariot) ;
- écritures JSONL échappées en ASCII et sans CRLF ;
- `git diff --text` et `-z` ;
- un échec de git interrompt le contrôle sans écrire de repère ;
- types des champs vérifiés par `registre.py` à l'écriture.

**Modèle de menace.** La section 12 dit désormais ce que le contrôle couvre et ce qu'il ne couvre pas.
- Il vise les erreurs et les incidents.
- Il n'empêche pas une manœuvre délibérée de l'opérateur, seul administrateur du dépôt : auteur Git forgé, code du contrôle neutralisé, exécution supprimée, écriture directe sur la branche du journal.
- Ces manœuvres laissent des traces publiques, que le relecteur peut rechercher.

Ce choix est celui de Nathan : aucune protection complète n'est possible avec un seul administrateur.

**Tests :**
- `test_errata_et_unicite_du_cycle` reprend votre scénario : ligne émise le 1er, fait le 10, détection le 12. Elle est annulée ; une copie inscrite n'annule pas l'original ; un erratum sans inscription est ignoré.
- `test_controle_registres` porte sur un dépôt Git jetable. Il couvre une ligne tardive, une copie, un décalage étranger, l'absence de fuseau, une plage non contrôlée, des lignes « poison », des types inattendus, un CRLF, un octet NUL, le jugement poussée par poussée, une relance ancienne, l'absence de l'activité du dépôt et les fichiers des workflows.
- `test_branche_du_journal` couvre une branche absente ou recréée.
- `test_registre` couvre U+2028 et les types.
- `test_annonces_et_grappes_d_ajout` vérifie qu'une annonce inscrite est écartée.

**Mutations :** chaque garde retirée fait échouer son test.

**Sur GitHub :** la branche `controles` est créée, et les deux premières exécutions ont écrit leur repère. L'activité du dépôt est lue : 71 poussées.

## N2. EV-35 : chiffre partiel

Accepté. Le critère vise le nombre d'actes antimusulmans recensés sur l'ensemble de l'année 2026. Un chiffre portant sur une partie de l'année ne compte pas. Banque v1.10.

## N3. Résolution postérieure au gel, à la reprise

Accepté. `questions.py` n'écarte que les résolutions dont la date du fait est au plus tard celle du gel. Il refuse en outre de régénérer une banque déjà écrite (audit). Testé dans `test_rattrapage`, avec mutation.

## N4. Délai en jours entiers

Sans objet : le délai est supprimé.

## Défauts trouvés par les audits internes et non encore cités

- **Annonces tardives.** Une annonce consignée après l'enregistrement de la résolution ne coupe plus la question. Test et mutation.
- **Lignes inscrites et reprise.** Les vérifications de reprise de `comparateurs.py` et `ensemble.py` lisent aussi les lignes inscrites : un cycle annulé n'est pas réémis.
- **Ordre des grappes.** Les grappes sont triées avant le test par permutation : la valeur p ne dépend plus de l'ordre du registre.
- **Reportés à `controle/phase1.md` :**
  - calibration : un fait entre le gel et une émission tardive retire des « oui ». Classé souhaitable : le sens du biais est prudent, vers « recalibrer » ;
  - durée de la dernière prévision d'un cycle émise après le 1er ;
  - Brier descriptif par auteur ;
  - protection de la branche `controles` à poser sur GitHub.

## Vérifications

- `tests.py` : dix-neuf tests conformes.
- `controle_banque.py` : conforme.
- Workflow vérifié sur GitHub.
