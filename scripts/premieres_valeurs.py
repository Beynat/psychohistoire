"""Journal des premières valeurs collectées (noyau, section 8.8 ; relecture 13, L1).

Usage : python scripts/premieres_valeurs.py
Pour chaque série de VARIABLES (scripts/commun.py), écrit dans data/premieres_valeurs.jsonl, en ajout
seul, chaque période qui apparaît pour la première fois dans data/historique : série, période, valeur,
date de collecte. Une révision ultérieure de la série n'y change rien. scripts/resolution.py résout une
question de variable sur cette première valeur, et prend sa date de collecte comme date du fait.
Lancé par la collecte nocturne, après historique.py et webstat.py.
"""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from commun import RACINE, VARIABLES, serie

JOURNAL = RACINE / "data" / "premieres_valeurs.jsonl"


def lire():
    vus = {}
    if JOURNAL.exists():
        for l in JOURNAL.read_text("utf-8").splitlines():
            if l.strip():
                d = json.loads(l)
                vus.setdefault((d["serie"], d["periode"]), d)
    return vus


def mettre_a_jour(maintenant=None):
    t = maintenant or datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")
    vus = lire()
    neuves = []
    for nom in VARIABLES:
        try:
            pts = serie(nom)
        except FileNotFoundError:
            continue
        for p, v in pts:
            if (nom, p) not in vus:
                neuves.append({"serie": nom, "periode": p, "valeur": v, "collecte_le": t})
    if neuves:
        with JOURNAL.open("a", encoding="utf-8") as f:
            for d in neuves:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
    return neuves


if __name__ == "__main__":
    n = mettre_a_jour()
    print(f"{len(n)} première(s) valeur(s) inscrite(s) dans {JOURNAL.relative_to(RACINE)}")
