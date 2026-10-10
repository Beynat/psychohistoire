"""Tables du réseau v0 : gabarit d'élicitation, contrôle d'une réponse, agrégation (feuille de route v0, bloc 4).

Usage :
    python scripts/tables.py gabarit SORTIE.json        gabarit à remplir par un évaluateur (ancien format :
                                                        loi de référence et multiplicateurs)
    python scripts/tables.py gabarit_cas N1,N2 SORTIE.json
                                                        gabarit « lois par cas » (étape 4) : une loi complète par
                                                        cas de parents, justification par cas, avis direct
    python scripts/tables.py controle_cas R1.json R2.json ...
                                                        contrôles automatiques d'une ronde (justification vide,
                                                        loi invalide, marginale implicite à plus de 5 points de
                                                        l'avis direct, sens opposés entre évaluateurs) ; code 1
                                                        si un défaut bloque l'agrégation
    python scripts/tables.py agreger_cas R1.json R2.json ... --version TEXTE
                                                        agrège les lois par cas (moyenne des log-cotes, zéro isolé
                                                        au plancher) et remplace les nœuds dans tables_v0.json
    python scripts/tables.py controle_tables            diagnostic des tables agrégées (référence minoritaire,
                                                        calage sur un avis direct)
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


# ---------------------------------------------------------------------------------------------------------------
# Lois par cas (feuille de route, étape 4 ; revues du 10 octobre 2026, C.1 et 4.1)

SEUIL_MARGINALE = 5      # points entre la marginale impliquée par les lois d'un évaluateur et son avis direct
SEUIL_SENS = 0.2         # log-cote : écart au cas le plus fréquent au-delà duquel deux sens opposés sont un défaut


def _structure():
    return lire_json(STRUCT)


def cas_du_noeud(n, noeuds):
    """Liste des clés de cas d'un nœud (produit des états des parents, précédé de l'état du mois précédent pour une
    variable d'état), au format de reseau.cles_cas."""
    import itertools
    axes = []
    if "etats" in n:
        axes.append([f"prec={e}" for e in n["etats"]])
    for q in n.get("parents", []):
        qid = q if isinstance(q, str) else q["id"]
        axes.append([f"{qid}={e}" for e in etats(noeuds[qid])])
    return ["|".join(c) for c in itertools.product(*axes)] if axes else [""]


def questions_du_noeud(nid, s):
    """Questions de la banque dont la mesure lit le nœud."""
    out = []
    for q, m in s["mesures"].items():
        c = m["caracteristique"]
        if any(x.get("noeud") == nid for x in c.get("elements", [c])):
            out.append(q)
    return out


def poids_cas(nid, trajectoires=1500, graine=11):
    """Fréquence de chaque cas de parents dans le réseau actuel (paramètres agrégés), sur les mois où le nœud est
    tiré : tous les mois pour une variable, la fenêtre restante pour un pivot « à tout moment » non encore survenu,
    le mois de la date pour un pivot daté. Donnée aux évaluateurs pour qu'ils voient quels cas pèsent."""
    import random
    import reseau
    s = _structure()
    t = lire_json("modele/reseau/tables_v0.json")
    obs = reseau.observations(s)
    reseau.PRIORS = reseau.lois_a_priori(s, t, obs)
    noeuds = reseau.noeuds_de(s)
    n = noeuds[nid]
    params = {i: dict(x) for i, x in t["noeuds"].items()}
    rng = random.Random(graine)
    compte, tot = {}, 0.0
    for _ in range(trajectoires):
        tr = reseau.simuler(s, params, obs, rng)
        if "etats" in n:
            mois = range(len(reseau.MOIS))
        elif n["nature"] == "daté":
            mois = [reseau.idx(n["date"])]
        else:
            d0, d1 = reseau.idx(n["fenetre"][0]), reseau.idx(n["fenetre"][1])
            mois = [k for k in range(d0, d1 + 1) if (k == d0 or tr[nid][k - 1] != "oui")
                    and not any(nid in v["interdit"] and (lambda j: j is not None and k <= j + v["duree_mois"])(reseau.premier_oui(tr[v["si"]], k))
                                for v in s.get("verrous", []))]
        for k in mois:
            et = {}
            for q in n.get("parents", []):
                kk = k - reseau.dec(q)
                if kk >= 0 and tr[reseau.pid(q)][kk] is not None:
                    et[reseau.pid(q)] = tr[reseau.pid(q)][kk]
                elif kk >= 0 and noeuds[reseau.pid(q)].get("nature") == "daté":
                    et[reseau.pid(q)] = reseau.APriori(reseau.PRIORS[reseau.pid(q)])
            prec = (tr[nid][k - 1] if k else n.get("reference")) if "etats" in n else None
            for w, c in reseau.cles_cas(n, et, noeuds, prec):
                compte[c] = compte.get(c, 0.0) + w
                tot += w
    return {c: round(compte.get(c, 0.0) / tot, 4) for c in cas_du_noeud(n, noeuds)}


def gabarit_cas(ids):
    s = _structure()
    ev = {e["id"]: e for e in lire_json("modele/evenements.json")["evenements"]}
    import reseau
    noeuds = reseau.noeuds_de(s)
    g = {"evaluateur": None, "date": None, "format": "lois par cas v1",
         "lecture": ("Des cas qui ont la même loi peuvent être regroupés par un joker : remplacer, par exemple, "
                     "« PV-VAINQ=PHI » par « PV-VAINQ=* » dans la clé, et supprimer les cas couverts ; chaque cas doit rester "
                     "couvert, et le plus précis l'emporte. "
                     "Pour chaque nœud et chaque cas (combinaison des états de ses parents, et état du mois précédent pour "
                     "une variable d'état), donner la loi complète demandée : pour un pivot « à tout moment », la "
                     "probabilité qu'il survienne sur toute sa fenêtre si ce cas valait pendant toute la fenêtre ; pour "
                     "un pivot daté, la loi de ses issues à sa date ; pour une variable d'état, la loi de son état le mois "
                     "suivant. Probabilités en fractions de somme 1. Chaque cas a une justification : un fait sourcé (URL "
                     "ou référence) ou la mention « jugement » suivie du raisonnement. « poids_reseau » indique la "
                     "fréquence du cas dans le réseau actuel : les cas fréquents comptent le plus. Donner enfin, dans "
                     "« direct », votre probabilité pour chaque question indiquée, jugée directement ; elle sert à vérifier "
                     "que vos lois sont cohérentes avec votre avis d'ensemble, pas de cible. Pour un pivot « à tout moment » dont "
                     "un parent est lui-même un événement (une censure, une dissolution), le cas « parent=oui » s'applique "
                     "au reste de la fenêtre à partir de sa survenue. Un verrou (« verrous ») rend la survenue impossible "
                     "pendant la durée indiquée, quel que soit le cas : ne pas le recompter dans les probabilités."),
         "noeuds": {}, "direct": {},
         "observations": (lire_json("modele/reseau/observations.json") or {}).get("etats"),
         "date_du_jour": __import__("datetime").date.today().isoformat()}
    for nid in ids:
        n = noeuds[nid]
        par = []
        for q in n.get("parents", []):
            qid = q if isinstance(q, str) else q["id"]
            pn = noeuds[qid]
            par.append({"id": qid, "nom": pn["nom"], "etats": etats(pn), "decalage": 0 if isinstance(q, str) else q.get("decalage", 0),
                        "definition": pn.get("definition") or pn.get("date") or pn.get("fenetre")})
        w = poids_cas(nid)
        cible = n.get("etats") or n.get("issues") or ["oui", "non"]
        x = {"nom": n["nom"], "nature": n.get("nature", "variable d'état"), "parents": par,
             "definition": n.get("definition"), "date": n.get("date"), "fenetre": n.get("fenetre"),
             "issues": cible,
             "cas": {c: {"poids_reseau": w[c], "loi": ({"oui": None} if n.get("nature") == "à tout moment" else {e: None for e in cible}),
                         "justification": None} for c in cas_du_noeud(n, noeuds)}}
        x["verrous"] = [v for v in s.get("verrous", []) if nid in v["interdit"]]
        if n.get("profil"):
            x["profil"] = "risque concentré sur les mois de revue programmée des agences (calendrier sourcé) ; donner la probabilité sur toute la fenêtre"
        g["noeuds"][nid] = x
        for q in questions_du_noeud(nid, s):
            e = ev.get(q)
            if e:
                g["direct"][q] = {"critere": e.get("critere"), "fenetre": e["fenetre"],
                                  "probabilite": None if e["issues"] == ["oui", "non"] else {i: None for i in e["issues"]}}
    return g


def correspond(cle, motif):
    """Une clé de cas complète correspond-elle à un motif à jokers (« parent=* ») ? Rend le nombre de jokers, ou None."""
    a, b = cle.split("|"), motif.split("|")
    if len(a) != len(b):
        return None
    j = 0
    for x, y in zip(a, b):
        if y.endswith("=*") and x.split("=")[0] == y[:-2]:
            j += 1
        elif x != y:
            return None
    return j


def lois_de(rep, nid, cles=None):
    """Table « cas » d'un évaluateur pour un nœud, au format du moteur (float pour « à tout moment », loi sinon).
    Un évaluateur peut regrouper des cas par des jokers (« PV-VAINQ=* ») : chaque cas complet prend la règle la plus
    précise qui lui correspond."""
    brut = {c: (x["loi"]["oui"] if set(x["loi"]) == {"oui"} else x["loi"]) for c, x in rep["noeuds"][nid]["cas"].items()}
    if cles is None:
        import reseau
        cles = cas_du_noeud(reseau.noeuds_de(_structure())[nid], reseau.noeuds_de(_structure()))
    out = {}
    for c in cles:
        cand = [(correspond(c, m), m) for m in brut]
        cand = [x for x in cand if x[0] is not None]
        if not cand:
            raise ValueError(f"{nid} : cas {c} non couvert")
        out[c] = brut[min(cand)[1]]
    return out


def marginales(rep, trajectoires=1500):
    """Prévisions des questions des nœuds de la réponse quand le réseau utilise les lois de cet évaluateur (les autres
    nœuds aux tables actuelles) : marginale impliquée, comparée à son avis direct."""
    import reseau
    s = _structure()
    t = json.loads(json.dumps(lire_json("modele/reseau/tables_v0.json")))
    for nid in rep["noeuds"]:
        t["noeuds"][nid] = {"cas": lois_de(rep, nid), "sigma": 0.3}
    ev = {e["id"]: e for e in lire_json("modele/evenements.json")["evenements"]}
    qs = [q for q in reseau.questions_banque(s, list(ev.values())) if q.get("evenement") in rep.get("direct", {})]
    p = reseau.prevoir(s, t, reseau.observations(s), qs, tirages=15, trajectoires=trajectoires // 15)
    return {q["evenement"]: {k: v for k, v in p[q["id"]].items() if k != "i80"} for q in qs}


def verifier_cas(rep):
    """Défauts d'une réponse : loi absente ou invalide, justification vide, cas non couvert, avis direct absent."""
    d = []
    for nid, x in rep.get("noeuds", {}).items():
        try:
            lois_de(rep, nid)
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            d.append(f"{nid} : {e}")
        for c, y in x.get("cas", {}).items():
            l = y.get("loi") or {}
            if not l or any(not isinstance(v, (int, float)) or v < 0 for v in l.values()):
                d.append(f"{nid} [{c}] : loi absente ou non numérique")
            elif set(l) != {"oui"} and abs(sum(l.values()) - 1) > 0.02:
                d.append(f"{nid} [{c}] : somme {sum(l.values()):.3f}")
            elif set(l) == {"oui"} and not 0 <= l["oui"] <= 1:
                d.append(f"{nid} [{c}] : probabilité hors de [0 ; 1]")
            j = (y.get("justification") or "").strip()
            if len(j) < 15:
                d.append(f"{nid} [{c}] : justification vide")
    for q, v in rep.get("direct", {}).items():
        if (v.get("probabilite") if isinstance(v, dict) else v) is None:
            d.append(f"direct {q} : absent")
    return d


def principale(l):
    """Valeur résumée d'une loi pour comparer des sens : P(oui), ou probabilité de la première issue."""
    return l if isinstance(l, (int, float)) else next(iter(l.values()))


def sens_opposes(reps):
    """Défauts de sens : pour chaque nœud, cas le plus fréquent comme référence ; pour chaque autre cas et chaque
    issue, l'écart de log-cote au cas de référence chez chaque évaluateur ; deux évaluateurs dont les écarts
    dépassent SEUIL_SENS en sens opposés forment un défaut (seconde ronde, protocole IDEA)."""
    d = []
    nids = set.intersection(*(set(r["noeuds"]) for r in reps))
    for nid in sorted(nids):
        cas = reps[0]["noeuds"][nid]["cas"]
        ref = max(cas, key=lambda c: cas[c].get("poids_reseau", 0))
        for c in cas:
            if c == ref:
                continue
            ls = [lois_de(r, nid) for r in reps]
            issues = ["oui"] if not isinstance(ls[0][c], dict) else list(ls[0][c])
            for i in issues:
                ecarts = []
                for l in ls:
                    a = l[c] if not isinstance(l[c], dict) else l[c][i]
                    b = l[ref] if not isinstance(l[ref], dict) else l[ref][i]
                    ecarts.append(lo(a) - lo(b))
                if any(e > SEUIL_SENS for e in ecarts) and any(e < -SEUIL_SENS for e in ecarts):
                    d.append({"noeud": nid, "cas": c, "reference": ref, "issue": i, "ecarts": [round(e, 2) for e in ecarts]})
    return d


def ecarts_marginaux(rep, m=None):
    m = m or marginales(rep)
    out = []
    for q, v in rep.get("direct", {}).items():
        direct = v.get("probabilite") if isinstance(v, dict) else v
        if q not in m or direct is None:
            continue
        dd = {"oui": 100 * direct} if isinstance(direct, (int, float)) and direct <= 1 else \
             {"oui": direct} if isinstance(direct, (int, float)) else {k: (100 * x if x <= 1 else x) for k, x in direct.items()}
        for k, x in dd.items():
            if k in m[q] and abs(m[q][k] - x) > SEUIL_MARGINALE:
                out.append({"question": q, "issue": k, "implique": m[q][k], "direct": round(x, 1)})
    return out


def sigma_pondere(disp):
    """σ d'un nœud : moyenne des dispersions par cas, pondérée par la fréquence du cas, au moins 0,3."""
    tw = sum(w for w, _ in disp)
    return round(max(sum(w * d for w, d in disp) / tw if tw > 0 else 0.3, 0.3), 3)


def agreger_cas(reps, version):
    """Agrégation des lois par cas : moyenne des log-cotes cas par cas (zéro isolé au plancher) ; σ du nœud =
    dispersion moyenne entre évaluateurs. Remplace les nœuds dans tables_v0.json (anciens paramètres retirés)."""
    ALERTES.clear()
    t = lire_json("modele/reseau/tables_v0.json")
    for nid in reps[0]["noeuds"]:
        ls = [lois_de(r, nid) for r in reps]
        poids = {c: x.get("poids_reseau", 1.0) for c, x in reps[0]["noeuds"][nid]["cas"].items()}
        cas, disp = {}, []
        for c in ls[0]:
            vals = [l[c] for l in ls]
            w = poids.get(c, 0.0)
            if isinstance(vals[0], dict):
                cas[c] = {k: round(v, 5) for k, v in moy_loi(vals, f"{nid} [{c}]").items()}
                disp.append((w, dispersion(vals)))
            else:
                v = plancher(vals, PLANCHER_P, f"{nid} [{c}]")
                cas[c] = 0.0 if all(x == 0 for x in v) else round(1 / (1 + math.exp(-statistics.mean(lo(x) for x in v))), 5)
                disp.append((w, statistics.pstdev([lo(x) for x in v])))
        # σ du nœud : dispersion moyenne pondérée par la fréquence des cas (un cas sous verrou, de poids nul, ne compte pas)
        t["noeuds"][nid] = {"cas": cas, "sigma": sigma_pondere(disp),
                            "evaluateurs": [r.get("evaluateur") for r in reps], "format": "lois par cas v1"}
        if ALERTES:
            t["noeuds"][nid]["alertes"] = [a for a in ALERTES if a.startswith(nid)]
    t["version"] = version
    (RACINE / "modele/reseau/tables_v0.json").write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", "utf-8")
    return t


def controle_tables():
    """Diagnostic des tables agrégées (ancien format) : nœuds calés sur un avis direct, et signature « marginale
    donnée pour la loi de référence » (état de référence d'un parent minoritaire, loi de base à moins de 3 points
    de l'avis direct de la question qui lit le nœud, multiplicateurs non triviaux)."""
    import reseau
    s = _structure()
    t = lire_json("modele/reseau/tables_v0.json")
    noeuds = reseau.noeuds_de(s)
    obs = reseau.observations(s)
    pri = reseau.lois_a_priori(s, t, obs)
    d = []
    for nid, x in t["noeuds"].items():
        if x.get("calibre") or "médiane" in str(x.get("derive", "")) or "suggestion" in str(x.get("derive", "")) or "reste de la probabilité" in str(x.get("derive", "")):
            d.append({"noeud": nid, "defaut": "calage ou dérivation à la main", "detail": x.get("calibre") or x.get("derive")})
        n = noeuds[nid]
        for q in n.get("parents", []):
            qid = reseau.pid(q)
            qn = noeuds[qid]
            if qn.get("nature") == "daté" and qid in pri:
                ref = reference(qn)
                mult = x.get("multiplicateurs", {}).get(qid, {})
                if pri[qid].get(ref, 1) < 0.4 and mult and any(abs(math.log(m)) > 0.2 for md in mult.values() for m in md.values() if m > 0):
                    for qq in questions_du_noeud(nid, s):
                        dir_ = t.get("direct", {}).get(qq)
                        if isinstance(dir_, (int, float)) and "p_fenetre" in x and abs(100 * x["p_fenetre"] - dir_) < 3:
                            d.append({"noeud": nid, "defaut": "référence minoritaire", "parent": qid,
                                      "detail": f"référence {ref} à {round(100 * pri[qid][ref])} %, loi de base {round(100 * x['p_fenetre'], 1)} % contre avis direct {dir_} % ({qq})"})
    return d


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["gabarit"] and len(a) == 2:
        json.dump(gabarit(), open(a[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Gabarit écrit dans {a[1]}")
    elif a[:1] == ["verifier"] and len(a) == 2:
        d = verifier(json.load(open(a[1], encoding="utf-8")))
        print("conforme" if not d else "NON CONFORME :\n- " + "\n- ".join(d))
        sys.exit(1 if d else 0)
    elif a[:1] == ["gabarit_cas"] and len(a) == 3:
        json.dump(gabarit_cas(a[1].split(",")), open(a[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Gabarit écrit dans {a[2]}")
    elif a[:1] == ["controle_cas"] and len(a) >= 2:
        reps = [json.load(open(f, encoding="utf-8")) for f in a[1:]]
        bloque = False
        for f, r in zip(a[1:], reps):
            d = verifier_cas(r)
            print(f"{f} : {'conforme' if not d else 'NON CONFORME'}")
            for x in d:
                print(f"  - {x}")
            bloque |= bool(d)
            for e in ecarts_marginaux(r):
                print(f"  marginale implicite {e['question']} {e['issue']} : {e['implique']} contre avis direct {e['direct']}")
                bloque = True
        so = sens_opposes(reps) if len(reps) > 1 else []
        for x in so:
            print(f"SENS OPPOSÉS {x['noeud']} [{x['cas']}] {x['issue']} (référence {x['reference']}) : {x['ecarts']}")
        sys.exit(1 if bloque or so else 0)
    elif a[:1] == ["agreger_cas"] and len(a) >= 3:
        version = a[a.index("--version") + 1] if "--version" in a else "tables v0"
        fichiers = [x for x in a[1:] if not x.startswith("--") and x != version]
        agreger_cas([json.load(open(f, encoding="utf-8")) for f in fichiers], version)
        print(f"modele/reseau/tables_v0.json mis à jour ({len(fichiers)} évaluateurs)")
    elif a[:1] == ["controle_tables"]:
        for x in controle_tables():
            print(json.dumps(x, ensure_ascii=False))
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
