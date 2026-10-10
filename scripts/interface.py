"""Données de l'interface v1 (feuille de route v0, bloc 7) : écrit data/interface_v1.json, lu par reseau.html.

Usage : python scripts/interface.py

Rassemble, sans rien calculer de nouveau sur les probabilités :
- la carte : pivots (date ou fenêtre), variables d'état et leur dernier état observé, liens (avec les variables et
  indicateurs qui les portent), jalons rattachés à chaque lien et leur statut ;
- le témoin et le réseau : pour chaque question du dernier cycle, la dernière prévision de chaque auteur
  (médiane de l'ensemble, réseau v0, comparateurs) et, une fois résolue, l'issue et le score de Brier ;
- l'actualité : faits suivis par le tri, avec questions concernées, stade retenu, statut et niveau de vigilance
  (règle de modele/interface/actualite.md), et faits sans question ; jamais la caractérisation proposée par
  l'agent de tri, ni la nature « vie privée » (annexe, sections 11.2 et 11.6) ;
- les échéances : fenêtres des questions de la banque et dates fixes du calendrier.
"""
import json
from datetime import date, timedelta

from commun import RACINE, lire_json, lire_jsonl


def registre_courant():
    for r in ("registre/v0.jsonl", "registre/essai_v0.jsonl"):
        if (RACINE / r).exists() and (RACINE / r).read_text("utf-8").strip():
            return r
    return None


def suffixe(reg):
    nom = reg.split("/")[-1].replace(".jsonl", "")
    return "" if nom == "protocole" else f"_{nom}"


def vigilance(f, questions_ev):
    """Règle proposée dans modele/interface/actualite.md : élevé, modéré ou faible."""
    stade = f.get("stade_retenu")
    s7 = f.get("sources_7_derniers_jours", 0)
    if stade in ("mise en cause formelle", "décision") or f.get("peut_resoudre") or s7 >= 5:
        return "élevé"
    pres = any(q.removeprefix("Q-") in questions_ev for q in f.get("concerne", []))
    if stade == "procédure engagée" or s7 >= 3 or pres:
        return "modéré"
    return "faible"


def brier(p, issue, issues):
    return round(sum(((p.get(i, 0) / 100) - (1.0 if i == issue else 0.0)) ** 2 for i in issues), 4)


def construire():
    s = lire_json("modele/reseau/structure_v0.json")
    tables = lire_json("modele/reseau/tables_v0.json") or {}
    obs = (lire_json("modele/reseau/observations.json") or {}).get("etats", {})
    ev = {e["id"]: e for e in lire_json("modele/evenements.json")["evenements"]}
    noeuds = {n["id"]: n for n in s["variables_etat"] + s["pivots"]}

    # Jalons et statuts
    defs = lire_jsonl("modele/jalons/definitions.jsonl")
    statuts = {}
    for x in lire_jsonl("modele/jalons/statuts.jsonl"):
        statuts[x["jalon"]] = x["statut"]
    auj = date.today().isoformat()
    jalons = []
    for j in defs:
        st = statuts.get(j["id"]) or ("attendu" if auj < j["fenetre"]["debut"] else "en cours" if auj <= j["fenetre"]["fin"] else "à constater")
        lien = j["lien"]
        # Jalons définis avant le découpage de la censure (structure v0.2) : rattachés à la partie de leur fenêtre.
        for ancien, (avant, apres) in {"PV-CENSURE1": ("PV-CENSURE1a", "PV-CENSURE1b")}.items():
            if ancien in lien.replace(" ", "").split("→"):
                lien = lien.replace(ancien, avant if j["fenetre"]["debut"] < "2027-01-01" else apres)
        jalons.append({"id": j["id"], "lien": lien, "observable": j["observable"], "fenetre": j["fenetre"],
                       "niveau": j["niveau"], "type": j["type"], "statut": st,
                       "rapport": round(j["vraisemblances"]["a"] / j["vraisemblances"]["b"], 2)})

    # Liens : parent → enfant ; une variable d'état ou un indicateur parent est « porté » par le lien
    liens = []
    for n in s["pivots"] + s["variables_etat"]:
        for p in n.get("parents", []):
            pid = p if isinstance(p, str) else p["id"]
            liens.append({"de": pid, "vers": n["id"], "decalage": 0 if isinstance(p, str) else p.get("decalage", 0),
                          "jalons": [j["id"] for j in jalons if j["lien"].replace(" ", "") in (f"{pid}→{n['id']}",)]})

    # Mesures : question rattachée à chaque nœud
    rattache = {}
    for q, m in s["mesures"].items():
        c = m["caracteristique"]
        for x in ([c] + c.get("elements", [])):
            if x.get("noeud"):
                rattache.setdefault(x["noeud"], []).append(q)

    pivots = []
    for n in s["pivots"]:
        d = {"id": n["id"], "nom": n["nom"], "nature": n["nature"], "issues": n["issues"],
             "questions": sorted(set(rattache.get(n["id"], []))),
             "indicateurs": [v["nom"] for k, v in sorted(s.get("indicateurs", {}).get("liens", {}).items())
                             if any(l["noeud"] == n["id"] for l in v["liens"])]}
        if n["nature"] == "daté":
            d["date"] = n["date"]
            d["date_note"] = n.get("date_note")
        else:
            d["fenetre"] = n["fenetre"]
        pivots.append(d)
    variables = [{"id": v["id"], "nom": v["nom"], "etats": v["etats"], "definition": v.get("definition"),
                  "observe": obs.get(v["id"], {}), "questions": sorted(set(rattache.get(v["id"], [])))}
                 for v in s["variables_etat"]]

    # Témoin et réseau : dernière prévision par auteur et par question
    reg = registre_courant()
    previsions, cycle = {}, None
    if reg:
        for l in lire_jsonl(reg):
            if "probabilites" not in l or "question" not in l:
                continue
            a = l.get("auteur", "")
            if a.startswith("ensemble :"):
                continue
            previsions.setdefault(l["question"], {})[a] = {"p": l["probabilites"], "emise": l["emise"],
                                                            "i80": l.get("intervalle_80")}
            cycle = l.get("origine", "").removeprefix("cycle ").split(",")[0] or cycle
    res = {}
    if reg:
        from resolution import resolutions_effectives
        res = resolutions_effectives(suffixe(reg))
    qs = {}
    for f in sorted((RACINE / "data/cycles").glob("*/questions.json")):
        for q in lire_json(str(f.relative_to(RACINE)))["questions"]:
            qs[q["id"]] = q
    lignes = []
    for qid, auteurs in previsions.items():
        q = qs.get(qid)
        if not q or q["type"] == "variable":
            continue
        r = res.get(qid)
        ligne = {"id": qid, "texte": q["texte"], "pool": q["pool"], "issues": q["issues"], "echeance": q["echeance"],
                 "auteurs": {a: v for a, v in auteurs.items()},
                 "resolution": {"issue": r.get("issue"), "date_fait": r.get("date_fait")} if r else None}
        if r and r.get("issue") in q["issues"]:
            ligne["brier"] = {a: brier(v["p"], r["issue"], q["issues"]) for a, v in auteurs.items()}
        lignes.append(ligne)
    lignes.sort(key=lambda x: x["echeance"])

    # Actualité
    rep = lire_json("data/reprise.json", {})
    faits = []
    for k, f in rep.get("faits", {}).items():
        faits.append({"fait": k, "premier_jour": f["premier_jour"], "dernier_jour": f["dernier_jour"],
                      "titres": f["titres"], "sources": f["sources_distinctes"], "concerne": f["concerne"],
                      "stade": f.get("stade_retenu"), "statut": f.get("statut"), "type": f.get("type_fait"),
                      "allegation": f.get("stade_retenu") == "allégation",
                      "vigilance": vigilance(f, ev)})
    faits.sort(key=lambda x: (x["dernier_jour"], x["titres"]), reverse=True)
    libres = sorted(({"fait": k, **v} for k, v in rep.get("non_rattaches", {}).items()
                     if v["dernier_jour"] >= (date.today() - timedelta(days=14)).isoformat()),
                    key=lambda x: -x["titres_7_derniers_jours"])[:15]

    # Échéances
    echeances = sorted(({"id": i, "nom": e["nom"], "debut": e["fenetre"]["debut"], "fin": e["fenetre"]["fin"],
                         "pool": e["pool"], "reseau": i in s["mesures"]}
                        for i, e in ev.items() if e["source_accessible"]), key=lambda x: x["fin"])
    return {"genere_le": date.today().isoformat(), "registre": reg, "cycle": cycle,
            "version_structure": s.get("version"), "version_tables": tables.get("version"),
            "codes_candidats": s.get("codes_candidats"),
            "pivots": pivots, "variables": variables, "liens": liens, "jalons": jalons,
            "questions": lignes, "actualite": {"faits": faits, "sans_question": libres,
                                               "emergences": rep.get("emergences", [])},
            "echeances": echeances}


if __name__ == "__main__":
    d = construire()
    (RACINE / "data/interface_v1.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), "utf-8")
    print(f"data/interface_v1.json : {len(d['pivots'])} pivots, {len(d['liens'])} liens, {len(d['jalons'])} jalons, "
          f"{len(d['questions'])} questions, {len(d['actualite']['faits'])} faits")
