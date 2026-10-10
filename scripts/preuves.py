"""Preuves du réseau : jalons, faits imprévus et pivots tranchés, appliqués par un seul moteur (feuille de route,
étape 2 ; revues méthodologiques du 10 octobre 2026).

Une preuve est une vraisemblance par issue d'un nœud, L(issue) = P(fait constaté | issue du nœud). Le moteur
(scripts/reseau.py, prevoir) pondère chaque trajectoire par le produit des vraisemblances des preuves : l'effet porte
sur tout le réseau, vers l'aval comme vers l'amont (un fait sur un enfant renseigne aussi ses parents).

Issue d'un nœud dans une trajectoire : son issue finale pour un pivot daté ; « oui » s'il survient dans sa fenêtre,
« non » sinon, pour un pivot « à tout moment » ; son état au mois de la preuve pour une variable d'état.

Trois classes, fixées avant l'observation :
- « tranche » : le fait implique une issue, sauf retournement. Jalon équivalent à un état du réseau, ou jalon dont le
  rapport entre la plus forte et la plus faible vraisemblance atteint SEUIL_TRANCHE (20) ; pivot inscrit comme
  tranché dans observations.json ; fait imprévu retenu comme tel. Vraisemblances appliquées telles quelles, sans
  réduction ni plafond : la probabilité de retournement est déjà dans la plus faible vraisemblance.
- « indice » : le fait est corrélé à l'issue sans l'impliquer. Vraisemblances réduites par la puissance k (0,5 tant
  qu'il n'est pas estimé, annexe, section 10.4). Un jalon « qui tranche » manqué est un indice.
- « allégation » : aucune mise à jour (annexe, section 11.2, cas f).

Usage des jalons : les preuves « qui tranche » observées entrent dans les prévisions notées (ce sont des
observations) ; les indices n'entrent que dans le registre fantôme tant que les jalons ne sont pas activés (annexe,
section 10.6).

Usage : python scripts/preuves.py classes        classe de chaque jalon (vraisemblances v2)
        python scripts/preuves.py liste [JOUR]   preuves en vigueur au jour donné
"""
import json
import sys
from datetime import date

from commun import RACINE, lire_json, lire_jsonl

K = 0.5
SEUIL_TRANCHE = 20
V2 = "modele/jalons/vraisemblances_v2.json"
JOURNAL = "modele/reseau/preuves.jsonl"


def classe_jalon(v):
    """Classe d'un jalon d'après ses vraisemblances v2 (fixée avant l'observation)."""
    if v.get("classe"):
        return v["classe"]
    if v.get("etat_reseau"):
        return "tranche"
    L = [x for x in v["vraisemblances"].values()]
    return "tranche" if min(L) > 0 and max(L) / min(L) >= SEUIL_TRANCHE else "indice"


def reduire(L, k):
    return {i: x ** k for i, x in L.items()}


def preuve_jalon(jid, v, statut, F=1.0, k=K):
    """Preuve tirée d'un jalon selon son statut : observé (L), manqué (1 - L), en cours (1 - L·F, F part écoulée de
    sa fenêtre). Rend None si le statut ne renseigne rien."""
    L = v["vraisemblances"]
    classe = classe_jalon(v)
    if statut == "observé":
        eff = dict(L)
    elif statut == "manqué":
        eff, classe = {i: 1 - x for i, x in L.items()}, "indice"
    elif statut == "en cours" and F > 0:
        eff, classe = {i: 1 - x * F for i, x in L.items()}, "indice"
    else:
        return None
    if classe == "indice":
        eff = reduire(eff, k)
    return {"id": jid, "source": "jalon", "noeud": v["noeud"], "classe": classe, "statut": statut,
            "vraisemblances": eff}


def preuves_jalons(jour, k=K):
    """Preuves des jalons au jour donné (statuts de scripts/jalons.py, vraisemblances v2)."""
    import jalons
    v2 = lire_json(V2)["jalons"]
    out = []
    for jid, (j, st) in jalons.etats(jour).items():
        if jid not in v2:
            continue
        F = 0.0
        if st == "en cours":
            d0, d1, t = (date.fromisoformat(x) for x in (j["fenetre"]["debut"], j["fenetre"]["fin"], jour))
            F = min(max((t - d0).days / max((d1 - d0).days, 1), 0), 1)
        p = preuve_jalon(jid, v2[jid], st, F, k)
        if p:
            out.append(p)
    return out


def preuves_journal(jour):
    """Preuves consignées dans modele/reseau/preuves.jsonl (faits imprévus, ajout seul), en vigueur au jour donné :
    la dernière décision par identifiant, si elle est retenue et hors allégation."""
    der = {}
    for p in lire_jsonl(JOURNAL):
        if p.get("decide_le", "")[:10] <= jour:
            der[p["id"]] = p
    return [p for p in der.values() if p.get("retenu") and p.get("classe") in ("tranche", "indice")]


def preuves_notees(jour, k=K):
    """Preuves des prévisions notées : jalons « qui tranche » observés et faits imprévus retenus."""
    j = [p for p in preuves_jalons(jour, k) if p["classe"] == "tranche"]
    return j + preuves_journal(jour)


def preuves_fantome(jour, k=K):
    """Preuves du registre fantôme : tous les jalons (indices réduits par k) et les faits imprévus retenus."""
    return preuves_jalons(jour, k) + preuves_journal(jour)


def preuves_pivots(obs, structure):
    """Pivots inscrits comme tranchés dans observations.json : preuves « qui tranche » (L = 1 pour l'issue observée,
    0 sinon), et non états imposés, pour que leurs parents non observés soient mis à jour."""
    pivots = {p["id"]: p for p in structure["pivots"]}
    out = []
    for n, d in obs.items():
        if n in pivots and d:
            mois, issue = max(d.items())
            issues = pivots[n].get("issues") or ["oui", "non"]
            out.append({"id": f"OBS-{n}", "source": "observation", "noeud": n, "classe": "tranche", "mois": mois,
                        "vraisemblances": {i: (1.0 if i == issue else 0.0) for i in issues}})
    return out


def issue_noeud(traj, n, noeud, mois=None):
    """Issue d'un nœud dans une trajectoire (voir l'en-tête)."""
    x = traj[n]
    if n.startswith("VE-"):
        from reseau import idx
        return x[idx(mois)] if mois else next((v for v in reversed(x) if v is not None), None)
    if noeud.get("nature") == "à tout moment":
        return "oui" if "oui" in x else "non"
    return next((v for v in reversed(x) if v is not None), None)


def poids(preuves, traj, noeuds):
    w = 1.0
    for p in preuves:
        e = issue_noeud(traj, p["noeud"], noeuds[p["noeud"]], p.get("mois"))
        w *= p["vraisemblances"].get(e, 1.0)
        if w == 0:
            return 0.0
    return w


if __name__ == "__main__":
    a = sys.argv[1:]
    jour = next((x for x in a if len(x) == 10 and x[4] == "-"), date.today().isoformat())
    if a[:1] == ["classes"]:
        v2 = lire_json(V2)["jalons"]
        for jid, v in v2.items():
            L = v["vraisemblances"]
            print(f"{jid}  {classe_jalon(v):8} {v['noeud']:13} rapport {max(L.values()) / min(L.values()):6.1f}")
    elif a[:1] == ["liste"]:
        for p in preuves_jalons(jour) + preuves_journal(jour):
            print(json.dumps(p, ensure_ascii=False))
    else:
        sys.exit(__doc__)
