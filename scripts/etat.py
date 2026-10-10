"""États mensuels des variables du réseau, tirés des séries de data/etat/ (feuille de route v0, bloc 3).

Usage : python scripts/etat.py [--ecrire]
Affiche, mois par mois, l'état de VE-POP, VE-SOND, VE-RN, VE-MOBIL et VE-LYCEE selon les définitions de
modele/reseau/structure_v0.json ; avec --ecrire, complète modele/reseau/observations.json (les états déjà
inscrits ne sont pas modifiés). VE-ECART vient de la collecte nocturne (data/historique/ecart_FR_DE_pb.csv).

Sondages : moyenne des hypothèses du mois qui testent Édouard Philippe (hypothèse principale), corrigée de
l'erreur historique des sondages de premier tour par bloc (CORRECTION, en points). La correction vaut 0 en v0 :
elle est à estimer sur 2017 et 2022 (écart entre la moyenne du dernier mois et le résultat) à une passe ultérieure.
"""
import json
import statistics
import sys

from commun import RACINE, lire_json, lire_jsonl

CORRECTION = {"RN": 0.0, "centre": 0.0, "gauche": 0.0, "droite": 0.0}
BLOCS = {"Le Pen": "RN", "Bardella": "RN", "Philippe": "centre", "Attal": "centre", "Mélenchon": "gauche",
         "Glucksmann": "gauche", "Ruffin": "gauche", "Tondelier": "gauche", "Roussel": "gauche", "Faure": "gauche",
         "Retailleau": "droite", "Lisnard": "droite", "Wauquiez": "droite", "Bertrand": "droite"}


def bloc(nom):
    return next((b for k, b in BLOCS.items() if k in nom), None)


def etats():
    out = {}
    for p in lire_jsonl("data/etat/popularite.jsonl"):
        v = p.get("president")
        if v is not None:
            out.setdefault("VE-POP", {})[p["mois"]] = "< 25 %" if v < 25 else "25-35 %" if v <= 35 else "> 35 %"
    parmois = {}
    for s in lire_jsonl("data/etat/sondages.jsonl"):
        if any("Philippe" in k for k in s["scores"]):
            parmois.setdefault(s["date_fin_terrain"][:7], []).append(s["scores"])
    for m, liste in parmois.items():
        rn = statistics.mean(max(v for k, v in sc.items() if bloc(k) == "RN") for sc in liste if any(bloc(k) == "RN" for k in sc))
        rn += CORRECTION["RN"]
        out.setdefault("VE-RN", {})[m] = "< 30 %" if rn < 30 else "30-35 %" if rn <= 35 else "> 35 %"
        meilleur = {}
        for sc in liste:
            for b in ("centre", "gauche", "droite"):
                vals = [v for k, v in sc.items() if bloc(k) == b]
                if vals:
                    meilleur.setdefault(b, []).append(max(vals) + CORRECTION[b])
        moy = {b: statistics.mean(v) for b, v in meilleur.items()}
        if moy:
            out.setdefault("VE-SOND", {})[m] = max(moy, key=moy.get)
    for j in lire_jsonl("data/etat/mobilisation.jsonl"):
        m = j["date"][:7]
        man, eta = j.get("manifestants_interieur"), j.get("etablissements_perturbes_education")
        if man is not None:
            e = "forte" if man > 500000 else "modérée" if man >= 200000 else "calme"
            o = out.setdefault("VE-MOBIL", {})
            o[m] = max(o.get(m, "calme"), e, key=["calme", "modérée", "forte"].index)
        if eta is not None:
            e = "forte" if eta >= 1000 else "modérée" if eta >= 300 else "calme"
            o = out.setdefault("VE-LYCEE", {})
            o[m] = max(o.get(m, "calme"), e, key=["calme", "modérée", "forte"].index)
    return out


if __name__ == "__main__":
    e = etats()
    for v, d in sorted(e.items()):
        print(v, " ".join(f"{m}:{s}" for m, s in sorted(d.items())[-6:]))
    if "--ecrire" in sys.argv:
        f = "modele/reseau/observations.json"
        o = lire_json(f) or {"etats": {}}
        for v, d in e.items():
            for m, s in d.items():
                if m >= "2026-10":
                    o["etats"].setdefault(v, {}).setdefault(m, s)
        (RACINE / f).write_text(json.dumps(o, ensure_ascii=False, indent=1), "utf-8")
        print("observations complétées")
