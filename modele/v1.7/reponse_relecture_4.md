# Réponse à la relecture 4 (protocole v1.6 → v1.7)

Relecture : `relecture_4.md`. Protocole révisé : `../protocole.md`.
Légende : **accepté**, **accepté en partie** (avec limite explicite), **rejeté** (avec motif).

La relecture ne relève aucun défaut bloquant et cinq importants. Les cinq sont acceptés, ainsi que les souhaitables, à une adaptation près sur la protection de branche. Conformément au gel (section 12), la v1.7 ne contient que des corrections demandées en relecture.

## Défauts importants

| Point | Décision | Correction |
| --- | --- | --- |
| E1 Critère de direction mal centré | Accepté | Les critères 10.11 et 11.7 utilisent Z = Σ d (y − p) / √(Σ d² p (1 − p)), au seuil unilatéral de 10 %, à 40 mises à jour résolues. Le test de signe est conservé pour la variante « donnée arrivée ensuite » (11.7). |
| E2 Porte d'activation et facteur k | Accepté | Un registre fantôme (`registre/fantome.jsonl`) enregistre chaque semaine les probabilités qu'auraient les nœuds avec les jalons actifs. L'activation est décidée quand Z est significatif sur les mises à jour fantômes résolues (au moins 30). k est estimé par régression logistique de l'issue sur le log-rapport proposé, avec la log-cote avant en décalage. En attendant, k = 0,5, déclaré arbitraire. Sections 10.4 et 10.6. |
| E3 Un jalon inactif fait taire un fait décisif | Accepté | Tant que les jalons sont inactifs, un jalon observé ou manqué est renvoyé à la section 11 comme un fait ordinaire. Ses vraisemblances gelées ne servent qu'au registre fantôme. Section 10.5. |
| E4 Banque d'événements et résolution | Accepté | Nouvelle section 8.8 : fichier `modele/evenements.json` fixé avant le 1er novembre à partir du balayage v1 ; résolution par script pour les séries, sur source primaire officielle pour les événements ; deux agents en cas d'ambiguïté, puis un troisième ; annulation pour tous les comparateurs si le désaccord persiste ou si la source manque 30 jours après l'échéance. |
| E5 La correction du biais fausse le critère 8.6 | Accepté | La correction s'applique au modèle et à l'ensemble direct, et les critères de la section 8.6 sont jugés sur les estimations non corrigées. Sections 8.4 et 8.6. |

## Souhaitables

| Point | Décision | Correction |
| --- | --- | --- |
| Seuil d'application | Accepté | Cinq évaluateurs par défaut, sur au moins trois modèles. Plancher d'erreur type égal au plancher de dispersion. Amplitude minimale : pas de mise à jour si le rapport réduit est compris entre 0,8 et 1,25. Sept évaluateurs et plafond de 10 pour un fait très diagnostique. Section 11.4. |
| Alignement 11.3 et 11.4 | Accepté | Le cas d se fait en un seul tour, sans montrer la ligne actuelle. |
| Test 8.7 | Accepté | Choix mécanique des captures (texte de la question, liste fixe de pages à la date d'ouverture) et au moins 50 questions. |
| Couples (a, b) | Accepté | Trois couples : précédent observé, précédent manqué, précédent non résolu ou invalidé (et premier jalon). Section 10.2. |
| Intensité faible ou forte | Accepté | Un jalon de transmission porte sur la présence du mécanisme ou sur sa force. Section 10.2. |
| Contrôle des registres | Accepté en partie | Le contrôle couvre désormais les décisions de tri. Définitions et statuts des jalons sont deux journaux séparés en ajout seul. Sur la protection de branche, la poussée forcée et la suppression seront interdites (réglage fait par Nathan). **Limite :** un contrôle obligatoire ne bloquerait pas les poussées faites avec les droits d'administrateur, qui sont ceux de ce projet. Le contrôle reste donc détectif : un échec est visible publiquement et se corrige par erratum. Section 12. |
| Tri | Accepté | Un fichier de décisions par mois (`data/tri/AAAA-MM.json`), lu par la collecte. |
| Date du scrutin | Accepté | « Second tour » au lieu d'une date, en section 5.2. |
| Piste exploratoire | Accepté | Une ligne d'erratum signale que P-005 et PV-08 ont été estimées sur un niveau de 120 pb non vérifié. |
| README du registre | Accepté | Champs alignés sur la section 0. |

## Faisabilité de la phase 1

**Accepté.** La liste de contrôle `modele/controle/phase1.md` est complétée :
- fichier d'événements et script de résolution ;
- historique long des séries ;
- collecte des cotes externes avec volume et écart entre offre et demande ;
- taux de base des comparateurs ;
- protection de branche ;
- cycle à blanc mi-octobre sur la piste exploratoire.

## Question pour la relecture 5

Le seuil d'application à cinq évaluateurs, avec plancher d'erreur type et amplitude minimale, est-il maintenant correctement réglé ? Laisse-t-il passer une proportion acceptable de faits sans effet, sans rendre la couche inerte ?
