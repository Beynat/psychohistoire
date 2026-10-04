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
           "modele/correspondances_p1.json", "data/historique/_collecte.json"] + sorted(
    str(p.relative_to(RACINE)) for p in (RACINE / "data/historique").glob("*.csv"))

if __name__ == "__main__":
    sys.argv = [a for a in sys.argv if a != "--essai"] + (["--essai"] if "--essai" in sys.argv else [])
    if len([a for a in sys.argv if a != "--essai"]) not in (2, 3):
        sys.exit("usage : python scripts/geler.py AAAA-MM-JJ [ETIQUETTE]")
    args = [a for a in sys.argv if a != "--essai"]
    cycle = args[2] if len(args) == 3 else args[1][:7]
    # Le gel est daté du jour réel d'exécution (noyau, section 8.8 ; relecture 13, S11), sauf cycle d'essai.
    import re
    from datetime import date
    if re.fullmatch(r"\d{4}-\d{2}", cycle) and sys.argv[1] != date.today().isoformat() and "--essai" not in sys.argv:
        sys.exit(f"La date de gel {sys.argv[1]} n'est pas celle du jour ({date.today().isoformat()}).")
    dest = RACINE / "data" / "cycles" / cycle / "gel"
    if (dest / "manifeste.json").exists():
        sys.exit(f"Le cycle {cycle} est déjà gelé : un gel n'est jamais réécrit.")
    fichiers = {}
    for f in A_GELER:
        src = RACINE / f
        if not src.exists():
            # Un fichier manquant fait échouer le gel (audit interne, v1.24) : sinon un script lirait le fichier
            # courant, postérieur au gel.
            sys.exit(f"Gel impossible : {f} manquant.")
        cible = dest / (src.name if not f.startswith("data/historique") else f"historique/{src.name}")
        cible.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, cible)
        fichiers[f] = empreinte(f)
    ecrire_json(f"data/cycles/{cycle}/gel/manifeste.json",
                {"cycle": cycle, "date_gel": sys.argv[1], "gele_le": maintenant(), "fichiers": fichiers})
    print(f"Cycle {cycle} gelé : {len(fichiers)} fichiers.")
