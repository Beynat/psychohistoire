"""Rapport d'écarts du réseau (feuille de route, étape 7 ; revue 2, section 4.5, point 5).

Usage : python scripts/ecarts.py [REFERENCE] [--tirages N] [--trajectoires N] [--seuil POINTS]
    Compare les prévisions des questions de la banque rattachées au réseau entre la version de référence
    (REFERENCE : un commit git, HEAD par défaut) et la copie de travail : structure, tables et calendrier de la
    référence contre ceux de la copie, même moteur (copie de travail), mêmes observations et preuves, même graine.
    Affiche les écarts d'au moins SEUIL points (2 par défaut), triés. À joindre à chaque entrée du journal qui
    modifie le réseau.
"""
import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import preuves as pv
import reseau
from commun import RACINE, lire_json


def version(ref, chemin):
    r = subprocess.run(["git", "show", f"{ref}:{chemin}"], cwd=RACINE, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"{chemin} introuvable dans {ref}")
    return json.loads(r.stdout)


def prevoir(structure, tables, calendrier, nt, ntr):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(calendrier, f, ensure_ascii=False)
    reseau.CHEMIN_CALENDRIER = f.name
    reseau._PROFILS.clear()
    qs = reseau.questions_banque(structure, lire_json("modele/evenements.json")["evenements"])
    jour = date.today().isoformat()
    p = reseau.prevoir(structure, tables, reseau.observations(structure), qs, nt, ntr, preuves=pv.preuves_notees(jour))
    reseau.CHEMIN_CALENDRIER = "modele/reseau/calendrier.json"
    reseau._PROFILS.clear()
    Path(f.name).unlink()
    return p, qs


def ecarts(ref="HEAD", nt=100, ntr=100, seuil=2.0):
    a, qs = prevoir(*(version(ref, f) for f in reseau.FICHIERS_RESEAU), nt, ntr)
    b, _ = prevoir(*(lire_json(f) for f in reseau.FICHIERS_RESEAU), nt, ntr)
    out = []
    for q in qs:
        for i, v in b.get(q["id"], {}).items():
            if i in ("i80", "es", "non"):
                continue
            x = a.get(q["id"], {}).get(i)
            if x is not None and abs(v - x) >= seuil:
                out.append((abs(v - x), q["id"], i, x, v))
    return sorted(out, reverse=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    nt = int(args[args.index("--tirages") + 1]) if "--tirages" in args else 100
    ntr = int(args[args.index("--trajectoires") + 1]) if "--trajectoires" in args else 100
    seuil = float(args[args.index("--seuil") + 1]) if "--seuil" in args else 2.0
    opts = {"--tirages", "--trajectoires", "--seuil"}
    libres = [x for k, x in enumerate(args) if not x.startswith("--") and (k == 0 or args[k - 1] not in opts)]
    ref = libres[0] if libres else "HEAD"
    r = ecarts(ref, nt, ntr, seuil)
    print(f"Écarts d'au moins {seuil} points entre {ref} et la copie de travail ({nt} × {ntr}) :")
    for _, q, i, x, v in r:
        print(f"  {q} {i} : {x} → {v} ({v - x:+.1f})")
    if not r:
        print("  aucun")
