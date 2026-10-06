# Liste de contrôle — phase 1 (premier cycle P : le 1er du mois qui suit la première version définitive, au plus tôt le 1er novembre 2026)

La phase 1 ne démarre que si chaque point est coché, avec le commit correspondant (protocole, section 3).

## Scripts

- [x] `scripts/questions.py` : banque de questions, seuils aux quantiles de la marche aléatoire, grappes, pools (environ 113 questions et 47 grappes par cycle au 1er novembre 2026).
- [x] `scripts/geler.py` : gel des données, manifeste à empreintes SHA-256, gel jamais réécrit.
- [x] `scripts/registre.py` : ajout au registre, horodatage par l'horloge système, propositions et résolutions ; tests dans `scripts/tests.py`.
- [x] `scripts/notation.py` : Brier, logarithmique, Murphy, Brier pondéré dans le temps, test par grappes à permutation de signes.
- [x] `scripts/puissance.py` : puissance publiée dans `data/puissance.json` sur la banque réelle (chiffres repris dans le noyau, section 8.6, qui seul fait foi).
- [x] `scripts/comparateurs.py` : persistance, taux de base ramené à la fenêtre, 50 %.

## Données et questions

- [x] `modele/evenements.json` : généré par `scripts/evenements.py` depuis `modele/banque/criteres.json` (critères réécrits et ajouts des relectures 8 à 15) ; 42 événements, 55 questions d'événement, 51 résolubles (banque v1.5, 4 octobre 2026).
- [x] Historique long des séries mensuelles et trimestrielles (taux 10 ans FR et DE et écart depuis 1990, IPCH depuis 1997, dette, PIB, chômage) : `collecte/historique.py`, `data/historique/` (4 octobre 2026).
- [x] Collecte des cotes externes pour P1 : Polymarket (232 marchés France, volume, écart offre-demande, drapeau de fiabilité), `collecte/cotes.py`. Metaculus exige un jeton : inaccessible, limite consignée (4 octobre 2026).
- [x] Taux de base des 50 questions d'événement résolubles (hors EV-05, loi uniforme ; banque v1.5), deux classes de référence ou plus (une seule pour EV-46, faute d'autre, et pour EV-28b et EV-33b, qui reprennent la classe retenue de leur première période), fourchette et classe retenue : `modele/taux_base/`, fusion `scripts/taux_base.py` → `modele/taux_base.json` (4 octobre 2026). Non bornés depuis la v1.22 (relecture 17, I3) : le score logarithmique borne seul ses probabilités. Plusieurs comptages reposent sur des sources partielles, signalées dans le champ « incertitude » : à revoir au premier bilan.
- [x] `scripts/resolution.py` : séries par script, événements par propositions d'agents concordantes, troisième avis, annulation.

## Ensemble direct

- [x] Consigne des cinq prévisionnistes rédigée et versionnée : `modele/consigne_ensemble.md` (v1.5).
- [x] Agrégation par médiane non extrémisée, scriptée : `scripts/ensemble.py` (au moins 5 prévisionnistes et 3 modèles, contrôle des réponses).

## Exécution

- [x] Procédure du cycle mensuel écrite : `modele/controle/cycle_mensuel.md`.
- [x] Procédure du tri écrite : `modele/controle/tri.md`, avec `scripts/tri.py` (4 octobre 2026).

- [x] Tâches planifiées créées : tri (lundi, mercredi, vendredi, 17 h 47), cycle mensuel (du 1er au 7 de chaque mois, 7 h 52, à partir du 1er novembre 2026), le 4 octobre 2026. Passée du 1er au 8 le 6 octobre 2026 (v1.26), avec la date de gel du manifeste à la reprise et l'erratum en cas d'échec d'horodatage.
- [x] Règle de rattrapage testée sur un passage manqué simulé (`test_rattrapage`, 5-6 octobre 2026) : reprise sur la date du gel du manifeste, étapes déjà faites non rejouées. Tâche planifiée alignée le 6 octobre 2026.
- [x] Journal des premières valeurs collectées (`scripts/premieres_valeurs.py`, `data/premieres_valeurs.jsonl`), lancé par la collecte nocturne (relecture 13, L1).
- [x] Clé API Webstat en secret GitHub `WEBSTAT_KEY` ; OAT quotidienne (TEC 10, depuis 2010) collectée chaque nuit par `collecte/webstat.py` ; seuils de l'écart calés sur le niveau quotidien corrigé du décalage avec la série BCE (4 octobre 2026).
- [x] Workflow de contrôle des registres actif : ajout seul, `--no-renames`, horodatage dans la fenêtre de poussée, décisions de tri en JSONL (section 12). Passé avec succès sur les poussées du cycle à blanc et de l'essai planifié (4 octobre 2026) ; étendu aux ajouts à la banque (`modele/banque/ajouts.jsonl`).
- [x] Tags `protocole-v*` et `annexe-phase3-v*` protégés contre la suppression et la mise à jour (ruleset actif depuis le 4 octobre 2026).
- [x] Branche `main` protégée contre la poussée forcée et la suppression (ruleset actif depuis le 4 octobre 2026).
- [x] Cycle à blanc sur la piste exploratoire, chaîne complète (4 octobre 2026) : `data/cycles/2026-10/ESSAI.md`. Quatre problèmes trouvés et corrigés ; un reste ouvert (série quotidienne de l'OAT).

## Prérequis de la phase 2 (P + 1 mois)

- [x] Écart de taux OAT-Bund journalier collecté depuis 2010 : TEC 10 (Banque de France) moins Bund 10 ans (Bundesbank, courbe Svensson). Décalage moyen avec la série BCE : environ −9 pb sur 12 mois, corrigé à l'ancrage.
- [ ] Historique journalier 2010-2025 pour le rétro-test (section 7.1).
- [ ] Source des sondages de la présidentielle identifiée et collectée (agrégat public ou instituts), avec l'historique des présidentielles 2002 à 2022 pour l'erreur des sondages (section 7.1).

## À examiner au bilan de la phase 1 (relecture 20)

- Contrôle des correspondances P1 : il se fait par événement ; un événement déjà en P1 au premier gel peut y faire passer d'autres questions mensuelles, et les questions de variable ne sont pas couvertes.

## Souhaitables de la relecture 21 reportés

- [ ] S4 : collecte nocturne de la valeur AGSI+ du 1er février 2027 (API), à écrire avant le 2 février 2027 ; le critère d'EV-38 la retient en premier (v1.26).
- [ ] S9 : levée d'une annonce consignée à tort par erratum dans `registre/annonces.jsonl`, et terme à l'exclusion d'émission quand l'acte annoncé échoue.
- [ ] S10 : `geler.py --essai` refusé pour une étiquette AAAA-MM à partir de 2026-11 ; tests réétiquetés (étiquettes d'essai distinctes).
- [ ] S1 et S2 : ajouts par la procédure d'ajout (fin des fonctions du Premier ministre par décret, quelle qu'en soit la cause ; référendum ; écart OAT-BTP de signe positif ; clause pour une présidentielle anticipée).

## Souhaitables de l'audit interne v1.27 reportés

- [ ] Calibration (I1 de l'audit, classé souhaitable : sens prudent) : un fait survenu entre le gel et une émission tardive (rattrapage) retire des « oui » de la calibration de l'auteur concerné, ce qui pousse vers « recalibrer ». Publier le nombre de questions ainsi retirées ; envisager de faire partir les questions au lendemain de la date limite d'émission.
- [ ] S2 : le Brier pondéré descriptif publié par auteur dépend de sa date de première émission ; le signaler dans le bilan (le test de 8.6, sur période commune, n'est pas touché).
