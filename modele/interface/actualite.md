# Volet actualité — attentes (à travailler avec la v1 de l'interface)

Exprimées par Nathan le 4 octobre 2026. Hors protocole : c'est l'affichage de ce que le tri et l'annexe (section 11.2) produisent déjà.

Le volet doit présenter clairement :
1. **Les ajouts quotidiens** : les faits triés du jour (regroupés par fait, pas par titre), avec leur caractérisation (nature, stade, appui) et leur source.
2. **Ce sur quoi ils peuvent influer** : questions concernées (champ `concerne`), questions qu'ils pourraient résoudre (champ `decision`), et, à partir de la phase 3, jalons et nœuds rattachés.
3. **Un niveau de vigilance** (important ou peu important), descriptif, sans effet sur les probabilités.

Proposition de règle pour le niveau de vigilance, à valider :
- **Élevé** : stade « mise en cause formelle » ou « décision » ; ou fait qui peut résoudre une question ; ou reprise d'au moins cinq sources distinctes en une semaine sur un fait de nature pénale liée à la fonction.
- **Modéré** : stade « procédure engagée » ; ou allégation reprise par au moins trois sources distinctes ; ou fait qui concerne une question de P1 ou de P2b liée à la présidentielle.
- **Faible** : allégation peu reprise, réaction, fait sans question concernée.

Le niveau évolue avec le fait (nouvelle étape, reprise, réexamen, classement « retombé ») et l'historique reste visible.

Données disponibles : `data/tri/AAAA-MM.jsonl` (décisions, caractérisation), `data/reprise.json` (reprise par fait), `data/veille.json` (titres), `modele/evenements.json` (questions).
