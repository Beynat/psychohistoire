"""Données de la carte (feuille de route, bloc 10) : écrit data/carte_v0.json, lu par reseau.html.

Usage : python scripts/carte.py [--tirages N] [--trajectoires N]

Tire des trajectoires du réseau v0 avec le moteur (scripts/reseau.py, mêmes tables, observations et faits retenus que
les prévisions du registre) et les écrit sous forme compacte, pour que la page calcule elle-même, sans nouvelle
estimation : la probabilité de chaque issue sur une fenêtre choisie, le chemin le plus probable, le chemin vers une
issue choisie et l'influence de chaque lien. Rien n'est écrit au registre : la carte est une lecture du réseau, pas
une prévision notée.

Codage d'une trajectoire : une chaîne d'un caractère par pivot, dans l'ordre de « pivots ».
- pivot daté : rang de l'issue (0, 1, …) ;
- pivot « à tout moment » : rang du mois de survenue en base 36 (0 = octobre 2026), « - » s'il ne survient pas.
Variables d'état : répartition des états par mois, sur l'ensemble des trajectoires.
"""
import json
import random
import sys

import reseau
from commun import RACINE, lire_json

COURT = {
    "PV-NOTE": "Note dégradée", "PV-PDE": "Procédure déficit durcie", "PV-TPI": "Achats de la BCE (TPI)",
    "PV-CENSURE1a": "Censure d'ici fin 2026", "PV-CENSURE1b": "Censure janv.-mai 2027", "PV-BUDGET": "Loi de finances 2027",
    "PV-GOUV": "Départ du Premier ministre", "PV-DISSOL1": "Dissolution avant l'élection", "PV-AUDIENCE": "Audience en cassation",
    "PV-POURVOI": "Arrêt de cassation", "PV-ECOLO": "Choix des écologistes", "PV-BLOC": "Candidatures du centre",
    "PV-GAUCHE": "Candidats de gauche", "PV-LEPEN": "Candidature Le Pen", "PV-DUEL": "Second tour",
    "PV-VAINQ": "Président élu", "PV-DISSOL2a": "Dissolution en mai-juin 2027", "PV-DISSOL2b": "Dissolution après juin 2027", "PV-MAJOR": "Majorité absolue",
    "PV-CENSURE2": "Censure après l'élection",
}
LIBELLE_OUI = {
    "PV-NOTE": "dégradation", "PV-PDE": "durcissement", "PV-TPI": "achats", "PV-CENSURE1a": "censure",
    "PV-CENSURE1b": "censure", "PV-GOUV": "départ", "PV-DISSOL1": "dissolution", "PV-AUDIENCE": "audience tenue",
    "PV-DISSOL2a": "dissolution", "PV-DISSOL2b": "dissolution", "PV-CENSURE2": "censure",
}
LIBELLE_NON = {
    "PV-NOTE": "note maintenue", "PV-PDE": "pas de durcissement", "PV-TPI": "pas d'achats", "PV-CENSURE1a": "pas de censure",
    "PV-CENSURE1b": "pas de censure", "PV-GOUV": "reste en fonctions", "PV-DISSOL1": "pas de dissolution",
    "PV-AUDIENCE": "pas d'audience", "PV-DISSOL2a": "pas de dissolution", "PV-DISSOL2b": "pas de dissolution", "PV-CENSURE2": "pas de censure",
}
NOMS = {"RN": "RN", "PHI": "Philippe", "ATT": "Attal", "MEL": "Mélenchon", "GLU": "Glucksmann", "RET": "Retailleau",
        "LIS": "Lisnard", "AUT": "autre", "AUTRE": "autre duel"}


def libelle_issue(pid, issue):
    if issue == "oui":
        return LIBELLE_OUI.get(pid, "oui")
    if issue == "non":
        return LIBELLE_NON.get(pid, "non")
    if pid == "PV-DUEL":
        return NOMS["AUTRE"] if issue == "AUTRE" else " – ".join(NOMS.get(c, c) for c in issue.split("-"))
    if pid == "PV-VAINQ":
        return NOMS.get(issue, issue)
    return issue


def construire(tirages=100, trajectoires=40, graine=20261010):
    s = lire_json("modele/reseau/structure_v0.json")
    tables = lire_json("modele/reseau/tables_v0.json")
    obs = reseau.observations()
    reseau.FAITS = reseau.faits_retenus()
    rng = random.Random(graine)
    pivots = s["pivots"]
    ve = [v["id"] for v in s["variables_etat"]]
    codes, comptes = [], {v: [dict() for _ in reseau.MOIS] for v in ve}
    for _ in range(tirages):
        params = reseau.perturber(tables, rng)
        for _ in range(trajectoires):
            t = reseau.simuler(s, params, obs, rng)
            c = []
            for p in pivots:
                x = t[p["id"]]
                if p["nature"] == "daté":
                    c.append(str(p["issues"].index(x[-1])))
                else:
                    k = next((k for k, v in enumerate(x) if v == "oui"), None)
                    c.append("-" if k is None else "0123456789abcdefghijklmnopqrstuvwxyz"[k])
            codes.append("".join(c))
            for v in ve:
                for k, e in enumerate(t[v]):
                    comptes[v][k][e] = comptes[v][k].get(e, 0) + 1
    n = len(codes)
    variables = []
    for v in s["variables_etat"]:
        variables.append({"id": v["id"], "nom": v["nom"], "etats": v["etats"],
                          "observe": obs.get(v["id"], {}),
                          "par_mois": [[round(100 * comptes[v["id"]][k].get(e, 0) / n, 1) for e in v["etats"]]
                                       for k in range(len(reseau.MOIS))]})
    sortie = []
    for p in pivots:
        d = {"id": p["id"], "nom": p["nom"], "court": COURT.get(p["id"], p["nom"]), "nature": p["nature"],
             "issues": p["issues"], "libelles": [libelle_issue(p["id"], i) for i in p["issues"]],
             "parents": [{"id": reseau.pid(x), "decalage": reseau.dec(x)} for x in p.get("parents", [])],
             "hypotheses": tables["noeuds"].get(p["id"], {}),
             "indicateurs": [{"id": k, "nom": v["nom"], "mecanisme": l.get("mecanisme")}
                             for k, v in sorted(s.get("indicateurs", {}).get("liens", {}).items())
                             for l in v["liens"] if l["noeud"] == p["id"]]}
        if p["nature"] == "daté":
            d["date"] = p["date"]
            if p.get("date_note"):
                d["date_note"] = p["date_note"]
        else:
            d["fenetre"] = p["fenetre"]
        if p.get("conditionnelle"):
            d["conditionnelle"] = p["conditionnelle"]
        if p.get("exclusions"):
            d["exclusions"] = p["exclusions"]
        sortie.append(d)
    return {"version_structure": s.get("version"), "version_tables": tables.get("version"),
            "mois": reseau.MOIS, "tirages": tirages, "trajectoires_par_tirage": trajectoires, "graine": graine,
            "pivots": sortie, "variables": variables, "codes": codes,
            "codes_candidats": s.get("codes_candidats")}


if __name__ == "__main__":
    a = sys.argv[1:]
    nt = int(a[a.index("--tirages") + 1]) if "--tirages" in a else 100
    ntr = int(a[a.index("--trajectoires") + 1]) if "--trajectoires" in a else 40
    d = construire(nt, ntr)
    (RACINE / "data/carte_v0.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), "utf-8")
    print(f"data/carte_v0.json : {len(d['codes'])} trajectoires, {len(d['pivots'])} pivots")
