# Passation — état du projet au 6 octobre 2026

Document de reprise pour une nouvelle session. Le dépôt fait foi ; ce fichier ne remplace pas `modele/protocole.md` ni `modele/journal.md`.

## Objet

Psychohistoire : des prévisions datées et notées sur la France, d'octobre 2026 à septembre 2028. Dépôt public `Beynat/psychohistoire`. Le test central (noyau, section 8.6) compare un réseau bayésien (phase 3) à un ensemble direct de prévisionnistes IA (phase 1), sur des événements sans cote (P2b) et des questions conjointes (P2c).

## État

- **Versions.** Noyau v1.28, annexe de la phase 3 v1.7, banque v1.10 (55 questions, 42 événements), consigne de l'ensemble v1.5. Les tags `protocole-vX.Y` et `annexe-phase3-vX.Y` sont posés automatiquement.
- **Statut.** `modele/statut.json` vaut `definitif: false` : aucun cycle réel ne peut tourner. Le premier cycle prévu est celui du 1er novembre 2026.
- **Relectures.** Le compteur du critère d'arrêt est à zéro. La relecture de validation 21 (v1.26) puis la relecture de suivi 22 (v1.28, avec trois audits internes) ont été traitées. Prochaine étape : relecture de validation 23, en session neuve (`modele/v1.27/demande_relecture_23.md`).
- **Tests.** `python scripts/tests.py` (19 tests) et `python scripts/controle_banque.py` doivent passer avant chaque commit.

## Processus de relecture (noyau, section 12)

- **Relecture de validation.** Complète, en session neuve, par un autre Claude que Nathan relaie. Seules ces relectures comptent. Critère d'arrêt : deux relectures de validation consécutives sans défaut bloquant ni important ; Nathan déclare ensuite la version définitive dans `statut.json`.
- **Relecture de suivi.** Après une validation qui relève un défaut bloquant ou important, conduite dans la session du même relecteur. Elle vérifie seulement les corrections et ne compte pas.
- **Grille de classement** (section 12) :
  - bloquant : antériorité, intégrité des registres, cycle impossible ;
  - important : biais orienté d'un verdict de 8.6, ou issue de question contestable, avec un scénario à l'appui ;
  - souhaitable : tout le reste.
- **Audit interne avant chaque relecture de validation.** Un agent neuf éprouve par des essais trois propriétés :
  - deux auteurs aux prévisions identiques obtiennent le même score ;
  - aucune sélection, aucun poids ni aucune durée ne dépend de l'issue ;
  - aucune prévision ou donnée n'est postérieure à ce qu'elle prétend précéder.

  Les défauts graves des relectures 15 à 20 relevaient presque tous de ces trois familles, et plusieurs venaient des corrections elles-mêmes.
- **Fichiers.** Chaque version a son dossier `modele/vX.Y/`, qui contient la relecture reçue (texte intégral), la réponse point par point et la demande suivante. Le journal (`modele/journal.md`) reçoit une ligne par version, et le motif de `statut.json` est mis à jour.
- **Contrôle des corrections.** Chaque correction de code est accompagnée d'un test discriminant, et d'un contrôle par mutation : on remet l'ancien code et on vérifie que le test échoue.

## Contraintes à respecter

- Ne jamais demander ni afficher la clé Webstat : elle vit seulement dans le secret GitHub `WEBSTAT_KEY`.
- Aucune donnée d'essai dans `registre/protocole.jsonl`. Les essais utilisent des registres suffixés, sur une copie, ou des cycles nommés autrement que `AAAA-MM`.
- Ne pas publier la caractérisation proposée des faits d'actualité ni d'éléments de vie privée (annexe, section 11.2).
- Ne créer, modifier ou déclencher une tâche planifiée qu'avec l'accord de Nathan. Deux tâches existent :
  - cycle mensuel : `trig_01SJXN4Fmwjue8foVBeRXddV`, du 1er au 8 du mois à 7 h 52 (le 8 : déclaration d'un cycle manqué seulement), avec des gardes sur la date et sur `statut.json` ;
  - tri : `trig_01M5gsZGtbMwVYGUbaCRpELn`, lundi, mercredi et vendredi à 17 h 47.
- Journal des contrôles : branche `controles`, écrite par le seul workflow ; ne jamais y pousser. Modèle de menace : noyau, section 12, « Limites du contrôle ».
- Sources : méthode de fiabilité dans `modele/sources.md`. Une source n'est primaire que pour ses propres actes ; se méfier des médias partisans.

## Travaux en attente

1. Relecture de validation 23, puis la suite jusqu'au critère d'arrêt. Protéger la branche `controles` sur GitHub (suppression et réécriture).
2. Rattrapage : testé (`test_rattrapage`) ; tâche du cycle mensuel alignée le 6 octobre 2026 (du 1er au 8, date de gel du manifeste à la reprise).
3. Première collecte de données complète, puis v1 de l'outil et de l'interface.
4. Volet actualité de l'interface (`modele/interface/actualite.md`), qui doit montrer :
   - les ajouts quotidiens ;
   - les jalons et questions qu'ils peuvent influencer ;
   - un niveau de vigilance (important ou peu important).
5. Avant la phase 3 : la liste `modele/controle/phase3.md` (périmètre, copie aveugle, grappes des questions conjointes, statistique Z et facteur k sur une prévision indépendante de l'issue, marginale non calée).
6. Ajouts différés à la banque, par la procédure d'ajout : législatives anticipées, Nouvelle-Calédonie, régionales et départementales 2028, croissance du PIB, taux de la BCE, droits de douane entre les États-Unis et l'UE, grève dans la fonction publique en 2027 ; et, depuis la relecture 21, fin des fonctions du Premier ministre quelle qu'en soit la cause, référendum, écart OAT-BTP de signe positif, clause pour une présidentielle anticipée. Autres souhaitables reportés : `modele/controle/phase1.md`.

## Préférences de Nathan

Il écrit en français et attend un style clair, direct et synthétique, sans emoji et avec peu de mise en forme. Le challenger quand une faille est réelle, pas par principe. Il lit ses messages avec bienveillance : il emploie des raccourcis. Il veut avancer sans bloquer le processus sur des sujets de second ordre.
