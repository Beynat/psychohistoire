"""Contrôle de la banque d'événements (noyau, sections 8.8 et 12 ; relecture 9, H3).

Usage : python scripts/controle_banque.py   (code de sortie 1 en cas d'erreur)
1. Après le premier gel d'un cycle réel (étiquette AAAA-MM à partir de 2026-11), un événement déjà gelé
   ne change plus : critère, issues, fenêtre, nature, pool, accessibilité, questions mensuelles et
   source de résolution doivent être identiques, dans modele/evenements.json, à leur valeur dans le
   PREMIER gel où l'événement apparaît (relecture 10, I3). Seuls les ajouts sont permis.
3. Aucun gel de cycle réel tant que modele/statut.json n'est pas « définitif » (relecture 11, S1).
4. Gels : l'empreinte de chaque fichier gelé est égale à celle inscrite dans son manifeste
   (relecture 10, S5).
2. Ajouts (modele/banque/ajouts.jsonl) : identifiants uniques (entre eux et avec criteres.json), champ
   « ajoute_le » présent, au plus cinq ajouts entre deux gels successifs.
"""
import json
import re
import sys
from datetime import datetime

from commun import RACINE, empreinte, lire_json

CHAMPS = ("critere", "issues", "fenetre", "nature", "pool", "source_accessible", "mensuelle", "source_resolution",
          "acte", "evenement", "taux_base_mode", "reference_externe",   # relecture 13, S3
          "nom", "sous_question")   # texte remis aux prévisionnistes (relecture 15, S7)
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
    statut = lire_json("modele/statut.json", {"definitif": False})
    if gels and not statut.get("definitif"):
        erreurs.append(f"gel du cycle réel {gels[0][0]} présent alors que le protocole n'est pas déclaré définitif (noyau, section 12)")
    premiers = {}
    for et, _ in gels:
        for e in lire_json(f"data/cycles/{et}/gel/evenements.json")["evenements"]:
            premiers.setdefault(e["id"], (et, e))
    for i, (et, e) in premiers.items():
        a = actuels.get(i)
        if a is None:
            erreurs.append(f"{i} : gelé au cycle {et}, absent de la banque (retrait interdit)")
            continue
        for c in CHAMPS:
            if e.get(c) != a.get(c):
                erreurs.append(f"{i} : champ « {c} » modifié depuis son premier gel (cycle {et})")
    # Taux de base figés au premier gel de chaque événement (relecture 12, S3).
    tb_actuel = lire_json("modele/taux_base.json", {"questions": {}})["questions"]
    tb_premier = {}
    for et, _ in gels:
        for i, q in (lire_json(f"data/cycles/{et}/gel/taux_base.json") or {"questions": {}})["questions"].items():
            tb_premier.setdefault(i, (et, q.get("utilisee")))
    for i, (et, u) in tb_premier.items():
        if i in tb_actuel and tb_actuel[i].get("utilisee") != u:
            erreurs.append(f"{i} : taux de base modifié depuis son premier gel (cycle {et})")
    for et, m in gels:
        for src, emp in m.get("fichiers", {}).items():
            nom = src.split("/")[-1]
            copie = f"data/cycles/{et}/gel/" + (f"historique/{nom}" if src.startswith("data/historique") else nom)
            if not (RACINE / copie).exists():
                erreurs.append(f"{copie} : fichier gelé absent")
            elif empreinte(copie) != emp:
                erreurs.append(f"{copie} : empreinte différente de celle du manifeste")
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
