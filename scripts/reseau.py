"""Moteur du réseau bayésien dynamique v0 (feuille de route v0, bloc 4).

Usage :
    python scripts/reseau.py --controle [--tirages N] [--trajectoires N]
        Prévisions sur les fenêtres de la banque et contrôle de cohérence avec les probabilités données
        directement par les évaluateurs ; aucune écriture.
    python scripts/reseau.py ETIQUETTE --registre registre/<fichier>.jsonl [--tirages N] [--trajectoires N]
        Prévisions pour les questions du cycle ETIQUETTE (fenêtre propre à chaque question), écrites au registre
        par scripts/registre.py, auteur « réseau v0 », avec la version des tables et l'intervalle à 80 %.

Fichiers : modele/reseau/structure_v0.json (nœuds, parents, mesures), modele/reseau/tables_v0.json (paramètres
agrégés des évaluateurs, scripts/tables.py), modele/reseau/observations.json (états observés par mois).

Paramétrage (aucune probabilité mensuelle n'est demandée aux évaluateurs) :
- pivot « daté » : loi de base de ses issues, parents à leur état de référence ; un multiplicateur sur le poids de
  chaque issue pour chaque autre état d'un parent (log-linéaire, sans interaction) ; ou une loi par état d'un
  parent (« conditionnelle ») ; des exclusions (issue impossible selon l'état d'un parent) ;
- pivot « à tout moment » : probabilité de survenue sur sa fenêtre, parents de référence, convertie en risque
  mensuel constant h = 1 - (1 - P)^(1/n) ; un multiplicateur sur ce risque par état de parent ;
- variable d'état : transition d'un mois au suivant, multiplicateurs par état de parent ;
- parent « decalage » : 1 = état du mois précédent (seul moyen de boucler sans cycle au sein d'un mois) ;
- mesure : une question de la banque en fonction d'une caractéristique de la trajectoire.
"""
import json
import math
import random
import sys

from commun import lire_json

VERSION = "réseau v0"
DEBUT, FIN = (2026, 10), (2028, 9)
SIGMA_PLANCHER = 0.3


def _mois():
    a, m, out = DEBUT[0], DEBUT[1], []
    while (a, m) <= FIN:
        out.append(f"{a:04d}-{m:02d}")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return out


MOIS = _mois()


def idx(s):
    k = s[:7]
    return 0 if k < MOIS[0] else len(MOIS) - 1 if k > MOIS[-1] else MOIS.index(k)


def logit(p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def sig(x):
    return 1 / (1 + math.exp(-x))


def normaliser(d):
    s = sum(d.values())
    return {k: v / s for k, v in d.items()} if s > 0 else {k: 1 / len(d) for k in d}


def tirer(dist, rng):
    u, c = rng.random(), 0.0
    for k, v in dist.items():
        c += v
        if u <= c:
            return k
    return k


def pid(p):
    return p if isinstance(p, str) else p["id"]


def dec(p):
    return 0 if isinstance(p, str) else p.get("decalage", 0)


def noeuds_de(structure):
    return {n["id"]: n for n in structure["variables_etat"] + structure["pivots"]}


def ordre(structure):
    """Ordre topologique au sein d'un mois ; un parent au mois précédent ne crée pas d'arête."""
    noeuds = noeuds_de(structure)
    vus, out = set(), []

    def visiter(i, pile):
        if i in vus:
            return
        if i in pile:
            raise SystemExit(f"Cycle au sein d'un mois passant par {i} : {' → '.join(pile + [i])}")
        for p in noeuds[i].get("parents", []):
            if dec(p) == 0 and pid(p) in noeuds:
                visiter(pid(p), pile + [i])
        vus.add(i)
        out.append(i)
    for i in noeuds:
        visiter(i, [])
    return out, noeuds


def perturber(tables, rng):
    """Un jeu de paramètres tiré autour des valeurs agrégées : bruit en log-cotes (lois, risques, transitions)
    et en log (multiplicateurs), d'écart-type sigma du nœud (au moins 0,3, noyau section 4.4)."""
    out = {}
    for nid, t in tables["noeuds"].items():
        s = max(t.get("sigma", SIGMA_PLANCHER), SIGMA_PLANCHER)
        bruit = lambda d: normaliser({k: sig(logit(v) + rng.gauss(0, s)) if v > 0 else 0.0 for k, v in d.items()})
        u = dict(t)
        if "base" in t:
            u["base"] = bruit(t["base"])
        if "conditionnelle" in t:
            u["conditionnelle"] = {e: bruit(d) for e, d in t["conditionnelle"].items()}
        if "p_fenetre" in t:
            u["p_fenetre"] = sig(logit(t["p_fenetre"]) + rng.gauss(0, s))
        if "transition" in t:
            u["transition"] = {e: bruit(d) for e, d in t["transition"].items()}
        if "multiplicateurs" in t:
            u["multiplicateurs"] = {par: {etat: {iss: m * math.exp(rng.gauss(0, s / 2)) for iss, m in d.items()}
                                          for etat, d in pd.items()} for par, pd in t["multiplicateurs"].items()}
        out[nid] = u
    return out


def multiplicateurs(t, etats):
    tot = {}
    for par, etat in etats.items():
        for iss, m in t.get("multiplicateurs", {}).get(par, {}).get(etat, {}).items():
            tot[iss] = tot.get(iss, 1.0) * m
    return tot


def appliquer(base, mults, exclus=()):
    poids = {k: (0.0 if any(c in k.split("-") for c in exclus) else v * mults.get(k, 1.0)) for k, v in base.items()}
    return normaliser(poids)


def simuler(structure, params, obs, rng):
    """Une trajectoire. obs : {nœud: {mois: état}} observé ; un état observé remplace le tirage."""
    rangs, noeuds = ordre(structure)
    traj = {i: [None] * len(MOIS) for i in noeuds}
    for k in range(len(MOIS)):
        for i in rangs:
            n, t = noeuds[i], params[i]
            etats = {}
            for p in n.get("parents", []):
                kk = k - dec(p)
                if kk >= 0 and traj[pid(p)][kk] is not None:
                    etats[pid(p)] = traj[pid(p)][kk]
            vu = obs.get(i, {}).get(MOIS[k])
            if i.startswith("VE-"):
                if vu:
                    traj[i][k] = vu
                    continue
                prec = traj[i][k - 1] if k else t["reference"]
                traj[i][k] = tirer(appliquer(t["transition"][prec], multiplicateurs(t, etats)), rng)
            elif n["nature"] == "daté":
                km = idx(n["date"])
                if k < km:
                    continue
                if k > km:
                    traj[i][k] = traj[i][k - 1]
                    continue
                if vu:
                    traj[i][k] = vu
                    continue
                base = t["base"]
                cond = n.get("conditionnelle")
                if cond and cond in etats:
                    base = t["conditionnelle"][etats[cond]]
                exclus = [c for par, d in n.get("exclusions", {}).items() for c in d.get(etats.get(par), [])]
                traj[i][k] = tirer(appliquer(base, multiplicateurs(t, etats), exclus), rng)
            else:   # à tout moment, absorbant
                d0, d1 = idx(n["fenetre"][0]), idx(n["fenetre"][1])
                if k < d0:
                    continue
                if k and traj[i][k - 1] == "oui":
                    traj[i][k] = "oui"
                    continue
                if k > d1:
                    traj[i][k] = traj[i][k - 1]
                    continue
                if vu:
                    traj[i][k] = vu
                    continue
                h = 1 - (1 - t["p_fenetre"]) ** (1 / (d1 - d0 + 1))
                h = min(h * multiplicateurs(t, etats).get("oui", 1.0), 0.95)
                traj[i][k] = "oui" if rng.random() < h else "non"
    return traj


def valeur(c, traj, noeuds, fen):
    """Caractéristique c d'une trajectoire sur la fenêtre fen (début, fin) de la question."""
    a = idx(c.get("debut") or fen[0])
    b = idx(min(c.get("fin") or fen[1], fen[1]) if c.get("fin") else fen[1])
    x = traj.get(c.get("noeud"), [])
    if c["type"] == "issue":
        return next((v for v in reversed(x) if v is not None), None)
    if c["type"] == "survenue":
        return "oui" if any(x[k] == "oui" for k in range(a, b + 1)) else "non"
    if c["type"] == "etat_max":
        ordre_e = noeuds[c["noeud"]]["etats"]
        vals = [x[k] for k in range(a, b + 1) if x[k] is not None]
        return max(vals, key=ordre_e.index) if vals else None
    if c["type"] == "contient":
        v = next((v for v in reversed(x) if v is not None), None)
        return "oui" if v and c["code"] in v.split("-") else "non"
    if c["type"] == "conjonction":
        return "|".join(str(valeur(e, traj, noeuds, fen)) for e in c["elements"])
    raise SystemExit(f"Caractéristique inconnue : {c['type']}")


def chercher(table, v):
    """Valeur de table pour v ; clés à jokers « * » par élément d'une conjonction, la plus précise d'abord."""
    if v in table:
        return table[v]
    parts = v.split("|")
    cands = []
    for k in table:
        kp = k.split("|")
        if len(kp) == len(parts) and all(a == "*" or a == b for a, b in zip(kp, parts)):
            cands.append((kp.count("*"), k))
    if not cands:
        return 0.0
    return table[min(cands)[1]]


def loi(mesure, tables_mesures, ev_id, v, issues):
    """Loi des issues de la question pour la valeur v de la caractéristique."""
    tab = tables_mesures.get(ev_id, mesure["table"])
    if tab == "identite":
        return {i: (1.0 if i == v else 0.0) for i in issues}
    x = chercher(tab, v)
    if x is None:
        raise SystemExit(f"{ev_id} : entrée « {v} » de la table de mesure non renseignée")
    if isinstance(x, dict):
        d = {i: x.get(i, 0) / 100 for i in issues}
        return d
    return {"oui": x / 100, "non": 1 - x / 100}


def prevoir(structure, tables, obs, questions, tirages=200, trajectoires=100, graine=20261010):
    """questions : liste de {id, evenement, issues, fenetre: [début, fin]} ou de conjointes {id, composantes}.
    Rend {id: {issue: %, ..., i80: [bas, haut] sur l'issue « oui » ou la première issue}}."""
    rng = random.Random(graine)
    noeuds = noeuds_de(structure)
    mes = structure["mesures"]
    tm = tables.get("mesures", {})
    simples = [q for q in questions if "composantes" not in q]
    conj = [q for q in questions if "composantes" in q]
    acc = {q["id"]: [] for q in questions}
    for _ in range(tirages):
        params = perturber(tables, rng)
        som = {q["id"]: {} for q in questions}
        for _ in range(trajectoires):
            traj = simuler(structure, params, obs, rng)
            p_oui = {}
            for q in simples:
                m = mes[q["evenement"]]
                d = loi(m, tm, q["evenement"], valeur(m["caracteristique"], traj, noeuds, q["fenetre"]), q["issues"])
                for i, v in d.items():
                    som[q["id"]][i] = som[q["id"]].get(i, 0.0) + v
                p_oui[q["id"]] = d.get("oui")
            for q in conj:
                pa, pb = (p_oui.get(c) for c in q["composantes"])
                p = (pa or 0) * (pb or 0)     # indépendance conditionnelle à la trajectoire
                som[q["id"]]["oui"] = som[q["id"]].get("oui", 0.0) + p
                som[q["id"]]["non"] = som[q["id"]].get("non", 0.0) + 1 - p
        for q in questions:
            acc[q["id"]].append({i: v / trajectoires for i, v in som[q["id"]].items()})
    out = {}
    for q in questions:
        tir = acc[q["id"]]
        issues = list(tir[0])
        moy = normaliser({i: sum(t.get(i, 0) for t in tir) / len(tir) for i in issues})
        cle = "oui" if "oui" in issues else issues[0]
        xs = sorted(t.get(cle, 0) for t in tir)
        out[q["id"]] = {**{i: round(100 * v, 1) for i, v in moy.items()},
                        "i80": [round(100 * xs[int(0.1 * (len(xs) - 1))], 1), round(100 * xs[int(0.9 * (len(xs) - 1))], 1)]}
    return out


def questions_banque(structure, evenements, debut="2026-10-10"):
    """Questions de fenêtre de la banque rattachées au réseau (contrôle de cohérence)."""
    ev = {e["id"]: e for e in evenements}
    qs = [{"id": f"Q-{i}", "evenement": i, "issues": ev[i]["issues"],
           "fenetre": [max(ev[i]["fenetre"]["debut"], debut), ev[i]["fenetre"]["fin"]]}
          for i in structure["mesures"] if i in ev]
    for cid, (a, b) in structure.get("conjointes", {}).items():
        if a in structure["mesures"] and b in structure["mesures"]:
            qs.append({"id": f"Q-{cid}", "composantes": [f"Q-{a}", f"Q-{b}"]})
    return qs


def questions_cycle(structure, etiquette):
    out = []
    for q in lire_json(f"data/cycles/{etiquette}/questions.json")["questions"]:
        if q["type"] == "evenement" and q["details"]["evenement"] in structure["mesures"]:
            out.append({"id": q["id"], "evenement": q["details"]["evenement"], "issues": q["issues"],
                        "fenetre": [q["fenetre"]["debut"], q["fenetre"]["fin"]]})
        elif q["type"] == "conjointe":
            out.append({"id": q["id"], "composantes": q["details"]["composantes"]})
    # Les composantes d'une conjointe doivent être calculées dans le même passage.
    ids = {q["id"] for q in out}
    return [q for q in out if "composantes" not in q or all(c in ids for c in q["composantes"])]


def observations():
    o = lire_json("modele/reseau/observations.json") or {}
    return o.get("etats", {})


if __name__ == "__main__":
    args = sys.argv[1:]
    structure = lire_json("modele/reseau/structure_v0.json")
    tables = lire_json("modele/reseau/tables_v0.json")
    if tables is None:
        sys.exit("modele/reseau/tables_v0.json absent : tables non encore élicitées.")
    nt = int(args[args.index("--tirages") + 1]) if "--tirages" in args else 200
    ntr = int(args[args.index("--trajectoires") + 1]) if "--trajectoires" in args else 100
    if "--controle" in args:
        qs = questions_banque(structure, lire_json("modele/evenements.json")["evenements"])
        prev = prevoir(structure, tables, observations(), qs, nt, ntr)
        alertes = 0
        for q in qs:
            p = prev[q["id"]]
            direct = tables.get("direct", {}).get(q["id"].removeprefix("Q-"))
            cle = "oui" if "oui" in p else next(iter(p))
            ecart = "" if direct is None or not isinstance(direct, (int, float)) else f"  évaluateurs {direct}"
            if ecart and abs(p[cle] - direct) > 10:
                ecart += "  ÉCART > 10 points"
                alertes += 1
            print(f"{q['id']:10} {json.dumps({k: v for k, v in p.items() if k != 'i80'}, ensure_ascii=False)}  i80 {p['i80']}{ecart}")
        print(f"{alertes} écart(s) de plus de 10 points")
        sys.exit(0)
    etiquette = args[0]
    if "--registre" not in args:
        sys.exit("Indiquer --registre registre/<fichier>.jsonl")
    reg = args[args.index("--registre") + 1]
    qs = questions_cycle(structure, etiquette)
    prev = prevoir(structure, tables, observations(), qs, nt, ntr)
    lignes = [{"question": q["id"], "probabilites": {k: v for k, v in prev[q["id"]].items() if k != "i80"},
               "piste": "v0", "auteur": VERSION, "version": tables.get("version", VERSION),
               "origine": f"cycle {etiquette}", "donnees": f"gel du cycle {etiquette}",
               "intervalle_80": prev[q["id"]]["i80"]} for q in qs]
    from registre import ajouter
    t = ajouter(reg, lignes)
    print(f"{len(lignes)} prévisions du réseau ajoutées à {reg}, émises le {t}")
