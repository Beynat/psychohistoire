Bonjour,

La relecture 7 avait clos le processus sur la méthode (noyau v1.10, annexe v1.1). Avant le premier cycle du 1er novembre 2026, je vous demande une huitième relecture, d'une nature différente : elle porte sur le **fond**, c'est-à-dire sur ce que le modèle prévoit, en plus de la méthode. Même cadre : critique scientifique, exhaustive et sans complaisance.

Ce qui l'a motivée : en préparant le premier cycle, nous avons constaté que la banque d'événements ignore presque tout l'international et le choc énergétique, alors qu'une présidentielle se joue largement sur ces sujets. Une source engagée a aussi été citée comme un fait dans une analyse, ce qui a conduit à une méthode de fiabilité des sources.

Dépôt : https://github.com/Beynat/psychohistoire. Le noyau (tag `protocole-v1.10`) et l'annexe (tag `annexe-phase3-v1.1`) sont inchangés.

Pièces à lire :
- **Analyse du périmètre** : `modele/analyse/2026-10/synthese.md`, avec ses deux rapports sources (`campagne.md`, `international.md`, sources typées en fin de document) ;
- **Banque actuelle** : `modele/evenements.json` (21 événements) et `scripts/commun.py` (séries) ;
- **Fiabilité des sources** : `modele/sources.md`, `modele/sources.json`, `scripts/sources.py` ;
- **Exécution** : `modele/controle/cycle_mensuel.md`, `modele/controle/tri.md`, `scripts/tri.py`, `scripts/verifier_reponse.py`, `modele/consigne_ensemble.md` (v1.3) ;
- **Journal** : `modele/journal.md`, dont les lignes du 4 octobre après la relecture 7 (essai d'un cycle planifié et corrections).

Je vous demande, dans l'ordre :

1. **Fond.**
   - Pour une année de présidentielle, le périmètre proposé couvre-t-il les sujets qui comptent ? Que manque-t-il, que faut-il retirer ?
   - Pour chacun des événements EV-18 à EV-38 : le critère est-il résoluble sans ambiguïté, sur la source indiquée et dans l'horizon ? L'événement apporte-t-il une information, ou est-il quasi certain, redondant ou sans effet sur la France ?
   - La réécriture du critère d'EV-05 (bloc de chaque candidat) : quelle formulation recommandez-vous ?
2. **Méthode.**
   - La méthode de fiabilité des sources : catégories, critères de classement, règles d'usage, indicateur. Les règles d'usage sont-elles compatibles avec la section 8.8 (résolution) et la section 8.9 (données arrivées en cours de cycle) ? Faut-il les inscrire au noyau ?
   - La règle d'ajout proposée (section 6 de la synthèse) : ajouts à la banque à chaque cycle, avant le gel, sans retrait ni modification d'une question émise. Le protocole prévoit aujourd'hui des ajouts à la seule analyse trimestrielle. La proposition crée-t-elle un biais, et comment l'encadrer ?
   - L'entrée des moteurs internationaux comme nœuds racines exogènes en phase 3 (section 5 de la synthèse).
3. **Nouveaux défauts** dans les pièces d'exécution modifiées depuis la relecture 7, classés en bloquants, importants et souhaitables, avec constat, problème et correction proposée.

Les faits d'actualité postérieurs à votre propre information viennent des rapports joints ; leurs sources sont citées et typées, et ceux qui n'ont pu être recoupés y sont signalés. Merci de signaler toute affirmation qui vous paraît douteuse.

Merci.
