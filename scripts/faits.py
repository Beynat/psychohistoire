"""Faits imprévus : seuil d'application de la preuve virtuelle (annexe, section 11.4 ; feuille de route v0, bloc 8).

Usage : python scripts/faits.py decider < avis.json     avis.json : {"fait", "noeud", "issues": [...],
            "avis": [{"evaluateur", "modele", "p": {issue: P(fait | issue)}}, ...]}
        Écrit la décision dans modele/reseau/faits.jsonl (ajout seul) ; le moteur du réseau applique les faits
        retenus comme multiplicateurs sur le nœud à partir du mois du fait, pendant « duree_mois » mois (champ de
        l'avis, 3 par défaut) ; sur une variable d'état, l'effet s'éteint dès qu'une observation postérieure au fait
        l'a absorbé (étape 1 de la feuille de route, 10 octobre 2026).

Règles : rapport de chaque issue rapporté à l'issue de référence (la dernière), en log ; pas de mise à jour si les
évaluateurs divergent de signe, si la moyenne est à moins de deux erreurs types de zéro (dispersion au moins
σ_plancher = 0,3), ou si le rapport appliqué est entre 0,8 et 1,25 ; plafond du rapport brut entre 1/3 et 3 ;
rapport appliqué = rapport plafonné à la puissance k_faits = 0,5.
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
DUREE_MOIS = 3


def decider(f):
    issues = f["issues"]
    ref = issues[-1]
    out = {}
    motif = []
    for i in issues[:-1]:
        lr = [math.log(a["p"][i] / a["p"][ref]) for a in f["avis"]]
        if any(x > 0 for x in lr) and any(x < 0 for x in lr):
            motif.append(f"{i} : évaluateurs de signes opposés")
            continue
        m = statistics.mean(lr)
        sd = max(statistics.pstdev(lr) if len(lr) > 1 else 0.0, SIGMA_PLANCHER)
        if abs(m) < 2 * sd / math.sqrt(len(lr)):
            motif.append(f"{i} : moins de deux erreurs types de zéro")
            continue
        brut = min(max(math.exp(m), 1 / 3), 3)
        applique = brut ** K_FAITS
        if 0.8 <= applique <= 1.25:
            motif.append(f"{i} : rapport appliqué {applique:.2f} entre 0,8 et 1,25")
            continue
        out[i] = round(applique, 3)
    return {"fait": f["fait"], "noeud": f["noeud"], "mois": f.get("mois"), "multiplicateurs": out,
            "duree_mois": f.get("duree_mois", DUREE_MOIS), "retenu": bool(out), "motifs": motif}


if __name__ == "__main__":
    if sys.argv[1:] != ["decider"]:
        sys.exit(__doc__)
    f = json.load(sys.stdin)
    d = decider(f)
    d["decide_le"] = datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")
    with (RACINE / "modele/reseau/faits.jsonl").open("a", encoding="utf-8") as h:
        h.write(json.dumps(d, ensure_ascii=True) + "\n")
    print(json.dumps(d, ensure_ascii=False))
