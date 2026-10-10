"""Tables du réseau v0 : gabarit d'élicitation, contrôle d'une réponse, agrégation (feuille de route v0, bloc 4).

Usage :
    python scripts/tables.py gabarit SORTIE.json        gabarit à remplir par un évaluateur
    python scripts/tables.py verifier REPONSE.json      contrôle d'une réponse (code 1 si non conforme)
    python scripts/tables.py agreger R1.json R2.json ... [--version TEXTE]
                                                        écrit modele/reseau/tables_v0.json

Ce qu'un évaluateur donne, nœud par nœud (jamais une probabilité mensuelle) :
- variable d'état : pour chaque état du mois précédent, la loi de l'état du mois suivant, parents à leur état de
  référence ; pour chaque autre état d'un parent, des multiplicateurs sur le poids des états d'arrivée ;
- pivot daté : la loi de ses issues, parents à leur état de référence (ou une loi par état du parent
  « conditionnelle ») ; des multiplicateurs par état de parent ;
- pivot « à tout moment » : la probabilité de survenue sur toute sa fenêtre, parents de référence ; un
  multiplicateur sur le risque par état de parent ;
- mesure non exacte : les probabilités de sa table ;
- « direct » : pour chaque question de la banque rattachée, sa probabilité sur la fenêtre restante, jugée
  directement ; elle sert au contrôle de cohérence (écart de plus de 10 points avec le réseau signalé).
Agrégation : moyenne en log-cotes des probabilités, moyenne géométrique des multiplicateurs, médiane des
« direct » ; « sigma » d'un nœud = dispersion moyenne entre évaluateurs en log-cotes (au moins 0,3).
Un zéro n'est gardé que s'il est unanime : un zéro isolé (probabilité ou multiplicateur) est ramené au plancher
(PLANCHER_P, PLANCHER_M) et signalé dans « alertes » ; aucun évaluateur n'a de droit de veto (étape 1 de la feuille
de route, 10 octobre 2026).
"""
import json
import math
import statistics
import sys

from commun import RACINE, lire_json

STRUCT = "modele/reseau/structure_v0.json"
PLANCHER_P = 0.01   # probabilité substituée à un zéro isolé
PLANCHER_M = 0.05   # multiplicateur substitué à un zéro isolé
ALERTES = []


def reference(n):
    """État de référence d'un nœud quand il est parent."""
    if "etats" in n:
        return n["reference"]
    return "non" if n["nature"] == "à tout moment" else n["issues"][0]


def etats(n):
    return n.get("etats") or n["issues"]


def gabarit():
    s = lire_json(STRUCT)
    noeuds = {n["id"]: n for n in s["variables_etat"] + s["pivots"]}
    ev = {e["id"]: e for e in lire_json("modele/evenements.json")["evenements"]}
    g = {"evaluateur": None, "date": None, "lecture": "Remplir chaque null. Probabilités en fractions (0-1) dont la somme vaut 1 par loi ; multiplicateurs positifs, 1 = sans effet, 0 = impossible ; supprimer un multiplicateur inutile ou le laisser à 1. Les parents sont à leur état de référence partout où il n'est pas précisé.",
         "noeuds": {}, "mesures": {}, "direct": {}}
    for i, n in noeuds.items():
        par = {}
        for p in n.get("parents", []):
            pid = p if isinstance(p, str) else p["id"]
            pn = noeuds[pid]
            par[pid] = {"reference": reference(pn), "decalage": 0 if isinstance(p, str) else p.get("decalage", 0),
                        "autres_etats": [e for e in etats(pn) if e != reference(pn)]}
        cible = etats(n) if "etats" in n or n["nature"] == "daté" else ["oui"]
        mult = {pid: {e: {c: 1.0 for c in cible} for e in d["autres_etats"]} for pid, d in par.items()
                if pid != n.get("conditionnelle")}
        x = {"nom": n["nom"], "parents": par, "multiplicateurs": mult}
        if "etats" in n:
            x["reference"] = n["reference"]
            x["transition"] = {e: {f: None for f in n["etats"]} for e in n["etats"]}
            x["definition"] = n.get("definition")
        elif n["nature"] == "daté":
            x["date"] = n["date"]
            if n.get("conditionnelle"):
                x["conditionnelle"] = {e: {c: None for c in n["issues"]} for e in etats(noeuds[n["conditionnelle"]])}
                x["base"] = {c: None for c in n["issues"]}
                x["note"] = n.get("note")
            else:
                x["base"] = {c: None for c in n["issues"]}
        else:
            x["fenetre"] = n["fenetre"]
            x["p_fenetre"] = None
        g["noeuds"][i] = x
    for q, m in s["mesures"].items():
        e = ev.get(q)
        if not m.get("exacte"):
            multi = e and e["issues"] != ["oui", "non"]
            # Question à plusieurs issues : chaque entrée à remplir est une loi en % sur les issues de la question.
            table = {k: ({c: None for c in (["François Hollande", "autre"] if q == "EV-05" else e["issues"])}
                         if multi and v is None else v) for k, v in m["table"].items()}
            g["mesures"][q] = {"question": m.get("question"), "table": table,
                               "unite": "loi en % sur les issues" if multi else "probabilité de « oui » en %"}
        if e:
            g["direct"][q] = None if e["issues"] == ["oui", "non"] else {c: None for c in e["issues"]}
    g["codes_candidats"] = s.get("codes_candidats")
    return g


def verifier(r):
    s = lire_json(STRUCT)
    g = gabarit()
    d = []
    for i, x in g["noeuds"].items():
        y = r.get("noeuds", {}).get(i)
        if not y:
            d.append(f"{i} : absent")
            continue
        lois = []
        if "transition" in x:
            lois += [(f"{i} transition {e}", y.get("transition", {}).get(e)) for e in x["transition"]]
        if "conditionnelle" in x:
            lois += [(f"{i} conditionnelle {e}", y.get("conditionnelle", {}).get(e)) for e in x["conditionnelle"]]
        elif "base" in x:
            lois.append((f"{i} base", y.get("base")))
        for nom, l in lois:
            if not isinstance(l, dict) or any(not isinstance(v, (int, float)) or v < 0 for v in l.values()):
                d.append(f"{nom} : loi absente ou valeur non numérique")
            elif abs(sum(l.values()) - 1) > 0.02:
                d.append(f"{nom} : somme {sum(l.values()):.3f} au lieu de 1")
        if "p_fenetre" in x and not (isinstance(y.get("p_fenetre"), (int, float)) and 0 < y["p_fenetre"] < 1):
            d.append(f"{i} p_fenetre : absente ou hors de ]0 ; 1[")
        for par, pd in y.get("multiplicateurs", {}).items():
            for e, md in pd.items():
                for c, m in md.items():
                    if not isinstance(m, (int, float)) or m < 0:
                        d.append(f"{i} multiplicateur {par}={e} sur {c} : {m}")
    for q, m in g["mesures"].items():
        t = r.get("mesures", {}).get(q, {}).get("table")
        if not isinstance(t, dict):
            d.append(f"mesure {q} : table absente")
            continue
        for k, v in t.items():
            modele_k = m["table"].get(k)
            if v is None:
                d.append(f"mesure {q} : entrée « {k} » non renseignée")
            elif isinstance(modele_k, dict):
                if not isinstance(v, dict) or any(not isinstance(x, (int, float)) for x in v.values()) or abs(sum(v.values()) - 100) > 1:
                    d.append(f"mesure {q} : entrée « {k} » doit être une loi en % de somme 100")
            elif not isinstance(v, (int, float)) or not 0 <= v <= 100:
                d.append(f"mesure {q} : entrée « {k} » doit être un pourcentage")
    for q, v in g["direct"].items():
        w = r.get("direct", {}).get(q)
        if w is None:
            d.append(f"direct {q} : absent")
    return d


def lo(p):
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def plancher(vals, p, ou=""):
    """Zéros isolés remplacés par le plancher p (signalés) ; zéro unanime conservé."""
    if all(v == 0 for v in vals) or not any(v == 0 for v in vals):
        return vals
    ALERTES.append(f"{ou} : zéro isolé ramené à {p} ({vals})")
    return [p if v == 0 else v for v in vals]


def moy_loi(lois, ou=""):
    """Moyenne en log-cotes, issue par issue, puis normalisation ; une issue nulle chez tous reste nulle, un zéro
    isolé est ramené au plancher."""
    cles = lois[0].keys()
    out = {}
    for c in cles:
        vals = plancher([l.get(c, 0) for l in lois], PLANCHER_P, f"{ou} {c}")
        out[c] = 0.0 if all(v == 0 for v in vals) else 1 / (1 + math.exp(-statistics.mean(lo(v) for v in vals)))
    s = sum(out.values())
    return {c: v / s for c, v in out.items()}


def dispersion(lois):
    ecarts = []
    for c in lois[0]:
        vals = [lo(l.get(c, 0)) for l in lois if l.get(c, 0) > 0]
        if len(vals) >= 2:
            ecarts.append(statistics.pstdev(vals))
    return statistics.mean(ecarts) if ecarts else 0.0


def moy_mult(ms, ou=""):
    ms = plancher(ms, PLANCHER_M, ou)
    return 0.0 if all(m == 0 for m in ms) else math.exp(statistics.mean(math.log(m) for m in ms))


def agreger(reponses, version):
    ALERTES.clear()
    g = gabarit()
    out = {"version": version, "evaluateurs": [r.get("evaluateur") for r in reponses], "noeuds": {}, "mesures": {}, "direct": {}}
    for i, x in g["noeuds"].items():
        ys = [r["noeuds"][i] for r in reponses]
        t, disp = {}, []
        if "transition" in x:
            t["reference"] = x["reference"]
            t["transition"] = {e: moy_loi([y["transition"][e] for y in ys], f"{i} transition {e}") for e in x["transition"]}
            disp += [dispersion([y["transition"][e] for y in ys]) for e in x["transition"]]
        if "conditionnelle" in x:
            t["conditionnelle"] = {e: moy_loi([y["conditionnelle"][e] for y in ys], f"{i} {e}") for e in x["conditionnelle"]}
            t["base"] = t["conditionnelle"][next(iter(t["conditionnelle"]))]
            disp += [dispersion([y["conditionnelle"][e] for y in ys]) for e in x["conditionnelle"]]
        elif "base" in x:
            t["base"] = moy_loi([y["base"] for y in ys], f"{i} base")
            disp.append(dispersion([y["base"] for y in ys]))
        if "p_fenetre" in x:
            l = [lo(y["p_fenetre"]) for y in ys]
            t["p_fenetre"] = 1 / (1 + math.exp(-statistics.mean(l)))
            disp.append(statistics.pstdev(l))
        mult = {}
        for y in ys:
            for par, pd in y.get("multiplicateurs", {}).items():
                for e, md in pd.items():
                    for c, m in md.items():
                        mult.setdefault(par, {}).setdefault(e, {}).setdefault(c, []).append(m)
        t["multiplicateurs"] = {par: {e: {c: moy_mult(ms, f"{i} {par}={e} {c}")
                                          for c, ms in md.items()} for e, md in pd.items()} for par, pd in mult.items()}
        t["sigma"] = round(max(statistics.mean(disp) if disp else 0.3, 0.3), 3)
        out["noeuds"][i] = t
    for q in g["mesures"]:
        tabs = [r["mesures"][q]["table"] for r in reponses]
        agg = {}
        for k in tabs[0]:
            vals = [tb[k] for tb in tabs]
            if all(isinstance(v, dict) for v in vals):
                agg[k] = {c: round(100 * v, 2) for c, v in moy_loi([{c: x / 100 for c, x in v.items()} for v in vals]).items()}
            else:
                agg[k] = round(100 / (1 + math.exp(-statistics.mean(lo(v / 100) for v in vals))), 2)
        out["mesures"][q] = agg
    for q in g["direct"]:
        vals = [r["direct"][q] for r in reponses]
        if all(isinstance(v, (int, float)) for v in vals):
            out["direct"][q] = round(statistics.median(vals), 1)
        else:
            out["direct"][q] = {c: round(statistics.median(v[c] for v in vals), 1) for c in vals[0]}
    if ALERTES:
        out["alertes"] = list(ALERTES)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["gabarit"] and len(a) == 2:
        json.dump(gabarit(), open(a[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Gabarit écrit dans {a[1]}")
    elif a[:1] == ["verifier"] and len(a) == 2:
        d = verifier(json.load(open(a[1], encoding="utf-8")))
        print("conforme" if not d else "NON CONFORME :\n- " + "\n- ".join(d))
        sys.exit(1 if d else 0)
    elif a[:1] == ["agreger"] and len(a) >= 3:
        version = a[a.index("--version") + 1] if "--version" in a else "tables v0"
        fichiers = [x for x in a[1:] if not x.startswith("--") and x != version]
        reps = [json.load(open(f, encoding="utf-8")) for f in fichiers]
        for f, r in zip(fichiers, reps):
            d = verifier(r)
            if d:
                sys.exit(f"{f} non conforme : {d[:5]}")
        (RACINE / "modele/reseau/tables_v0.json").write_text(json.dumps(agreger(reps, version), ensure_ascii=False, indent=1), "utf-8")
        print(f"modele/reseau/tables_v0.json écrit ({len(reps)} évaluateurs)")
    else:
        sys.exit(__doc__)
