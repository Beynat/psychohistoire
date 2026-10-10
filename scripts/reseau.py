"""Moteur du réseau bayésien dynamique v0 (feuille de route v0, bloc 4).

Usage :
    python scripts/reseau.py ETIQUETTE [--registre registre/<fichier>.jsonl] [--tirages 200] [--trajectoires 100]
    python scripts/reseau.py --controle          (contrôle de cohérence seul, sans écriture)

Lit modele/reseau/structure_v0.json (nœuds, parents, mesures) et modele/reseau/tables_v0.json (paramètres
agrégés des évaluateurs), simule le réseau mois par mois d'octobre 2026 à septembre 2028 et calcule, pour
chaque question de la banque rattachée, la probabilité de ses issues. Avec --registre, écrit ces prévisions
au registre par scripts/registre.py (auteur « réseau v0 », champ « version »), pour les questions du cycle
ETIQUETTE.

Paramétrage (jamais de probabilité mensuelle demandée aux évaluateurs) :
- nœud « daté » : loi de base de ses issues, parents à leur état de référence ; pour chaque autre état d'un
  parent, un multiplicateur sur la cote de chaque issue (modèle log-linéaire sans interaction) ;
- nœud « à tout moment » : probabilité de survenue sur toute sa fenêtre, parents à leur état de référence,
  convertie en risque mensuel constant h = 1 - (1 - P)^(1 / n) ; multiplicateurs sur ce risque selon l'état
  courant des parents ;
- variable d'état : matrice de transition d'un mois au suivant (ligne = état du mois précédent), et
  multiplicateurs sur la cote de chaque état d'arrivée selon l'état des parents ;
- mesure (question de la banque) : probabilité de « oui » selon la valeur d'une caractéristique de la
  trajectoire (issue d'un pivot, survenue d'un événement dans une fenêtre, état maximal d'une variable sur des
  mois donnés), ou correspondance exacte (0 ou 100 %).

Incertitude : chaque tirage perturbe les paramètres en log-cotes (écart-type « sigma » de chaque nœud, au moins
0,3, noyau section 4.4), puis simule des trajectoires ; la prévision est la moyenne, publiée avec l'intervalle
à 80 % entre tirages.
"""
import json
import math
import random
import sys
from datetime import date

from commun import RACINE, lire_json

VERSION = "réseau v0"
DEBUT, FIN = (2026, 10), (2028, 9)
SIGMA_PLANCHER = 0.3


def mois_liste():
    a, m = DEBUT
    out = []
    while (a, m) <= FIN:
        out.append(f"{a:04d}-{m:02d}")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return out


MOIS = mois_liste()


def idx_mois(s):
    """Index du mois d'une date AAAA-MM ou AAAA-MM-JJ (borné à la période simulée)."""
    k = s[:7]
    if k < MOIS[0]:
        return 0
    if k > MOIS[-1]:
        return len(MOIS) - 1
    return MOIS.index(k)


def logit(p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def normaliser(d):
    s = sum(d.values())
    return {k: v / s for k, v in d.items()} if s > 0 else {k: 1 / len(d) for k in d}


def appliquer_mult(base, mults):
    """Multiplie la cote de chaque issue (rapport à la somme des autres) par son multiplicateur, renormalise."""
    poids = {k: base[k] * mults.get(k, 1.0) for k in base}
    return normaliser(poids)


def tirer(dist, rng):
    u, c = rng.random(), 0.0
    for k, v in dist.items():
        c += v
        if u <= c:
            return k
    return k


def perturber(tables, rng):
    """Un jeu de paramètres : perturbation en log-cotes (lois de base, transitions, risques) et en log (multiplicateurs)."""
    out = {}
    for nid, t in tables["noeuds"].items():
        s = max(t.get("sigma", SIGMA_PLANCHER), SIGMA_PLANCHER)
        u = dict(t)
        if "base" in t:
            u["base"] = normaliser({k: 1 / (1 + math.exp(-(logit(v) + rng.gauss(0, s)))) for k, v in t["base"].items()})
        if "p_fenetre" in t:
            u["p_fenetre"] = 1 / (1 + math.exp(-(logit(t["p_fenetre"]) + rng.gauss(0, s))))
        if "transition" in t:
            u["transition"] = {e: normaliser({k: 1 / (1 + math.exp(-(logit(v) + rng.gauss(0, s)))) for k, v in ligne.items()})
                               for e, ligne in t["transition"].items()}
        if "multiplicateurs" in t:
            u["multiplicateurs"] = {par: {etat: {iss: m * math.exp(rng.gauss(0, s / 2)) for iss, m in d.items()}
                                          for etat, d in par_d.items()}
                                    for par, par_d in t["multiplicateurs"].items()}
        out[nid] = u
    return out


def mults_parents(t, etat_parents):
    """Produit des multiplicateurs des parents qui ne sont pas à leur état de référence."""
    tot = {}
    for par, etat in etat_parents.items():
        for iss, m in t.get("multiplicateurs", {}).get(par, {}).get(etat, {}).items():
            tot[iss] = tot.get(iss, 1.0) * m
    return tot


def ordre(structure):
    """Ordre topologique au sein d'une tranche ; les parents « mois précédent » ne créent pas d'arête."""
    noeuds = {n["id"]: n for n in structure["variables_etat"] + structure["pivots"]}
    vus, out = set(), []

    def visiter(i, pile):
        if i in vus:
            return
        if i in pile:
            raise SystemExit(f"Cycle au sein d'une tranche passant par {i} : {' → '.join(pile + [i])}")
        for p in noeuds[i].get("parents", []):
            if p in noeuds:
                visiter(p, pile + [i])
        vus.add(i)
        out.append(i)
    for i in noeuds:
        visiter(i, [])
    return out, noeuds


def simuler(structure, params, initial, rng):
    """Une trajectoire : pour chaque nœud, l'état mois par mois (variables, pivots « à tout moment ») ou l'issue
    et son mois (pivots datés)."""
    rangs, noeuds = ordre(structure)
    traj = {i: [None] * len(MOIS) for i in noeuds}
    for k in range(len(MOIS)):
        for i in rangs:
            n, t = noeuds[i], params[i]
            parents = {p: traj[p][k] for p in n.get("parents", []) if p in traj}
            if n["id"].startswith("VE-"):
                prec = traj[i][k - 1] if k else initial.get(i, t["reference"])
                if k == 0 and i in initial:
                    traj[i][k] = initial[i]
                    continue
                dist = appliquer_mult(t["transition"][prec], mults_parents(t, {p: e for p, e in parents.items() if e is not None}))
                traj[i][k] = tirer(dist, rng)
            elif n["nature"] == "daté":
                km = idx_mois(n["date"])
                if k < km:
                    continue
                if k == km:
                    obs = initial.get(i)
                    traj[i][k] = obs if obs else tirer(appliquer_mult(t["base"], mults_parents(t, {p: e for p, e in parents.items() if e is not None})), rng)
                else:
                    traj[i][k] = traj[i][k - 1]
            else:   # à tout moment
                d0, d1 = idx_mois(n["fenetre"][0]), idx_mois(n["fenetre"][1])
                if k and traj[i][k - 1] == "oui":
                    traj[i][k] = "oui"
                    continue
                if not (d0 <= k <= d1):
                    traj[i][k] = "non" if k > d1 or k < d0 else None
                    continue
                h = 1 - (1 - t["p_fenetre"]) ** (1 / (d1 - d0 + 1))
                m = mults_parents(t, {p: e for p, e in parents.items() if e is not None}).get("oui", 1.0)
                h = min(h * m, 0.95)
                traj[i][k] = "oui" if rng.random() < h else "non"
    return traj


def caracteristique(mesure, traj, structure):
    """Valeur, sur une trajectoire, de la caractéristique d'une mesure."""
    c = mesure["caracteristique"]
    if c["type"] == "issue":
        return traj[c["noeud"]][-1] if traj[c["noeud"]][-1] is not None else next((x for x in reversed(traj[c["noeud"]]) if x), None)
    if c["type"] == "survenue":
        a, b = idx_mois(c["debut"]), idx_mois(c["fin"])
        return "oui" if any(traj[c["noeud"]][k] == "oui" for k in range(a, b + 1)) else "non"
    if c["type"] == "etat_max":
        etats = c["ordre"]
        a, b = idx_mois(c["debut"]), idx_mois(c["fin"])
        vals = [traj[c["noeud"]][k] for k in range(a, b + 1) if traj[c["noeud"]][k] is not None]
        return max(vals, key=etats.index) if vals else None
    if c["type"] == "conjonction":
        return "|".join(str(caracteristique({"caracteristique": s}, traj, structure)) for s in c["elements"])
    raise SystemExit(f"Caractéristique inconnue : {c['type']}")


def prevoir(structure, tables, initial, tirages=200, trajectoires=100, graine=20261010):
    rng = random.Random(graine)
    mesures = tables["mesures"]
    par_tirage = {q: [] for q in mesures}
    for _ in range(tirages):
        params = perturber(tables, rng)
        cpt = {q: {} for q in mesures}
        for _ in range(trajectoires):
            traj = simuler(structure, params, initial, rng)
            for q, m in mesures.items():
                v = caracteristique(m, traj, structure)
                p = m["table"].get(str(v), m["table"].get("*", 0.0)) / 100
                cpt[q]["oui"] = cpt[q].get("oui", 0.0) + p
        for q in mesures:
            par_tirage[q].append(cpt[q]["oui"] / trajectoires)
    out = {}
    for q, xs in par_tirage.items():
        xs = sorted(xs)
        moy = sum(xs) / len(xs)
        out[q] = {"oui": round(100 * moy, 1), "non": round(100 * (1 - moy), 1),
                  "i80": [round(100 * xs[int(0.1 * (len(xs) - 1))], 1), round(100 * xs[int(0.9 * (len(xs) - 1))], 1)]}
    return out


def controle(structure, tables, initial, prev):
    """Écart entre la probabilité du réseau et celle donnée directement par les évaluateurs sur la fenêtre de
    chaque question (champ « direct » de la mesure) : au-delà de 10 points, signalé."""
    alertes = []
    for q, m in tables["mesures"].items():
        if m.get("direct") is not None and abs(prev[q]["oui"] - m["direct"]) > 10:
            alertes.append(f"{q} : réseau {prev[q]['oui']} %, évaluateurs {m['direct']} % (écart > 10 points)")
    return alertes


def charger():
    structure = lire_json("modele/reseau/structure_v0.json")
    tables = lire_json("modele/reseau/tables_v0.json")
    if tables is None:
        raise SystemExit("modele/reseau/tables_v0.json absent : tables non encore élicitées.")
    initial = (lire_json("modele/reseau/observations.json") or {}).get("etats", {})
    return structure, tables, initial


if __name__ == "__main__":
    args = sys.argv[1:]
    structure, tables, initial = charger()
    nt = int(args[args.index("--tirages") + 1]) if "--tirages" in args else 200
    ntr = int(args[args.index("--trajectoires") + 1]) if "--trajectoires" in args else 100
    prev = prevoir(structure, tables, initial, nt, ntr)
    alertes = controle(structure, tables, initial, prev)
    for a in alertes:
        print("ALERTE", a)
    if "--controle" in args:
        for q, p in sorted(prev.items()):
            print(f"{q:12} {p['oui']:5} %  [{p['i80'][0]} ; {p['i80'][1]}]")
        sys.exit(1 if alertes else 0)
    etiquette = args[0]
    reg = args[args.index("--registre") + 1] if "--registre" in args else None
    if not reg:
        sys.exit("Indiquer --registre registre/<fichier>.jsonl")
    qs = {q["id"]: q for q in lire_json(f"data/cycles/{etiquette}/questions.json")["questions"]}
    lignes = []
    for q, m in tables["mesures"].items():
        for qid in m.get("questions_cycle", [f"Q-{q}"]):
            if qid in qs and set(qs[qid]["issues"]) == {"oui", "non"}:
                lignes.append({"question": qid, "probabilites": {"oui": prev[q]["oui"], "non": prev[q]["non"]},
                               "piste": "v0", "auteur": VERSION, "version": tables.get("version", VERSION),
                               "origine": f"cycle {etiquette}", "donnees": f"gel du cycle {etiquette}",
                               "intervalle_80": prev[q]["i80"]})
    from registre import ajouter
    t = ajouter(reg, lignes)
    print(f"{len(lignes)} prévisions du réseau ajoutées à {reg}, émises le {t}")
