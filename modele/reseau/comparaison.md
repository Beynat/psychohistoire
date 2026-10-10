# Comparaison pré-enregistrée : réseau contre témoin (étape 6)

Écrite le 10 octobre 2026, avant le premier cycle v0 (1er novembre 2026) et avant toute résolution d'une question prévue par le réseau. Elle ne change plus ; un changement ultérieur est une nouvelle version, journalisée, qui ne s'applique qu'aux cycles suivants.

## Ce que l'on compare

La question de fond : une décomposition structurée (le réseau) prévoit-elle mieux qu'un jugement global (l'ensemble direct de cinq modèles) ? Et les passes de correction rapportent-elles quelque chose ?

Auteurs comparés, deux à deux :
1. « réseau v0 » (courant, corrigé par les passes) contre « ensemble direct » ;
2. « réseau v0 gelé » (version témoin figée à la fin du bloc 1) contre « ensemble direct » ;
3. « réseau v0 » contre « réseau v0 gelé » : gain des passes.

## Périmètre

Seules les questions prévues par les deux auteurs d'une paire, au même cycle (période commune, départ commun ; noyau, section 8.5) : pour le réseau, les questions rattachées (mesures de `structure_v0.json`) et les conjointes. Aucun score global mêlant questions rattachées et non rattachées n'est publié pour le réseau. Le pool PR (questions rapides) est comparé à part.

## Statistique

- Score : Brier pondéré dans le temps (noyau, section 8.5 ; `scripts/notation.py`), Brier multi-issues pour les questions à plusieurs issues. Le score logarithmique est publié en complément, sans verdict.
- Différence appariée par question (auteur A − auteur B), sommée par grappe (grappes figées à la première émission).
- Test : permutation des signes des grappes (exacte jusqu'à 16 grappes, 20 000 tirages au-delà), seuil unilatéral de 10 % dans chaque sens : trois verdicts (A meilleur, B meilleur, non concluant). Écart moyen par question et intervalle à 80 % par rééchantillonnage des grappes (`test_grappes`).
- Analyse de robustesse : le même test sans chaque grappe tour à tour.

## Calendrier et décision

- Premier bilan descriptif au cycle de février 2027 (questions rapides et premières questions résolues), sans verdict si moins de 10 grappes.
- Bilan de la comparaison 3 (gain des passes) à la mi-2027 : si le réseau courant ne fait pas mieux que le réseau gelé (verdict « non concluant » ou « gelé meilleur »), Nathan décide du maintien du rythme des passes.
- Les questions encore ouvertes à la date d'un bilan sont publiées avec lui.

## Ce qui est interdit

Aucune passe ne lit les prévisions de l'ensemble ou des comparateurs sur une question ouverte. Le choix des questions comparées ne dépend d'aucun score. Les prévisions notées sont celles émises ; un recalcul par une version ultérieure n'est jamais noté.
