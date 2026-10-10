# Maquette de l'organigramme (non déployée, 10 octobre 2026)

Organigramme des pivots, de gauche à droite (causes vers conséquences), mis en page par ELK (elkjs 0.9.3), destiné à remplacer la frise de `reseau.html` (étape 8 de la feuille de route `modele/feuille_de_route.md`).

Fabrication actuelle (provisoire, à intégrer aux scripts) :
1. `python scripts/carte.py` (trajectoires des pivots) ;
2. `python modele/interface/organigramme/sim_variables.py SORTIE_VE.json` (mêmes trajectoires, états des variables) ;
3. `prep.py` lit `data/carte_v0.json`, `data/interface_v1.json`, les tables, `modele/jalons/vraisemblances_v2.json` et le fichier des variables (chemin codé en dur dans le script : à paramétrer), et écrit les données de la maquette ;
4. le gabarit `gabarit.html` reçoit `__DATA__` (données) et `__ELK__` (bibliothèque, à remplacer par `<script src="https://cdn.jsdelivr.net/npm/elkjs@0.9.3/lib/elk.bundled.js">` en ligne).

Contenu : cartes (événement et probabilité), fenêtre de détail au clic (« D'où vient ce chiffre » : décomposition par la cause principale, autres facteurs, fiabilité des paramètres ; jalons à surveiller avec options avant et après), variables suivies chaque mois, liste des questions hors réseau. Les effets des jalons sont aujourd'hui calculés localement : l'étape 2 (moteur de preuve unique) les remplace.
