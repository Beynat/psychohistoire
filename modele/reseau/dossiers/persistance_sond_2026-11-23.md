# Dossier de faits : persistance de la deuxième place (état au 23 novembre 2026)

Lot L9 : VE-SOND, « deuxième place derrière le RN dans les intentions de vote ». États : centre, serré, gauche, droite. Parents : VE-POP (décalage 1 mois), PV-BLOC, PV-SOUTIEN (définitions dans noeuds.json).

Ce dossier met à jour le dossier du 16 octobre 2026 (modele/reseau/dossiers/sondages_offre_gauche_2026-10-16.md). Il ne contient aucune probabilité ni aucun avis sur l'avenir.

Rangs selon modele/sources.md :
- PO primaire officielle, I institut, MR média de référence, S spécialisée, W tertiaire, ME média engagé, MEE média d'État, PP partie prenante.
- Un fait appuyé seulement par S, W, ME, MEE ou PP est marqué « non vérifié ».
- Les notices de la Commission des sondages sont notées [PO/I] : la Commission est PO pour le dépôt, l'institut est I pour ses chiffres.
- Un chiffre d'institut connu seulement par un article de presse est noté [MR, chiffre I].

Domaines non classés, traités comme dans le dossier du 16 octobre :
- lagazettefrance.fr et lepetitjournal.com (reprises AFP) : MR « à vérifier ».
- internazionale.it (reprise d'une dépêche Reuters) : MR « à vérifier ».
- elyseescope.com (site sans rédacteur nommé ni source citée) : W.
- en.wikipedia.org : W.

Le fichier modele/sources.json n'a pas été lu (hors périmètre de la consigne). Ces classements sont donc provisoires.

Recherches web : 13. Aucun marché de prédiction ni site de paris n'a été consulté. Fichiers de travail (wikitexte, scripts, notices) : /tmp/elic23/travail_dossier/.

---

## 1. Sondages

### 1.1 Série mensuelle de VE-SOND, 2025-2026 (reprise de /tmp/elic23/serie_2026.md)

Calcul sur data/etat/sondages.jsonl (hypothèses testant Édouard Philippe, meilleur candidat de chaque bloc, moyenne simple des hypothèses du mois, sans correction), état au 23 novembre 2026 après rattrapage de la collecte d'octobre et de novembre.

| Mois | Hypothèses | RN | Centre | Gauche | Droite | Écart 2e-3e | État VE-SOND |
|---|---|---|---|---|---|---|---|
| 2025-03 | 5 | 35.2 | 22.8 | 12.8 | 6.4 | 10.0 | centre |
| 2025-04 | 13 | 32.6 | 21.9 | 10.9 | 7.7 | 11.0 | centre |
| 2025-05 | 4 | 30.8 | 21.0 | 13.6 | 14.2 | 6.8 | centre |
| 2025-09 | 3 | 33.3 | 17.0 | 14.3 | 9.3 | 2.7 | centre |
| 2025-10 | 8 | 33.3 | 17.4 | 13.6 | 9.2 | 3.8 | centre |
| 2025-11 | 2 | 35.8 | 17.0 | 13.2 | 7.8 | 3.8 | centre |
| 2026-02 | 5 | 35.8 | 18.4 | 11.2 | 10.8 | 7.2 | centre |
| 2026-03 | 6 | 35.2 | 22.0 | 12.2 | 7.6 | 9.8 | centre |
| 2026-04 | 2 | 33.0 | 19.0 | 12.0 | 9.5 | 7.0 | centre |
| 2026-05 | 18 | 33.3 | 17.4 | 13.8 | 8.9 | 3.7 | centre |
| 2026-06 | 8 | 34.9 | 18.9 | 13.6 | 9.4 | 5.2 | centre |
| 2026-07 | 12 | 34.6 | 18.0 | 15.3 | 8.0 | 2.6 | centre |
| 2026-08 | 11 | 34.1 | 17.6 | 16.1 | 7.0 | 1.5 | serré |
| 2026-09 | 41 | 33.6 | 17.0 | 16.4 | 7.4 | 0.6 | serré |
| 2026-10 | 37 | 34.7 | 14.1 | 16.5 | 6.8 | 2.4 | gauche |
| 2026-11 | 24 | 33.1 | 11.7 | 18.2 | 9.1 | 6.5 | gauche (mois en cours, 24 hypothèses au 23 nov.) |

Lecture factuelle de la série :
- 16 mois observés. État « centre » 12 fois, « serré » 2 fois (août et septembre 2026), « gauche » 2 fois (octobre et novembre 2026).
- Le bloc deuxième derrière le RN change une fois : du centre à la gauche, en octobre 2026.
- En novembre (mois non clos), le troisième bloc est le centre (11,7), devant la droite (9,1) de 2,6 points.

### 1.2 Sondages de premier tour à fin de terrain postérieure au 15 octobre 2026

Source : data/etat/sondages.jsonl, 68 lignes (hypothèses) de fin de terrain du 16 octobre au 19 novembre 2026. 67 portent « verifie » : true (notice de la Commission des sondages ou document de l'institut) [PO/I]. Une ligne porte false : Toluna-Harris du 5 novembre, hypothèse reprise d'un site espagnol (democrata.es) [W, non vérifié]. Les notices n'ont pas été relues ligne à ligne dans cette session. Une seule a été recontrôlée : Ifop pour Sud Radio, notice 10392, voir plus bas.

| Institut (commanditaire) | Fin de terrain | Hyp. | Le Pen | Mélenchon | Philippe | Glucksmann | Attal | Lisnard |
|---|---|---|---|---|---|---|---|---|
| Elabe (BFMTV, La Tribune Dimanche) | 16 oct., 13 nov. | 12 | 31-33,5 | 15-18,5 | 9,5-16,5 | 10,5-16,5 | 4-10,5 | 5,5-10,5 |
| Ifop-Fiducial (LCI, Le Figaro, Sud Radio) | 19 oct., 29 oct., 4 nov., 16 nov. | 21 | 32-38 | 15-20 | 9,5-19 | 8-18 | 4-13 | 5,5-14 |
| Toluna-Harris Interactive (M6, RTL, L'Express) | 21 oct., 5 nov., 19 nov. | 12 | 30-36 | 17-19 | 9-16 | 11-14 | 4-11 | 7-12 |
| Cluster17 (Politico) | 22 oct., 10 nov. | 7 | 27-33 | 18,5-20,5 | 8-17 | 8-14 | 2-12 | 8-10 |
| Ipsos (Le Parisien) | 22 oct. | 4 | 32-33,5 | 17 | 13-15 | 13-15,5 | 4-9,5 | 6,5 |
| OpinionWay (CNews, Europe 1, JDD ; Les Echos, Radio Classique) | 22 oct., 10 nov., 12 nov. | 6 | 31-36 | 16-17 | 11-12 | 10-13 | 3-10 | 6-12 |
| YouGov (HuffPost) | 17 nov. | 5 | 32-40 | 17-22 | 7-16 | 9-12 | 4-7 | 9-10 |

Fourchettes sur les 67 lignes vérifiées : Le Pen 27-40 ; Mélenchon 15-22 ; Philippe 7-19 ; Glucksmann 8-18 ; Attal 2-13 ; Lisnard 5,5-14. Teddy Riner est testé dans 8 hypothèses, de 2 à 5 %.

Remarques :
- Les fourchettes mélangent des hypothèses différentes : Philippe seul, Philippe avec Attal, avec ou sans Lisnard, Hollande, Riner ou Lagarde.
- Ifop pour Sud Radio (terrain du 2 au 4 novembre, notice publiée le 20 novembre) teste un « candidat unique de la droite et du centre » [PO/I] notice 10392 : https://www.commission-des-sondages.fr/notices/files/notices/2026/novembre/10392-pres-iv-ifop-sud-radio-20-novembre.pdf
  - Philippe seul : Philippe 19, Mélenchon 18, Glucksmann 13, Le Pen 37 (notice lue).
  - Retailleau seul : 14. Lisnard seul : 14. Attal seul (avec Mélenchon et Glucksmann) : 13.
  - C'est la seule hypothèse de la période où le centre devance nettement la gauche (1 point).
- Cluster17 pour Politico (10 novembre) teste Christine Lagarde : 14 dans une hypothèse sans Philippe, 8 dans une hypothèse avec Philippe (8) et Attal (2) [PO/I, ligne vérifiée du fichier]. Lagarde ne figure dans aucun bloc de la définition de VE-SOND.
- Ifop pour LCI (27-29 octobre) : Glucksmann recule « de près de 3 points » par rapport à la vague d'octobre. Mélenchon devance Philippe d'au moins 2 points dans tous les scénarios [MR, chiffre I] Public Sénat, 4 novembre 2026 : https://www.publicsenat.fr/actualites/politique/sondage-presidentielle-2027-un-second-tour-le-pen-melenchon-assure-la-droite-et-le-bloc-central-peine-a-remonter-lisnard-confirme-sa-percee

Comparaison centre et gauche par hypothèse (hypothèses avec Philippe, fin de terrain après le 15 octobre, calcul sur le fichier) :
- 47 hypothèses. La gauche devance le centre dans 43, égalité dans 1, centre devant dans 3.
- Les 3 cas où le centre est devant : Elabe du 16 octobre (2 hypothèses, +1 et +0,5) et Ifop pour Sud Radio (Philippe candidat unique, +1).
- En novembre, la droite égale ou dépasse le centre dans 6 hypothèses sur 24 : Cluster17 (1), YouGov (3), Toluna-Harris du 19 novembre (2).

Écarts systématiques entre instituts (moyennes simples des hypothèses de chaque institut, période du 16 octobre au 19 novembre) :

| Institut | RN | Mélenchon | Glucksmann | Philippe (toutes hyp.) | Écart gauche − centre (hyp. avec Philippe) |
|---|---|---|---|---|---|
| Ifop | 35,9 | 17,5 | 12,8 | 13,3 | +4,2 (15 hyp.) |
| YouGov | 34,2 | 19,2 | 10,0 | 10,0 | +9,2 (4 hyp.) |
| Toluna-Harris | 33,7 | 18,2 | 12,0 | 12,3 | +5,5 (8 hyp.) |
| OpinionWay | 33,5 | 16,2 | 11,7 | 11,8 | +4,4 (5 hyp.) |
| Ipsos | 33,1 | 17,0 | 13,9 | 14,0 | +3,0 (3 hyp.) |
| Elabe | 32,4 | 16,5 | 14,5 | 13,9 | +2,6 (8 hyp.) |
| Cluster17 | 30,7 | 19,6 | 11,2 | 13,6 | +5,6 (4 hyp.) |

Constats :
- RN : Ifop est le plus haut (35,9 en moyenne, jusqu'à 38). Cluster17 est le plus bas (30,7, jusqu'à 27). L'écart entre les deux est de 5,2 points.
- Mélenchon : Cluster17 et YouGov sont les plus hauts (19 à 20). Elabe et OpinionWay sont les plus bas (16 à 16,5).
- Glucksmann : Elabe est le plus haut (14,5). YouGov est le plus bas (10,0).
- Philippe : Elabe et Ipsos sont les plus hauts (environ 14). YouGov est le plus bas (10,0).
- Écart gauche − centre : il va de 2,6 (Elabe) à 9,2 (YouGov).
- Limite : chaque institut teste un jeu d'hypothèses différent (Attal présent ou non, Lisnard, Riner, Lagarde). Les écarts ci-dessus mêlent l'effet de l'institut et l'effet de l'hypothèse.

---

## 2. Taux de base : persistance du deuxième (cycles 1995 à 2022)

### 2.1 Classe de référence, méthode et sources

Classe : présidentielles de 1995, 2002, 2007, 2012, 2017 et 2022 (6 cycles). Premier tour : 23 avril 1995, 21 avril 2002, 22 avril 2007, 22 avril 2012, 23 avril 2017, 10 avril 2022. Pour comparaison, le premier tour de 2027 est le 18 avril (calendrier.json, CAL-T1, [PO]). L'horizon « 5 mois » de 2027 correspond donc au 18 novembre 2026.

Sources :
- 2002 à 2022 : wikitexte des pages « Opinion polling for the 2002 (… 2007, 2012, 2017, 2022) French presidential election », téléchargé le 23 novembre 2026 [W]. Exemple : https://en.wikipedia.org/wiki/Opinion_polling_for_the_2017_French_presidential_election
- 1995 : la page de sondages n'existe pas sur Wikipédia en anglais (erreur « Not Found »). Seul le tableau de la section « Opinion polls » de https://en.wikipedia.org/wiki/1995_French_presidential_election a été utilisé [W]. Il compte 23 sondages, presque tous Sofres, dont 1 à 5 par mois.
- Résultats du premier tour : lignes « election » des mêmes tableaux et section « Results » de l'article 1995 [W]. Les décisions du Conseil constitutionnel n'ont pas été relues dans cette session.
- Statut : tout ce qui suit en 2.2 à 2.4 est non vérifié (source W). Aucun sondage historique n'a été recontrôlé sur une notice ou un document d'institut.

Méthode (scripts /tmp/elic23/travail_dossier/parse_wiki.py et analyse_cycles.py) :
- Une ligne du tableau vaut une hypothèse. Les valeurs « <1 % » sont codées à la moitié.
- Fenêtre de chaque horizon : sondages dont la fin de terrain tombe à ±15 jours de la date « premier tour moins k mois ».
- Candidats : moyenne de chaque candidat sur les hypothèses de la fenêtre. Seuls les candidats testés dans au moins la moitié des hypothèses sont classés.
- Blocs : dans chaque hypothèse, le bloc est compté par son meilleur candidat, puis on fait la moyenne des hypothèses. C'est la règle de VE-SOND, sans pondération par institut.
- Blocs retenus :
  - FN/RN : Le Pen (Jean-Marie, puis Marine).
  - Centre : Bayrou, Macron, Lepage, Borloo, Morin.
  - Gauche : PS, écologistes, PCF, FG/LFI, extrême gauche, Chevènement, Taubira.
  - Droite : RPR, UMP et LR (dont Balladur, Chirac, Sarkozy, Fillon, Juppé, Pécresse), Madelin, Villepin, Boutin.
  - Hors blocs : Villiers, Dupont-Aignan, Pasqua, Mégret, Saint-Josse, Lassalle, Zemmour.
- « Deuxième » au sens de la consigne : premier = bloc ou candidat en tête (le FN/RN quand il est premier) ; deuxième = suivant.
- La méthode diffère de celle du dossier du 16 octobre (moyenne par institut, puis moyenne des instituts). Les chiffres de 2017 et 2022 peuvent donc différer légèrement.

### 2.2 Deuxième à 5, 3 et 1 mois du premier tour

Notation : candidat (score moyen). « Écart » = deuxième moins troisième, en points. n = nombre d'hypothèses dans la fenêtre.

| Cycle | Horizon (n, instituts) | 1er / 2e / 3e candidats | Écart cand. | 1er / 2e / 3e blocs | Écart blocs |
|---|---|---|---|---|---|
| 1995 | 5 mois (3, Sofres) | Delors 29,7 / **Balladur 26,0** / Chirac 15,0 | 11,0 | gauche 29,7 / **droite 26,0** / FN 9,0 | 17,0 |
| 1995 | 3 mois (2, Sofres) | Balladur 30,5 / **Jospin 18,5** / Chirac 17,5 | 1,0 | droite 30,5 / **gauche 18,5** / FN 11,8 | 6,7 |
| 1995 | 1 mois (5, Sofres) | Chirac 25,4 / **Jospin 21,2** / Balladur 19,0 | 2,2 | droite 25,4 / **gauche 21,2** / FN 12,1 | 9,1 |
| 2002 | 5 mois (5, 5 inst.) | Chirac 25,6 / **Jospin 22,6** / Chevènement 9,4 | 13,2 | droite 25,6 / **gauche 22,6** / FN 8,6 | 14,0 |
| 2002 | 3 mois (12, 6 inst.) | Chirac 24,9 / **Jospin 22,1** / Chevènement 11,2 | 10,9 | droite 24,9 / **gauche 22,1** / FN 9,2 | 12,9 |
| 2002 | 1 mois (28, 7 inst.) | Chirac 23,1 / **Jospin 20,9** / Le Pen 10,5 | 10,4 | droite 23,1 / **gauche 20,9** / FN 10,5 | 10,4 |
| 2007 | 5 mois (16, 4 inst.) | Sarkozy 33,5 / **Royal 31,4** / Le Pen 13,3 | 18,1 | droite 32,4 / **gauche 28,4** / FN 13,3 | 15,1 |
| 2007 | 3 mois (19, 7 inst.) | Sarkozy 31,9 / **Royal 28,0** / Le Pen 12,1 | 15,9 | droite 31,9 / **gauche 28,0** / FN 12,1 | 15,9 |
| 2007 | 1 mois (55, 7 inst.) | Sarkozy 29,4 / **Royal 24,9** / Bayrou 20,5 | 4,4 | droite 29,4 / **gauche 24,9** / centre 20,5 | 4,4 |
| 2012 | 5 mois (9, 7 inst.) | Hollande 31,8 / **Sarkozy 26,6** / Le Pen 17,3 | 9,3 | gauche 31,8 / **droite 26,6** / FN 17,3 | 9,3 |
| 2012 | 3 mois (37, 10 inst.) | Hollande 29,5 / **Sarkozy 24,4** / Le Pen 18,7 | 5,7 | gauche 29,5 / **droite 24,4** / FN 18,7 | 5,7 |
| 2012 | 1 mois (47, 9 inst.) | Sarkozy 28,0 / **Hollande 27,6** / Le Pen 15,9 | 11,7 | droite 28,0 / **gauche 27,6** / FN 15,9 | 11,7 |
| 2017 | 5 mois (33, 7 inst.) | Fillon 28,1 / **Le Pen 25,3** / Macron 15,1 | 10,2 | droite 27,8 / **FN 25,3** / centre 14,9 | 10,4 |
| 2017 | 3 mois (28, 6 inst.) | Le Pen 25,7 / **Fillon 21,6** / Macron 20,5 | 1,1 | FN 25,7 / **droite 21,6** / centre 20,5 | 1,1 |
| 2017 | 1 mois (69, 10 inst.) | Le Pen 25,4 / **Macron 24,9** / Fillon 18,6 | 6,3 | FN 25,4 / **centre 24,9** / droite 18,6 | 6,3 |
| 2022 | 5 mois (43, 5 inst.) | Macron 25,5 / **Le Pen 17,9** / Zemmour 15,4 | 2,5 | centre 25,5 / **RN 17,9** / droite 9,3 | 8,6 |
| 2022 | 3 mois (57, 7 inst.) | Macron 25,0 / **Le Pen 16,7** / Pécresse 16,3 | 0,4 | centre 25,0 / **RN 16,7** / droite 16,3 | 0,4 |
| 2022 | 1 mois (87, 12 inst.) | Macron 28,7 / **Le Pen 17,6** / Mélenchon 12,3 | 5,3 | centre 28,7 / **RN 17,6** / gauche 12,3 | 5,3 |

Qualifiés au second tour, avec le premier tour en % des exprimés [W, non vérifié] :
- 1995 : Jospin et Chirac. Balladur arrive troisième.
- 2002 : Chirac (19,88) et Le Pen (16,86). Jospin arrive troisième (16,18).
- 2007 : Sarkozy (31,18) et Royal (25,87).
- 2012 : Hollande (28,63) et Sarkozy (27,18).
- 2017 : Macron (24,01) et Le Pen (21,30). Fillon arrive troisième (20,01).
- 2022 : Macron (27,85) et Le Pen (23,15). Mélenchon arrive troisième (21,95).

Repères de contexte (rappels, non vérifiés) :
- 1995 : la fenêtre à 5 mois précède le renoncement de Delors (décembre 1994). Jospin n'y est pas testé.
- 2017 : la fenêtre à 5 mois chevauche la victoire de Fillon à la primaire de la droite (fin novembre 2016).

### 2.3 Décomptes

Le deuxième à 5 mois s'est-il qualifié ?
- Par candidat : 4 cycles sur 6 (Royal 2007, Sarkozy 2012, Le Pen 2017, Le Pen 2022). Les deux échecs sont Balladur en 1995 et Jospin en 2002.
- Par bloc (un candidat du bloc qualifié) : 5 sur 6. Seul échec : la gauche en 2002.

À 3 mois : 4 sur 6, par candidat comme par bloc. Les échecs sont Jospin en 2002 et Fillon (droite) en 2017.

À 1 mois : 5 sur 6, par candidat comme par bloc. Seul échec : Jospin en 2002.

Le deuxième à 5 mois est-il encore deuxième à 1 mois ?
- Par candidat : 3 sur 6 (2002, 2007, 2022).
- Par bloc : 3 sur 6 (2002, 2007, 2022).
- Dans 3 des 6 cycles, le deuxième par bloc à 5 mois est premier à 1 mois : droite en 1995, droite en 2012, FN en 2017.
- Aucun bloc deuxième à 5 mois n'est passé troisième à 1 mois. Par candidat, Balladur l'est en 1995.

Le premier à 5 mois s'est-il qualifié ? 4 sur 6. Les échecs sont Delors en 1995 (non candidat) et Fillon en 2017.

Les deux premiers candidats à 5 mois sont-ils les deux qualifiés ? 3 sur 6 (2007, 2012, 2022).

Changements de deuxième place d'un mois sur l'autre, par bloc, sur les 12 mois avant le premier tour. Les mois sans sondage sont sautés. Un changement « avec le même premier » est un échange entre deuxième et troisième ; c'est l'analogue le plus direct de VE-SOND, où le RN reste premier.

| Cycle | Mois observés | Transitions | Changements du 2e | dont même premier | dont changement de premier |
|---|---|---|---|---|---|
| 1995 | 9 (1 à 4 sondages par mois) | 8 | 2 | 0 | 2 |
| 2002 | 11 | 10 | 2 | 0 | 2 |
| 2007 | 12 | 11 | 4 | 0 | 4 |
| 2012 | 12 | 11 | 2 | 0 | 2 |
| 2017 | 11 (pas d'août 2016) | 10 | 5 | 1 (janvier à février 2017 : droite puis centre, FN premier) | 4 |
| 2022 | 12 | 11 | 3 | 2 (novembre à décembre 2021 : RN puis droite ; décembre à janvier : droite puis RN, centre premier) | 1 |
| Total | 67 | 61 | 18 (0,30 par transition) | 3 (0,05 par transition) | 15 |

Coude-à-coude, par bloc (écart de 2 points ou moins entre deuxième et troisième, moyenne mensuelle) :
- 1995, 2002, 2007 : aucun.
- 2012 : avril 2011, un mois (écart 0,4 ; droite devant le FN). La droite reste deuxième en mai (écart 2,3).
- 2017 : février 2017, un mois (écart 2,0 ; centre devant la droite, FN premier). Le centre reste deuxième en mars (écart 5,9).
- 2022 : de décembre 2021 à février 2022, trois mois (écarts 1,1, 0,5 et 1,9). Le deuxième change pendant l'épisode : droite en décembre, puis RN en janvier et février. L'épisode prend fin en mars avec le RN deuxième (écart 5,3).
- Total : 3 épisodes en 6 cycles, de 1, 1 et 3 mois, soit 5 mois sur 67 observés.
- Avec la méthode du dossier du 16 octobre (moyenne par institut), février 2017 avait un écart de 3,1 et n'était pas un coude-à-coude. L'épisode de 2022 était identique (3 mois).

Série actuelle (1.1), pour comparaison :
- Sur les 12 derniers mois (décembre 2025 à novembre 2026), 10 mois sont observés (pas de décembre ni de janvier).
- Il y a 2 changements d'état sur 9 transitions : centre puis serré (juillet-août), serré puis gauche (septembre-octobre).
- Le bloc deuxième change une fois (centre puis gauche, en octobre).
- Un coude-à-coude de 2 mois (août-septembre 2026). Il se termine avec un écart de 2,4 en octobre, puis 6,5 en novembre (mois non clos).

### 2.4 Limites de la classe de référence

- Six cycles seulement, et deux tableaux minces. 1995 ne contient presque que du Sofres, avec 2 à 5 sondages par fenêtre. 2002 compte 4 à 6 sondages par mois avant janvier 2002.
- Le FN/RN n'est premier que rarement : à 3 et à 1 mois en 2017, et dans quelques mois de 2016-2017 et du printemps 2021. Depuis le 16 octobre 2026, il est premier dans les 68 hypothèses du fichier. Le seul précédent d'un coude-à-coude derrière un FN premier est 2017 (Fillon et Macron à 3 mois, écart 1,1).
- Configurations différentes : président sortant candidat (2002, 2012, 2022), primaires (2006 PS, 2011 PS, 2016 LR et PS, 2021 EELV), retraits tardifs. Le classement en blocs est conventionnel (Bayrou au centre, Chevènement à gauche, Zemmour hors blocs).
- Le filtre « testé dans au moins la moitié des hypothèses » écarte les candidats non encore désignés. Exemple : Royal avant novembre 2006 ; le classement mensuel par candidat de 2006 n'est donc pas fiable et n'est pas donné.
- Source W (Wikipédia) : non vérifiée. Les tableaux peuvent contenir des erreurs de saisie. L'analyse automatique peut en ajouter (étiquettes, colonnes fusionnées).
- Agrégateurs : aucun agrégateur d'époque (moyennes publiées par un média ou un institut) n'a été consulté. La Commission des sondages n'a pas été consultée pour les cycles passés.

---

## 3. Faits datés depuis le 16 octobre 2026

### 3.1 Candidatures déclarées

- 9 novembre 2026 : Teddy Riner annonce sa candidature dans une vidéo et un entretien au Parisien. Slogan : « La France qu'on veut ». Interrogé sur la droite ou la gauche : « Ni l'un, ni l'autre ». Aucun parti n'est mentionné [MR] LCP, 9 novembre 2026 : https://lcp.fr/actualites/le-judoka-teddy-riner-annonce-sa-candidature-a-l-election-presidentielle-de-2027-444920 ; [MR] Public Sénat, 9 novembre 2026 : https://www.publicsenat.fr/actualites/politique/presidentielle-2027-le-judoka-teddy-riner-se-lance-dans-la-course-a-lelysee-au-milieu-dune-multitude-de-candidats
- Liste des candidats déclarés selon Public Sénat (9 novembre, même lien) [MR] :
  - Centre et droite : Philippe (septembre 2024), Attal (mai 2026), Becht, Retailleau (désigné par les adhérents LR en avril, 73,8 %), Lisnard, Bertrand (août).
  - Villepin : intention confirmée, sans candidature officialisée.
  - Le Pen (7 juillet) et Zemmour (septembre).
  - Gauche : Mélenchon (mai), Glucksmann, Tondelier, Bouamrane, Ruffin, Roussel, Batho.
  - Autres : Polony, Arthaud, Dupont-Aignan, Philippot, Asselineau, Kazib, Labib, Lalanne, Mathieu.
- Public Sénat donne 66,13 % à Glucksmann au premier tour de la primaire. Le dossier du 16 octobre donnait 66,17 % (LCP). L'écart n'est pas résolu.
- 23 octobre 2026 : Villepin dit avoir dépassé 300 signatures. Fait connu seulement par le titre d'un lien de LCP (article du 1er novembre, voir 3.2), donc non vérifié.
- Christine Lagarde : Reuters écrit qu'elle quitte la BCE le 7 février. Interrogée par Politico sur une éventuelle candidature, elle veut « retrouver ma liberté de parole » (traduction). Elle ne se déclare pas [MR, à vérifier] Reuters repris par Internazionale, 12 novembre 2026 : https://www.internazionale.it/ultime-notizie-reuters/2026/11/12/ecb-s-lagarde-would-rival-centrists-in-french-presidential-race-poll-shows
- François Hollande : non déclaré. Selon l'AFP, il repousse sa décision de décembre à janvier. Il ne veut pas se présenter contre Glucksmann. Il est autour de 7 à 8 % [MR, à vérifier] AFP reprise par La Gazette France, 4 novembre 2026 : https://www.lagazettefrance.fr/article/presidentielle-hollande-ne-lache-rien-malgre-la-victoire-de-glucksmann

### 3.2 Bloc central et droite : candidature unique, primaire, départage

- Rappel : le 10 juin 2026, le comité de liaison du bloc central constate un désaccord entre Philippe et Attal sur la primaire. Il évoque une décantation par les sondages vers octobre ou novembre [MR] Public Sénat, 10 juin 2026 : https://www.publicsenat.fr/actualites/politique/presidentielle-2027-le-comite-de-liaison-a-acte-quil-y-avait-sur-la-primaire-un-desaccord-entre-edouard-philippe-et-gabriel-attal
- 27 octobre 2026 : Yaël Braun-Pivet appelle à un candidat unique du centre et de la droite. Elle cite Gérard Larcher comme recours. Fait connu seulement par un lien de l'article LCP du 1er novembre, donc non vérifié.
- Vers le 29 octobre 2026 : Attal propose une « grande primaire des démocrates ». Les camps Philippe et Retailleau la critiquent [MR] LCP, 1er novembre 2026 : https://lcp.fr/actualites/presidentielle-2027-edouard-philippe-ne-veut-pas-de-la-primaire-de-gabriel-attal-444599
- 1er novembre 2026, sur TF1 : Philippe dit « Je ne crois pas que cette primaire aura lieu ». Il ajoute : « Au mois de février, chacun prendra ses responsabilités » [MR] LCP, même lien.
- 1er novembre 2026 : Attal juge la primaire « inéluctable ». Selon lui, aucun candidat n'est en situation d'être au second tour [MR] LCP, 16 novembre 2026 : https://lcp.fr/actualites/je-n-y-participerai-pas-edouard-philippe-accepte-une-discussion-a-droite-mais-ferme
- 6 novembre 2026 : Philippe annonce un « grand tour » des régions jusqu'à fin décembre. Il refuse primaire et débats avec ses concurrents [MR, à vérifier] AFP reprise par La Gazette France : https://www.lagazettefrance.fr/article/edouard-philippe-entame-une-tournee-des-regions-refusant-toujours-la-primaire
- Mardi 10 novembre 2026 : Retailleau écrit à Philippe, Attal et Lisnard. Il propose une primaire les 31 janvier et 7 février 2027. Attal dit qu'une primaire « s'impose ». Le porte-parole de Philippe refuse toute date [MR] LCP (AFP), 12 novembre 2026 : https://lcp.fr/actualites/presidentielle-bruno-retailleau-propose-une-primaire-les-31-janvier-et-7-fevrier-445008
- 14 novembre 2026 : Gérard Larcher, président du Sénat, invite les candidats de la droite et du centre à définir « une méthode de départage ». Il propose un ralliement à un candidat unique début 2027 [MR] LCP, 16 novembre (lien ci-dessus).
- 15 novembre 2026, au Parisien : Philippe accepte une discussion proposée par Larcher, mais pas sur une primaire : « Cette primaire, je n'y participerai pas » [MR] LCP, 16 novembre.
- 16 novembre 2026 : environ mille élus locaux demandent une primaire dans une tribune du Figaro [MR] LCP, 16 novembre.
- 17 novembre 2026 : les directeurs de campagne d'Attal, de Retailleau et de Lisnard se réunissent, sans l'équipe de Philippe. Une chaise reste vide pour elle [MR] Public Sénat : https://www.publicsenat.fr/actualites/politique/primaire-les-equipes-dattal-retailleau-et-lisnard-salignent-sur-un-vote-en-janvier-moins-sur-le-cas-deric-zemmour ; [MR] LCP, 18 novembre 2026 : https://lcp.fr/actualites/presidentielle-2027-entre-gabriel-attal-bruno-retailleau-et-david-lisnard-une-primaire
  - Pistes communes :
    - primaire ouverte à deux tours, en vote électronique ;
    - les 17 et 24 janvier, ou les 24 et 31 janvier 2027 ;
    - participation d'environ 2 euros ;
    - retrait des perdants ;
    - exclusion des alliances avec les partis extrêmes.
  - Désaccord sur Zemmour : le camp Attal y est opposé, le camp Lisnard moins catégorique.
  - Le camp Lisnard écrit qu'« aucun accord n'a été conclu à ce stade ».
  - Prochaine réunion annoncée vers les 26 ou 27 novembre.
  - Gérald Darmanin, soutien de Philippe, demande à Retailleau et Attal de se retirer (LCP).
- 18 novembre 2026 : Philippe présente son projet. Fait connu par le titre d'un article de Public Sénat lu en résultat de recherche, contenu non lu : https://www.publicsenat.fr/actualites/politique/capitalisation-suppression-de-250-000-postes-de-fonctionnaires-autonomie-des-ecoles-fin-des-35-heures-aides-pour-les-familles-edouard-philippe-presente-son-projet-massif-et
- Au 23 novembre 2026 : aucune primaire n'est arrêtée, aucun candidat du bloc central ne s'est retiré, et la discussion proposée par Larcher n'a pas de date confirmée. Philippe et Attal restent tous deux candidats (PV-BLOC : « les deux » à cette date).

### 3.3 Écologistes, Glucksmann, Mélenchon

- 18 novembre 2026, au 20 heures de France 2 : Marine Tondelier se dit prête à travailler à une coalition autour de la candidature de Mélenchon. Elle propose une semaine de discussions vers un accord programmatique, gouvernemental et législatif. Elle dit rester candidate et ne pas changer de programme [MR] Public Sénat, 19 novembre 2026 : https://www.publicsenat.fr/actualites/politique/la-main-tendue-de-marine-tondelier-a-melenchon-peut-elle-faire-imploser-les-ecologistes ; [MR, à vérifier] AFP reprise par Le Petit Journal, 18-19 novembre 2026 : https://lepetitjournal.com/expat-politique/actualites/apres-le-pas-de-tondelier-vers-melenchon-glucksmann-en-appelle-la-tradition-pro-europeenne-des
- Calendrier interne des Écologistes (Public Sénat, 19 novembre) [MR] :
  - 26 novembre : le conseil fédéral arrête les scénarios soumis aux adhérents ;
  - 30 novembre : rattachement des parlementaires au parti ;
  - 10 au 13 décembre : vote des adhérents sur trois options (candidature autonome, soutien à Mélenchon, rapprochement avec Glucksmann).
- Le texte exact des options, les règles de majorité et de quorum ne sont pas publiés à cette date.
- Yannick Jadot, rallié à Glucksmann, est « suspendu du parti » selon Public Sénat [MR] (19 novembre). Le dossier du 16 octobre ne l'appuyait que sur un agrégateur (W) ; le fait est désormais appuyé par une source MR. Jadot dénonce l'ouverture sur X.
- Réactions de LFI : Manuel Bompard y voit « une bonne nouvelle » (AFP) ; Paul Vannier une « étape importante » (Public Sénat). Le sénateur Gabriel Amard exige un accord de gouvernement avant les législatives.
- Mélenchon : aucune réaction publique au 19 novembre, selon Public Sénat [MR]. Un site sans rédacteur nommé affirme qu'il a « répondu favorablement », sans date ni citation [W, non vérifié] https://www.elyseescope.com/le-radar/jean-luc-melenchon-repond-tondelier
- Rappel : le 22 juillet 2026, dans Reporterre, Mélenchon a proposé aux Écologistes un accord « global et au carré » (présidentielle, législatives, régionales). Il leur donnait « deux ou trois mois » [MR] LCP, 23 juillet 2026 : https://lcp.fr/index%2Ephp/actualites/apres-l-heure-ce-ne-sera-plus-l-heure-melenchon-acte-la-rupture-avec-le-ps-et-presse-les
- Glucksmann, 19 novembre 2026, sur franceinfo : il juge le choix de Tondelier contraire à la tradition pro-européenne des écologistes. Il lance un appel direct aux électeurs écologistes. Son meeting de lancement est prévu le 6 décembre à Paris (AFP, lien ci-dessus).
- Des discussions avaient été engagées entre les équipes de Glucksmann et de Tondelier avant le 18 novembre. Ce fait vient d'un sénateur écologiste cité par Public Sénat, donc d'une source non nommée.
- Olivier Faure (PS) « regrette » le choix. Il reconnaît une dynamique de Mélenchon « visible à l'œil nu » (AFP, 19 novembre).
- Niveaux cités par l'AFP le 19 novembre : Tondelier environ 3 %, Glucksmann 11 à 13 %, Mélenchon près de 20 %.
- Aucune primaire ni procédure de départage n'est annoncée à gauche.

### 3.4 Popularité du président (parent VE-POP, décalage d'un mois)

- Baromètre de référence du projet (Ifop-Endrix pour L'Opinion, satisfaits), octobre 2026 : 17 %, stable par rapport à septembre (17). C'est le deuxième plus bas niveau depuis 2017. Les « très mécontents » sont 56 %. Terrain du 7 au 16 octobre, 1 951 personnes, publication le 19 octobre [I] https://www.ifopgroup.com/article/indices-de-popularite-barometre-ifop-opinion-octobre-2026/ (valeur déjà dans data/etat/popularite.jsonl). État VE-POP : « < 25 % ».
- Ifop-Endrix, novembre 2026 : non publié ou non trouvé au 23 novembre. L'URL attendue répond 404.
- Autres baromètres, mesures différentes, non substituables :
  - Ipsos BVA - CESI pour La Tribune Dimanche, octobre 2026 : jugement favorable sur l'action du président 15 % (−1), défavorable 82 % (+1) [I] https://www.ipsos.com/sites/default/files/ct/news/documents/2026-10/Ipsos-bva-CESI-La-Tribune-Dimanche-Barometre-Politique-octobre-2026-web.pdf (dates de terrain non relevées). Le baromètre de novembre n'est pas en ligne à l'URL attendue (404).
  - Elabe pour Les Echos, novembre 2026 : confiance 13 % (−4 en un mois, −11 depuis août), plus bas de ce baromètre, sous les 14 % de Hollande en novembre 2016. Terrain les 3 et 4 novembre, 1 004 personnes [MR, chiffre I] Public Sénat, 5 novembre 2026 : https://www.publicsenat.fr/actualites/politique/sondage-82-des-francais-ne-font-pas-confiance-a-emmanuel-macron-qui-bat-le-record-dimpopularite-de-francois-hollande-a-lelysee . Octobre est donc à 17 % dans ce baromètre (calcul).

---

## 4. Incertitudes et points non trouvés

1. Novembre 2026 n'est pas clos : 24 hypothèses au 23 novembre. L'état « gauche » d'octobre repose sur un écart de 2,4 points, proche du seuil de 2.
2. Une ligne de novembre (Toluna-Harris du 5 novembre) vient d'une source W et porte « verifie » : false. Les 67 autres lignes n'ont pas été relues dans cette session, sauf la notice Ifop pour Sud Radio (10392).
3. Plusieurs hypothèses récentes testent des configurations hors de la définition de VE-SOND : Lagarde (aucun bloc), Riner (aucun bloc), Hollande (exclu du bloc de gauche), « candidat unique » sans Philippe. La règle « hypothèses testant Philippe » écarte celles sans Philippe.
4. Les écarts entre instituts (1.2) mêlent effet d'institut et effet d'hypothèse. Aucun redressement n'a été fait.
5. Taux de base (section 2) : source W, non vérifiée.
   - 6 cycles, dont 1995 très mince (Sofres seul) et 2002 mince avant janvier.
   - Le FN/RN est premier seulement en 2017 (à 3 et à 1 mois).
   - Les résultats officiels n'ont pas été relus sur les décisions du Conseil constitutionnel.
   - Le seuil « testé dans la moitié des hypothèses » et le classement des blocs sont des conventions de ce dossier.
6. Les chiffres de 2017 diffèrent de ceux du dossier du 16 octobre pour février 2017 (2,0 contre 3,1), selon la méthode d'agrégation.
7. Bloc central :
   - Le contenu du projet présenté par Philippe le 18 novembre n'a pas été lu.
   - La date de la discussion proposée par Larcher n'est pas connue.
   - Les déclarations de Braun-Pivet (27 octobre) et de Villepin (23 octobre) ne sont connues que par des titres de liens.
   - Aucune réaction de Bertrand à la primaire, postérieure au 16 octobre, n'a été trouvée. Public Sénat dit seulement qu'il exclut d'y prendre part.
8. Écologistes :
   - Le texte des trois options du vote de décembre, les règles de majorité et de quorum ne sont pas publiés au 23 novembre (conseil fédéral le 26 novembre).
   - La réaction propre de Mélenchon à l'offre de Tondelier n'a pas été trouvée dans une source PO, I ou MR.
9. Popularité : le baromètre Ifop-Endrix de novembre n'a pas été trouvé ; le baromètre Ipsos de novembre non plus. Les dates de terrain d'Ipsos d'octobre n'ont pas été relevées.
10. Primaire PS - Place publique : l'écart entre 66,13 % (Public Sénat) et 66,17 % (LCP) n'est pas résolu.
