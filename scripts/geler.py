"""Gel des données d'un cycle (noyau, section 8.2).

Usage : python scripts/geler.py AAAA-MM-JJ [ETIQUETTE]   (étiquette du cycle, par défaut AAAA-MM)
Copie les données utilisées par le cycle dans data/cycles/<AAAA-MM>/gel/ et écrit un manifeste
avec l'empreinte SHA-256 de chaque fichier et l'heure du gel. Le commit du gel doit précéder
toute prévision du cycle ; un gel déjà fait n'est jamais réécrit.
"""
import shutil
import sys

from commun import RACINE, ecrire_json, empreinte, maintenant

A_GELER = ["data/collecte.json", "data/cotes.json", "modele/evenements.json", "modele/taux_base.json",
           "modele/correspondances_p1.json"] + sorted(
    str(p.relative_to(RACINE)) for p in (RACINE / "data/historique").glob("*.csv"))

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("usage : python scripts/geler.py AAAA-MM-JJ [ETIQUETTE]")
    cycle = sys.argv[2] if len(sys.argv) == 3 else sys.argv[1][:7]
    dest = RACINE / "data" / "cycles" / cycle / "gel"
    if (dest / "manifeste.json").exists():
        sys.exit(f"Le cycle {cycle} est déjà gelé : un gel n'est jamais réécrit.")
    fichiers = {}
    for f in A_GELER:
        src = RACINE / f
        if not src.exists():
            continue
        cible = dest / (src.name if not f.startswith("data/historique") else f"historique/{src.name}")
        cible.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, cible)
        fichiers[f] = empreinte(f)
    ecrire_json(f"data/cycles/{cycle}/gel/manifeste.json",
                {"cycle": cycle, "date_gel": sys.argv[1], "gele_le": maintenant(), "fichiers": fichiers})
    print(f"Cycle {cycle} gelé : {len(fichiers)} fichiers.")
