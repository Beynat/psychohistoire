Je récupère la v1.11 au tag indiqué et je lis les pièces avant de rendre la relecture 9.

**Verdict.** La banque réécrite est nettement meilleure : critères propres, sources nommées, EV-05 par candidat et en P1, date du fait présente dans toute la chaîne. Il reste quatre défauts importants, dont deux viennent des corrections elles-mêmes : le taux de base s'effondre à l'approche de l'échéance pour les événements constatés à date fixe, et le seuil de 40 grappes de la section 8.6 n'est plus atteignable avec la nouvelle définition des grappes. Cette relecture n'est donc pas sans défaut important.

J'ai lu le noyau au tag `protocole-v1.11` (commit `8d79001`), les 49 critères, les taux de base et les scripts. J'ai exécuté les tests et généré une banque pour un gel au 1er novembre sur une copie du dépôt.

## 1. Suivi de la relecture 8

| Point | Jugement | Motif |
|---|---|---|
| 1.1 Périmètre | Suffisante | Les six manques sont couverts (EV-39 à EV-45, confiance des ménages). |
| 1.1 International en pool P2e | Encadrement suffisant | Descriptif, hors critères 8.6. Deux critères à reprendre (EV-28, EV-32, section 2). |
| 1.2 EV-18 à EV-38 | Suffisante | Retraits et réécritures conformes. |
| 1.3 EV-05 | Suffisante | Issues par personne, référence Polymarket inscrite au registre (vérifié par exécution). |
| 2.1 Sources | Suffisante | Règle au noyau, primaire pour ses seuls actes, critère d'indépendance éditoriale. Reste : `cour-de-cassation.fr` et `moodys.com`, sources de résolution de la banque, ne sont pas classés. |
| 2.2 Règle d'ajout | Suffisante dans le texte | Rien ne vérifie le plafond de cinq ni l'antériorité au gel, et un ajout peut reprendre un identifiant existant. |
| 2.3 Nœuds racines | Suffisante | |
| G1 Critères transmis | Suffisante | Seul `critere` part aux prévisionnistes. |
| G2 Date du fait | Suffisante | Deux résidus (section 4, souhaitables). |
| G3, G4 | Suffisantes | |
| Souhaitables | Suffisantes | Le changement de grappes a une conséquence non traitée (H2). |
| Affirmations douteuses | Suffisantes | |

## 2. Critères

La plupart sont résolubles tels quels. Ceux qui ne le sont pas, au mot près :

| Critère | Problème | Correction |
|---|---|---|
| EV-C2 Outre-mer | « Collectivité d'outre-mer » désigne en droit les seules collectivités de l'article 74 : ni les Antilles, ni Mayotte, ni la Nouvelle-Calédonie. Un couvre-feu pour mineurs ou après un cyclone compterait. | « Département, région ou collectivité d'outre-mer, ou Nouvelle-Calédonie » ; couvre-feu général, pour motif d'ordre public. |
| EV-28 Cessez-le-feu | La durée minimale a disparu : une trêve générale de 32 heures comme celle d'avril 2026 résoudrait « oui ». | « Sans terme fixé, ou d'au moins 30 jours ». |
| EV-42 Carburants | « Abaisse le tarif de l'accise sur le gazole » inclut une baisse sur le gazole non routier des agriculteurs ou des pêcheurs. | « Tarif normal applicable au gazole routier ou aux essences ». |
| EV-39 Mobilisation | Le ministère ne publie pas ce chiffre : il le donne aux agences. | Source : « chiffre du ministère de l'Intérieur rapporté par deux agences ». |
| EV-36 Défense | Rien n'est prévu si aucun projet de loi n'est déposé au 31 octobre 2027. | Ajouter l'issue ou dire « non ». |
| EV-43 Cohabitation | Le critère compte aussi un Premier ministre de coalition, issu d'un parti allié qui avait son candidat. | Renommer « Premier ministre issu d'un parti concurrent au premier tour ». |
| EV-40 Second tour | Cas d'une élection acquise au premier tour, ou d'un retrait entre les deux tours. | Une phrase. |
| EV-08 Ingérence | « Visant l'élection » n'exige pas que la publication nomme le scrutin. | « Qui désigne expressément l'élection de 2027 comme cible ». |
| EV-13, EV-23 | Chiffre de mi-journée ou final ; Intérieur ou Conseil constitutionnel. | Nommer une seule valeur. |
| EV-17 | « Le parti qui a investi » au singulier. | Préciser en cas d'investitures multiples. |
| EV-20 | La non-admission du pourvoi n'a pas d'issue. | La ranger avec « rejet ». |

**Issues possiblement acquises au 1er novembre :**
- **EV-32.** Le rapport international évoque une prolongation de la trêve au sommet de fin septembre. Si elle est confirmée, la réponse « non » est connue, mais ne se résoudra que le 31 mars.
- **EV-01.** Moody's statue le 23 octobre.
- **EV-15, EV-39.** Le budget est en séance à partir du 13 octobre.
- **EV-08.** Une publication de VIGINUM peut intervenir à tout moment.

L'étape 1 bis traite les quatre derniers cas. EV-32 lui échappe.

**Compatibilité avec la section 8.8.** Oui pour tous, sauf EV-39 tant que sa source n'est pas réécrite.

## 3. Taux de base

**Les classes retenues sont défendables comme lignes de base naïves.** Trois remarques :
- **EV-41.** Les présences de Philippe et d'Attal sont combinées comme indépendantes, alors qu'elles sont liées (un seul candidat du centre est plausible). L'hypothèse est écrite ; elle gonfle « les deux » à 41 %, quand le marché donne 9 %.
- **EV-20.** 78 % pour « pas d'arrêt » contredit le calendrier annoncé par la Cour. C'est acceptable pour un taux de base, à condition de ne pas le lire comme une prévision.
- **Entrées périmées.** `taux_base.json` garde EV-05 par blocs et EV-10 retiré.

**EV-45.** Le point ouvert est correctement signalé, pas encore traité.
- De mémoire, la loi de financement pour 2026 décale le calendrier d'un trimestre pour les générations 1964 à 1968 et laisse 64 ans à partir de 1969. La génération 1968 serait donc à 63 ans et 9 mois de façon durable. À vérifier sur Légifrance, comme vous le prévoyez.
- Si c'est exact, le critère est mal choisi : le statu quo donne « oui » sans qu'il se passe rien, et la question ne dit pas si le nouvel exécutif touche à la réforme.
- Je recommande de porter le critère sur une génération non concernée par la suspension (1970, à 64 ans aujourd'hui). « Oui » signifierait alors un abaissement voté.

## 4. Nouveaux défauts

Aucun bloquant.

### Importants

**H1. Le taux de base est faux pour les événements constatés à date fixe.**
- **Constat.** `comparateurs.py` ramène tout taux de base à la fenêtre restante par un risque constant. Calculé sur vos fichiers :

| Événement | Taux sur la fenêtre | Taux ramené, un mois avant l'échéance |
|---|---|---|
| EV-40a Le Pen au second tour | 30 % | 3 % |
| EV-45 Âge légal | 87,5 % | 11 % |
| EV-17 Majorité | 66,7 % | 4,3 % |
| EV-36 Défense | 73,3 % | 9,6 % |

- **Problème.** Le risque constant vaut pour un événement qui peut survenir à tout moment (censure, attentat), pas pour une issue constatée un jour donné. Une vingtaine d'événements de la nouvelle banque sont de ce second type. Le comparateur devient absurde à l'approche de l'échéance, et l'écart de l'ensemble au taux de base (section 8.4) perd son sens.
- **Correction.** Un champ explicite par événement, « survenue » ou « constat à date », et pas de conversion pour le second.

**H2. Le seuil de 40 grappes n'est plus atteignable.**
- **Constat.** Avec une grappe par événement, la banque compte 32 grappes en P2b. Treize seulement sont closes au 30 septembre 2027, toutes avant le premier tour. La section 8.6 dit encore que « les 40 grappes devraient être atteintes vers septembre 2027 », avec une puissance de 55 à 68 %. `data/puissance.json` et la liste de contrôle datent de l'ancienne définition.
- **Problème.** Le verdict tombera à la date butoir, sur 13 grappes closes plus les arcs de la phase 3, avec une puissance bien plus faible qu'annoncé. « Grappe résolue » n'est pas défini quand les questions mensuelles d'un événement sont résolues mais pas sa fenêtre. Ce changement de grappes venait de ma relecture 8 ; sa conséquence n'a pas été tirée.
- **Correction.** Recalculer la puissance sur la banque réelle et réécrire le paragraphe « Calendrier attendu ». Définir la grappe résolue. Fixer le verdict à la date butoir avec le nombre de grappes attendu, ou repousser la butée.

**H3. La banque n'est pas protégée contre la modification.**
- **Constat.** Le workflow surveille `ajouts.jsonl`, pas `criteres.json`. `evenements.json` est régénéré à chaque exécution.
- **Problème.** La règle « aucune modification du critère d'une question émise » ne repose sur aucun contrôle. Un critère réécrit après émission déplacerait la cible sans laisser de trace visible.
- **Correction.** Après le premier gel, faire échouer le contrôle si un critère déjà gelé change. Les gels portent déjà l'empreinte de `evenements.json`. Les corrections des critères de la section 2 doivent donc être faites avant le 1er novembre.

**H4. Cinq critères ambigus** (EV-C2, EV-28, EV-42, EV-39, EV-45) : voir sections 2 et 3. Ils se corrigent en une phrase chacun, mais avant émission.

### Souhaitables

- **Date du fait pour une issue « non ».** Rien ne dit quelle date porter quand l'événement n'a pas eu lieu. Règle à écrire : la fin de la fenêtre.
- **Brier pondéré dans le temps.** Il court jusqu'à l'échéance, même après le fait. Pour une dégradation de note survenue en novembre 2026, la dernière prévision serait comptée jusqu'en septembre 2028. L'arrêter à la date du fait.
- **Ajouts.** Vérifier par script le plafond de cinq, l'antériorité au gel et l'unicité des identifiants.
- **Exception au gel.** Les sections 8.8 et 12 sont cohérentes entre elles. La section 12 pourrait dire que `criteres.json` est figé au premier gel, ce qui lève toute ambiguïté avec H3.
- **Indicateur des sources.** La détection des sources non lues dépend des mentions du rapport (18 trouvées, 26 comptées à la main) : le dire dans la sortie du script.

## 5. Critère d'arrêt

**Cette relecture n'est pas sans défaut important** : aucun bloquant, quatre importants (H1 à H4). Le compteur reste à zéro.

Les quatre se corrigent sans toucher à la méthode : un champ par événement, un paragraphe du noyau à recalculer, un contrôle à ajouter, cinq phrases de critères.

## Ce qui est solide

1. La banque couvre maintenant ce qui décide le scrutin : qualification, candidatures, réponse aux prix, mobilisation résoluble, et la période qui suit l'élection.
2. La date du fait est appliquée de la proposition à la notation, et les tests passent.
3. Les taux de base donnent leurs classes, leurs sources et leurs incertitudes, y compris quand elles renversent le résultat.