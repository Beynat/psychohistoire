"""Analyse de sensibilité du réseau (feuille de route, étape 4).

Usage : python scripts/sensibilite.py [--tirages M] [--trajectoires N] [--noeuds A,B,...] [--sortie FICHIER]

Pour chaque nœud, seuls ses paramètres sont tirés au hasard (même bruit que les prévisions : σ du nœud, au moins
0,3, en log-cotes), les autres restant aux valeurs agrégées ; les trajectoires utilisent les mêmes nombres
aléatoires d'un tirage à l'autre (même graine), pour que l'écart vienne du paramètre et non de la simulation.
L'écart-type obtenu, en points, sur chaque question rattachée mesure ce que l'incertitude de ce nœud fait à la
question (effet de premier ordre, sans interaction). Le classement des nœuds par somme de ces écarts-types sur les
questions de la banque fixe l'ordre des rondes d'élicitation. Écrit modele/reseau/sensibilite.json par défaut.
"""
import json
import math
import random
import statistics
import sys

import reseau
from commun import RACINE, lire_json


def evaluer(structure, params, obs, qs, noeuds, n, graine):
    """Probabilité de chaque question (issue « oui », ou chaque issue) pour un jeu de paramètres fixé."""
    mes = structure["mesures"]
    tm = TABLES.get("mesures", {})
    som = {q["id"]: {} for q in qs}
    for j in range(n):
        rngs = {i: random.Random(f"{graine}-{j}-{i}") for i in noeuds}
        traj = reseau.simuler(structure, params, obs, None, rngs=rngs)
        p_oui = {}
        for q in qs:
            if "composantes" in q:
                continue
            m = mes[q["evenement"]]
            d = reseau.loi(m, tm, q["evenement"], reseau.valeur(m["caracteristique"], traj, noeuds, q["fenetre"]), q["issues"])
            p_oui[q["id"]] = d.get("oui")
            for i, v in d.items():
                som[q["id"]][i] = som[q["id"]].get(i, 0.0) + v
        for q in qs:
            if "composantes" in q:
                pa, pb = (p_oui.get(c) for c in q["composantes"])
                som[q["id"]]["oui"] = som[q["id"]].get("oui", 0.0) + (pa or 0) * (pb or 0)
    return {q: {i: 100 * v / n for i, v in d.items()} for q, d in som.items()}


TABLES = None


def analyser(tirages=30, trajectoires=300, liste=None, graine=5):
    global TABLES
    s = lire_json("modele/reseau/structure_v0.json")
    TABLES = lire_json("modele/reseau/tables_v0.json")
    obs = reseau.observations(s)
    reseau.PRIORS = reseau.lois_a_priori(s, TABLES, obs)
    qs = reseau.questions_banque(s, lire_json("modele/evenements.json")["evenements"])
    noeuds = reseau.noeuds_de(s)
    base = {i: dict(t) for i, t in TABLES["noeuds"].items()}
    ref = evaluer(s, base, obs, qs, noeuds, trajectoires, graine)
    rng = random.Random(graine + 1)
    out = {}
    for nid in (liste or TABLES["noeuds"]):
        tirs = []
        for _ in range(tirages):
            pert = reseau.perturber({"noeuds": {nid: TABLES["noeuds"][nid]}}, rng)
            params = {**base, nid: pert[nid]}
            tirs.append(evaluer(s, params, obs, qs, noeuds, trajectoires, graine))
        effets = {}
        for q in qs:
            for i in ref[q["id"]]:
                if i == "non":
                    continue
                xs = [t[q["id"]].get(i, 0.0) for t in tirs]
                sd = statistics.pstdev(xs)
                if sd >= 0.5:
                    effets[f"{q['id']} {i}"] = round(sd, 1)
        par_q = {}
        for k, v in effets.items():
            qq = k.split(" ")[0]
            par_q[qq] = max(par_q.get(qq, 0), v)
        out[nid] = {"total": round(sum(par_q.values()), 1), "sigma": TABLES["noeuds"][nid].get("sigma"),
                    "effets": dict(sorted(effets.items(), key=lambda x: -x[1]))}
        print(f"{nid:13} total {out[nid]['total']:6.1f}  " + ", ".join(f"{k} {v}" for k, v in list(out[nid]["effets"].items())[:4]), flush=True)
    return {"version_tables": TABLES.get("version"), "tirages": tirages, "trajectoires": trajectoires,
            "lecture": "écart-type, en points, de chaque question quand seuls les paramètres du nœud sont tirés ; total = somme sur les questions du plus fort écart-type par question",
            "noeuds": dict(sorted(out.items(), key=lambda x: -x[1]["total"]))}


if __name__ == "__main__":
    a = sys.argv[1:]
    m = int(a[a.index("--tirages") + 1]) if "--tirages" in a else 30
    n = int(a[a.index("--trajectoires") + 1]) if "--trajectoires" in a else 300
    liste = a[a.index("--noeuds") + 1].split(",") if "--noeuds" in a else None
    sortie = a[a.index("--sortie") + 1] if "--sortie" in a else "modele/reseau/sensibilite.json"
    r = analyser(m, n, liste)
    (RACINE / sortie).write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"{sortie} écrit")
