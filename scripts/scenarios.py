"""Scénarios de rupture codés comme interventions (feuille de route, étape 14 ; revue 2, point 14).

Usage : python scripts/scenarios.py [--tirages N] [--trajectoires N] [--ids S-01,S-02]
        Compare, pour chaque scénario de modele/reseau/scenarios.json, les prévisions du réseau avec et sans ses
        interventions (même graine, mêmes observations, mêmes preuves). Un attendu est tenu si la question bouge d'au
        moins « seuil_points » dans le sens annoncé (« ± » : dans un sens ou l'autre). Écrit
        modele/reseau/scenarios_resultats.json ; code 1 si un scénario « exige » échoue.

Un scénario exploratoire qui ne produit aucun effet signale un port ou un lien manquant : il est inscrit aux points
ouverts de modele/reseau/procedure.md, pas corrigé d'office (la structure se décide sur un défaut identifié).
"""
import json
import sys

import reseau
from commun import RACINE, lire_json


def appliquer(interventions, obs):
    """Observations et chocs du scénario, ajoutés aux observations réelles."""
    obs = json.loads(json.dumps(obs))
    chocs = []
    for k, x in enumerate(interventions):
        if x["type"] == "observation":
            for m in x["mois"]:
                obs.setdefault(x["noeud"], {})[m] = x["etat"]
        elif x["type"] == "choc":
            chocs.append({"id": f"SCEN-{k}", "ports": x["ports"], "mois": x["mois"],
                          "duree_mois": x.get("duree_mois", 3), "retenu": True})
        else:
            raise SystemExit(f"intervention inconnue : {x['type']}")
    return obs, chocs


def exprimable(sc, structure):
    """Défauts d'expression : port ou nœud inconnu, état hors des états du nœud."""
    ports = {p["id"] for p in structure.get("ports", [])}
    noeuds = {n["id"]: n for n in structure["variables_etat"] + structure["pivots"]}
    d = []
    for x in sc["interventions"]:
        if x["type"] == "choc":
            d += [f"port inconnu {p}" for p in x["ports"] if p not in ports]
        elif x["type"] == "observation":
            n = noeuds.get(x["noeud"])
            if not n:
                d.append(f"nœud inconnu {x['noeud']}")
            elif x["etat"] not in (n.get("etats") or n.get("issues") or ["oui", "non"]):
                d.append(f"état inconnu {x['etat']} pour {x['noeud']}")
    return d


def tenu(avant, apres, sens, seuil):
    d = apres - avant
    return d >= seuil if sens == "+" else d <= -seuil if sens == "-" else abs(d) >= seuil


def evaluer(tirages=40, trajectoires=100, ids=None):
    s = lire_json("modele/reseau/structure_v0.json")
    t = lire_json("modele/reseau/tables_v0.json")
    sc_all = lire_json("modele/reseau/scenarios.json")
    seuil = sc_all.get("seuil_points", 2)
    obs = reseau.observations(s)
    qs = reseau.questions_banque(s, lire_json("modele/evenements.json")["evenements"])
    chocs_reels = reseau.chocs_retenus()
    reseau.CHOCS = chocs_reels
    base = reseau.prevoir(s, t, obs, qs, tirages, trajectoires)
    out = []
    for sc in sc_all["scenarios"]:
        if ids and sc["id"] not in ids:
            continue
        r = {"id": sc["id"], "recit": sc["recit"], "exige": sc.get("exige", False), "defauts": exprimable(sc, s)}
        if r["defauts"]:
            r["tenu"] = False
            out.append(r)
            continue
        o2, ch = appliquer(sc["interventions"], obs)
        reseau.CHOCS = chocs_reels + ch
        p = reseau.prevoir(s, t, o2, qs, tirages, trajectoires)
        reseau.CHOCS = chocs_reels
        lignes = []
        for groupe, oblig in (("attendus", True), ("exploratoires", False)):
            for a in sc.get(groupe, []):
                q = f"Q-{a['question']}"
                av, ap = base.get(q, {}).get(a["issue"]), p.get(q, {}).get(a["issue"])
                ok = av is not None and ap is not None and tenu(av, ap, a["sens"], seuil)
                lignes.append({**a, "avant": av, "apres": ap, "tenu": ok, "obligatoire": oblig})
        r["resultats"] = lignes
        r["tenu"] = all(x["tenu"] for x in lignes if x["obligatoire"])
        r["ess"] = p.get("__ess__", {}).get("part")
        out.append(r)
    return {"seuil_points": seuil, "tirages": tirages, "trajectoires": trajectoires, "scenarios": out}


if __name__ == "__main__":
    a = sys.argv[1:]
    nt = int(a[a.index("--tirages") + 1]) if "--tirages" in a else 40
    ntr = int(a[a.index("--trajectoires") + 1]) if "--trajectoires" in a else 100
    ids = a[a.index("--ids") + 1].split(",") if "--ids" in a else None
    r = evaluer(nt, ntr, ids)
    (RACINE / "modele/reseau/scenarios_resultats.json").write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", "utf-8")
    ko = False
    for x in r["scenarios"]:
        print(f"{x['id']} {'tenu' if x['tenu'] else 'NON TENU'}{' (exigé)' if x['exige'] else ''} {'; '.join(x['defauts'])}")
        for l in x.get("resultats", []):
            print(f"   {l['question']} {l['issue']} {l['sens']} : {l['avant']} → {l['apres']} {'ok' if l['tenu'] else 'non'}{'' if l['obligatoire'] else ' (exploratoire)'}")
        ko |= x["exige"] and not x["tenu"]
    sys.exit(1 if ko else 0)
