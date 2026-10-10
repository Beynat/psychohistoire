"""Faits imprévus : décision d'application comme preuve du réseau (annexe, section 11.4 ; feuille de route, étape 2).

Usage : python scripts/faits.py choc < choc.json
        choc.json : {"id", "fait", "stade", "mois": "AAAA-MM", "avis": [{"evaluateur", "ports": ["P-…", …]}, …]}
        Choc imprévu comme intervention (étape 9) : les évaluateurs choisissent seulement les points d'entrée touchés
        (« ports » de la structure, trois au plus), jamais une intensité ; l'intensité vient du barème par stade
        (modele/reseau/bareme_chocs.json, calé sur des précédents sourcés). Un port est retenu s'il est choisi par la
        majorité des évaluateurs ; stade « allégation » : aucun effet (annexe, section 11.2). Écrit la décision dans
        modele/reseau/chocs.jsonl (ajout seul) ; le moteur l'applique à partir du mois du fait, jusqu'à absorption
        par l'observation suivante du nœud (sondage, baromètre) ou au plus la durée du barème.
        python scripts/faits.py decider < avis.json
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


def delta_port(port, stade, bareme):
    """Intensité d'un choc sur un port, en log-cote, selon le barème : variable ordinale, points convertis par
    « points_par_unite » (inclinaison d'une unité de log-cote par rang) ; pivot, rapport de cotes entre la
    probabilité de retrait du stade et la probabilité de retrait de référence."""
    b = bareme["stades"][stade]
    if port["noeud"].startswith("VE-"):
        if port["noeud"] not in bareme["largeur_classe"]:
            return 0.0
        pts = b["points_popularite"] if port["noeud"] == "VE-POP" else b["points_intentions"]
        sens = 1 if port.get("sens", "hausse") == "hausse" else -1
        # Un choc ne joue que dans le sens du port (baisse pour un port « baisse ») : sinon intensité nulle.
        return round(max(sens * pts, 0) / bareme["largeur_classe"][port["noeud"]], 3)
    cle = {"PV-GOUV": "p_retrait_ministre"}.get(port["noeud"], "p_retrait_candidat")
    if port["noeud"] not in ("PV-GOUV", "PV-LEPEN", "PV-RNAUTRE", "PV-BLOC"):
        return 0.0   # port sans barème établi (vacance, écart de taux…)
    lo = lambda p: math.log(p / (1 - p))
    return round(max(lo(b[cle]) - lo(bareme["p_retrait_reference"]), 0.0), 3)


def choc(f, structure=None, bareme=None):
    from commun import lire_json
    structure = structure or lire_json("modele/reseau/structure_v0.json")
    bareme = bareme or lire_json("modele/reseau/bareme_chocs.json")
    ports = {p["id"]: p for p in structure.get("ports", [])}
    base = {"id": f["id"], "fait": f["fait"], "stade": f["stade"], "mois": f["mois"], "ports": {}, "retenu": False}
    if f["stade"] == "allégation" or f["stade"] not in bareme["stades"]:
        return {**base, "motif": "allégation ou stade hors barème : en observation, sans effet"}
    n = len(f["avis"])
    votes = {}
    for a in f["avis"]:
        for p in a["ports"][:3]:
            if p not in ports:
                raise SystemExit(f"port inconnu : {p}")
            votes[p] = votes.get(p, 0) + 1
    retenus = {p: delta_port(ports[p], f["stade"], bareme) for p, v in votes.items() if v > n / 2}
    retenus = {p: d for p, d in retenus.items() if d > 0}
    return {**base, "ports": retenus, "retenu": bool(retenus), "duree_mois": bareme["stades"][f["stade"]].get("duree_mois", 3),
            "votes": votes, "motif": "ports choisis par la majorité des évaluateurs ; intensité du barème"}


if __name__ == "__main__":
    if sys.argv[1:] == ["choc"]:
        d = choc(json.load(sys.stdin))
        d["decide_le"] = datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")
        with (RACINE / "modele/reseau/chocs.jsonl").open("a", encoding="utf-8", newline="\n") as h:
            h.write(json.dumps(d, ensure_ascii=True) + "\n")
        print(json.dumps(d, ensure_ascii=False))
        sys.exit(0)
    if sys.argv[1:] != ["decider"]:
        sys.exit(__doc__)
    f = json.load(sys.stdin)
    d = decider(f)
    d["decide_le"] = datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")
    with (RACINE / "modele/reseau/preuves.jsonl").open("a", encoding="utf-8", newline="\n") as h:
        h.write(json.dumps(d, ensure_ascii=True) + "\n")
    print(json.dumps(d, ensure_ascii=False))
