# Dossier de faits : sondages et offre de gauche (état au 16 octobre 2026)

Lot L8 : VE-SOND (deuxième place derrière le RN, état « serré » si les deux premiers blocs derrière le RN sont à 2 points ou moins), PV-ECOLO (vote des adhérents des Écologistes, 10-13 décembre 2026), PV-SOUTIEN (bénéficiaire du soutien des Écologistes), PV-BLOC (candidatures Philippe et Attal), PV-GAUCHE (nombre de candidats de gauche), PV-DUEL (duel du second tour).

Ce dossier reprend et met à jour les dossiers du 10 octobre 2026 (offre_presidentielle_2026-10-10.md et presidentielle_2026-10-10.md). Il ne contient aucune probabilité ni aucun avis sur l'avenir. Rangs selon modele/sources.md : PO primaire officielle, I institut, MR média de référence, S spécialisée, W tertiaire, ME média engagé, MEE média d'État, PP partie prenante. Un fait appuyé seulement par S, W, ME, MEE ou PP est marqué « non vérifié ». Les notices de la Commission des sondages sont notées [PO/I] : la Commission est PO pour le dépôt, l'institut est I pour ses chiffres.

Domaines non classés dans sources.json et utilisés ici : tolunacorporate.com (site d'institut, traité en I) ; lepetitjournal.com, lagazettefrance.fr, sudradio.fr, fr.news.yahoo.com et actu.orange.fr (reprises de dépêches AFP, BFMTV, 20 Minutes ou L'Express ; traités en MR « à vérifier », car l'origine est une agence ou un média de référence) ; ground.news (agrégateur, W) ; en.wikipedia.org (W, règle de suffixe).

Recherches web : 29. Aucun marché de prédiction ni site de paris n'a été consulté.

---

## 1. Sondages

### 1.1 Série mensuelle de VE-SOND, mars 2025 à septembre 2026 (calcul sur data/etat/sondages.jsonl)

Méthode, identique à la définition du nœud et à la règle de erreur_sondages.json :
- Hypothèses de premier tour qui testent Édouard Philippe, seules retenues.
- Chaque bloc est compté par son candidat le mieux placé dans l'hypothèse. Centre : Philippe, Attal. Gauche : Mélenchon, Glucksmann, Ruffin, Tondelier, Roussel, Faure. Droite : Retailleau, Lisnard, Wauquiez, Bertrand. Hollande, Cazeneuve, Royal et Maurel ne figurent pas dans la liste du bloc de gauche ; ils ne comptent donc pas, même quand ils sont testés.
- Moyenne des hypothèses par institut, puis moyenne simple des instituts, par mois de fin de terrain. Aucune correction de l'erreur historique.
- Les 5 lignes « verifie » : false du fichier sont incluses, comme dans le calcul du projet.
- Mois absents : juin, juillet et août 2025, décembre 2025 et janvier 2026 (aucune hypothèse avec Philippe dans le fichier).

| Mois | Instituts / hypothèses | RN | Centre | Gauche | Droite | Écart 1er-2e bloc derrière le RN | État |
|---|---|---|---|---|---|---|---|
| mars 2025 | 2 / 5 | 35,2 | 23,0 | 12,8 | 6,2 | 10,2 | centre |
| avril 2025 | 3 / 13 | 32,3 | 21,6 | 11,1 | 8,2 | 10,5 | centre |
| mai 2025 | 2 / 4 | 30,8 | 21,0 | 13,6 | 14,2 | 6,8 (sur la droite) | centre |
| septembre 2025 | 1 / 3 | 33,3 | 17,0 | 14,3 | 9,3 | 2,7 | centre |
| octobre 2025 | 3 / 8 | 33,4 | 17,2 | 13,7 | 9,3 | 3,5 | centre |
| novembre 2025 | 2 / 2 | 35,8 | 17,0 | 13,2 | 7,8 | 3,8 | centre |
| février 2026 | 1 / 5 | 35,8 | 18,4 | 11,2 | 10,8 | 7,2 | centre |
| mars 2026 | 3 / 6 | 35,3 | 21,2 | 12,6 | 7,6 | 8,6 | centre |
| avril 2026 | 1 / 2 | 33,0 | 19,0 | 12,0 | 9,5 | 7,0 | centre |
| mai 2026 | 4 / 18 | 32,9 | 17,0 | 14,3 | 8,9 | 2,7 | centre |
| juin 2026 | 2 / 8 | 35,3 | 18,9 | 13,9 | 9,1 | 5,0 | centre |
| juillet 2026 | 6 / 12 | 34,5 | 18,1 | 15,5 | 7,9 | 2,6 | centre |
| août 2026 | 3 / 11 | 34,2 | 17,6 | 16,1 | 6,9 | 1,4 | serré |
| septembre 2026 | 6 / 41 | 33,4 | 16,7 | 16,7 | 7,5 | 0,1 | serré |

Lecture factuelle :
- Sur 14 mois observés, l'état est « centre » 12 fois (mars 2025 à juillet 2026) et « serré » 2 fois (août et septembre 2026). Les états « gauche » et « droite » n'apparaissent pas.
- Le bloc en tête derrière le RN ne change jamais dans la moyenne mensuelle : c'est toujours le centre, à égalité en septembre 2026 (16,7 contre 16,7 avant arrondi : écart 0,1).
- L'écart passe de plus de 10 points au printemps 2025 à 0,1 point en septembre 2026. Il est de 2,6 à 2,7 points en septembre 2025, mai 2026 et juillet 2026.
- Variante en moyenne simple de toutes les hypothèses (sans pondération par institut) : écart de 1,5 en août et 0,6 en septembre 2026 ; même état.
- Par hypothèse, en septembre 2026 : le centre est devant la gauche dans 23 hypothèses sur 41, la gauche dans 18.
- Le RN est compté par Le Pen ou Bardella selon l'hypothèse (Le Pen seule depuis juillet 2026).

### 1.2 Sondages de premier tour publiés depuis le 1er octobre 2026

Liste des notices de la Commission des sondages d'octobre 2026, lue le 16 octobre (35 notices « présidentielle ») [PO] https://www.commission-des-sondages.fr/notices/ . Cinq contiennent des intentions de vote de premier tour. Les autres portent sur la popularité, le potentiel électoral (Toluna-Harris pour L'Opinion, 8 octobre), la primaire (Elabe, 3 octobre ; Toluna-Harris, 9 octobre) ou l'actualité. Les cinq notices ont été lues en entier.

| Institut (commanditaire) | Terrain | Échantillon | Avant ou après la primaire du 11 octobre | Source primaire |
|---|---|---|---|---|
| Odoxa (Backbone, Public Sénat, presse régionale, Le Nouvel Obs) | 24 sept.-7 oct. 2026 | 12 005 interrogés, 11 103 inscrits ; 7 374 à 7 599 exprimés | avant | [PO] notice 10310 : https://www.commission-des-sondages.fr/notices/files/notices/2026/octobre/10310-pres-iv-odoxa-14-octobre.pdf (méthode et questionnaire, sans tableau) ; [I] rapport Odoxa du 14 octobre : https://www.odoxa.fr/wp-content/uploads/2026/10/Odoxa-Backbone-pour-la-Presse-Regionale-Public-Senat-et-le-Nouvel-Obs-IV-a-lelection-presidentielle-de-2027.pdf |
| Toluna-Harris Interactive (M6, RTL) | 5-8 oct. 2026 | 2 348 interrogés, 2 004 inscrits ; 1 251 à 1 285 exprimés | avant | [PO/I] notice 10305 : https://www.commission-des-sondages.fr/notices/files/notices/2026/octobre/10305-pres-iv-toluna-harris-interactive-12-octobre.pdf |
| Ifop-Fiducial (LCI, Sud Radio) | 12-14 oct. 2026 | 1 525 interrogés, 1 390 inscrits ; 1 024 à 1 081 exprimés | après | [PO/I] notice 10314 : https://www.commission-des-sondages.fr/notices/files/notices/2026/octobre/10314-pres-climat-politique-post-primaire-ps-pp-ifop-lci-14-octobre.pdf |
| OpinionWay (Les Echos, Radio Classique), Presitrack vague 3 | 13-14 oct. 2026 | 1 001 interrogés, 978 inscrits, 731 certains d'aller voter | après | [PO/I] notice 10318 : https://www.commission-des-sondages.fr/notices/files/notices/2026/octobre/10318-pres-presitrack-v3-opinionway-15-octobre.pdf |
| OpinionWay (CNews) | 13-14 oct. 2026 | 1 043 interrogés, 978 inscrits, 731 certains d'aller voter | après | [PO/I] notice 10319 : https://www.commission-des-sondages.fr/notices/files/notices/2026/octobre/10319-pres-iv-opinionway-cnews-15-octobre.pdf |

Scores de premier tour (en % des exprimés) :

| Sondage | Hypothèse | Le Pen | Philippe | Attal | Mélenchon | Glucksmann | Hollande | Tondelier | Roussel | Retailleau | Autres |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Odoxa | Philippe | 37 | 17 | — | 18 | 9,5 | — | 3 | 2 | 6,5 | Arthaud 0,5, NDA 2, Zemmour 4,5 |
| Odoxa | Attal | 38 | — | 11 | 18,5 | 10,5 | — | 3,5 | 2 | 9 | Arthaud 1, NDA 2, Zemmour 4,5 |
| Toluna-Harris | Glucksmann, Attal, Philippe | 35 | 13 | 5 | 18 | 10 | — | 2 | 2 | 7 | Arthaud 1, NDA 2, Zemmour 5 |
| Toluna-Harris | Glucksmann, Philippe | 36 | 17 | — | 18 | 10 | — | 3 | 2 | 7 | Arthaud 1, NDA 2, Zemmour 4 |
| Toluna-Harris | Glucksmann, Attal | 36 | — | 12 | 18 | 11 | — | 3 | 2 | 10 | Arthaud 1, NDA 2, Zemmour 5 |
| Toluna-Harris | Hollande, Philippe | 36 | 17 | — | 18 | — | 7 | 4 | 3 | 8 | Arthaud 1, NDA 2, Zemmour 4 |
| Toluna-Harris | Hollande, Attal | 37 | — | 12 | 19 | — | 7 | 5 | 2 | 10 | Arthaud 1, NDA 2, Zemmour 5 |
| Ifop | Philippe et Attal | 34 | 14 | 6 | 16 | 14 | — | 2 | 2,5 | 6,5 | NDA 2, Zemmour 3 |
| Ifop | Philippe | 35 | 18 | — | 16 | 13,5 | — | 2,5 | 3 | 6,5 | Arthaud 0,5, NDA 2, Zemmour 3 |
| Ifop | Attal | 36 | — | 13 | 17 | 16 | — | 2 | 2,5 | 8 | Arthaud 0,5, NDA 2, Zemmour 3 |
| Ifop | Ruffin, Villepin, Lisnard | 32 | 13 | 5 | 16 | 11,5 | — | 2 | 2 | 5 | Ruffin 2, Villepin 1,5, Lisnard 6, NDA 1, Zemmour 3 |
| OpinionWay (Les Echos) | Attal et Philippe | 35 | 12 | 7 | 14 | 13 | — | 3 | 3 | 7 | Arthaud <1, NDA 2, Zemmour 4 |
| OpinionWay (Les Echos) | Attal | 37 | — | 11 | 15 | 16 | — | 3 | 2 | 9 | Arthaud 1, NDA 2, Zemmour 4 |
| OpinionWay (Les Echos) | Philippe | 35 | 15 | — | 15 | 15 | — | 3 | 2 | 8 | Arthaud 1, NDA 2, Zemmour 4 |
| OpinionWay (CNews) | liste unique | 35 | 12 | 5 | 15 | 13 | — | 2 | 1 | 6 | Bouamrane <1, Lisnard 4, Arthaud 1, NDA 1, Zemmour 5 |

Remarques sur les sources :
- Odoxa : la notice déposée ne contient pas les résultats ; les scores viennent du rapport de l'institut [I]. Le terrain (24 septembre-7 octobre) précède la primaire. L'institut écrit : « Mélenchon est passé devant lui avec 18% (+2 pts) vs 17% ». Il donne aussi Le Pen 53, Philippe 47 au second tour, et Le Pen 68, Mélenchon 32 [I] https://www.odoxa.fr/sondage/melenchon-est-passe-devant-philippe-au-premier-tour-marine-le-pen-est-plus-que-jamais-la-grande-favorite-pour-2027-a-la-fois-au-premier-et-au-second-tour/ (14 octobre 2026).
- Toluna-Harris : second tour, Le Pen 56 contre Philippe 44, et Le Pen 67 contre Mélenchon 33 [PO/I] notice 10305. Le baromètre précédent (22-24 septembre) donnait 57-43 et 69-31 (dossier du 10 octobre).
- Ifop : la notice ne contient aucun second tour. Sud Radio (15 octobre) donne Retailleau à 6 % dans l'hypothèse Ruffin-Villepin-Lisnard ; la notice donne 5 %, retenu ici : https://www.sudradio.fr/ifop/exclu-presidentielle-2027-glucksmann-grignote-le-pen-reste-intouchable
- OpinionWay (Les Echos), hypothèse 1 : le tableau de la notice place 4 % sur la ligne « Marine Le Pen » et 35 % sur la ligne « Eric Zemmour ». Les hypothèses 2 et 3 et l'ordre du questionnaire indiquent une inversion des étiquettes. La ligne est écrite avec Le Pen 35 et Zemmour 4, et l'inversion est notée.
- OpinionWay (CNews) : le questionnaire de la notice liste François Hollande et Karim Bouamrane, mais pas Glucksmann. Le tableau publié donne Glucksmann à 13 % et Bouamrane à moins de 1 %, sans ligne Hollande. Les seconds tours testés sont Le Pen 56 contre Philippe 44, Le Pen 56 contre Glucksmann 44, et Le Pen 68 contre Mélenchon 32. Cette ligne est écrite avec « verifie » : false.

Fichier /tmp/claude-0/elic16/sondages_octobre.jsonl : 15 lignes au format de sondages.jsonl, une par hypothèse de premier tour. 14 lignes portent « verifie » : true (notice ou rapport de l'institut lu) et 1 ligne porte false (OpinionWay pour CNews). Valeurs « <1 % » codées 0,5. Les deux notices OpinionWay sont tirées du même échantillon de 978 inscrits.

### 1.3 VE-SOND pour octobre 2026, mois en cours (calcul provisoire au 16 octobre)

En ajoutant ces 15 lignes à la série, octobre 2026 donne 4 instituts et 10 hypothèses avec Philippe. Les moyennes sont : RN 35,3, centre 15,2, gauche 16,7, droite 6,8. L'écart est de 1,5 point, état « serré », avec la gauche devant. Sans la ligne non vérifiée : centre 15,3, gauche 16,6, écart 1,3, état « serré ».

C'est le premier mois de la série où la gauche est devant le centre dans la moyenne. Le mois n'est pas clos : d'autres vagues sont attendues, notamment Ifop vague 7, Elabe, Ipsos, YouGov et Cluster17.

Découpage par rapport à la primaire du 11 octobre (moyennes par institut, hypothèses avec Philippe) :
- Avant : Odoxa et Toluna-Harris, 4 hypothèses. Centre 16,3, gauche 18,0 (Mélenchon dans les 4), Glucksmann 8,1, écart 1,7.
- Après : Ifop et OpinionWay, 6 hypothèses. Centre 13,5, gauche 15,2, Glucksmann 13,3, écart 1,7. Sans la ligne CNews : centre 14,2, gauche 15,2, écart 1,0.
- Après la primaire, la gauche est comptée par Mélenchon dans 5 hypothèses sur 6. Dans la sixième (OpinionWay pour Les Echos, Philippe seul), Glucksmann et Mélenchon sont à égalité, à 15.

Même institut, avant et après la primaire (premier tour) :
- Ifop, du 25-29 septembre au 12-14 octobre. Hypothèse avec Philippe et Attal : Glucksmann 11 puis 14, Mélenchon 15 puis 16, Philippe 16 puis 14, Le Pen 32 puis 34. Avec Philippe seul : Glucksmann 11 puis 13,5, Philippe 21 puis 18. Avec Attal seul : Glucksmann 13 puis 16, Attal 15 puis 13.
- OpinionWay pour Les Echos, du 9 septembre au 13-14 octobre. Hypothèse avec les deux : Glucksmann 9 puis 13, Philippe 15 puis 12. Avec Philippe seul : Glucksmann 10 puis 15, Philippe 19 puis 15. Avec Attal seul : Glucksmann 12 puis 16, Attal 14 puis 11.
- Toluna-Harris, du 22-24 septembre au 5-8 octobre, sans primaire entre les deux : Glucksmann 10 puis 10 (avec Philippe seul), Mélenchon 18 puis 18.
- Les septembres viennent de data/etat/sondages.jsonl.

---

## 2. Taux de base de la dynamique (cycles 2017 et 2022)

### 2.1 Classe de référence et sources

- Classe : sondages de premier tour publiés de mai de l'année N-1 à avril de l'année N (12 mois avant le premier tour), en 2016-2017 et 2021-2022.
- Agrégation : moyenne des hypothèses par institut, puis moyenne simple des instituts, par mois de fin de terrain (même règle qu'au point 1).
- Source : tableaux de Wikipédia en anglais, « Opinion polling for the 2017 French presidential election » et « … 2022 … », texte brut téléchargé le 16 octobre 2026 : https://en.wikipedia.org/wiki/Opinion_polling_for_the_2017_French_presidential_election et https://en.wikipedia.org/wiki/Opinion_polling_for_the_2022_French_presidential_election [W]. On obtient 339 hypothèses de 14 instituts pour 2017 et 481 hypothèses de 15 instituts pour 2022.
- Statut : non vérifié, car c'est une source W. Aucun sondage n'a été recontrôlé sur une notice dans cette session. Le projet utilise le même index pour erreur_sondages.json.
- Août 2016 : aucun sondage n'est listé, donc 11 mois observés pour 2017.

### 2.2 Par candidat (tous candidats, RN compris)

2017 (11 mois). La deuxième place change 3 fois :
- Le Pen jusqu'en décembre 2016 ;
- Fillon en janvier 2017 (Le Pen passe première) ;
- Macron en février et mars ;
- Le Pen en avril (Macron premier).

Aucun mois n'a un écart entre deuxième et troisième de 2 points ou moins. Les plus petits sont 3,1 points (février 2017) et 4,0 points (janvier et avril 2017). Au niveau des hypothèses, l'écart médian entre deuxième et troisième est de 2,0 points en février 2017.

2022 (12 mois). La deuxième place change 3 fois :
- Macron en mai 2021 ;
- Le Pen de juin à novembre ;
- Pécresse en décembre 2021 ;
- Le Pen de janvier à avril 2022.

Trois mois consécutifs ont un écart de 2 points ou moins : décembre 2021 (Pécresse 17,3, Le Pen 15,9), janvier 2022 (Le Pen 16,6, Pécresse 15,9) et février 2022 (Le Pen 16,6, Zemmour 14,7). C'est donc un seul coude-à-coude, de 3 mois. Il prend fin en mars 2022, avec un écart de 5,7 points.

Premier candidat hors FN/RN, l'analogue le plus proche de VE-SOND, qui exclut le RN :
- 2017 : 2 changements. Juppé laisse la place à Fillon en novembre 2016, à cause du résultat de la primaire de la droite qui modifie les hypothèses testées. Fillon laisse la place à Macron en février 2017. Aucun mois n'a un écart de 2 points ou moins ; le minimum est de 3,1 points en février 2017.
- 2022 : 0 changement, Macron reste en tête tous les mois. Aucun mois n'a un écart de 2 points ou moins ; le minimum est de 6,9 points.

### 2.3 Par bloc (définition proche de VE-SOND)

Blocs retenus :
- Centre : Macron et Bayrou.
- Gauche : PS, écologistes, LFI et PCF.
- Droite : LR.
- 2022 seulement : Zemmour compté à part.

Deux mesures, sur les deux cycles :
- Le premier bloc derrière le FN/RN change 1 fois en 2017 : la droite passe derrière le centre en février 2017. Il ne change pas en 2022 : le centre reste devant.
- L'écart entre les deux premiers blocs derrière le FN/RN n'est jamais de 2 points ou moins. Il varie de 3,1 à 16,2 points en 2017 et de 6,9 à 15,6 points en 2022.

Décompte : aucun mois « serré » sur 23 mois observés. La classe ne contient que deux cycles. Le RN n'y était pas le premier bloc de façon continue : il était premier dans 7 des 11 mois de 2017 et dans 1 des 12 mois de 2022.

---

## 3. Effet des ralliements et des soutiens sur les sondages

Les intentions de vote viennent de l'index Wikipédia décrit en 2.1 [W] ; elles sont donc non vérifiées. Les dates des retraits viennent de sources MR.

| Événement | Date | Avant (fenêtre, hypothèses) | Après (fenêtre, hypothèses) | Écart observé |
|---|---|---|---|---|
| Bayrou renonce et propose une alliance à Macron, qui l'accepte | 22 février 2017 [MR] Public Sénat : https://www.publicsenat.fr/actualites/politique/bayrou-renonce-a-briguer-l-elysee-macron-accepte-son-offre-d-alliance-55766 | 29 janv.-21 févr. 2017, hypothèses avec Bayrou (23 hypothèses, 6 instituts) : Macron 20,7, Bayrou 5,1. Hypothèses sans Bayrou de la même période : Macron 22,2 | 24 févr.-23 mars 2017 (59 hypothèses, 9 instituts) : Macron 25,1 | Macron +4,4 par rapport aux hypothèses avec Bayrou (somme Macron + Bayrou avant : 25,8) |
| Jadot retire sa candidature au profit de Hamon | 23 février 2017 [MR] Public Sénat, 24 février 2017 (dossier du 10 octobre) ; accord approuvé par 79,53 % des votants écologistes [MR] Public Sénat, 26 février 2017 : https://www.publicsenat.fr/actualites/politique/presidentielle-l-accord-hamon-jadot-approuve-par-les-ecologistes-55928 | mêmes 23 hypothèses : Hamon 14,9, Jadot 1,6 | 24 févr.-10 mars : Hamon 14,0 ; 24 févr.-23 mars : Hamon 13,5 | Hamon -0,9 à -1,4 (somme Hamon + Jadot avant : 16,5) |
| Victoire de Hamon à la primaire du PS (repère pour une primaire) | 29 janvier 2017 (rappel, non vérifié) | 1er-27 janv. 2017, hypothèses avec Hamon (5 instituts) : Hamon 7,9 | 30 janv.-28 févr. 2017 (9 instituts) : Hamon 14,8 | Hamon +6,9 |
| Montebourg se retire sans soutenir personne | 19 janvier 2022 (date non vérifiée). Annonce « sans se rallier à un autre candidat » [MR, à vérifier] Europe 1, 18 janvier 2022 : https://www.europe1.fr/politique/presidentielle-montebourg-va-annoncer-le-retrait-de-sa-candidature-4088599 | 1er-18 janv. 2022 (15 hypothèses, 6 instituts) : Montebourg 0,9, Roussel 2,1, Hidalgo 2,8, Taubira 4,1 | 20 janv.-18 févr. (60 hypothèses, 8 instituts) : Roussel 3,5, Hidalgo 2,4, Taubira 4,0 | aucun gain supérieur à 1,4 point pour un candidat de gauche |
| Taubira retire sa candidature (181 parrainages), sans soutien immédiat | 2 mars 2022 [MR] Public Sénat : https://www.publicsenat.fr/actualites/politique/presidentielle-christiane-taubira-annonce-qu-elle-retire-sa-candidature-196538 | 1er févr.-1er mars 2022 (62 hypothèses, 9 instituts) : Taubira 3,2, Mélenchon 10,9, Hidalgo 2,2, Jadot 5,1 | 3 mars-2 avril (91 hypothèses, 10 instituts) : Mélenchon 13,5, Hidalgo 1,9, Jadot 5,2 | Mélenchon +2,6, sur une période qui contient aussi l'invasion de l'Ukraine (24 février) |

Faits liés :
- Le 5 mars 2022, la Primaire populaire apporte son soutien à Mélenchon. Seul le titre a été lu [MR] La Libre, 5 mars 2022 : https://www.lalibre.be/international/europe/elections-france/2022/03/05/exit-taubira-la-primaire-populaire-apporte-son-soutien-a-jean-luc-melenchon-XFRMBHQ2AVEULMSZFDC2MF2VH4/
- Aucune mesure n'isole l'effet propre d'un soutien. Les écarts ci-dessus mélangent changement d'hypothèse, tendance de fond et événements concomitants.

---

## 4. Écologistes : vote de décembre, positions et précédents

### 4.1 Procédure (rappel du dossier du 10 octobre, sans changement trouvé)

- Référendum interne du 10 au 13 décembre 2026, avec deux options : être représenté par Marine Tondelier, ou soutenir un candidat d'une autre force de gauche. Le texte des options sera présenté dans la seconde quinzaine de novembre. La motion de la direction a été adoptée avec 69,44 % des voix le 21 septembre 2026 [MR] LCP, 21 septembre 2026 : https://lcp.fr/actualites/candidature-a-la-presidentielle-pas-de-choix-definitif-des-ecologistes-avant-la-mi ; [MR] Public Sénat, même date.
- Le 16 octobre 2026, 20 Minutes écrit que la stratégie ne sera pas tranchée avant le 13 décembre. Les militants choisiront entre candidature autonome et retrait derrière un autre candidat [MR, à vérifier] 20 Minutes repris par Yahoo : https://fr.news.yahoo.com/sport/pr%C3%A9sidentielle-2027-personne-ne-gagnera-081418673.html
- Règles de majorité, de quorum et de désignation nominative du bénéficiaire : non trouvées.
- Antécédent interne : le 7 mai 2026, des membres des trois courants d'opposition à Tondelier ont déposé une motion pour remettre en jeu sa candidature si la primaire n'avait pas lieu avant le 30 octobre 2026. La direction l'a qualifiée de « manoeuvre de bas étage » [MR, à vérifier] AFP reprise par La Gazette France, 7 mai 2026 : https://www.lagazettefrance.fr/article/presidentielle-les-opposants-a-tondelier-reclament-un-nouveau-vote-interne-en-cas-d-absence-de-primaire

### 4.2 Positions déclarées depuis le 11 octobre 2026

Marine Tondelier (direction) :
- Le 11 octobre, elle déplore que le vainqueur soit « celui qui fait le choix du repli » [MR, à vérifier] AFP reprise par Le Petit Journal, 12 octobre 2026 : https://lepetitjournal.com/expat-politique/apres-une-primaire-reussie-les-choses-serieuses-commencent-pour-glucksmann-455946
- Elle prend acte du résultat sans annoncer de soutien [MR] LCP, 11 octobre 2026 : https://lcp.fr/actualites/victoire-de-raphael-glucksmann-a-la-primaire-socialiste-premieres-reactions-des
- Sur X, elle défend « le refus du clanisme et du concept des gauches irréconciliables » [MR, à vérifier] BFMTV avec AFP, repris par Yahoo, 11 octobre 2026 : https://fr.news.yahoo.com/victoire-rapha%C3%ABl-glucksmann-marine-tondelier-174921647.html
- Le 16 octobre : « Je continue de mener une double campagne : pour l'écologie et pour l'union ». Elle refuse de « désigner le roi du cimetière » entre Glucksmann et Mélenchon (20 Minutes, lien ci-dessus).

Courants et élus :
- Jérémie Iordanoff, proche de Jadot, appelle à « ouvrir des négociations » et juge la réaction de Tondelier « pas à la hauteur ». Le courant « Faire gagner l'écologie » demande que le désaccord stratégique soit tranché par un vote des adhérents [MR, à vérifier] 6Médias avec L'Express, repris par Orange, 12 octobre 2026 : https://actu.orange.fr/politique/presidentielle-raphael-glucksmann-vainqueur-de-la-primaire-sociale-democrate-division-chez-les-ecologistes-magic-CNT000002sFUju.html
- Sandrine Rousseau (aile gauche) demande d'accélérer la désignation. Elle serait prête à rejoindre un bloc mené par Mélenchon ; c'est rapporté au conditionnel, donc non vérifié. Elle aurait dit sur franceinfo qu'une victoire de Glucksmann signifierait « la fin d'un idéal » (même source).
- Yannick Jadot soutient Glucksmann depuis le 24 août 2026 [MR, à vérifier] AFP reprise par Sud Radio, 24 août 2026 : https://www.sudradio.fr/societe/a-gauche-la-bataille-saccelere-glucksmann-et-melenchon-lorgnent-les-ecologistes. Il doit présenter pour Glucksmann les « 100 jours » d'une « révolution écologiste » (AFP, 12 octobre, lien ci-dessus).
- Selon un agrégateur, Jadot a été suspendu à titre conservatoire pour trois mois par le secrétariat exécutif des Écologistes le 25 septembre 2026, pour ce soutien. Non vérifié (W) : https://ground.news/article/greens-suspend-yannick-jadot. Une dépêche AFP titrée « Jadot suspendu temporairement des Écologistes pour son soutien à Glucksmann » a été trouvée sur Boursedirect, mais la page ne répond plus (titre seul).

### 4.3 Approches de Glucksmann et de Mélenchon depuis le 11 octobre

Glucksmann :
- Le soir de sa victoire, il déclare : « Il n'y aura pas d'accord avec LFI » [MR] Public Sénat, 11 octobre 2026 : https://www.publicsenat.fr/actualites/politique/ce-soir-la-bataille-de-france-commence-apres-sa-victoire-a-la-primaire-de-la-gauche-raphael-glucksmann-assure-que-rien-ne-le-fera-l
- Il annonce un accord avec la « gauche démocratique et républicaine », sans nommer de partenaires (même source).
- Il appelle les citoyens écologistes, humanistes et « républicains » à le rejoindre. Son équipe veut éviter de longues négociations entre partis, à la différence de Hamon en 2017 (AFP, 12 octobre, Le Petit Journal).
- Aucune proposition écrite ni rencontre datée avec la direction des Écologistes n'a été trouvée.

Mélenchon :
- Aucune déclaration ni démarche envers les Écologistes, datée du 11 au 16 octobre, n'a été trouvée.
- Le 11 octobre, Paul Vannier (LFI) juge que le PS « sort de la scène politique nationale » (LCP, 11 octobre).
- Position antérieure : le 21 août 2026, Paul Vannier déclare que les Écologistes « doivent soutenir la candidature de Mélenchon ». Il évoque un « accord de gouvernement et accord législatif » [MR, à vérifier] AFP reprise par La Gazette France, 21 août 2026 : https://www.lagazettefrance.fr/article/presidentielle-tondelier-persiste-dans-son-appel-a-l-union-lfi-attend-un-ralliement

### 4.4 Niveaux de Tondelier en octobre (point 1.2)

- Avant la primaire : 2 à 5 % (Odoxa et Toluna-Harris).
- Après la primaire : 2 à 3 % (Ifop et OpinionWay).
- Repère : Jadot a obtenu 4,63 % des exprimés en 2022 [PO] Conseil constitutionnel (dossier du 10 octobre).

### 4.5 Précédents

- 2017 : le 23 février, Jadot retire sa candidature au profit de Hamon. Le 26 février, l'accord est approuvé par 79,53 % de « oui », 15,39 % de « non » et 5,08 % de blancs. La participation n'est pas donnée [MR] Public Sénat, 26 février 2017 (lien en 3).
  - Contenu de l'accord : sécurisation des députés sortants, dont Duflot ; points de programme sur le nucléaire, Notre-Dame-des-Landes et les institutions ; liberté pour EELV de présenter des candidats face au PS dans certaines circonscriptions.
  - Délai : 3 jours entre l'annonce et l'approbation.
  - Huit jours plus tôt, 89,70 % des adhérents avaient approuvé l'ouverture de discussions (dossier du 10 octobre).
- 2022 : Jadot, désigné par la primaire écologiste de septembre 2021, est resté candidat jusqu'au premier tour (4,63 %) [PO] (dossier du 10 octobre).
- Sur 9 présidentielles de 1974 à 2022, une candidature écologiste figure sur la liste officielle 8 fois ; seule 2017 fait exception (dossier du 10 octobre ; vérifié pour 2012 et 2022 seulement).
- Accords écrits entre écologistes et socialistes : l'accord Hamon-Jadot de 2017 est vérifié (Public Sénat) [MR]. Trois autres accords sont des rappels non vérifiés, sans source lue dans cette session : l'accord PS-EELV de novembre 2011 pour 2012, la NUPES de mai 2022 (LFI, EELV, PS, PCF) et le Nouveau Front populaire de juin 2024.

---

## 5. Primaire PS - Place publique

### 5.1 Résultat du 11 octobre 2026

Glucksmann est désigné dès le premier tour. Les résultats ont été proclamés le 11 octobre peu après 18 h par Patrick Mennucci, président de la commission d'organisation [MR] LCP, 11 octobre 2026 : https://lcp.fr/actualites/primaire-socialiste-vainqueur-des-le-1er-tour-raphael-glucksmann-sera-le-candidat-de-la

| Candidat | Voix | % |
|---|---|---|
| Raphaël Glucksmann | 79 613 | 66,17 |
| Olivier Faure | 17 398 | 14,46 |
| Ségolène Royal | n. d. | 7,62 |
| Emmanuel Maurel | n. d. | 5,92 |
| Jérôme Guedj | n. d. | 5,83 |

Participation : 120 787 votants sur un corps électoral de 134 467 électeurs, après suppression des doublons, soit 89,82 % [MR] Public Sénat, 11 octobre 2026 : https://www.publicsenat.fr/actualites/politique/primaire-de-la-gauche-raphael-glucksmann-plie-le-match-et-remporte-le-scrutin-des-le-premier-tour-avec-66. Le nombre de voix de Faure vient de la dépêche AFP reprise par Le Petit Journal, 11-12 octobre 2026 [MR, à vérifier] : https://lepetitjournal.com/expat-politique/actualites/presidentielle-glucksmann-designe-des-le-premier-tour-comme-le-candidat-de-la-gauche-sociale-455938. Le second tour prévu les 16 et 17 octobre n'a pas lieu.

### 5.2 Ralliements et refus depuis le 11 octobre

Candidats battus (LCP, 11 octobre, réactions) :
- Faure : il évoque une « majorité très claire », sans soutien formel dans cet article. À Glucksmann : « Tu as su convaincre une majorité de votants » (AFP, 12 octobre). Selon l'AFP, il affirme que le PS décidera « seul » de sa stratégie législative.
- Royal se dit « très déçue ». La charte signée par les cinq candidats prévoit le soutien au gagnant.
- Maurel annonce un soutien « loyal et exigeant ».
- Guedj salue une victoire « nette, sans bavure, éclatante ».

Hors primaire :
- Hollande : non déclaré. Selon Public Sénat, il espère être « une voie de recours » d'ici janvier si Glucksmann ne crée pas de dynamique. C'est une paraphrase, sans citation directe (11 octobre, lien en 5.1). Glucksmann le dit « le bienvenu » (Public Sénat, 11 octobre). En août, l'AFP rapportait qu'il visait une annonce éventuelle en décembre [MR, à vérifier] AFP reprise par Sud Radio, 17 août 2026 : https://www.sudradio.fr/societe/presidentielle-francois-hollande-recours-toujours
- Cazeneuve : aucune déclaration postérieure au 11 octobre n'a été trouvée. Il reste candidat déclaré hors primaire depuis juillet 2026 (dossier du 10 octobre).
- Bouamrane : aucune déclaration postérieure au 11 octobre n'a été trouvée. Il est testé à moins de 1 % par OpinionWay pour CNews (13-14 octobre).
- Ruffin : il ironise sur la primaire et vise les « apparatchiks, notamment de Place publique ». Il n'annonce ni soutien ni retrait (LCP, 11 octobre). Le 9 septembre, il était présenté comme candidat déclaré [MR] LCP : https://lcp.fr/actualites/primaire-de-gauche-toujours-pret-a-y-participer-francois-ruffin-reproche-a-raphael. Ifop le teste à 2 % (12-14 octobre).
- Roussel (PCF) : aucune réaction trouvée.

### 5.3 Sondages testant Glucksmann

- Après la primaire : Glucksmann obtient 11,5 à 16 % chez Ifop (12-14 octobre) et 13 à 16 % chez OpinionWay (13-14 octobre).
- Avant la primaire : 9,5 à 10,5 % chez Odoxa et 10 à 11 % chez Toluna-Harris.
- Les variations par institut, à hypothèse comparable, sont détaillées en 1.3.
- Au second tour, OpinionWay pour CNews donne Le Pen 56 contre Glucksmann 44 (ligne non vérifiée, voir 1.2). En août, Ifop donnait 55-45 (dossier du 10 octobre).

---

## 6. Centre : Philippe et Attal (actes datés)

- 22 mai 2026 : Attal se déclare candidat (non vérifié, W, dossier du 10 octobre). Philippe est candidat déclaré depuis le 4 septembre 2024 (non vérifié, W).
- 24 août 2026 : l'entourage d'Attal affirme que Philippe « est en train de perdre son pari » [MR, à vérifier] AFP reprise par La Gazette France : https://www.lagazettefrance.fr/article/presidentielle-philippe-en-train-de-perdre-son-pari-dans-le-bloc-central-estime-l-entourage-d-attal
- 27 août 2026, sur BFMTV/RMC : Attal dit avoir proposé à Philippe un « vote de départage » si personne ne s'impose. Philippe, « à ce stade, il ne le souhaite pas », selon Attal [MR, à vérifier] AFP reprise par La Gazette France, 27 août 2026 : https://www.lagazettefrance.fr/article/attal-n-a-pas-peur-d-une-primaire-renvoie-la-responsabilite-sur-philippe
- 3 septembre 2026 : Attal déclare : « Nous proposons un vote de départage, on ne va pas faire un chifoumi ! » [MR] LCP (dossier du 10 octobre).
- 8 septembre 2026 : Philippe propose un comité des partis de la droite et du centre, avec une première réunion « autour de la Toussaint ». Attal et Retailleau refusent l'élargissement [MR] LCP et Public Sénat, 9 septembre 2026 (dossier du 10 octobre).
- 17 septembre 2026 : Attal propose des « États-Unis d'Europe » [MR] Public Sénat : https://www.publicsenat.fr/actualites/politique/gabriel-attal-veut-construire-les-etats-unis-deurope-proposition-choc-pour-relancer-lideal-europeen
- Du 1er au 16 octobre 2026 : aucun acte daté de Philippe ou d'Attal sur leur candidature ou sur un départage n'a été trouvé. Aucun retrait, aucune réunion tenue, aucun mécanisme arrêté. La réunion « autour de la Toussaint » reste à venir.
- Sondages d'octobre, hypothèses à un seul candidat du centre :
  - Philippe seul : 15 à 18 % ;
  - Attal seul : 11 à 13 % ;
  - avec les deux : Philippe 12 à 14 %, Attal 5 à 7 % (point 1.2).
  - Odoxa écrit que Philippe « est aujourd'hui de loin un bien meilleur candidat pour le centre » qu'Attal [I], ce qui est une appréciation de l'institut.

---

## 7. Incertitudes et points non trouvés

1. Octobre 2026 n'est pas clos. L'état « serré » avec la gauche devant repose sur 4 instituts, dont 2 dont le terrain précède la primaire, et dont un (Odoxa) a commencé son terrain le 24 septembre. Ifop vague 7, Elabe, Ipsos, YouGov, Cluster17 et Verian n'ont pas publié d'intentions de vote d'octobre à la date du dossier.
2. OpinionWay pour CNews : la notice contient une incohérence (Hollande au questionnaire, Glucksmann au tableau). Elle est écrite avec « verifie » : false. Pour OpinionWay pour Les Echos, l'hypothèse 1 a des étiquettes Le Pen et Zemmour inversées dans la notice ; l'inversion a été corrigée et signalée.
3. La définition du bloc de gauche dans VE-SOND exclut Hollande. Dans les hypothèses Toluna-Harris avec Hollande, la gauche est comptée par Mélenchon.
4. Les taux de base 2017 et 2022 et les effets des ralliements reposent sur l'index Wikipédia [W]. Ils sont non vérifiés, car aucun sondage n'a été recontrôlé sur une notice. La classe ne compte que 2 cycles et 23 mois. La date du retrait de Montebourg (19 janvier 2022) et celle de la victoire de Hamon (29 janvier 2017) sont des rappels.
5. Écologistes : les règles du référendum (majorité, quorum, désignation nominative) et le texte des options ne sont pas publiés. La suspension de Jadot ne repose que sur un agrégateur (W) et un titre AFP. Aucune démarche de Mélenchon envers les Écologistes depuis le 11 octobre n'a été trouvée, et aucune proposition écrite de Glucksmann non plus.
6. Primaire : le nombre de voix de Royal, Maurel et Guedj n'a pas été trouvé. Aucune déclaration de Cazeneuve, de Bouamrane ou de Roussel postérieure au 11 octobre n'a été trouvée. La position de Hollande n'est connue que par une paraphrase de Public Sénat.
7. Centre : aucun acte d'octobre. Les dates de déclaration de Philippe et d'Attal ne reposent que sur Wikipédia.
8. Second tour : les seuls duels d'octobre sont Toluna-Harris (Le Pen-Philippe 56-44, Le Pen-Mélenchon 67-33), Odoxa (53-47 et 68-32) et OpinionWay pour CNews (56-44 contre Philippe et contre Glucksmann, 68-32 contre Mélenchon, ligne non vérifiée). Aucun duel Philippe-Glucksmann, Philippe-Mélenchon ou Attal-Mélenchon n'a été trouvé en octobre.
9. Accords écologistes-socialistes antérieurs à 2017 et postérieurs (2011, NUPES 2022, NFP 2024) : rappels non vérifiés.
10. Pages non lues : dépêche AFP sur la suspension de Jadot (Boursedirect, page disparue), Reporterre (erreur d'accès), Politis (payant).

## Note de calcul ajoutée le 16 octobre 2026 (moyennes de référence du réseau)

Moyennes mensuelles calculées par scripts/etat.py, qui fait foi pour VE-SOND : hypothèses testant Philippe, chaque bloc compté par son candidat le mieux placé, moyenne des hypothèses du mois. Elles peuvent différer légèrement des moyennes de la section 1 (mode de calcul). Octobre 2026 : 9 hypothèses vérifiées testant Philippe, mois non clos.

| Mois | Hypothèses | Centre | Gauche | Droite | État |
|---|---|---|---|---|---|
| 2025-03 | 5 | 22.8 | 12.8 | 6.4 | centre |
| 2025-04 | 13 | 21.9 | 10.9 | 7.7 | centre |
| 2025-05 | 4 | 21.0 | 13.6 | 14.2 | centre |
| 2025-09 | 3 | 17.0 | 14.3 | 9.3 | centre |
| 2025-10 | 8 | 17.4 | 13.6 | 9.2 | centre |
| 2025-11 | 2 | 17.0 | 13.2 | 7.8 | centre |
| 2026-02 | 5 | 18.4 | 11.2 | 10.8 | centre |
| 2026-03 | 6 | 22.0 | 12.2 | 7.6 | centre |
| 2026-04 | 2 | 19.0 | 12.0 | 9.5 | centre |
| 2026-05 | 18 | 17.4 | 13.8 | 8.9 | centre |
| 2026-06 | 8 | 18.9 | 13.6 | 9.4 | centre |
| 2026-07 | 12 | 18.0 | 15.3 | 8.0 | centre |
| 2026-08 | 11 | 17.6 | 16.1 | 7.0 | serré |
| 2026-09 | 41 | 17.0 | 16.4 | 7.4 | serré |
| 2026-10 | 9 | 15.1 | 16.6 | 6.9 | serré |
