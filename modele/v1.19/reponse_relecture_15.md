# Réponse à la relecture de validation 15

Noyau v1.19 ; annexe v1.7 (inchangée) ; banque v1.5 ; consigne de l'ensemble v1.5. Registre du protocole vide.

La relecture 15 relève trois défauts importants : le compteur du critère d'arrêt reste à zéro. Tous les points sont traités, sauf S12 (c), différé avec motif.

## Défauts importants

**I1. Calibration et sélection des « oui » précoces.** Corrigé.
- **Code.** `notation.py` ne retient pour la calibration que les questions échues à la date du test, quelle que soit leur issue, comme le test de valeur ajoutée. La calibration est calculée avec et sans les questions ajoutées (`calibration_8_6`, `calibration_8_6_sans_ajouts`), avec le verdict combiné.
- **Test.** `test_calibration_questions_echues` reprend votre scénario : 13 questions de fenêtre à 20 %, trois « oui » le 15 mars 2027, bilan au 30 septembre 2027. Aucune question n'est retenue. Contrôle par mutation : sans le filtre, le test échoue (trois questions retenues).
- **Texte.** Section 8.6 : questions échues à la date du test, quelle que soit leur issue ; dernière prévision de cycle avant résolution ; avec et sans ajouts (S4 traité du même coup).

**I2. Cotes et marginale non calée.** Corrigé dans le texte ; le réseau n'existe pas encore, il n'y a donc pas de code à modifier.
- **Section 4.5.** Les prévisions notées en P2a, P2b et P2c sont celles du réseau entièrement non calé : aucun nœud calé, aucune ligne de table modifiée à la suite d'une comparaison à une cote, donc aucune propagation. Elles sont enregistrées avant tout calage ; les sorties calées sont publiées à part.
- **Section 7.4.** Un écart de plus de 15 points à une référence externe est consigné et justifié, sans retouche de la table utilisée pour la notation.
- **Sections 8.3 et 8.6.** Alignées : « marginale du réseau entièrement non calé ». Le paragraphe « Limite connue » ne prétend plus qu'à cette condition qu'une question cotée ne favorise aucun des deux auteurs.

**I3. Gouvernabilité après 2026.** Corrigé, dans la banque et non dans les ajouts.
- **Deux sous-questions de censure** sur le modèle d'EV-15 : EV-15b (du 1er janvier au 2 mai 2027) et EV-15c (du 3 mai 2027 au 30 septembre 2028). Nature « survenue », questions mensuelles, source Assemblée nationale (scrutins). Leurs fenêtres étant disjointes, ce sont deux grappes distinctes de celle d'EV-15. J'ai retenu la censure plutôt que la démission du Premier ministre, pour votre motif.
- **Taux de base** (`modele/taux_base/groupe_relecture_r15.json`), sur trois classes de référence : Ve République (2 motions adoptées en 68 ans) ; Assemblée sans majorité depuis juin 2022 (1 en 4,3 ans, aucune adoption en 2025 et 2026, motions rejetées au moins jusqu'au 6 juillet 2026) ; fenêtres pré- ou post-présidentielles (0 sur 11).
  - EV-15b : 7,4 %, classe de la majorité relative, comme pour EV-15.
  - EV-15c : 4,1 %, classe de la Ve République, car la composition de l'Assemblée après 2027 n'est pas connue. La classe de la majorité relative (28 %) en est la borne haute.
- **Puissance** recalculée (voir S2).

## Souhaitables

- **S1. Fuite par la recherche web.** La consigne v1.5 exige la liste des adresses consultées (champ `adresses`). `verifier_reponse.py` rejette une réponse sans ce champ, ou qui cite le dépôt, sa page publiée ou un marché de prédiction (Polymarket, Kalshi, Metaculus, Manifold, PredictIt) ; le prévisionniste est alors relancé. Test : `test_verifier_reponse`. La liste reste déclarative : une adresse omise échappe au contrôle, ce qui est écrit en 8.6.
- **S2. Procédure de la phase 3.** Écrite en 8.6, « Conduite de la phase 3 » :
  - (a) **aveuglement** : les évaluateurs et l'opérateur travaillent sur une copie du dépôt sans les registres de prévisions ;
  - (b) **périmètre** : la liste des événements couverts est publiée au démarrage et ne se réduit pas. Un nœud retiré continue d'être prévu par sa dernière table ; une question du périmètre sans prévision du modèle est notée sur le taux de base. Le code correspondant sera écrit avec la phase 3, avant son démarrage ;
  - (c) **sensibilité** : le bilan publie, pour chaque test, le verdict refait en retirant chaque grappe tour à tour (`sans_chaque_grappe`).
- **S3. Qui est le modèle.** Le bilan contient une rubrique `bilan_8_6_modele`, qui calcule en une fois les critères pour le modèle, quel que soit l'auteur de référence demandé : valeur ajoutée contre l'ensemble direct, persistance (P2a), taux de base (P2b) avec et sans ajouts, et calibration. Chaque test porte une phrase de lecture du verdict. La multiplicité des tests est mentionnée dans la phrase sur la preuve faible.
- **S4.** Traité avec I1.
- **S5. Ancrage quotidien.** La loi des seuils et du comparateur de persistance est désormais celle de l'écart historique entre un point quotidien, pris au même jour du mois que l'ancrage, et la moyenne du mois cible (`commun.variations_ancrees`, partagée par `questions.py` et `comparateurs.py`). L'effet dépend du jour d'ancrage :
  - Brent, ancré le 29 septembre, horizon 1 : écart-type de 5,6 $ au lieu de 6,8 $, conformément à votre analyse ;
  - écart de taux, ancré le 1er octobre : 8,7 pb au lieu de 8,1 pb, car le point de départ précède alors d'un mois et demi la moyenne visée.

  Texte : section 8.4.
- **S6. Séries non collectées.** La collecte inscrit la date de la dernière collecte réussie de chaque série dans `data/historique/_collecte.json`, gelé avec le cycle. `questions.py` n'émet aucune question sur une série, ou sur sa série quotidienne d'ancrage, non collectée dans les trois jours précédant le gel (testé). Texte : section 8.2.
- **S7.** `nom` et `sous_question` sont ajoutés aux champs figés (`controle_banque.py` et section 12). La section 8.8 dit désormais que le nom, la sous-question et le critère sont transmis.
- **S8.** Section 8.7 : si la coupure vérifiée d'un évaluateur est postérieure au 1er juillet 2026, les questions résolues avant cette coupure sont écartées pour tous.
- **S9.** Le « cas ambigu » de 8.8 renvoie à la règle des délais pour l'absence de source (30 jours avec deux recherches vaines, 60 jours sinon).
- **S10. Grappes emboîtées.** Règle : fenêtres disjointes, grappes distinctes ; fenêtres qui se chevauchent ou s'emboîtent, une seule grappe. Elle est appliquée par `questions.py` (composantes par chevauchement) et testée : EV-C3a et EV-C3b forment une grappe, EV-16a et EV-16b deux. Texte : section 8.3.
- **S11. Critères** (banque v1.5) :
  - EV-19 : les deux organisations issues du NPA comptent ;
  - EV-20 : lecture du dispositif statuant sur le pourvoi de Marine Le Pen, et cassation sur un autre pourvoi rangée en « cassation totale ou partielle » ;
  - EV-07 : durée établie par le communiqué officiel, à défaut par celui de l'opérateur ou par deux agences ;
  - EV-08 : une mise en garde générale ne suffit pas ;
  - EV-38 : valeur affichée par AGSI+ le 3 février 2027, capture archivée ;
  - EV-42 : E85 exclu des essences ;
  - EV-13 : lecture à 30 jours ;
  - EV-45 : version en vigueur le 30 septembre 2028, sans effet différé.
- **S12. Couverture.**
  - (a) **Seconde série P2e** : EV-28b (Ukraine, octobre 2027 à septembre 2028) et EV-33b (UE-Israël, juillet 2027 à septembre 2028), avec la classe de référence de leur première période ramenée à la nouvelle fenêtre. Pour la Chine et les États-Unis, les indicateurs utiles dépendent de faits encore inconnus : issue de la suspension chinoise qui expire le 10 novembre 2026 (couverte par EV-32), et aucune élection fédérale avant novembre 2028. Ils passeront par la procédure d'ajout en 2027 ; P2e étant hors des critères de 8.6, ces ajouts n'affectent aucun verdict.
  - (b) **BCE** : EV-46, activation du TPI en faveur de la France (source BCE, survenue). Taux de base de 2,2 % : achats ciblés de la BCE par État-membre et par an depuis 1999.
  - (c) **Nouvelle-Calédonie** : différé. Le calendrier n'est pas stabilisé à la date de la réponse (provinciales reportées à plusieurs reprises, consultation anticipée abandonnée selon la presse, révision constitutionnelle en cours), et aucun critère ne peut être daté aujourd'hui. À réexaminer par la procédure d'ajout dès qu'une date est publiée au Journal officiel.
- **S13.** `phase1.md` renvoie aux chiffres du noyau au lieu de les recopier. Les décomptes de la banque sont mis à jour. L'étape 4 du cycle cite la consigne en vigueur (v1.5).
- **S14.** Le texte des questions mensuelles donne la période du gel à la fin du mois (testé). Section 8.1 alignée.

## Effets sur la puissance

Banque v1.5, P2b au 30 septembre 2027 : 17 grappes, 105 questions, dont 12 informatives. Puissance pour P2b seul : 17 à 19 % pour un écart de Brier de 0,02, et 27 à 36 % pour 0,04. Avec P2c : 25 à 32 % et 49 à 59 %. Bilan final de 2028 : 28 grappes, 26 questions informatives.

EV-15b et EV-15c ne comptent pas parmi les questions informatives à leur taux de base. Leur échelle dépendra des probabilités réellement prévues.

## Vérifications

- `tests.py` : dix tests conformes, dont deux nouveaux (`test_calibration_questions_echues`, `test_verifier_reponse`). Les cas S6, S10, S14 et S3 sont ajoutés à `test_regles_du_bilan`.
- `controle_banque.py` : conforme.
- `taux_base.py`, `evenements.py` et `puissance.py` ont été relancés.
