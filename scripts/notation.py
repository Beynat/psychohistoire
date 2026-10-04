"""Notation des prévisions résolues (noyau, sections 8.5 et 8.6).

Usage : python scripts/notation.py [registre/<fichier>.jsonl] [--reference AUTEUR]
Écrit data/bilans/<date>.json (ou bilan_<suffixe>) et affiche un résumé.

Pour chaque auteur (comparateurs, ensemble direct, puis modèle) et chaque pool :
- Brier (somme sur les issues des écarts au carré) et score logarithmique, sur la dernière
  prévision émise avant l'échéance ;
- Brier pondéré dans le temps : moyenne, sur chaque jour de l'émission à l'échéance, du Brier de
  la dernière probabilité inscrite ce jour-là (section 8.5) ;
- décomposition de Murphy (fiabilité, résolution, incertitude) sur les questions binaires, en
  dix classes de probabilité.
Comparaison de la référence (par défaut l'ensemble direct en phase 1) à chaque autre auteur sur
les questions communes dont l'échéance est passée à la date du test, quelle que soit leur issue
(relecture 10, I1 : une question de fenêtre résolue « oui » avant son échéance n'entre pas seule
dans le test). Score testé : Brier pondéré dans le temps (noyau, section 8.5). Différences sommées par grappe, statistique
t = Σ D_g / √(Σ D_g²) ; valeur p unilatérale par permutation des signes des grappes (exacte sous
16 grappes, 20 000 tirages au-delà). Une prévision émise après la résolution publique de sa
question est exclue (section 8.8).
"""
import itertools
import math
import random
import sys
from datetime import date, timedelta

from commun import ecrire_json, lire_jsonl, log_score, maintenant
from resolution import suffixe, toutes_les_questions


def brier(dist, issue):
    return sum((dist.get(k, 0) / 100 - (1.0 if k == issue else 0.0)) ** 2 for k in dist)


def logs(dist, issue):
    return log_score(dist.get(issue, 0) / 100, True)


def murphy(paires):
    """paires : (p, y) binaires. Renvoie fiabilité, résolution, incertitude (Murphy 1973)."""
    if not paires:
        return None
    n, ybar = len(paires), sum(y for _, y in paires) / len(paires)
    classes = {}
    for p, y in paires:
        classes.setdefault(min(int(p * 10), 9), []).append((p, y))
    fia = sum(len(c) * (sum(p for p, _ in c) / len(c) - sum(y for _, y in c) / len(c)) ** 2 for c in classes.values()) / n
    res = sum(len(c) * (sum(y for _, y in c) / len(c) - ybar) ** 2 for c in classes.values()) / n
    return {"fiabilite": round(fia, 4), "resolution": round(res, 4), "incertitude": round(ybar * (1 - ybar), 4)}


def test_grappes(diffs):
    """diffs : {grappe: [différences de Brier référence − autre]}. Négatif = la référence est meilleure."""
    D = [sum(v) for v in diffs.values()]
    G = len(D)
    if G == 0 or all(d == 0 for d in D):
        return {"grappes": G, "t": None, "p_unilaterale": None, "p_unilaterale_autre": None, "verdict": "non concluant"}
    t = sum(D) / math.sqrt(sum(d * d for d in D))
    obs = sum(D)
    if G <= 16:
        sims = [sum(s * d for s, d in zip(signes, D)) for signes in itertools.product((1, -1), repeat=G)]
    else:
        rnd = random.Random(0)
        sims = [sum(d if rnd.random() < .5 else -d for d in D) for _ in range(20000)]
    p = sum(1 for x in sims if x <= obs) / len(sims)
    p_autre = sum(1 for x in sims if x >= obs) / len(sims)
    # Trois verdicts au seuil de 10 % dans chaque sens (noyau, section 8.6).
    verdict = ("référence meilleure" if p < 0.10 else "autre meilleur" if p_autre < 0.10 else "non concluant")
    return {"grappes": G, "t": round(t, 3), "p_unilaterale": round(p, 4), "p_unilaterale_autre": round(p_autre, 4),
            "verdict": verdict}


def bilan(reg="registre/protocole.jsonl", reference="ensemble direct", aujourdhui=None):
    aujourdhui = aujourdhui or date.today().isoformat()
    sfx = suffixe(reg)
    qs = toutes_les_questions()
    res = {r["question"]: r for r in lire_jsonl(f"registre/resolutions{sfx}.jsonl") if r.get("issue") is not None}
    prev = {}
    for l in lire_jsonl(reg):
        if "probabilites" in l and l["question"] in res:
            prev.setdefault((l.get("auteur", "modèle"), l["question"]), []).append(l)
    scores, exclues = {}, []
    for (auteur, qid), lignes in prev.items():
        q, r = qs[qid], res[qid]
        lignes.sort(key=lambda l: l["emise"])
        # Exclues : émises après l'échéance, après l'enregistrement de la résolution, ou le jour du fait
        # ou après (relecture 8, G2 : un prévisionniste lancé après le fait ne doit pas être noté).
        lignes = [l for l in lignes if l["emise"][:10] <= q["echeance"] and l["emise"] < r["emise"]
                  and l["emise"][:10] < r.get("date_fait", "9999-12-31")]
        if not lignes:
            exclues.append({"auteur": auteur, "question": qid, "motif": "émise après l'échéance ou la résolution"})
            continue
        # Brier pondéré : du jour d'émission à l'échéance, arrêté la veille du fait (relecture 9).
        fin = min(q["echeance"], (date.fromisoformat(r["date_fait"]) - timedelta(days=1)).isoformat()) \
            if r.get("date_fait") else q["echeance"]
        d0 = lignes[0]["emise"][:10]
        jour, k, cumul, n = date.fromisoformat(d0), 0, 0.0, 0
        while jour <= date.fromisoformat(fin):
            while k + 1 < len(lignes) and lignes[k + 1]["emise"][:10] <= jour.isoformat():
                k += 1
            cumul += brier(lignes[k]["probabilites"], r["issue"])
            n += 1
            jour += timedelta(days=1)
        der = lignes[-1]["probabilites"]
        scores[(auteur, qid)] = {"brier": brier(der, r["issue"]), "log": logs(der, r["issue"]),
                                 "brier_temps": cumul / max(n, 1), "pool": q["pool"], "grappe": q["grappe"],
                                 "binaire": len(q["issues"]) == 2,
                                 "p_oui": der.get("oui", 0) / 100, "y": r["issue"] == "oui"}
    auteurs = sorted({a for a, _ in scores})
    par_auteur = {}
    for a in auteurs:
        mes = {qid: s for (aa, qid), s in scores.items() if aa == a}
        pools = {}
        for s in mes.values():
            pools.setdefault(s["pool"], []).append(s)
        par_auteur[a] = {"questions": len(mes), "pools": {
            p: {"n": len(v), "brier": round(sum(x["brier"] for x in v) / len(v), 4),
                "log": round(sum(x["log"] for x in v) / len(v), 4),
                "brier_temps": round(sum(x["brier_temps"] for x in v) / len(v), 4),
                "murphy": murphy([(x["p_oui"], x["y"]) for x in v if x["binaire"]])} for p, v in pools.items()}}
    comparaisons = {}
    if reference in auteurs:
        for a in auteurs:
            if a == reference:
                continue
            diffs = {}
            for (aa, qid), s in scores.items():
                if aa == reference and (a, qid) in scores and qs[qid]["echeance"] <= aujourdhui:
                    diffs.setdefault(s["grappe"], []).append(s["brier_temps"] - scores[(a, qid)]["brier_temps"])
            comparaisons[a] = test_grappes(diffs)
    sortie = {"etabli_le": maintenant(), "registre": reg, "reference": reference,
              "questions_resolues": len(res), "auteurs": par_auteur, "comparaisons": comparaisons, "exclues": exclues}
    ecrire_json(f"data/bilans/bilan{sfx}_{aujourdhui}.json", sortie)
    return sortie


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ref = sys.argv[sys.argv.index("--reference") + 1] if "--reference" in sys.argv else "ensemble direct"
    if ref in args:
        args.remove(ref)
    b = bilan(args[0] if args else "registre/protocole.jsonl", ref)
    print(f"{b['questions_resolues']} questions résolues ; référence : {b['reference']}")
    for a, v in b["auteurs"].items():
        print(f"- {a} : " + " ; ".join(f"{p} n={x['n']} Brier {x['brier']} log {x['log']}" for p, x in v["pools"].items()))
    for a, c in b["comparaisons"].items():
        print(f"  {b['reference']} contre {a} : {c}")
