"""Faits imprévus : décision d'application comme preuve du réseau (annexe, section 11.4 ; feuille de route, étape 2).

Usage : python scripts/faits.py decider < avis.json
        avis.json : {"fait", "noeud", "issues": [...], "stade": "allégation" | "procédure" | "mise en cause" |
                     "décision" | "fait public", "mois": "AAAA-MM",
                     "avis": [{"evaluateur", "modele", "p": {issue: P(fait | issue)}}, ...]}
        Écrit la décision dans modele/reseau/preuves.jsonl (ajout seul) : vraisemblances par issue, appliquées par
        le moteur (scripts/reseau.py) comme preuve sur toutes les trajectoires, donc sur tout le réseau.

Règles :
- stade « allégation » : aucune mise à jour (annexe, section 11.2, cas f), décision consignée sans effet ;
- vraisemblances agrégées par moyenne géométrique des évaluateurs, rapportées à la plus forte ;
- pas d'application si les évaluateurs divergent de sens sur une issue (rapport à l'issue de référence, la dernière),
  ou si aucune issue n'est à plus de deux erreurs types de zéro (dispersion au moins σ_plancher = 0,3) ;
- classe « tranche » si le rapport entre la plus forte et la plus faible vraisemblance atteint 20 : appliquée telle
  quelle ; sinon « indice » : rapports plafonnés entre 1/3 et 3, puis réduits par la puissance k = 0,5.
"""
import json
import math
import statistics
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from commun import RACINE

SIGMA_PLANCHER = 0.3
K_FAITS = 0.5
PLAFOND = 3.0
SEUIL_TRANCHE = 20


def decider(f):
    issues = f["issues"]
    ref = issues[-1]
    base = {"id": f.get("id") or f"F-{f['fait'][:40]}", "source": "fait", "fait": f["fait"], "noeud": f["noeud"],
            "mois": f.get("mois"), "stade": f.get("stade")}
    if f.get("stade") == "allégation":
        return {**base, "classe": "allégation", "retenu": False, "vraisemblances": {},
                "motifs": ["allégation : en observation, sans mise à jour"]}
    motif, signif = [], False
    for i in issues[:-1]:
        lr = [math.log(a["p"][i] / a["p"][ref]) for a in f["avis"]]
        if any(x > 0 for x in lr) and any(x < 0 for x in lr):
            motif.append(f"{i} : évaluateurs de sens opposés")
            return {**base, "classe": None, "retenu": False, "vraisemblances": {}, "motifs": motif}
        m = statistics.mean(lr)
        sd = max(statistics.pstdev(lr) if len(lr) > 1 else 0.0, SIGMA_PLANCHER)
        if abs(m) >= 2 * sd / math.sqrt(len(lr)):
            signif = True
        else:
            motif.append(f"{i} : moins de deux erreurs types de zéro")
    if not signif:
        return {**base, "classe": None, "retenu": False, "vraisemblances": {}, "motifs": motif}
    L = {i: math.exp(statistics.mean(math.log(a["p"][i]) for a in f["avis"])) for i in issues}
    haut = max(L.values())
    L = {i: v / haut for i, v in L.items()}
    if min(L.values()) <= 1 / SEUIL_TRANCHE:
        classe = "tranche"
    else:
        classe = "indice"
        L = {i: max(v, 1 / PLAFOND) ** K_FAITS for i, v in L.items()}
    return {**base, "classe": classe, "retenu": True, "vraisemblances": {i: round(v, 4) for i, v in L.items()},
            "motifs": motif}


if __name__ == "__main__":
    if sys.argv[1:] != ["decider"]:
        sys.exit(__doc__)
    f = json.load(sys.stdin)
    d = decider(f)
    d["decide_le"] = datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")
    with (RACINE / "modele/reseau/preuves.jsonl").open("a", encoding="utf-8", newline="\n") as h:
        h.write(json.dumps(d, ensure_ascii=True) + "\n")
    print(json.dumps(d, ensure_ascii=False))
