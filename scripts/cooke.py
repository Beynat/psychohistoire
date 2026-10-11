"""Pondération des évaluateurs par le modèle classique de Cooke (feuille de route, étape 12).

Questions graines : l'état mensuel de chaque variable du réseau (VE-*). Chaque évaluateur de tables a donné, pour ces
nœuds, une loi par cas ; sa prévision d'une graine est sa loi au cas observé (état du mois précédent, parents décalés
observés), sans simulation. Un parent du même mois, inconnu à l'enregistrement, donne une loi par état de ce parent :
la graine est notée sur la loi de l'état réalisé (prévision conditionnelle). Un parent daté pas encore tranché est
remplacé par sa loi a priori du réseau, comme dans le moteur.

Usage : python scripts/cooke.py graines AAAA-MM     enregistre, au plus tard le 1er du mois, les prévisions de
                                                   chaque évaluateur pour le mois (modele/reseau/graines.jsonl,
                                                   ajout seul, horodaté par le script) ; au cycle mensuel, étape 4 bis
        python scripts/cooke.py scores              calibration, information et poids par évaluateur et par lot,
                                                   sur les graines résolues ; écrit modele/reseau/poids_cooke.json

Calibration (événements discrets) : chaque probabilité donnée à un état est un événement binaire, rangé par tranche
de 10 points ; statistique 2 Σ n_b I(s_b, p_b) (I : entropie relative entre fréquence observée s_b et probabilité
moyenne p_b de la tranche), comparée à un χ² à B degrés de liberté (B tranches non vides) ; C = 1 - F(stat).
Information : entropie relative moyenne de la loi donnée par rapport à la loi uniforme sur les états.
Poids : C × I si C ≥ α, sinon 0 ; α choisi, lot par lot, pour maximiser le score (C × I) du décideur (moyenne
pondérée des lois). Activation : un lot n'est pondéré que si chacun de ses évaluateurs a au moins MIN_GRAINES graines
résolues ; sinon poids égaux. Les poids s'appliquent à toutes les tables de l'évaluateur (mêmes rondes, même lot),
par moyenne pondérée des log-cotes (`tables.py agreger_cas --poids`).
"""
import glob
import json
import math
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import reseau
import tables
from commun import RACINE, lire_json, lire_jsonl

FICHIER = "modele/reseau/graines.jsonl"
SORTIE = "modele/reseau/poids_cooke.json"
MIN_GRAINES = 12
TRANCHES = [i / 10 for i in range(11)]


def mois_prec(m, k=1):
    a, mm = int(m[:4]), int(m[5:]) - k
    while mm < 1:
        a, mm = a - 1, mm + 12
    return f"{a:04d}-{mm:02d}"


def etat_observe(obs, noeud, n, mois):
    """État observé d'un nœud pour un mois : variable, valeur du mois ; pivot « à tout moment », « oui » s'il est
    survenu au plus tard ce mois, « non » sinon ; pivot daté, issue observée, ou None s'il n'est pas tranché."""
    d = obs.get(noeud, {})
    if "etats" in n:
        e = d.get(mois)
        return e if isinstance(e, str) else None
    if n.get("nature") == "à tout moment":
        return "oui" if any(m <= mois and e == "oui" for m, e in d.items()) else "non"
    vus = [e for m, e in d.items() if m <= mois]
    return vus[-1] if vus else None


def reponses():
    """Réponses par évaluateur (dernière ronde), lues dans les dossiers d'élicitation du dépôt."""
    out = {}
    for f in sorted(glob.glob(str(RACINE / "modele/reseau/elicitation_*/E*.json"))):
        if "ronde1" in f or "retour" in f:
            continue
        r = json.load(open(f, encoding="utf-8"))
        if isinstance(r, dict) and r.get("evaluateur") and "noeuds" in r:
            out[r["evaluateur"]] = r
    return out


def evaluateurs_actuels(t):
    """Évaluateurs dont les lois forment les tables actuelles, nœud par nœud."""
    return {i: n.get("evaluateurs", []) for i, n in t["noeuds"].items()}


def prevision(rep, nid, n, noeuds, obs, mois, priors):
    """Loi de l'évaluateur pour le nœud au mois, conditionnelle aux parents du même mois : {clé de condition: loi}."""
    prec = etat_observe(obs, nid, n, mois_prec(mois))
    if prec is None:
        return None
    etats, inconnus = {}, []
    for q in n.get("parents", []):
        qid, d = reseau.pid(q), (q.get("decalage", 0) if isinstance(q, dict) else 0)
        qn = noeuds[qid]
        e = etat_observe(obs, qid, qn, mois_prec(mois, d)) if d else None
        if e is None and d == 0 and ("etats" in qn or qn.get("nature") == "à tout moment"):
            inconnus.append(qid)
            continue
        if e is None:
            if qn.get("nature") == "daté" and qid in priors:
                e = reseau.APriori(priors[qid])
            else:
                return None
        etats[qid] = e
    lois = {"cas": tables.lois_de(rep, nid, tables.cas_du_noeud(n, noeuds))}
    import itertools
    out = {}
    for combo in itertools.product(*[tables.etats(noeuds[q]) for q in inconnus]):
        cle = "|".join(f"{q}={e}" for q, e in zip(inconnus, combo))
        v = reseau.valeur_cas(lois, n, {**etats, **dict(zip(inconnus, combo))}, noeuds, prec)
        s = sum(v.values())
        out[cle] = {k: round(x / s, 6) for k, x in v.items()}
    return {"conditions": inconnus, "lois": out}


def graines(mois, maintenant=None):
    maintenant = maintenant or datetime.now(ZoneInfo("Europe/Paris"))
    if maintenant.strftime("%Y-%m-%d") > f"{mois}-01":
        sys.exit(f"Graines de {mois} : enregistrement possible au plus tard le {mois}-01 (antériorité).")
    o = lire_json("modele/reseau/observations.json") or {}
    if (o.get("etabli_le") or "")[:7] <= mois_prec(mois):
        sys.exit(f"Graines de {mois} : les observations de {mois_prec(mois)} ne sont pas closes (établies le "
                 f"{o.get('etabli_le')}) ; mettre à jour modele/reseau/observations.json d'abord.")
    deja = {(g["mois"], g["noeud"], g["evaluateur"]) for g in lire_jsonl(FICHIER)}
    s = lire_json("modele/reseau/structure_v0.json")
    t = lire_json("modele/reseau/tables_v0.json")
    noeuds = {n["id"]: n for n in s["variables_etat"] + s["pivots"]}
    obs = o.get("etats", {})
    priors = reseau.lois_a_priori(s, t, reseau.observations(s))
    reps = reponses()
    lignes = []
    for nid, evs in evaluateurs_actuels(t).items():
        n = noeuds.get(nid)
        if not n or "etats" not in n:
            continue
        for e in evs:
            if (mois, nid, e) in deja or e not in reps or nid not in reps[e]["noeuds"]:
                continue
            p = prevision(reps[e], nid, n, noeuds, obs, mois, priors)
            if p:
                lignes.append({"mois": mois, "noeud": nid, "evaluateur": e, **p,
                               "enregistre_le": maintenant.isoformat(timespec="seconds")})
    with (RACINE / FICHIER).open("a", encoding="utf-8", newline="\n") as h:
        for x in lignes:
            h.write(json.dumps(x, ensure_ascii=True) + "\n")
    return lignes


def resolues(gs, obs, etabli_le, noeuds):
    """Graines dont le mois est clos à la dernière mise à jour des observations : (évaluateur, loi, état réalisé)."""
    out = []
    for g in gs:
        if (etabli_le or "")[:7] <= g["mois"]:
            continue
        reel = etat_observe(obs, g["noeud"], noeuds[g["noeud"]], g["mois"])
        cond = "|".join(f"{q}={etat_observe(obs, q, noeuds[q], g['mois'])}" for q in g["conditions"])
        if reel is None or cond not in g["lois"]:
            continue
        out.append((g["evaluateur"], g["mois"], g["noeud"], g["lois"][cond], reel))
    return out


def chi2_sf(x, k):
    """P(χ²_k > x), par la fonction gamma incomplète régularisée (série et fraction continue)."""
    if x <= 0:
        return 1.0
    a, z = k / 2, x / 2
    if z < a + 1:
        s, term, n = 1 / a, 1 / a, a
        while abs(term) > 1e-12 * abs(s):
            n += 1
            term *= z / n
            s += term
        return max(0.0, 1 - s * math.exp(-z + a * math.log(z) - math.lgamma(a)))
    b, c, d = z + 1 - a, 1e300, 1 / (z + 1 - a)
    h = d
    for i in range(1, 300):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1 / d if abs(d) > 1e-300 else 1e300
        c = b + an / c if abs(c) > 1e-300 else b
        h *= d * c
    return min(1.0, math.exp(-z + a * math.log(z) - math.lgamma(a)) * h)


def calibration(items):
    """items : [(loi, état réalisé)]. Rend C (0 à 1)."""
    tr = {}
    for loi, reel in items:
        for e, p in loi.items():
            b = min(int(p * 10), 9)
            tr.setdefault(b, []).append((p, 1.0 if e == reel else 0.0))
    stat = 0.0
    for xs in tr.values():
        n = len(xs)
        p = min(max(sum(x for x, _ in xs) / n, 1e-6), 1 - 1e-6)
        s = sum(y for _, y in xs) / n
        i = (s * math.log(s / p) if s > 0 else 0.0) + ((1 - s) * math.log((1 - s) / (1 - p)) if s < 1 else 0.0)
        stat += 2 * n * i
    return chi2_sf(stat, len(tr))


def information(items):
    """Entropie relative moyenne par rapport à la loi uniforme sur les états."""
    tot = 0.0
    for loi, _ in items:
        k = len(loi)
        tot += sum(p * math.log(p * k) for p in loi.values() if p > 0)
    return tot / len(items) if items else 0.0


def poids_alpha(scores, alpha):
    """Poids non normalisés : C × I si la calibration atteint α, 0 sinon."""
    return {e: (c * i if c >= alpha else 0.0) for e, (c, i) in scores.items()}


def poids_lot(par_eval):
    """par_eval : {évaluateur: [(clé de graine, loi, réel)]}. Poids normalisés et α retenu."""
    scores = {e: (calibration([(l, r) for _, l, r in xs]), information([(l, r) for _, l, r in xs])) for e, xs in par_eval.items()}
    communs = set.intersection(*(set(k for k, _, _ in xs) for xs in par_eval.values()))
    meilleur = None
    for alpha in sorted({0.0} | {c for c, _ in scores.values()}):
        w = poids_alpha(scores, alpha)
        if sum(w.values()) <= 0:
            continue
        w = {e: x / sum(w.values()) for e, x in w.items()}
        dm = []
        for k in sorted(communs):
            lois = {e: next(l for kk, l, _ in par_eval[e] if kk == k) for e in par_eval}
            reel = next(r for kk, _, r in next(iter(par_eval.values())) if kk == k)
            etats_ = list(next(iter(lois.values())))
            dm.append(({s: sum(w[e] * lois[e].get(s, 0) for e in lois) for s in etats_}, reel))
        sc = calibration(dm) * information(dm) if dm else 0.0
        if meilleur is None or sc > meilleur[0] + 1e-12:
            meilleur = (sc, alpha, w)
    return {"scores": {e: {"calibration": round(c, 4), "information": round(i, 4), "graines": len(par_eval[e])}
                       for e, (c, i) in scores.items()},
            "alpha": meilleur[1] if meilleur else None, "score_decideur": round(meilleur[0], 4) if meilleur else None,
            "poids": {e: round(x, 4) for e, x in meilleur[2].items()} if meilleur else None}


def scores(min_graines=MIN_GRAINES):
    s = lire_json("modele/reseau/structure_v0.json")
    t = lire_json("modele/reseau/tables_v0.json")
    noeuds = {n["id"]: n for n in s["variables_etat"] + s["pivots"]}
    o = lire_json("modele/reseau/observations.json")
    res = resolues(lire_jsonl(FICHIER), o.get("etats", {}), o.get("etabli_le"), noeuds)
    lots = {}
    for nid, evs in evaluateurs_actuels(t).items():
        if evs:
            lots.setdefault(tuple(sorted(evs)), set()).add(nid)
    out = {"min_graines": min_graines, "lots": []}
    for evs, nids in sorted(lots.items()):
        par_eval = {e: [(f"{m}|{nid}", loi, reel) for (ev, m, nid, loi, reel) in res if ev == e and nid in nids] for e in evs}
        actif = all(len(x) >= min_graines for x in par_eval.values())
        lot = {"evaluateurs": list(evs), "noeuds": sorted(nids), "actif": actif,
               "graines": {e: len(x) for e, x in par_eval.items()}}
        if actif:
            lot.update(poids_lot(par_eval))
        out["lots"].append(lot)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["graines"] and len(a) == 2:
        print(f"{len(graines(a[1]))} graines enregistrées pour {a[1]}")
    elif a[:1] == ["scores"]:
        r = scores()
        (RACINE / SORTIE).write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", "utf-8")
        print(json.dumps(r, ensure_ascii=False))
    else:
        sys.exit(__doc__)
