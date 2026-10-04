**Les six importants sont corrigés pour l'essentiel, mais la nouvelle règle de I1 introduit un défaut important.** `tests.py` et `controle_banque.py` passent.

**Nouveau défaut (important) : un cycle manqué est récompensé quand le fait survient.**
- **Défaut.** Avec un fait dans la fenêtre, la dernière prévision ne vaut que jusqu'au même jour du mois suivant son émission. Si l'auteur a manqué le cycle suivant et que le fait tombe dans ce mois, les jours entre cette date et le fait comptent pour zéro, comme une prévision certaine et juste. Sans fait, la même prévision vaut jusqu'à la prévision suivante. L'ancienne règle reportait la prévision sur le trou ; la nouvelle crée la prime.
- **Essai.** Deux prévisionnistes honnêtes identiques, l'un manquant les cycles 4 et 6 d'une fenêtre de 9 mois (10 % par mois) : 0,1490 pour le complet, 0,1448 pour l'incomplet. L'auteur incomplet gagne, à prévisions égales.
- **Scénario et sens.** Les comparateurs sont scriptés et ne manquent jamais. Si le modèle de phase 3 manque un cycle (rattrapage dépassé), le critère « le taux de base bat le modèle » est biaisé en sa faveur : sens non prudent. Si c'est l'ensemble qui manque (« le cycle passe sans ensemble direct »), le biais va vers le sens prudent.
- **Correction.** Faire valoir la dernière prévision avant un fait jusqu'au 1er du mois qui suit le fait, c'est-à-dire jusqu'au cycle prévu suivant, et non un mois après sa propre émission. J'ai simulé ce correctif : la règle reste propre (meilleur score 0,1503 pour la prévision honnête), et l'auteur incomplet est légèrement pénalisé au lieu d'être récompensé (0,1497 contre 0,1491).

## Défauts importants de la relecture 17

**I1. Correction suffisante quant à la propreté.** J'ai refait la simulation sur le nouveau `brier_pondere`. Avec un risque de 10 % par mois sur 9 mois, la prévision honnête obtient 0,149 ; réduite de 25 %, 0,157 ; gonflée de 25 %, 0,159 ; gonflée de 50 %, 0,187. À 3 % par mois, même ordre. La prévision honnête est optimale. Le défaut introduit est traité ci-dessus.

**I2. Correction suffisante.** La première prévision de cycle ne dépend pas de l'issue. Ma simulation de cette sélection donnait 9,5 % de verdicts « recalibrer » sous calibration parfaite, contre 94 % avant. Le code retient bien `cyc[0]` parmi les prévisions antérieures au fait.

**I3. Correction suffisante pour les verdicts de la section 8.6, avec un effet secondaire souhaitable.** Sans borne, les estimations k/n = 6/6 donnent 100 % à EV-C3b et une issue « pas d'avis » à 0 % pour EV-C4. Les deux questions échoient en septembre 2028 et n'entrent donc pas dans le test de 2027 ; seul le bilan descriptif de 2028 est touché. Le motif de EV-C3b propose lui-même un lissage. Mieux vaut un lissage de l'estimateur, (k + ½)/(n + 1) par exemple, qu'une borne de notation : il s'applique à l'estimation, pas à un auteur.

**I4. Correction suffisante.** `--date` fixe le test et le calcul se fait au cycle de décembre 2027. Les questions échues encore ouvertes sont publiées.

**I5 et I6. Corrections suffisantes.** Chaque critère n'a plus qu'une lecture.

## Souhaitables

1. **Z et k.** Report à la liste de la phase 3 : suffisant.
2. **`controle_banque.py`.** Suffisant. Mon essai par mutation sur une copie (seuil de EV-38 modifié sans régénération) est bien détecté.
3. **Même agent à deux passages.** L'explication est recevable : deux sessions sans mémoire sont indépendantes. Je retire la remarque.
4. **EV-17.** Maintien recevable.
5. **EV-43.** Suffisant.
6. **EV-07.** Suffisant.
7. **Texte des questions de variables.** Suffisant.
8. **Table de Student.** Suffisant.
9. **Couverture.** Report recevable.
10. **Périmètre.** Recevable.

Une remarque nouvelle, souhaitable et sans biais. Pour une question de variable, il n'y a qu'une prévision, et la valeur est en général collectée avant l'échéance. Le Brier pondéré vaut alors environ le Brier multiplié par (durée d'un mois / longueur de la période). Les horizons longs pèsent donc deux à quatre fois moins que l'horizon d'un mois dans les sommes par grappe. Le facteur ne dépend pas de l'issue et s'applique de même aux deux auteurs. Il vaut d'être mentionné dans la section 8.5, ou neutralisé en notant les questions à prévision unique sur leur Brier simple.

Il reste un important ouvert. La relecture de validation suivante ne pourra pas être propre tant qu'il n'est pas corrigé.