"""Contrôles de vraisemblance du réseau (16 octobre 2026, après la revue de Nathan : trois défauts visibles à la
lecture des sorties n'avaient été attrapés par aucun contrôle, parce que tous vérifiaient la cohérence interne).

Usage : python scripts/controles.py [--tirages N] [--trajectoires N]
        python scripts/controles.py --sorties      sorties lisibles, pour la relecture de vraisemblance d'une passe

1. Persistance des variables d'état : taux de bascule mensuel impliqué par les tables (part des mois où l'état
   change), état de départ par état de départ, comparé au taux observé dans les séries (data/etat/,
   data/historique/ ; au moins 5 mois observés dans l'état), avec un intervalle à 95 %
   (Clopper-Pearson). Hors de l'intervalle : défaut, sauf dérogation déclarée dans la structure
   (« derogations_controles », avec cause et tâche qui la lève). Une dérogation devenue sans objet fait échouer
   le contrôle : elle doit être retirée.
2. Chemins annoncés : une feuille assumée dont la justification cite un autre nœud (« l'effet passe par VE-SOND »)
   doit l'avoir pour descendant dans la structure.
3. Issues fourre-tout : une issue qui regroupe des options aux effets possiblement opposés (« soutien à un autre
   candidat », « autre … ») et pèse au moins 15 % doit être déclarée dans « issues_residuelles », avec la raison pour
   laquelle ses sous-cas n'ont pas d'effets différents en aval.
"""
import csv
import math
import random
import re
import sys

import reseau
from commun import RACINE, lire_json

SEUIL_FOURRE_TOUT = 15.0
MOTS_FOURRE_TOUT = re.compile(r"\b(autre|autres|soutien)\b", re.I)
ECART_DEPUIS = "1999-01"     # série OAT-Bund depuis l'euro : inclut les épisodes de tension (2011-2012)


def _consecutifs(d):
    """[(état de départ, bascule)] pour chaque paire de mois consécutifs observés."""
    ms = sorted(d)
    out = []
    for a, b in zip(ms, ms[1:]):
        ya, ma = map(int, a.split("-"))
        yb, mb = map(int, b.split("-"))
        if (yb * 12 + mb) - (ya * 12 + ma) == 1:
            out.append((d[a], d[a] != d[b]))
    return out


def bascules_observees():
    """{(variable, état de départ): (bascules, paires de mois consécutifs observés)} : le taux de bascule dépend de
    l'état (un écart de taux en zone de tension bascule bien plus souvent qu'en temps calme)."""
    import etat
    e = {v: d for v, d in etat.etats().items() if not v.startswith("_")}
    s = lire_json("modele/reseau/structure_v0.json")
    ve = {v["id"]: v for v in s["variables_etat"]}
    if "VE-ECART" in ve:
        with open(RACINE / "data/historique/ecart_FR_DE_pb.csv", encoding="utf-8") as f:
            ser = {r["periode"]: float(r["valeur"]) for r in csv.DictReader(f) if r["valeur"] and r["periode"] >= ECART_DEPUIS}
        e["VE-ECART"] = {m: ("< 120 pb" if x < 120 else "120-160 pb" if x <= 160 else "> 160 pb") for m, x in ser.items()}
    out = {}
    for v, d in e.items():
        for depart, b in _consecutifs(d):
            k, n = out.get((v, depart), (0, 0))
            out[(v, depart)] = (k + b, n + 1)
    return out


def _binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def intervalle(k, n, a=0.05):
    """Intervalle de Clopper-Pearson à 1 − a pour une proportion k / n (bissection)."""
    def cherche(f):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) else (lo, m)
        return (lo + hi) / 2
    bas = 0.0 if k == 0 else cherche(lambda p: 1 - _binom_cdf(k - 1, n, p) < a / 2)
    haut = 1.0 if k == n else cherche(lambda p: _binom_cdf(k, n, p) > a / 2)
    return bas, haut


def bascules_modele(structure, tables, tirages=4, trajectoires=150, graine=20261016, mois=12):
    """Taux de bascule mensuel moyen de chaque variable sur les MOIS premiers mois simulés (aux paramètres
    perturbés, avec les observations : le premier mois observé sert de point de départ)."""
    obs = reseau.observations(structure)
    reseau.PRIORS = reseau.lois_a_priori(structure, tables, obs, n=300)
    reseau.CHOCS = reseau.chocs_retenus()
    rng = random.Random(graine)
    ve = [v["id"] for v in structure["variables_etat"]]
    c, n = {}, {}
    for _ in range(tirages):
        params = reseau.perturber(tables, rng)
        for _ in range(trajectoires):
            t = reseau.simuler(structure, params, obs, rng)
            for v in ve:
                for k in range(1, min(mois, len(reseau.MOIS))):
                    if reseau.MOIS[k] in obs.get(v, {}):
                        continue     # mois observé : pas une transition du modèle
                    cle = (v, t[v][k - 1])
                    n[cle] = n.get(cle, 0) + 1
                    c[cle] = c.get(cle, 0) + (t[v][k] != t[v][k - 1])
    return {cle: (c[cle] / n[cle], n[cle]) for cle in n}


def persistance(structure, tables, **kw):
    """Défauts de persistance, état par état : [(variable, état de départ, taux du modèle, taux observé,
    intervalle, paires observées)]."""
    obs = bascules_observees()
    mod = bascules_modele(structure, tables, **kw)
    out = []
    for (v, e), (x, nm) in mod.items():
        if (v, e) not in obs or obs[(v, e)][1] < 5 or nm < 50:
            continue     # moins de 5 mois observés dans cet état, ou état trop rare dans le modèle : pas de test
        k, n = obs[(v, e)]
        b, h = intervalle(k, n)
        if not b <= x <= h:
            out.append((v, e, round(x, 3), round(k / n, 3), (round(b, 3), round(h, 3)), n))
    return out


def appliquer_derogations(structure, defauts):
    """Retire les défauts couverts par une dérogation déclarée (« derogations_controles » de la structure :
    {contrôle: {clé: {cause, levee_par}}}) ; rend (défauts restants, dérogations sans objet ou incomplètes).
    Clés : « VE-X|état » (persistance), « PV-X » (fourre-tout), « PV-X>VE-Y » (chemins)."""
    der = structure.get("derogations_controles", {})
    cle = {"persistance": lambda d: f"{d[0]}|{d[1]}", "fourre_tout": lambda d: d[0], "chemins": lambda d: f"{d[0]}>{d[1]}"}
    restants, inutiles = {}, []
    for c, ds in defauts.items():
        couverts = {cle[c](d) for d in ds}
        restants[c] = [d for d in ds if cle[c](d) not in der.get(c, {})]
        for k, v in der.get(c, {}).items():
            if k not in couverts or not v.get("cause") or not v.get("levee_par"):
                inutiles.append((c, k))
    return restants, inutiles


def descendants(structure, i):
    N = reseau.noeuds_de(structure)
    enfants = {}
    for n in N.values():
        for q in n.get("parents", []):
            enfants.setdefault(reseau.pid(q), set()).add(n["id"])
    vus, pile = set(), [i]
    while pile:
        for e in enfants.get(pile.pop(), ()):
            if e not in vus:
                vus.add(e)
                pile.append(e)
    return vus


def chemins_annonces(structure):
    """Feuilles assumées dont la justification cite un nœud qui n'est pas un descendant : [(nœud, cité)]."""
    N = reseau.noeuds_de(structure)
    out = []
    for i, txt in structure.get("feuilles_assumees", {}).items():
        d = descendants(structure, i)
        for c in sorted(set(re.findall(r"\b(?:PV|VE)-[A-Za-z0-9]+\b", txt)) - {i}):
            if c in N and c not in d:
                out.append((i, c))
    return out


def fourre_tout(structure, marges):
    """Issues fourre-tout non déclarées : [(nœud, issue, probabilité %)]."""
    dec = structure.get("issues_residuelles", {})
    out = []
    for p in structure["pivots"]:
        for i in p.get("issues") or []:
            v = (marges.get(p["id"]) or {}).get(i, 0.0)
            if MOTS_FOURRE_TOUT.search(i) and v >= SEUIL_FOURRE_TOUT and i not in dec.get(p["id"], {}):
                out.append((p["id"], i, v))
    return out


def marges_courantes(structure, tables, tirages=4, trajectoires=150):
    r = reseau.prevoir(structure, tables, reseau.observations(structure), [], tirages, trajectoires)
    return r["__pivots__"]


def tout(structure=None, tables=None, **kw):
    s = structure or lire_json("modele/reseau/structure_v0.json")
    t = tables or lire_json("modele/reseau/tables_v0.json")
    return appliquer_derogations(s, {"persistance": persistance(s, t, **kw), "chemins": chemins_annonces(s),
                                     "fourre_tout": fourre_tout(s, marges_courantes(s, t))})


def resume_sorties(chemin="data/organigramme_v0.json"):
    """Lecture brute des sorties pour une relecture de vraisemblance : chaque pivot avec ses issues principales et
    l'évolution depuis l'instantané de référence, sans tables ni registres."""
    d = lire_json(chemin)
    W = sum(d["poids"]) or 1.0
    t = (d.get("tendance") or {}).get("pivots", {})
    lignes = [f"Sorties du réseau au {d['etabli_le']} (évolution depuis le {(d.get('tendance') or {}).get('reference', '–')})"]
    for i, p in enumerate(d["pivots"]):
        a = [0.0] * len(p["issues"])
        for c, w in zip(d["codes"], d["poids"]):
            a[int(c[i])] += w
        a = [100 * x / W for x in a]
        top = sorted(range(len(a)), key=lambda k: -a[k])[:3] if p["k"] is None else [p["k"]]
        ev = lambda k: f" ({a[k] - t[p['id']]['avant'][k]:+.0f})" if p["id"] in t else ""
        lignes.append(f"- {p['titre']} ({p['quand']}) : " + " ; ".join(f"{p['libelles'][k]} {a[k]:.0f} %{ev(k)}" for k in top))
    return "\n".join(lignes)


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--sorties" in a:
        print(resume_sorties())
        sys.exit(0)
    kw = {"tirages": int(a[a.index("--tirages") + 1]) if "--tirages" in a else 4,
          "trajectoires": int(a[a.index("--trajectoires") + 1]) if "--trajectoires" in a else 150}
    s = lire_json("modele/reseau/structure_v0.json")
    obs = bascules_observees()
    mod = bascules_modele(s, lire_json("modele/reseau/tables_v0.json"), **kw)
    print("Persistance : part des mois où l'état change, selon l'état de départ — modèle | observé [intervalle à 95 %]")
    for (v, e), (x, nm) in sorted(mod.items()):
        k, n = obs.get((v, e), (0, 0))
        b, h = intervalle(k, n) if n else (None, None)
        print(f"  {v} depuis « {e} » : {x:.0%} ({nm} mois simulés) | {k}/{n}" + (f" [{b:.0%} ; {h:.0%}]" if n else " (jamais observé)"))
    r, inutiles = tout(s, **kw)
    for k_, v in r.items():
        print(f"{k_} : {v or 'aucun défaut non couvert'}")
    if inutiles:
        print("Dérogations sans objet ou incomplètes (à retirer ou compléter) :", inutiles)
    der = s.get("derogations_controles", {})
    if der:
        print("Dérogations déclarées :", der)
