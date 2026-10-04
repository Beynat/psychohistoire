"""Contrôle de la banque d'événements (noyau, sections 8.8 et 12 ; relecture 9, H3).

Usage : python scripts/controle_banque.py   (code de sortie 1 en cas d'erreur)
1. Après le premier gel d'un cycle réel (étiquette AAAA-MM à partir de 2026-11), un événement déjà gelé
   ne change plus : critère, issues, fenêtre, nature et pool de chaque identifiant présent dans le
   dernier gel doivent être identiques dans modele/evenements.json. Seuls les ajouts sont permis.
2. Ajouts (modele/banque/ajouts.jsonl) : identifiants uniques (entre eux et avec criteres.json), champ
   « ajoute_le » présent, au plus cinq ajouts entre deux gels successifs.
"""
import json
import re
import sys
from datetime import datetime

from commun import RACINE, lire_json

CHAMPS = ("critere", "issues", "fenetre", "nature", "pool")
PREMIER_CYCLE = "2026-11"


def gels_reels():
    out = []
    for d in sorted((RACINE / "data" / "cycles").glob("*/gel/manifeste.json")):
        et = d.parent.parent.name
        if re.fullmatch(r"\d{4}-\d{2}", et) and et >= PREMIER_CYCLE:
            out.append((et, lire_json(str(d.relative_to(RACINE)))))
    return out


def controler():
    erreurs = []
    actuels = {e["id"]: e for e in lire_json("modele/evenements.json")["evenements"]}
    gels = gels_reels()
    if gels:
        et, _ = gels[-1]
        figes = lire_json(f"data/cycles/{et}/gel/evenements.json")["evenements"]
        for e in figes:
            a = actuels.get(e["id"])
            if a is None:
                erreurs.append(f"{e['id']} : gelé au cycle {et}, absent de la banque (retrait interdit)")
                continue
            for c in CHAMPS:
                if e.get(c) != a.get(c):
                    erreurs.append(f"{e['id']} : champ « {c} » modifié depuis le gel du cycle {et}")
    base = [e["id"] for e in lire_json("modele/banque/criteres.json")["evenements"]]
    f = RACINE / "modele/banque/ajouts.jsonl"
    ajouts = [json.loads(l) for l in f.read_text("utf-8").splitlines() if l.strip()] if f.exists() else []
    ids = base + [a.get("id") for a in ajouts]
    doublons = sorted({i for i in ids if ids.count(i) > 1})
    if doublons:
        erreurs.append(f"identifiants en double : {doublons}")
    bornes = [datetime.fromisoformat(m["gele_le"]) for _, m in gels]
    for a in ajouts:
        if "ajoute_le" not in a:
            erreurs.append(f"{a.get('id')} : champ « ajoute_le » absent")
    dates = [datetime.fromisoformat(a["ajoute_le"]) for a in ajouts if "ajoute_le" in a]
    intervalles = list(zip([None] + bornes, bornes + [None]))
    for debut, fin in intervalles:
        n = sum(1 for d in dates if (debut is None or d > debut) and (fin is None or d <= fin))
        if n > 5:
            erreurs.append(f"{n} ajouts entre deux gels (maximum 5)")
    return erreurs


if __name__ == "__main__":
    e = controler()
    print("Banque conforme." if not e else "Banque NON CONFORME :\n- " + "\n- ".join(e))
    sys.exit(1 if e else 0)
