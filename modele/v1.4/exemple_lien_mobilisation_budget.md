# Exemple de lien et de chaîne de jalons (protocole v1.4, section 10)

**Statut : illustratif.** Ce document montre la structure sur un lien réel de la piste exploratoire. Les vraisemblances ne sont pas estimées : elles le seront par les évaluateurs (section 10.6). Les fenêtres parlementaires sont à vérifier sur l'ordre du jour de l'Assemblée avant tout gel.

## Lien L-04-01 : mobilisation contre le budget → budget 2027

- **Mécanisme.** Une mobilisation d'ampleur rend la non-censure coûteuse pour le PS, sans lequel aucune censure n'est arithmétiquement possible.
- **Sens.** PV-04 « mobilisation d'ampleur » favorise PV-01 « gouvernement censuré ».
- **Probabilité du lien.** P(M | mobilisation d'ampleur) = 0,50.
- **Intensité.** Décalage de la cote de censure de δ_faible = 0,4 ou δ_forte = 1,2 en log-cotes, avec P(forte) = 0,35. Autour d'une probabilité de censure de 32 %, cela donne 41 % (faible) ou 61 % (forte).
- **Décision écartée de la chaîne.** « Le gouvernement recule sur les mesures contestées » peut pousser le budget vers l'adoption comme vers la censure. Elle devient un sous-pivot de décision, « Recul gouvernemental », de niveau 2, et non un jalon (section 10.1).

## Chaîne de jalons

| Jalon | Niv. | Type | Fenêtre | Rôle | Porte sur | a | b | Rapport si observé | Rapport si manqué |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J1. Au moins 500 établissements perturbés lors d'une journée (ministère de l'Éducation) | 3 | État (PV-04) | 5 – 16 oct. | Favorable | Nœud PV-04 | 0,70 | 0,40 | 1,8 | 0,5 |
| J2. Le PS conditionne publiquement sa non-censure au retrait d'une mesure visée par la mobilisation (APL étudiantes, gel du point d'indice) | 2 | Transmission | 5 – 27 oct. | Nécessaire | M | 0,85 | 0,25 | 3,4 | 0,2 |
| J3. Amendement supprimant la mesure APL adopté en commission des finances | 3 | Transmission | Examen en commission, à vérifier | Favorable | I | 0,60 | 0,40 | 1,5 | 0,7 |
| J4. Sondage : au moins 55 % de soutien au mouvement | 3 | Transmission | 5 – 31 oct. | Favorable | I | 0,60 | 0,35 | 1,7 | 0,6 |
| J5. Première partie du budget rejetée à l'Assemblée | 2 | Transmission | Vote de la première partie, à vérifier | Favorable | M | 0,60 | 0,30 | 2,0 | 0,6 |
| J6. Motion de censure déposée avec des signataires PS | 2 | Transmission | Après un 49.3, ou au plus tard le 15 déc. | Nécessaire | M | 0,90 | 0,30 | 3,0 | 0,14 |

Les vraisemblances a et b de J3 à J6 sont posées sachant les jalons précédents de la chaîne (section 10.4).

« Journée à plus de 500 000 manifestants » n'est pas un jalon : elle tranche PV-04 et ne peut donc servir ni à l'intensité ni à la transmission (section 10.5).

## Déroulé illustratif

| Semaine | Événement | Lien : P(M) | P(forte) | Commentaire |
| --- | --- | --- | --- | --- |
| Définition (3 oct.) | — | 0,50 | 0,35 | Jalons gelés et commités |
| 5 – 11 oct. | J1 observé | 0,50 | 0,35 | Preuve sur PV-04, pas sur le lien |
| 19 – 25 oct. | J4 observé (rapport 1,7 ; plafond hebdomadaire log 2, appliqué en entier) | 0,50 | 0,48 | L'intensité monte, la probabilité ne bouge pas |
| 26 oct. – 1er nov. | J2 en retard (racine de 0,2 = 0,45) | 0,31 | 0,48 | Demi-baisse, non plafonnée (jalon nécessaire) |
| 2 – 8 nov. | J2 manqué (0,2 remplace le retard) | 0,17 | 0,48 | Le lien s'affaiblit nettement |

Dans ce scénario, l'écart d'influence de la mobilisation sur le budget tomberait d'environ ±12 points à environ ±4 points. Sur la carte, le lien passerait en pointillé, et le prochain jalon affiché deviendrait J5.

## Registre et notation

- Chaque jalon donne une question du pool P2d, par exemple « J2 observé entre le 5 et le 27 octobre ? », dont la probabilité est calculée par le réseau à la date d'émission.
- Les six questions forment une grappe, celle du lien L-04-01.
- Chaque mise à jour ajoute des lignes au registre pour PV-04, PV-01 et les pivots en aval dont la probabilité change d'au moins 0,1 point.
