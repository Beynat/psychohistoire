"""Moteur du réseau bayésien dynamique v0 (feuille de route v0, bloc 4).

Usage :
    python scripts/reseau.py --effet J-026 [observé|manqué] [JOUR]   ou   --effet '{preuve en JSON}'
        Effet d'un jalon ou d'une preuve sur tout le réseau (pivots et questions, avant → après, trié), avec le
        nombre de trajectoires effectives.
    python scripts/reseau.py --controle [--tirages N] [--trajectoires N]
        Prévisions sur les fenêtres de la banque et contrôle de cohérence avec les probabilités données
        directement par les évaluateurs ; aucune écriture.
    python scripts/reseau.py --geler
        Gèle la version témoin du réseau (modele/reseau/gele/, une seule fois ; étape 6).
    python scripts/reseau.py ETIQUETTE --registre registre/<fichier>.jsonl [--gele] [--tirages N] [--trajectoires N]
        Avec --gele : prévisions de la version témoin, auteur « réseau v0 gelé ». Sans : réseau courant, refusé si la
        structure, les tables ou le calendrier ont été modifiés dans les 48 heures avant le gel du cycle.
        Prévisions pour les questions du cycle ETIQUETTE (fenêtre propre à chaque question), écrites au registre
        par scripts/registre.py, auteur « réseau v0 », avec la version des tables et l'intervalle à 80 %.

Fichiers : modele/reseau/structure_v0.json (nœuds, parents, mesures), modele/reseau/tables_v0.json (paramètres
agrégés des évaluateurs, scripts/tables.py), modele/reseau/observations.json (états observés par mois).

Paramétrage (aucune probabilité mensuelle n'est demandée aux évaluateurs) :
- pivot « daté » : loi de base de ses issues, parents à leur état de référence ; un multiplicateur sur le poids de
  chaque issue pour chaque autre état d'un parent (log-linéaire, sans interaction) ; ou une loi par état d'un
  parent (« conditionnelle ») ; des exclusions (issue impossible selon l'état d'un parent) ;
- pivot « à tout moment » : probabilité de survenue sur sa fenêtre, parents de référence ; un multiplicateur par
  état de parent, demandé sur cette probabilité de fenêtre. Le moteur applique d'abord les multiplicateurs à la
  probabilité de fenêtre (rapport de probabilités quand il la baisse, rapport de cotes quand il la relève, pour rester
  sous 1), puis convertit en risque mensuel constant h = 1 - (1 - P')^(1/n), n mois de la fenêtre. Le multiplicateur
  n'est donc jamais composé de mois en mois (correction du 10 octobre 2026, feuille de route, étape 1). Quand un
  parent « à tout moment » survient en cours de fenêtre (déclencheur), n compte les mois restants depuis sa
  survenue : la probabilité qu'il implique porte sur le reste de la fenêtre. Un profil (« profil », étape 3) répartit
  la probabilité de fenêtre selon le poids de chaque mois (revues programmées des agences pour PV-NOTE) :
  h_k = 1 - (1 - P')^(w_k / Σw) ;
- verrou daté (« verrous » de la structure) : une issue juridiquement impossible pendant une durée après un fait
  (article 12 : pas de nouvelle dissolution dans l'année qui suit les élections) met le risque à zéro ;
- parent daté pas encore tranché : son multiplicateur est la moyenne de ses multiplicateurs sous sa loi a priori
  (estimée par le moteur, voir lois_a_priori), et non celui de son état de référence ;
- variable d'état : transition d'un mois au suivant, multiplicateurs par état de parent ;
- parent « decalage » : 1 = état du mois précédent (seul moyen de boucler sans cycle au sein d'un mois) ;
- mesure : une question de la banque en fonction d'une caractéristique de la trajectoire.

Observations : un état observé remplace le tirage. Pour une variable définie comme le maximum du mois (« agregat » :
« maximum »), l'observation du mois en cours (mois de « etabli_le » ou après) n'est qu'un minimum : le tirage est
restreint aux états au moins égaux.

Intervalle à 80 % : quantiles, entre tirages de paramètres, de la probabilité estimée, après retrait de la variance
de simulation (écarts des tirages à la moyenne réduits du facteur √((V − W) / V), V variance entre tirages, W
variance d'échantillonnage moyenne au sein d'un tirage).
"""
import json
import math
import random
import sys

from pathlib import Path

from commun import lire_json

VERSION = "réseau v0"
VERSION_GELEE = "réseau v0 gelé"
FICHIERS_RESEAU = ("modele/reseau/structure_v0.json", "modele/reseau/tables_v0.json", "modele/reseau/calendrier.json")
DOSSIER_GELE = "modele/reseau/gele"
DELAI_GEL_HEURES = 48
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
        if "cas" in t:
            u["cas"] = {c: (bruit(v) if isinstance(v, dict) else sig(logit(v) + rng.gauss(0, s)) if 0 < v < 1 else v)
                        for c, v in t["cas"].items()}
        if "multiplicateurs" in t:
            u["multiplicateurs"] = {par: {etat: {iss: m * math.exp(rng.gauss(0, s / 2)) for iss, m in d.items()}
                                          for etat, d in pd.items()} for par, pd in t["multiplicateurs"].items()}
        out[nid] = u
    return out


class APriori(dict):
    """État d'un parent daté pas encore tranché : sa loi a priori {issue: probabilité}."""


def multiplicateurs(t, etats):
    """Produit des multiplicateurs des parents. Parent pas encore tranché (APriori) : moyenne de ses multiplicateurs
    sous sa loi a priori, l'état de référence valant 1."""
    tot = {}
    for par, etat in etats.items():
        md = t.get("multiplicateurs", {}).get(par, {})
        if isinstance(etat, APriori):
            cibles = {c for d in md.values() for c in d}
            for iss in cibles:
                m = sum(p * md.get(e, {}).get(iss, 1.0) for e, p in etat.items())
                tot[iss] = tot.get(iss, 1.0) * m
            continue
        for iss, m in md.get(etat, {}).items():
            tot[iss] = tot.get(iss, 1.0) * m
    return tot


def p_modifiee(p, m):
    """Probabilité de fenêtre p après un multiplicateur m : rapport de probabilités si m ≤ 1, rapport de cotes si
    m > 1 (la probabilité reste sous 1 ; les deux coïncident pour une probabilité faible)."""
    if m <= 1:
        return p * m
    return p * m / (1 - p + p * m)


_PROFILS = {}
CHEMIN_CALENDRIER = "modele/reseau/calendrier.json"   # calendrier gelé pour la version témoin (charger)


def profil(n):
    """Poids de chaque mois de la fenêtre d'un pivot « à tout moment » (liste alignée sur MOIS). Sans profil : 1 par
    mois (risque constant). Profil « PV-NOTE » (calendrier.json, étape 3) : poids de revue pour chaque revue
    programmée du mois, poids hors revue sinon ; un profil peut aussi être donné en ligne {"poids": {mois: w},
    "defaut": w}."""
    cle = (n["id"], json.dumps(n.get("profil"), sort_keys=True))
    if cle in _PROFILS:
        return _PROFILS[cle]
    pr = n.get("profil")
    w = [1.0] * len(MOIS)
    if isinstance(pr, str):
        cal = lire_json(CHEMIN_CALENDRIER)
        d = cal["profils"][pr]
        revues = {}
        for e in cal["entrees"]:
            if e.get("revue"):
                revues[e["date"][:7]] = revues.get(e["date"][:7], 0) + d["poids_revue"]
        w = [revues.get(m, d["poids_hors_revue"]) for m in MOIS]
    elif isinstance(pr, dict):
        w = [pr["poids"].get(m, pr.get("defaut", 1.0)) for m in MOIS]
    _PROFILS[cle] = w
    return w


def premier_oui(x, k):
    """Mois de survenue d'un pivot « à tout moment » avant le mois k, ou None."""
    return next((j for j in range(k) if x[j] == "oui"), None)


def appliquer(base, mults, exclus=()):
    poids = {k: (0.0 if any(c in k.split("-") for c in exclus) else v * mults.get(k, 1.0)) for k, v in base.items()}
    return normaliser(poids)


PRIORS = None   # lois a priori des pivots datés {nœud: {issue: p}}, calculées par lois_a_priori


def cles_cas(n, etats, noeuds, prec=None):
    """Clés de la table par cas d'un nœud (« lois par cas », étape 4) : « prec=état » pour une variable d'état, puis
    « parent=état » dans l'ordre des parents. Un parent daté pas encore tranché est remplacé par sa loi a priori :
    rend la liste des (poids, clé). Parent absent : état de référence (variable), « non » (pivot à tout moment),
    première issue (pivot daté sans loi a priori)."""
    combos = [(1.0, [f"prec={prec}"] if prec is not None else [])]
    for q in n.get("parents", []):
        qid, qn = pid(q), noeuds.get(pid(q), {})
        e = etats.get(qid)
        if e is None:
            e = qn.get("reference") if "etats" in qn else ("non" if qn.get("nature") == "à tout moment" else (qn.get("issues") or ["?"])[0])
        options = [(p, x) for x, p in e.items()] if isinstance(e, APriori) else [(1.0, e)]
        combos = [(w * pw, c + [f"{qid}={x}"]) for w, c in combos for pw, x in options if pw > 0]
    return [(w, "|".join(c)) for w, c in combos]


def valeur_cas(t, n, etats, noeuds, prec=None):
    """Valeur de la table par cas (probabilité de fenêtre, ou loi), mélangée sur les parents non tranchés."""
    acc = None
    for w, c in cles_cas(n, etats, noeuds, prec):
        v = t["cas"][c]
        if isinstance(v, dict):
            acc = {k: (acc or {}).get(k, 0.0) + w * x for k, x in v.items()}
        else:
            acc = (acc or 0.0) + w * v
    return acc


def simuler(structure, params, obs, rng, priors=None, rngs=None):
    """Une trajectoire. rngs : générateur propre à chaque nœud (nombres aléatoires communs entre deux jeux de
    paramètres, pour l'analyse de sensibilité) ; à défaut, rng pour tous. obs : {nœud: {mois: état}} observé ; un état observé remplace le tirage ; un état
    {"au_moins": e} restreint le tirage aux états au moins égaux à e. priors : lois a priori des pivots datés,
    utilisées tant qu'un parent daté n'est pas tranché (à défaut, PRIORS ; sans loi, état de référence)."""
    priors = PRIORS if priors is None else priors
    rangs, noeuds = ordre(structure)
    verrous = structure.get("verrous", [])
    traj = {i: [None] * len(MOIS) for i in noeuds}
    for k in range(len(MOIS)):
        for i in rangs:
            n, t = noeuds[i], params[i]
            r = rngs[i] if rngs else rng
            etats = {}
            for p in n.get("parents", []):
                kk = k - dec(p)
                if kk >= 0 and traj[pid(p)][kk] is not None:
                    etats[pid(p)] = traj[pid(p)][kk]
                elif kk >= 0 and noeuds.get(pid(p), {}).get("nature") == "daté" and (priors or {}).get(pid(p)):
                    etats[pid(p)] = APriori(priors[pid(p)])
            vu = obs.get(i, {}).get(MOIS[k])
            minimum = None
            if isinstance(vu, dict):
                minimum, vu = vu.get("au_moins"), None
            if i.startswith("VE-"):
                if vu:
                    traj[i][k] = vu
                    continue
                prec = traj[i][k - 1] if k else t.get("reference", n.get("reference"))
                if "cas" in t:
                    loi_k = normaliser(valeur_cas(t, n, etats, noeuds, prec))
                else:
                    loi_k = appliquer(t["transition"][prec], multiplicateurs(t, etats))
                if minimum:
                    rang = n["etats"].index(minimum)
                    loi_k = normaliser({e: (v if n["etats"].index(e) >= rang else 0.0) for e, v in loi_k.items()})
                traj[i][k] = tirer(loi_k, r)
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
                exclus = [c for par, d in n.get("exclusions", {}).items()
                          if not isinstance(etats.get(par), APriori) for c in d.get(etats.get(par), [])]
                if "cas" in t:
                    traj[i][k] = tirer(appliquer(valeur_cas(t, n, etats, noeuds), {}, exclus), r)
                    continue
                base = t["base"]
                cond = n.get("conditionnelle")
                if cond and cond in etats and not isinstance(etats[cond], APriori):
                    base = t["conditionnelle"][etats[cond]]
                traj[i][k] = tirer(appliquer(base, multiplicateurs(t, etats), exclus), r)
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
                verrou = False
                for v in verrous:
                    if i in v["interdit"]:
                        j = premier_oui(traj[v["si"]], k)
                        if j is not None and k <= j + v["duree_mois"]:
                            verrou = True
                if verrou:
                    traj[i][k] = "non"
                    continue
                if "cas" in t:
                    p = valeur_cas(t, n, etats, noeuds)
                else:
                    p = p_modifiee(t["p_fenetre"], multiplicateurs(t, etats).get("oui", 1.0))
                # Parent « à tout moment » survenu en cours de fenêtre (déclencheur : censure → départ du Premier
                # ministre) : la probabilité qu'il implique porte sur le reste de la fenêtre, à partir de sa survenue.
                debut = d0
                for q in n.get("parents", []):
                    qn = noeuds.get(pid(q))
                    if qn and qn.get("nature") == "à tout moment" and etats.get(pid(q)) == "oui" \
                            and ("cas" in t or t.get("multiplicateurs", {}).get(pid(q), {}).get("oui")):
                        debut = max(debut, premier_oui(traj[pid(q)], k + 1) + dec(q))
                w = profil(n)
                reste = sum(w[min(debut, k):d1 + 1])
                h = 1 - (1 - min(p, 1 - 1e-9)) ** (w[k] / reste) if reste > 0 else 0.0
                traj[i][k] = "oui" if r.random() < h else "non"
    return traj


def reference_de(n):
    if "etats" in n:
        return n["reference"]
    return "non" if n.get("nature") == "à tout moment" else n["issues"][0]


def effet_local(n, t, noeuds, parent, etat, issue):
    """Probabilité de l'issue d'un nœud quand le parent passe de son état de référence à « etat », les autres parents
    restant à leur référence (variable d'état : depuis son état de référence ; pivot « à tout moment » : probabilité
    de fenêtre). Sert aux tests de monotonie (étape 7). Rend (p_référence, p_état)."""
    def p(et):
        if "etats" in n:
            loi_ = normaliser(valeur_cas(t, n, et, noeuds, n["reference"])) if "cas" in t else \
                appliquer(t["transition"][n["reference"]], multiplicateurs(t, et))
            return loi_.get(issue, 0.0)
        if n.get("nature") == "à tout moment":
            v = valeur_cas(t, n, et, noeuds) if "cas" in t else p_modifiee(t["p_fenetre"], multiplicateurs(t, et).get("oui", 1.0))
            return v if issue == "oui" else 1 - v
        if "cas" in t:
            return normaliser(valeur_cas(t, n, et, noeuds)).get(issue, 0.0)
        base = t["conditionnelle"][et[n["conditionnelle"]]] if n.get("conditionnelle") in et and "conditionnelle" in t else t["base"]
        return appliquer(base, multiplicateurs(t, et)).get(issue, 0.0)
    ref = {pid(q): reference_de(noeuds[pid(q)]) for q in n.get("parents", [])}
    return p(ref), p({**ref, parent: etat})


def lois_a_priori(structure, tables, obs, n=1000, graine=7, passes=2):
    """Loi a priori de chaque pivot daté, estimée sur n trajectoires aux paramètres agrégés. Première passe avec les
    parents non tranchés à leur état de référence, passes suivantes avec les lois de la passe précédente (un pivot
    daté peut agir, avant d'être tranché, sur une variable dont dépend un autre pivot daté)."""
    params = {i: dict(t) for i, t in tables["noeuds"].items()}
    datés = [p for p in structure["pivots"] if p["nature"] == "daté"]
    priors = {}
    for _ in range(passes):
        rng = random.Random(graine)
        comptes = {p["id"]: {} for p in datés}
        for _ in range(n):
            traj = simuler(structure, params, obs, rng, priors=priors)
            for p in datés:
                v = traj[p["id"]][-1]
                comptes[p["id"]][v] = comptes[p["id"]].get(v, 0) + 1
        issues = {p["id"]: p.get("issues") or sorted(comptes[p["id"]]) for p in datés}
        priors = {i: {e: c.get(e, 0) / n for e in issues[i]} for i, c in comptes.items()}
    return priors


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


SEUIL_ESS = 0.05   # part minimale de trajectoires effectives ; en dessous : « combinaison trop rare »


def quantile_pondere(xs, ws, q):
    paires = sorted(zip(xs, ws))
    tot, c = sum(ws), 0.0
    for x, w in paires:
        c += w
        if c >= q * tot:
            return x
    return paires[-1][0]


def prevoir(structure, tables, obs, questions, tirages=200, trajectoires=100, graine=20261010, preuves=None):
    """questions : liste de {id, evenement, issues, fenetre: [début, fin]} ou de conjointes {id, composantes}.
    preuves : vraisemblances par issue (scripts/preuves.py) ; chaque trajectoire est pondérée par leur produit.
    Un pivot inscrit comme tranché dans obs devient une preuve « qui tranche » (ses parents sont mis à jour) ; si
    les trajectoires effectives tombent sous SEUIL_ESS, il est imposé à la place (intervention), ce qui est signalé.
    Rend {id: {issue: %, ..., i80: [bas, haut] sur l'issue « oui » ou la première issue}}, plus « __pivots__ » (loi
    de chaque pivot) et « __ess__ » (trajectoires effectives, alerte « combinaison trop rare »)."""
    import preuves as pv
    global PRIORS
    noeuds = noeuds_de(structure)
    pivots_obs = {n: d for n, d in obs.items() if n in noeuds and not n.startswith("VE-") and d}
    obs_ve = {n: d for n, d in obs.items() if n not in pivots_obs}
    toutes = list(preuves or []) + pv.preuves_pivots(pivots_obs, structure)
    out = _prevoir(structure, tables, obs_ve, questions, tirages, trajectoires, graine, toutes)
    if pivots_obs and out["__ess__"]["part"] < SEUIL_ESS:
        out = _prevoir(structure, tables, obs, questions, tirages, trajectoires, graine, list(preuves or []))
        out["__ess__"]["imposes"] = sorted(pivots_obs)
    return out


def _prevoir(structure, tables, obs, questions, tirages, trajectoires, graine, preuves):
    import preuves as pv
    global PRIORS
    PRIORS = lois_a_priori(structure, tables, obs)
    rng = random.Random(graine)
    noeuds = noeuds_de(structure)
    mes = structure["mesures"]
    tm = tables.get("mesures", {})
    simples = [q for q in questions if "composantes" not in q and "rapide" not in q]
    conj = [q for q in questions if "composantes" in q]
    rap = [q for q in questions if "rapide" in q]
    v2 = (lire_json("modele/jalons/vraisemblances_v2.json") or {}).get("jalons", {}) if rap else {}
    cles = {q["id"]: ("oui" if "composantes" in q or "oui" in q["issues"] else q["issues"][0]) for q in questions}
    tot = {q["id"]: {} for q in questions}           # sommes pondérées sur tous les tirages
    par_tirage = {q["id"]: [] for q in questions}    # (moyenne pondérée, poids du tirage, variance de simulation)
    piv = {p["id"]: {} for p in structure["pivots"]}
    sw = sw2 = 0.0
    for _ in range(tirages):
        params = perturber(tables, rng)
        lignes = []
        for _ in range(trajectoires):
            traj = simuler(structure, params, obs, rng)
            w = pv.poids(preuves, traj, noeuds) if preuves else 1.0
            sw, sw2 = sw + w, sw2 + w * w
            if w == 0:
                continue
            for p in structure["pivots"]:
                e = pv.issue_noeud(traj, p["id"], p)
                piv[p["id"]][e] = piv[p["id"]].get(e, 0.0) + w
            res, p_oui = {}, {}
            for q in simples:
                m = mes[q["evenement"]]
                d = loi(m, tm, q["evenement"], valeur(m["caracteristique"], traj, noeuds, q["fenetre"]), q["issues"])
                res[q["id"]] = d
                p_oui[q["id"]] = d.get("oui")
            for q in conj:
                pa, pb = (p_oui.get(c) for c in q["composantes"])
                x = (pa or 0) * (pb or 0)     # indépendance conditionnelle à la trajectoire
                res[q["id"]] = {"oui": x, "non": 1 - x}
            for q in rap:
                d = q["rapide"]
                if d["rapide"] == "jalon":
                    # P(jalon observé | trajectoire) = vraisemblance v2 de l'issue du nœud dans la trajectoire
                    e = pv.issue_noeud(traj, d["noeud"], noeuds[d["noeud"]])
                    x = v2[d["jalon"]]["vraisemblances"].get(e, 0.0)
                    res[q["id"]] = {"oui": x, "non": 1 - x}
                else:
                    e = traj[d["noeud"]][idx(d["mois"])]
                    res[q["id"]] = {i: (1.0 if i == e else 0.0) for i in q["issues"]}
            lignes.append((w, res))
        W = sum(w for w, _ in lignes)
        for q in questions:
            for w, res in lignes:
                for i, v in res[q["id"]].items():
                    tot[q["id"]][i] = tot[q["id"]].get(i, 0.0) + w * v
            if W > 0:
                xs = [(w, res[q["id"]].get(cles[q["id"]], 0.0)) for w, res in lignes]
                m1 = sum(w * x for w, x in xs) / W
                var = sum(w * w * (x - m1) ** 2 for w, x in xs) / (W * W)
                par_tirage[q["id"]].append((m1, W, var))
    n = tirages * trajectoires
    ess = sw * sw / sw2 if sw2 > 0 else 0.0
    out = {}
    for q in questions:
        moy = normaliser(tot[q["id"]]) if tot[q["id"]] else {}
        # Erreur type de Monte-Carlo de la probabilité publiée (revue 2, test 12) : écart entre tirages / √tirages.
        pt0 = par_tirage[q["id"]]
        es = round(100 * math.sqrt(sum((x - sum(y for y, _, _ in pt0) / len(pt0)) ** 2 for x, _, _ in pt0) / max(len(pt0) - 1, 1) / len(pt0)), 2) if len(pt0) > 1 else None
        pt = par_tirage[q["id"]]
        if pt:
            xs, ws, vs = zip(*pt)
            mu = sum(x * w for x, w in zip(xs, ws)) / sum(ws)
            v_tot = sum(w * (x - mu) ** 2 for x, w in zip(xs, ws)) / sum(ws)
            v_sim = sum(w * v for w, v in zip(ws, vs)) / sum(ws)
            f = math.sqrt(max(v_tot - v_sim, 0.0) / v_tot) if v_tot > 0 else 0.0
            ys = [mu + f * (x - mu) for x in xs]
            i80 = [round(100 * quantile_pondere(ys, ws, 0.1), 1), round(100 * quantile_pondere(ys, ws, 0.9), 1)]
        else:
            i80 = [None, None]
        out[q["id"]] = {**{i: round(100 * v, 1) for i, v in moy.items()}, "i80": i80, "es": es}
    out["__pivots__"] = {k: {i: round(100 * v, 1) for i, v in normaliser(d).items()} if d else {} for k, d in piv.items()}
    out["__ess__"] = {"effectives": round(ess), "trajectoires": n, "part": round(ess / n, 4) if n else 0,
                      "alerte": ess / n < SEUIL_ESS if n else True, "preuves": [p["id"] for p in preuves]}
    return out


def ecart_direct(p, direct, seuil=10):
    """Comparaison d'une prévision du réseau p {issue: %} à l'avis direct des évaluateurs (nombre = « oui », ou loi
    par issue pour une question à plusieurs issues) ; rend (texte, alerte) où alerte vaut 1 si une issue s'écarte
    de plus de « seuil » points."""
    if isinstance(direct, (int, float)):
        d = {"oui": direct}
    elif isinstance(direct, dict):
        d = {k: v for k, v in direct.items() if k in p}
    else:
        return "", 0
    if not d:
        return "", 0
    texte = f"  évaluateurs {direct if isinstance(direct, (int, float)) else json.dumps(d, ensure_ascii=False)}"
    pire = max(d, key=lambda k: abs(p[k] - d[k]))
    if abs(p[pire] - d[pire]) > seuil:
        return texte + f"  ÉCART > {seuil} points ({pire} : {p[pire]} contre {d[pire]})", 1
    return texte, 0


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
        elif q["type"] == "rapide":
            out.append({"id": q["id"], "rapide": q["details"], "issues": q["issues"]})
    # Les composantes d'une conjointe doivent être calculées dans le même passage.
    ids = {q["id"] for q in out}
    return [q for q in out if "composantes" not in q or all(c in ids for c in q["composantes"])]


def geler():
    """Version témoin du réseau (feuille de route, étape 6) : copie de la structure, des tables et du calendrier dans
    modele/reseau/gele/, avec leurs empreintes ; une seule fois. Elle est ensuite notée comme un auteur à part
    (« réseau v0 gelé ») : seules les observations, les pivots tranchés et les preuves qui tranchent la font bouger."""
    import hashlib
    import shutil
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from commun import RACINE
    d = RACINE / DOSSIER_GELE
    if (d / "manifeste.json").exists():
        sys.exit(f"{DOSSIER_GELE} existe déjà : le réseau témoin ne se gèle qu'une fois.")
    d.mkdir(parents=True, exist_ok=True)
    emp = {}
    for f in FICHIERS_RESEAU:
        shutil.copyfile(RACINE / f, d / Path(f).name)
        emp[Path(f).name] = hashlib.sha256((RACINE / f).read_bytes()).hexdigest()
    m = {"gele_le": datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds"), "empreintes": emp,
         "regle": "jamais modifié ; noté comme « réseau v0 gelé » à côté du réseau courant (étape 6)"}
    (d / "manifeste.json").write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", "utf-8")
    return m


def charger(gele=False):
    """Structure et tables : courantes, ou version témoin gelée (empreintes vérifiées)."""
    if not gele:
        return lire_json(FICHIERS_RESEAU[0]), lire_json(FICHIERS_RESEAU[1])
    import hashlib
    from commun import RACINE
    m = lire_json(f"{DOSSIER_GELE}/manifeste.json")
    if not m:
        sys.exit("Réseau témoin non gelé (python scripts/reseau.py --geler).")
    for nom, h in m["empreintes"].items():
        if hashlib.sha256((RACINE / DOSSIER_GELE / nom).read_bytes()).hexdigest() != h:
            sys.exit(f"{DOSSIER_GELE}/{nom} : empreinte modifiée depuis le gel")
    global CHEMIN_CALENDRIER
    CHEMIN_CALENDRIER = f"{DOSSIER_GELE}/calendrier.json"
    _PROFILS.clear()
    return lire_json(f"{DOSSIER_GELE}/structure_v0.json"), lire_json(f"{DOSSIER_GELE}/tables_v0.json")


def controle_gel_48h(etiquette, maintenant=None):
    """Gel du réseau 48 heures avant chaque cycle (étape 6) : aucun commit sur la structure, les tables ou le
    calendrier dans les 48 heures qui précèdent le gel du cycle (manifeste du gel). Rend la liste des défauts."""
    import subprocess
    from datetime import datetime, timedelta
    from commun import RACINE
    m = lire_json(f"data/cycles/{etiquette}/gel/manifeste.json")
    if not m:
        return []   # cycle d'essai sans gel : pas de contrôle
    gel = datetime.fromisoformat(m["gele_le"])
    seuil = gel - timedelta(hours=DELAI_GEL_HEURES)
    d = []
    for f in FICHIERS_RESEAU:
        r = subprocess.run(["git", "log", "-1", "--format=%cI", "--", f], cwd=RACINE, capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            t = datetime.fromisoformat(r.stdout.strip())
            if seuil < t:
                d.append(f"{f} modifié le {t.isoformat()}, moins de {DELAI_GEL_HEURES} heures avant le gel du cycle ({gel.isoformat()})")
    return d


def observations(structure=None):
    """États observés. Variable « maximum du mois » : l'observation du mois en cours (mois de « etabli_le » ou après)
    devient un minimum {"au_moins": état}, le mois n'étant pas fini."""
    o = lire_json("modele/reseau/observations.json") or {}
    etats = o.get("etats", {})
    structure = structure or lire_json("modele/reseau/structure_v0.json")
    courant = (o.get("etabli_le") or "")[:7]
    maxima = {v["id"] for v in structure["variables_etat"] if v.get("agregat") == "maximum"}
    return {n: {m: ({"au_moins": e} if n in maxima and courant and m >= courant and isinstance(e, str) else e)
                for m, e in d.items()} for n, d in etats.items()}


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--geler" in args:
        print(json.dumps(geler(), ensure_ascii=False))
        sys.exit(0)
    gele = "--gele" in args
    structure, tables = charger(gele)
    if tables is None:
        sys.exit("modele/reseau/tables_v0.json absent : tables non encore élicitées.")
    nt = int(args[args.index("--tirages") + 1]) if "--tirages" in args else 200
    ntr = int(args[args.index("--trajectoires") + 1]) if "--trajectoires" in args else 100
    import preuves as pv
    from datetime import date
    jour = next((x for x in args if len(x) == 10 and x[4] == "-"), date.today().isoformat())
    if "--effet" in args:
        # Effet d'un fait sur tout le réseau : avant / après, pivots et questions, trié par écart.
        cible = args[args.index("--effet") + 1]
        qs = questions_banque(structure, lire_json("modele/evenements.json")["evenements"])
        base = pv.preuves_notees(jour)
        if cible.startswith("J-"):
            v2 = lire_json(pv.V2)["jalons"]
            statut = args[args.index("--effet") + 2] if len(args) > args.index("--effet") + 2 and not args[args.index("--effet") + 2].startswith("-") else "observé"
            ajout = pv.preuve_jalon(cible, v2[cible], statut)
        else:
            ajout = json.loads(cible)
        avant = prevoir(structure, tables, observations(), qs, nt, ntr, preuves=base)
        apres = prevoir(structure, tables, observations(), qs, nt, ntr, preuves=base + [ajout])
        print(f"Preuve : {json.dumps(ajout, ensure_ascii=False)}")
        rang = []
        for k, d in apres["__pivots__"].items():
            for i, v in d.items():
                rang.append((abs(v - avant["__pivots__"][k].get(i, 0)), f"{k} {i}", avant["__pivots__"][k].get(i, 0), v))
        for q in qs:
            for i, v in apres[q["id"]].items():
                if i not in ("i80", "es", "non"):
                    rang.append((abs(v - avant[q["id"]].get(i, 0)), f"{q['id']} {i}", avant[q["id"]].get(i, 0), v))
        for e, nom, a, b in sorted(rang, reverse=True):
            if e >= 1:
                print(f"{nom[:48]:48} {a:6.1f} → {b:6.1f}  ({b - a:+.1f})")
        e = apres["__ess__"]
        print(f"Trajectoires effectives : {e['effectives']} sur {e['trajectoires']}" + ("  COMBINAISON TROP RARE" if e["alerte"] else ""))
        sys.exit(0)
    if "--controle" in args:
        qs = questions_banque(structure, lire_json("modele/evenements.json")["evenements"])
        prev = prevoir(structure, tables, observations(), qs, nt, ntr, preuves=pv.preuves_notees(jour))
        alertes = 0
        for q in qs:
            p = prev[q["id"]]
            ecart, alerte = ecart_direct(p, tables.get("direct", {}).get(q["id"].removeprefix("Q-")))
            alertes += alerte
            print(f"{q['id']:10} {json.dumps({k: v for k, v in p.items() if k not in ('i80', 'es')}, ensure_ascii=False)}  i80 {p['i80']}  e.t. {p['es']}{ecart}")
        print(f"{alertes} écart(s) de plus de 10 points ; trajectoires effectives {prev['__ess__']}")
        sys.exit(0)
    etiquette = args[0]
    if "--registre" not in args:
        sys.exit("Indiquer --registre registre/<fichier>.jsonl")
    reg = args[args.index("--registre") + 1]
    defauts = [] if gele else controle_gel_48h(etiquette)
    if defauts:
        sys.exit("Gel de 48 heures non respecté (étape 6) : " + " ; ".join(defauts))
    qs = questions_cycle(structure, etiquette)
    prev = prevoir(structure, tables, observations(), qs, nt, ntr, preuves=pv.preuves_notees(jour))
    e = prev["__ess__"]
    if e["alerte"]:
        sys.exit(f"Combinaison trop rare : {e['effectives']} trajectoires effectives sur {e['trajectoires']} ; relancer avec plus de trajectoires.")
    lignes = [{"question": q["id"], "probabilites": {k: v for k, v in prev[q["id"]].items() if k not in ("i80", "es")},
               "piste": "v0", "auteur": VERSION_GELEE if gele else VERSION, "version": tables.get("version", VERSION),
               "origine": f"cycle {etiquette}", "donnees": f"gel du cycle {etiquette}",
               "intervalle_80": prev[q["id"]]["i80"], "erreur_type_mc": prev[q["id"]]["es"], "preuves": e["preuves"],
               "trajectoires_effectives": e["effectives"]} for q in qs]
    from registre import ajouter
    t = ajouter(reg, lignes)
    print(f"{len(lignes)} prévisions du réseau ajoutées à {reg}, émises le {t}")
