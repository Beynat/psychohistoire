"""Critère de direction des jalons et des faits imprévus (annexe, section 10.11 ; feuille de route v0, bloc 2).

Usage : python scripts/direction.py REGISTRE [--couche fantome|faits]

Pour chaque question résolue i dont la couche jugée a déplacé la probabilité d'au moins 0,5 point à sa
clôture : s_i = d_i (y_i − p_i), où p est la probabilité sans la couche (dernière prévision du réseau avant la
date du fait), d le déplacement dû à la couche (probabilité fantôme moins p), y = 1 si l'issue favorisée s'est
réalisée. Termes sommés par grappe ; Z = Σ S_g / √(Σ S_g²). Seuil unilatéral de 10 % sur au moins 40 questions
résolues ; loi de Student à (grappes − 1) degrés de liberté sous 15 grappes.
"""
import math
import sys

from commun import lire_jsonl
from resolution import resolutions_effectives, suffixe, toutes_les_questions


def quantile_student_90(ddl):
    """Quantile unilatéral à 90 % de la loi de Student (table usuelle ; normale au-delà de 30 degrés)."""
    t = {1: 3.078, 2: 1.886, 3: 1.638, 4: 1.533, 5: 1.476, 6: 1.440, 7: 1.415, 8: 1.397, 9: 1.383, 10: 1.372,
         11: 1.363, 12: 1.356, 13: 1.350, 14: 1.345, 15: 1.341, 20: 1.325, 30: 1.310}
    if ddl >= 30:
        return 1.2816
    return t.get(ddl) or t[max(k for k in t if k <= ddl)]


def statistique(reg, couche="fantome"):
    res = resolutions_effectives(suffixe(reg))
    qs = toutes_les_questions()
    base, fant = {}, {}
    for l in lire_jsonl(reg):
        if l.get("auteur") == "réseau v0" and "probabilites" in l:
            base.setdefault(l["question"], []).append(l)
    for l in lire_jsonl("registre/fantome.jsonl"):
        fant.setdefault(l["question"], []).append(l)
    termes = {}
    n = 0
    for q, r in res.items():
        if r.get("issue") is None or q not in base or q not in fant:
            continue
        df = r.get("date_fait") or ""
        b = [l for l in base[q] if l["emise"][:10] < df]
        f = [l for l in fant[q] if l["emise"][:10] < df]
        if not b or not f:
            continue
        lf = f[-1]
        issue = next(iter(k for k in lf["probabilites"] if k in b[-1]["probabilites"]))
        cible = lf.get("issue_cible") or ("oui" if "oui" in lf["probabilites"] else issue)
        p = b[-1]["probabilites"][cible] / 100
        d = lf["probabilites"][cible] / 100 - p
        if abs(d) < 0.005:
            continue
        y = 1.0 if r["issue"] == cible else 0.0
        g = (qs.get(q) or {}).get("grappe", q)
        termes[g] = termes.get(g, 0.0) + d * (y - p)
        n += 1
    if not termes:
        return {"questions": 0, "grappes": 0, "Z": None, "seuil": None, "actif": False}
    S = list(termes.values())
    den = math.sqrt(sum(s * s for s in S))
    Z = sum(S) / den if den > 0 else 0.0
    seuil = quantile_student_90(len(S) - 1) if len(S) < 15 else 1.2816
    return {"questions": n, "grappes": len(S), "Z": round(Z, 3), "seuil": seuil, "actif": n >= 40 and Z > seuil}


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    r = statistique(a[0])
    print(r)
