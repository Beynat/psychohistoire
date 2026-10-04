# Périmètre du modèle — analyse du 4 octobre 2026

Statut : proposition soumise à la relecture 8, puis traitée. La banque retenue est dans `modele/banque/criteres.json` ; les écarts avec cette proposition sont justifiés dans `modele/v1.11/reponse_relecture_8.md`. Ce document reste en l'état, comme trace.

Rapports sources, avec leurs sources typées : `campagne.md` (enjeux de la présidentielle) et `international.md` (moteurs internationaux). Indicateur de fiabilité (`modele/sources.md`) : 59 et 60 % de sources de rang 1 à 3. Les faits signalés « non vérifié » dans ces rapports ne servent à fixer aucun seuil.

## 1. Constat

La banque actuelle (21 événements, 3 séries de questions) est centrée sur les finances publiques, les mobilisations, les institutions et l'issue de l'élection. Elle laisse de côté ce qui domine la campagne début octobre 2026 :

1. **Le choc énergétique**, premier moteur de l'opinion. La guerre d'Iran (depuis février 2026) et le blocage d'Ormuz ont porté le Brent à 114 $ en moyenne en septembre (EIA) et l'inflation énergie en France à 20,9 % sur un an (Eurostat). Le pouvoir d'achat repasse en tête des préoccupations. Aucune question ne porte sur l'énergie.
2. **L'offre politique.** La gauche se fragmente (primaire du PS fermée, Écologistes en décembre, PCF et LFI seuls) ; deux échéances judiciaires pèsent sur les favoris (arrêt de cassation sur Marine Le Pen annoncé avant avril 2027, instruction du Havre visant Édouard Philippe). La banque n'a que l'issue finale par bloc.
3. **L'international par ses effets intérieurs** : énergie, relation transatlantique (droits de douane, défiance envers les États-Unis), Ukraine et défense (budget, troupes de réassurance), Proche-Orient (clivage à gauche, actes antisémites et antimusulmans), migrations. Seuls les taux allemands, l'écart Italie-Allemagne, l'euro-dollar et la BCE y figurent.
4. **Un défaut de la banque existante** : le critère d'EV-05 mélange des cotes de marché et des sondages avec le critère, et ne dit pas à quel bloc appartient chaque candidat. À réécrire avant le premier cycle.

## 2. Couverture des grands sujets mondiaux

| Sujet | Canal vers la France | Couverture proposée |
| --- | --- | --- |
| Iran, Ormuz, énergie | Prix, inflation, pouvoir d'achat, mobilisations, vote | Séries Brent et inflation énergie ; gazole ; stocks de gaz ; accord sur Ormuz |
| Gaza, Israël-Palestine | Clivage à gauche, ordre public, politique européenne | Actes antisémites et antimusulmans ; suspension de l'accord d'association UE-Israël ; fragmentation de la gauche. La CIJ ne statuera pas au fond dans l'horizon (ordonnance du 21 mai 2026 : duplique d'Israël au 22 mai 2029) |
| Ukraine, défense | Budget, troupes, ligne du RN sur la Russie | Cessez-le-feu ; troupes françaises en Ukraine ; crédits de défense 2028 |
| États-Unis de Trump | Exportations, OTAN, relation UE | Midterms ; suspension des préférences « Turnberry » |
| Chine | Industrie (terres rares, automobile), exportations agricoles | Prolongation de la suspension des contrôles sur les terres rares |
| Climat | Épisodes extrêmes, politique européenne | EV-09 existant ; aucun ajout |
| Migrations | Politique intérieure | Franchissements irréguliers (Frontex) |
| Afrique, Sahel | Faible effet mesurable sur l'horizon | Aucun ajout, faute de critère objectif à effet démontré |

## 3. Séries proposées (questions générées par quantiles, comme les séries existantes)

| Série | Source | État |
| --- | --- | --- |
| Brent, moyenne mensuelle ($/baril) | EIA, via FRED (DCOILBRENTEU) | Collectée (`collecte/historique.py`) |
| Inflation IPCH énergie, France (% sur un an) | Eurostat | Collectée |
| Prix moyen du gazole en France (€/l, hebdomadaire) | Bulletin pétrolier de la Commission européenne ou DGEC | À collecter |

Les stocks de gaz de l'UE (AGSI+) demandent une clé d'accès gratuite ; ils sont proposés comme événement (EV-38) plutôt que comme série.

## 4. Événements proposés

Les identifiants suivent la banque (EV-18 et suivants). Chaque critère est à relire au mot près.

**Offre politique et campagne**
- **EV-18 Écologistes.** Les adhérents des Écologistes, consultés en décembre 2026, retiennent une candidature autonome à la présidentielle plutôt qu'un ralliement. Source : résultat publié par Les Écologistes (partie prenante, seule source pour sa propre décision). Échéance : 31 décembre 2026.
- **EV-19 Fragmentation de la gauche.** Nombre de candidats, sur la liste arrêtée par le Conseil constitutionnel, investis ou soutenus par LFI, le PS, Place publique, Les Écologistes, le PCF, Debout !, LO ou le NPA. Issues : 3 ou moins ; 4 ; 5 ; 6 ou plus. Source : Conseil constitutionnel. Échéance : publication de la liste (mars 2027).
- **EV-20 Cassation Le Pen.** Issue du pourvoi de Marine Le Pen contre l'arrêt de la cour d'appel de Paris du 7 juillet 2026 au 31 mars 2027. Issues : rejet ; cassation totale ou partielle ; pas d'arrêt rendu. Source : Cour de cassation.
- **EV-21 Le Pen candidate.** Marine Le Pen figure sur la liste des candidats arrêtée par le Conseil constitutionnel. Source : Conseil constitutionnel. Échéance : mars 2027.
- **EV-22 Instruction du Havre.** Édouard Philippe est mis en examen dans l'information judiciaire sur la Cité numérique du Havre avant le 18 avril 2027. Source : communiqué du parquet ; à défaut, déclaration de son avocat. Échéance : 18 avril 2027.
- **EV-23 Participation.** Participation au premier tour (France entière, ministère de l'Intérieur). Issues : moins de 70 % ; 70 à 75 % ; 75 à 80 % ; 80 % ou plus. Échéance : 18 avril 2027.
- **EV-24 et EV-25 Enjeux.** Dans la vague de mars 2027 du baromètre Ipsos bva sur les préoccupations des Français, le pouvoir d'achat est cité par au moins 55 % (EV-24) ; l'immigration par au moins 35 % (EV-25). Source : Ipsos. Le nom exact de la série et sa périodicité sont à confirmer.
- **EV-26 Niveau du RN.** Dans la première vague de l'Enquête électorale française (Cevipof, Ipsos bva) publiée après le 1er novembre 2026, Marine Le Pen obtient moins de 31 % des intentions de vote au premier tour dans l'hypothèse principale. Source : Cevipof.

**Énergie et Moyen-Orient**
- **EV-27 Ormuz.** Avant le 31 mars 2027, les gouvernements des États-Unis et de l'Iran annoncent tous deux un accord écrit prévoyant la réouverture du détroit d'Ormuz à la navigation commerciale. Sources : Département d'État, ministère iranien des Affaires étrangères.
- **EV-38 Gaz.** Le remplissage agrégé des stockages de gaz de l'UE publié par AGSI+ pour le 1er février 2027 est inférieur à 35 %.

**Proche-Orient**
- **EV-33 Accord UE-Israël.** Avant le 30 juin 2027, le Conseil de l'UE adopte une décision suspendant tout ou partie de l'accord d'association UE-Israël. Source : Conseil de l'UE, Journal officiel de l'UE.
- **EV-34 et EV-35 Actes antireligieux.** Le bilan annuel 2026 du ministère de l'Intérieur fait état de plus de 1 320 actes antisémites (EV-34) ; de plus de 326 actes antimusulmans (EV-35), soit plus qu'en 2025. Échéance : publication du bilan (vers février 2027). À reconduire pour 2027.

**Ukraine et défense**
- **EV-28 Cessez-le-feu.** Entre le 1er octobre 2026 et le 30 septembre 2027, un cessez-le-feu général annoncé par les présidences russe et ukrainienne est en vigueur au moins 30 jours consécutifs sans être déclaré rompu par l'une d'elles.
- **EV-29 Troupes françaises.** Avant le 30 septembre 2028, l'Élysée ou le ministère des Armées annonce le déploiement de militaires français sur le territoire ukrainien, hors personnel diplomatique et attachés.
- **EV-36 Crédits de défense.** Les crédits de paiement de la mission Défense hors pensions, en loi de finances initiale pour 2028, sont d'au moins 68,3 Md€ (trajectoire de la programmation militaire actualisée, chiffre à vérifier sur le texte adopté). Source : loi de finances, Légifrance.

**États-Unis et Chine**
- **EV-30 Midterms.** À l'issue des élections du 3 novembre 2026, le Parti démocrate détient au moins 218 sièges à la Chambre des représentants (résultats certifiés). Source : Clerk of the House.
- **EV-31 Accord « Turnberry ».** Avant le 31 décembre 2027, un acte publié au Journal officiel de l'UE suspend tout ou partie des préférences tarifaires accordées aux États-Unis en application de cet accord.
- **EV-32 Terres rares.** Avant le 10 novembre 2026, le ministère chinois du Commerce annonce la prolongation de la suspension des contrôles à l'exportation sur les terres rares.

**Migrations**
- **EV-37 Frontex.** Le total 2027 des franchissements irréguliers détectés aux frontières extérieures de l'UE (données préliminaires de Frontex, janvier 2028) est inférieur au total 2026.

Chaque événement retenu après relecture reçoit, comme les autres, un taux de base estimé par trois groupes d'agents (`scripts/taux_base.py`) avant le premier cycle.

## 5. Conséquences pour le réseau (phase 3)

Les moteurs internationaux entrent comme nœuds racines exogènes, sans parent dans le réseau : énergie (mesurée par le Brent et le gaz), guerre au Moyen-Orient, guerre en Ukraine, relation transatlantique. Leurs enfants sont des nœuds français existants ou nouveaux : inflation, pouvoir d'achat, mobilisations, budget de défense, saillance des enjeux, issue de l'élection. La liste des nœuds sera fixée à l'élicitation de la phase 3 (printemps 2027), sur la base de cette banque élargie.

## 6. Règle d'ajout

Décision de Nathan (4 octobre 2026) : une erreur de périmètre repérée doit être corrigée tout de suite, pas après plusieurs mois. Proposition pour le noyau v1.11 : la banque d'événements peut recevoir des ajouts à chaque cycle, avant le gel, avec motif et taux de base ; aucun retrait ni modification de critère d'une question émise. Les ajouts n'introduisent pas de biais de comparaison, puisque tous les comparateurs répondent aux mêmes questions. La contrainte trimestrielle reste pour les nœuds du réseau, dont les tables sont estimées.
