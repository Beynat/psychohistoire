# Passation — état du projet au 10 octobre 2026

Document de reprise pour une nouvelle session. Le dépôt fait foi ; ce fichier ne remplace ni `modele/protocole.md` ni `modele/journal.md`.

## Objet

Psychohistoire : des prévisions datées et notées sur la France, d'octobre 2026 à septembre 2028. Dépôt public `Beynat/psychohistoire`. Le test central (noyau, section 8.6) compare un réseau bayésien (phase 3) à un ensemble direct de prévisionnistes IA (phase 1), sur des événements sans cote (P2b) et des questions conjointes (P2c).

## Cap fixé par Nathan le 10 octobre

1. **Une v0 déployée ce week-end.** L'objectif est un outil qui tourne de bout en bout (collecte, tri, questions, prévisions, notation, interface), pas un protocole parfait.
2. **Vérification et correction automatisées.** La boucle relecture → réponse → correction, relayée à la main jusqu'ici, doit tourner par sous-agents.
3. **Deux vérificateurs en parallèle.** Ils remontent des sujets différents ; leurs résultats sont fusionnés.
4. **Protocole en retrait.** Les formalités (critère d'arrêt, gel du texte, bilan et révisions de janvier) ne valent qu'à partir d'une version finale déployée, la « v0 ajustée ». D'ici là, on corrige et on avance. Restent en vigueur les règles qui protègent les données : registres en ajout seul, horodatage, contrôle à la poussée, tests.
5. **L'actualité comme test.** Le mouvement lycéen en cours montre comment les faits d'actualité sont intégrés (voir plus bas).
6. **Deux modèles de plus, après la France** : le monde, et le long terme. Le long terme est la psychohistoire proprement dite : un mouvement social n'est pas prévisible à court terme, mais sa probabilité sur une période peut l'être à partir d'indicateurs globaux.

## État

- **Versions.** Noyau v1.28 (la v1.27 est un tag intermédiaire, posé pendant un audit), annexe de la phase 3 v1.7, banque v1.10 (55 questions, 42 événements), consigne de l'ensemble v1.5. Les tags `protocole-vX.Y` et `annexe-phase3-vX.Y` sont posés automatiquement.
- **Statut.** `modele/statut.json` vaut `definitif: false`. Tant qu'il ne change pas, aucun cycle réel ne tourne : la tâche du cycle mensuel s'arrête d'elle-même. Le premier cycle prévu est celui du 1er novembre 2026.
- **Relectures.** La relecture de validation 23 a été demandée le 6 octobre (`modele/v1.27/demande_relecture_23.md`, sur le tag `protocole-v1.28`) ; son retour n'est pas dans le dépôt. Vu le point 4 du cap, elle sert de vérification et non plus de critère d'arrêt.
- **Tests.** `python scripts/tests.py` (19 tests) et `python scripts/controle_banque.py` passent. Les deux doivent passer avant chaque commit.
- **Ce qui tourne.** La collecte nocturne (GitHub Actions) et le tri (tâche planifiée, lundi, mercredi et vendredi). Le contrôle des registres s'exécute à chaque poussée et tient son journal sur la branche `controles`.
- **Registres.** `registre/protocole.jsonl` est vide. `registre/essai.jsonl` contient les cycles d'essai, et `registre/exploratoire.jsonl` la piste exploratoire, que l'interface (`index.html`, `data.json` v0.2 du 3 octobre) affiche aujourd'hui.

## Pour une v0 déployée

Ce qui manque, dans l'ordre :
1. **Décision de Nathan sur le statut.** Pour que le cycle du 1er novembre tourne, `statut.json` doit passer à `definitif: true` (ou la garde de la tâche doit viser un drapeau « v0 »). C'est la porte qui sépare les essais des données réelles, à décider explicitement et à journaliser.
2. **Cycle complet de bout en bout** avec les scripts actuels, sur un cycle d'essai (étiquette autre que `AAAA-MM`, registre suffixé) : gel, questions, comparateurs, cinq prévisionnistes, agrégation, résolution, notation, contrôle à la poussée. Le dernier essai complet date du 4 octobre, avant les versions 1.26 à 1.28.
3. **Interface v1** : afficher la piste protocole (questions du cycle, prévisions de l'ensemble et des comparateurs, scores une fois résolues) à côté de la piste exploratoire, et ajouter le volet actualité (`modele/interface/actualite.md` : ajouts quotidiens, questions concernées, niveau de vigilance).
4. **Protection de la branche `controles`** sur GitHub, contre la suppression et la réécriture. C'est à Nathan de la poser : le jeton de session n'a pas ce droit.
5. **Ajouts à la banque** jugés utiles pour la v0, par la procédure d'ajout. Liste dans « Travaux en attente ».

## Boucle de vérification automatisée (à construire)

Ce que les vérifications des 5 et 6 octobre ont appris :
- les corrections créent elles-mêmes des défauts. Trois audits successifs ont trouvé une quinzaine de défauts dans le seul contrôle à la poussée ;
- seuls les essais concrets les trouvent : copie du dépôt, dépôt Git jetable, scénario chiffré ;
- deux vérificateurs ne voient pas les mêmes choses.

Proposition :
- **Orchestrateur.** Une session lance deux vérificateurs neufs en parallèle (outil Agent), sur des angles distincts :
  - A, intégrité et antériorité : symétrie, indépendance vis-à-vis de l'issue, horodatage, registres, rattrapage, par essais sur copie ;
  - B, fond et conformité : critères de la banque, sources, actualité, texte contre code, interface.
- **Fusion.** L'orchestrateur dédoublonne, classe selon la grille (bloquant, important, souhaitable) et écarte ce qui n'a ni essai ni raisonnement précis.
- **Correction.** Chaque défaut bloquant ou important est corrigé, avec un test discriminant et un contrôle par mutation (remettre l'ancien code, vérifier que le test échoue) ; les souhaitables vont à une liste.
- **Arrêt.** On recommence jusqu'à un tour sans bloquant ni important, avec trois tours au plus ; au-delà, Nathan arbitre.
- **Garde-fous.** Les vérificateurs ne modifient rien et travaillent sur copie ; seul l'orchestrateur commite. On donne aux vérificateurs le modèle de menace (noyau, section 12, « Limites du contrôle ») pour éviter les manœuvres délibérées sans conséquence pratique.
- **Forme.** Une compétence (skill) « vérifier-et-corriger » réutilisable, ou une tâche planifiée déclenchée après chaque version, avec l'accord de Nathan.

## L'actualité : le mouvement lycéen comme test

Constat au 10 octobre, sur `data/tri/2026-10.jsonl` :
- 958 titres triés depuis le 5 octobre, aucun rattaché à une question ;
- 203 portent sur le mouvement lycéen : blocages, maintien de l'ordre, allocution du Premier ministre du 7 octobre, réponse du gouvernement.

Le mouvement est donc bien vu par le tri, mais aucune question ne le capte :
- EV-10 (extension du mouvement lycéen) a été retiré : aucune source officielle ne publie le nombre d'établissements bloqués ;
- EV-39 (journée à plus de 500 000 manifestants selon l'Intérieur) a un seuil hors de portée d'un mouvement lycéen ;
- EV-13 (grève dans la fonction publique) ne le concerne pas.

À faire :
- **Volet actualité.** Afficher ces faits regroupés (`fait`), avec leur vigilance, même sans question rattachée. C'est le cas typique du volet.
- **Questions candidates**, par la procédure d'ajout, résolubles sur des sources primaires :
  - acte du gouvernement en réponse (décret, circulaire, loi) ;
  - journée lycéenne et étudiante chiffrée par l'Intérieur au-dessus d'un seuil plus bas ;
  - saisine ou décision d'une juridiction sur le maintien de l'ordre ;
  - démission d'un ministre.
- **Motifs de non-rattachement.** Les relire comme un signal de ce qui manque à la banque.

## Deux modèles à venir

- **Monde.** Mêmes outils (banque, ensemble, comparateurs, notation), sur des événements internationaux : conflits, élections majeures, commerce, énergie, banques centrales. Sources primaires des institutions concernées et agences.
- **Long terme (psychohistoire).** On ne prévoit pas l'événement, mais sa probabilité sur une période (un à cinq ans) à partir d'indicateurs structurels lents. Pistes à examiner :
  - théorie structurelle-démographique de Turchin et son indicateur de tension politique ;
  - chômage des jeunes, inégalités, confiance dans les institutions, pouvoir d'achat, prix de l'énergie, démographie des diplômés.

  Les indicateurs seraient calibrés sur l'histoire, en France et dans des pays comparables. Les questions porteraient sur des fréquences (« au moins un mouvement de telle ampleur d'ici telle date »), notées comme les autres. C'est le cadre qui répond au cas lycéen.
- **Ordre.** Après la v0 France.

## Contraintes à respecter

- Ne jamais demander ni afficher la clé Webstat : elle vit seulement dans le secret GitHub `WEBSTAT_KEY`.
- Aucune donnée d'essai dans `registre/protocole.jsonl`. Les essais utilisent des registres suffixés, une copie, ou des cycles nommés autrement que `AAAA-MM`.
- Ne pas publier la caractérisation proposée des faits d'actualité ni d'éléments de vie privée (annexe, section 11.2).
- Ne créer, modifier ou déclencher une tâche planifiée qu'avec l'accord de Nathan. Deux tâches existent :
  - cycle mensuel : `trig_01SJXN4Fmwjue8foVBeRXddV`, du 1er au 8 du mois à 7 h 52 (le 8 sert seulement à déclarer un cycle manqué), avec des gardes sur la date et sur `statut.json` ; la date de gel du manifeste est reprise en cas de reprise ;
  - tri : `trig_01M5gsZGtbMwVYGUbaCRpELn`, lundi, mercredi et vendredi à 17 h 47.
- Journal des contrôles : branche `controles`, écrite par le seul workflow ; ne jamais y pousser. Racine dans `modele/controles_racine.txt`. Pour travailler hors ligne, `JOURNAL_CONTROLES` désigne une copie du journal.
- Sources : méthode de fiabilité dans `modele/sources.md`. Une source n'est primaire que pour ses propres actes ; se méfier des médias partisans.
- Chaque correction de code est accompagnée d'un test discriminant et d'un contrôle par mutation.

## Travaux en attente

1. v0 : les cinq points de « Pour une v0 déployée ».
2. Boucle de vérification automatisée.
3. Volet actualité et questions sur le mouvement lycéen.
4. Ajouts différés à la banque, par la procédure d'ajout : législatives anticipées, Nouvelle-Calédonie, régionales et départementales 2028, croissance du PIB, taux de la BCE, droits de douane entre les États-Unis et l'UE, grève dans la fonction publique en 2027, fin des fonctions du Premier ministre quelle qu'en soit la cause, référendum, écart OAT-BTP de signe positif, clause pour une présidentielle anticipée. Autres souhaitables reportés : `modele/controle/phase1.md`.
5. Avant la phase 3 : la liste `modele/controle/phase3.md`.
6. Modèles Monde et Long terme, après la v0.

## Préférences de Nathan

Il écrit en français et attend un style clair, direct et synthétique, sans emoji et avec peu de mise en forme. Le challenger quand une faille est réelle, pas par principe. Il lit ses messages avec bienveillance : il emploie des raccourcis. Il veut avancer sans bloquer le processus sur des sujets de second ordre.
