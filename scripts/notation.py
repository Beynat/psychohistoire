"""Notation des prévisions résolues (noyau, sections 8.5 et 8.6).

Usage : python scripts/notation.py [registre/<fichier>.jsonl] [--reference AUTEUR]
Écrit data/bilans/<date>.json (ou bilan_<suffixe>) et affiche un résumé.

Pour chaque auteur (comparateurs, ensemble direct, puis modèle) et chaque pool :
- Brier (½ Σ sur les issues de la question des écarts au carré, soit (p − y)² en binaire) et score logarithmique, sur la dernière
  prévision émise avant l'échéance ;
- Brier pondéré dans le temps : moyenne, sur chaque jour de l'émission à l'échéance, du Brier de
  la dernière probabilité inscrite ce jour-là (section 8.5) ;
- décomposition de Murphy (fiabilité, résolution, incertitude) sur les questions binaires, en
  dix classes de probabilité.
Comparaison de la référence (par défaut l'ensemble direct en phase 1) à chaque autre auteur sur
les questions communes dont l'échéance est passée à la date du test, quelle que soit leur issue
(relecture 10, I1 : une question de fenêtre résolue « oui » avant son échéance n'entre pas seule
dans le test). Score testé : Brier pondéré dans le temps (noyau, section 8.5), calculé pour chaque
comparaison sur la période commune aux deux auteurs (relecture 11, J1). Différences sommées par grappe, statistique
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
from resolution import cycles_du_registre, resolutions_effectives, suffixe, toutes_les_questions


def brier(dist, issue, issues=None):
    """Brier normalisé (relecture 12, S1) : ½ Σ_k (p_k − y_k)², qui vaut (p − y)² pour une question
    binaire, comme la formule de la section 8.5 ; les écarts de 8.6 (0,02, 0,04) sont dans cette unité."""
    # Somme sur les issues de la question (relecture 13, S11) : une issue absente de la prévision vaut 0.
    return 0.5 * sum((dist.get(k, 0) / 100 - (1.0 if k == issue else 0.0)) ** 2 for k in (issues or set(dist) | {issue}))


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


def test_calibration(items, rho=0.3, nsim=2000, graine=3):
    """Critère de calibration de la section 8.6 (relecture 13, S2). items : (p, y, grappe) des questions
    binaires de P2b et P2c échues à la date du test, dernière prévision de cycle avant résolution (relecture 15, I1). Statistique : terme de fiabilité de Murphy en dix classes.
    Loi sous calibration parfaite : issues tirées avec P(y = 1) = p, corrélées dans une grappe par une
    copule gaussienne de corrélation ρ = 0,3. Échec si la fiabilité observée dépasse le 90e centile."""
    from statistics import NormalDist
    if len(items) < 10:
        return {"questions": len(items), "verdict": "trop peu de questions"}
    obs = murphy([(p, y) for p, y, _ in items])["fiabilite"]
    nd, rnd = NormalDist(), random.Random(graine)
    grappes = sorted({g for _, _, g in items})
    sims = []
    for _ in range(nsim):
        u = {g: rnd.gauss(0, 1) for g in grappes}
        tir = [(p, nd.cdf(math.sqrt(rho) * u[g] + math.sqrt(1 - rho) * rnd.gauss(0, 1)) < p) for p, _, g in items]
        sims.append(murphy(tir)["fiabilite"])
    sims.sort()
    seuil = sims[int(0.9 * nsim)]
    return {"questions": len(items), "grappes": len(grappes), "fiabilite": obs, "seuil_90": round(seuil, 4),
            "verdict": "recalibrer" if obs > seuil else "conforme"}


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
    # Écart moyen par question et intervalle à 80 % par rééchantillonnage des grappes (relecture 11, S8).
    nq = [len(v) for v in diffs.values()]
    moyen = sum(D) / sum(nq)
    rb = random.Random(1)
    boots = []
    for _ in range(2000):
        idx = [rb.randrange(G) for _ in range(G)]
        boots.append(sum(D[i] for i in idx) / sum(nq[i] for i in idx))
    boots.sort()
    return {"grappes": G, "questions": sum(nq), "t": round(t, 3), "p_unilaterale": round(p, 4),
            "p_unilaterale_autre": round(p_autre, 4), "verdict": verdict, "ecart_moyen": round(moyen, 4),
            "intervalle_80": [round(boots[200], 4), round(boots[1799], 4)]}


def fin_brier(q, r):
    """Dernier jour du Brier pondéré : l'échéance, ou la veille du fait s'il la précède."""
    if r.get("date_fait"):
        return min(q["echeance"], (date.fromisoformat(r["date_fait"]) - timedelta(days=1)).isoformat())
    return q["echeance"]


def brier_pondere(lignes, issue, debut, fin):
    """Moyenne journalière, de debut à fin inclus, du Brier de la dernière prévision inscrite ce jour-là.
    Les jours antérieurs à la première prévision de l'auteur ne sont pas comptés : l'appelant fixe debut."""
    jour, k, cumul, n = date.fromisoformat(debut), -1, 0.0, 0
    while jour <= date.fromisoformat(fin):
        while k + 1 < len(lignes) and lignes[k + 1]["emise"][:10] <= jour.isoformat():
            k += 1
        if k >= 0:
            cumul += brier(lignes[k]["probabilites"], issue)
            n += 1
        jour += timedelta(days=1)
    return cumul / n if n else None


def bilan(reg="registre/protocole.jsonl", reference="ensemble direct", aujourdhui=None):
    aujourdhui = aujourdhui or date.today().isoformat()
    sfx = suffixe(reg)
    qs = toutes_les_questions(cycles_du_registre(reg))
    res = {q: r for q, r in resolutions_effectives(sfx).items() if r.get("issue") is not None}
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
        fin = fin_brier(q, r)
        d0 = lignes[0]["emise"][:10]
        cyc = [l for l in lignes if str(l.get("origine", "")).startswith("cycle")]
        der = lignes[-1]["probabilites"]
        der_cycle = cyc[-1]["probabilites"] if cyc else None
        scores[(auteur, qid)] = {"brier": brier(der, r["issue"]), "log": logs(der, r["issue"]),
                                 "brier_temps": brier_pondere(lignes, r["issue"], d0, fin), "pool": q["pool"], "grappe": q["grappe"],
                                 "lignes": lignes, "debut": d0, "fin": fin,
                                 "binaire": len(q["issues"]) == 2,
                                 "p_oui": (der_cycle or der).get("oui", 0) / 100, "cycle_seul": der_cycle is not None,
                                 "y": r["issue"] == "oui"}
    auteurs = sorted({a for a, _ in scores})
    # Événements ajoutés en cours de phase (noyau, section 8.8) : bilan avec et sans eux.
    import json as _json
    from commun import RACINE
    fa = RACINE / "modele/banque/ajouts.jsonl"
    ajoutes = {_json.loads(l)["id"] for l in fa.read_text("utf-8").splitlines() if l.strip()} if fa.exists() else set()
    evenement = lambda qid: (qs[qid].get("details") or {}).get("evenement") or qid.removeprefix("Q-")
    echue = lambda qid: qs[qid]["echeance"] <= aujourdhui
    par_auteur = {}
    for a in auteurs:
        mes = {qid: s for (aa, qid), s in scores.items() if aa == a}
        pools = {}
        for s in mes.values():
            pools.setdefault(s["pool"], []).append(s)
        # Calibration (section 8.6 ; relecture 15, I1) : questions échues à la date du test, quelle que soit
        # leur issue, comme pour le test de valeur ajoutée ; dernière prévision de cycle avant résolution ;
        # avec et sans les questions ajoutées.
        cal = [(qid, (x["p_oui"], x["y"], x["grappe"])) for qid, x in mes.items()
               if x["binaire"] and x["pool"] in ("P2b", "P2c") and x.get("cycle_seul") and echue(qid)]
        cal_avec = test_calibration([c for _, c in cal])
        cal_sans = test_calibration([c for qid, c in cal if evenement(qid) not in ajoutes])
        par_auteur[a] = {"questions": len(mes), "calibration_8_6": cal_avec, "calibration_8_6_sans_ajouts": cal_sans,
                         "pools": {
            p: {"n": len(v), "brier": round(sum(x["brier"] for x in v) / len(v), 4),
                "log": round(sum(x["log"] for x in v) / len(v), 4),
                "brier_temps": round(sum(x["brier_temps"] for x in v) / len(v), 4),
                "murphy": murphy([(x["p_oui"], x["y"]) for x in v if x["binaire"]])} for p, v in pools.items()}}

    def comparer(a, garder, instantanes=True, ref=None):
        ref = ref or reference
        diffs, echelles = {}, {}
        for (aa, qid), s in scores.items():
            if aa != ref or (a, qid) not in scores or not echue(qid) or not garder(qid, s):
                continue
            # Période commune (relecture 11, J1) : du plus tardif des deux premiers jours de prévision
            # à la veille du fait ou à l'échéance.
            o = scores[(a, qid)]
            ls, lo = s["lignes"], o["lignes"]
            if instantanes:
                # Instantanés mensuels (relecture 12, K3) : seules les prévisions des cycles mensuels
                # (origine « cycle … ») ; les mises à jour continues de la phase 3 sont exclues du test.
                ls = [l for l in ls if str(l.get("origine", "")).startswith("cycle")]
                lo = [l for l in lo if str(l.get("origine", "")).startswith("cycle")]
                if not ls or not lo:
                    continue
            debut = max(ls[0]["emise"][:10], lo[0]["emise"][:10])
            if debut > s["fin"]:
                continue
            issue = res[qid]["issue"]
            br, bo = brier_pondere(ls, issue, debut, s["fin"]), brier_pondere(lo, issue, debut, o["fin"])
            if br is not None and bo is not None:
                diffs.setdefault(s["grappe"], []).append(br - bo)
                pr = s["p_oui"] if s["binaire"] else None
                echelles.setdefault(s["grappe"], []).append(4 * pr * (1 - pr) if pr is not None else 1.0)
        t = test_grappes(diffs)
        t["reference"], t["autre"] = ref, a
        # Puissance recalculée sur les grappes réellement présentes (relecture 11, S8).
        if len(echelles) >= 2:
            import puissance
            rnd = random.Random(2)
            t["puissance_recalculee"] = {
                f"delta_{d}": round(puissance.puissance_echelles(list(echelles.values()), d, 0.3, 0.12, 1000, rnd), 3)
                for d in (0.02, 0.04)}
        # Analyse en retirant chaque grappe tour à tour (relecture 15, S2c), publiée avec le verdict.
        if len(diffs) >= 3:
            t["sans_chaque_grappe"] = {g: test_grappes({k: v for k, v in diffs.items() if k != g})["verdict"]
                                       for g in sorted(diffs)}
        return t

    def combine(avec, sans):
        # Verdict combiné (relecture 13, S9) : non concluant si les deux bilans diffèrent.
        return avec["verdict"] if avec["verdict"] == sans["verdict"] else "non concluant (bilans avec et sans ajouts divergents)"

    p2bc = lambda qid, s: s["pool"] in ("P2b", "P2c")
    p2bc_sans = lambda qid, s: p2bc(qid, s) and evenement(qid) not in ajoutes
    comparaisons = {}
    if reference in auteurs:
        for a in auteurs:
            if a == reference:
                continue
            # Test de la section 8.6 : pools P2b et P2c seulement (relecture 12, K2), avec et sans ajouts.
            avec, sans = comparer(a, p2bc), comparer(a, p2bc_sans)
            comparaisons[a] = {
                "verdict_8_6": combine(avec, sans),
                "critere_8_6": avec,
                "critere_8_6_sans_ajouts": sans,
                "toutes_questions_descriptif": comparer(a, lambda qid, s: True),
                # Apport des mises à jour continues, descriptif, sans décision (relecture 12, K3).
                "mises_a_jour_continues_descriptif": comparer(a, p2bc, instantanes=False),
            }
    # Bilan de la section 8.6 pour le modèle (relecture 15, S3), en une fois, quelle que soit la référence
    # demandée : valeur ajoutée contre l'ensemble direct ; persistance (P2a) et taux de base (P2b) contre le
    # modèle. Dans chaque test, « référence » désigne le premier auteur : verdict « référence meilleure »
    # = le modèle fait mieux que le comparateur, sauf pour la valeur ajoutée, où la référence est l'ensemble.
    bilan_8_6 = None
    if "modèle" in auteurs:
        ca, cs = par_auteur["modèle"]["calibration_8_6"], par_auteur["modèle"]["calibration_8_6_sans_ajouts"]
        bilan_8_6 = {"calibration": {"verdict": combine(ca, cs), "avec_ajouts": ca, "sans_ajouts": cs}}
        if "ensemble direct" in auteurs:
            avec = comparer("modèle", p2bc, ref="ensemble direct")
            sans = comparer("modèle", p2bc_sans, ref="ensemble direct")
            bilan_8_6["valeur_ajoutee"] = {"verdict": combine(avec, sans), "avec_ajouts": avec, "sans_ajouts": sans,
                                           "lecture": "« autre meilleur » = le modèle bat l'ensemble direct"}
        if "comparateur : persistance" in auteurs:
            t = comparer("comparateur : persistance", lambda qid, s: s["pool"] == "P2a", ref="modèle")
            bilan_8_6["persistance_P2a"] = {"verdict": t["verdict"], "test": t,
                                            "lecture": "« autre meilleur » = la persistance bat le modèle (échec méthodologique)"}
        if "comparateur : taux de base" in auteurs:
            avec = comparer("comparateur : taux de base", lambda qid, s: s["pool"] == "P2b", ref="modèle")
            sans = comparer("comparateur : taux de base", lambda qid, s: s["pool"] == "P2b" and evenement(qid) not in ajoutes, ref="modèle")
            bilan_8_6["taux_de_base_P2b"] = {"verdict": combine(avec, sans), "avec_ajouts": avec, "sans_ajouts": sans,
                                             "lecture": "« autre meilleur » = le taux de base bat le modèle (échec méthodologique)"}
    for v in scores.values():
        for k in ("lignes", "debut", "fin"):
            v.pop(k, None)
    sortie = {"etabli_le": maintenant(), "registre": reg, "reference": reference,
              "questions_resolues": len(res), "auteurs": par_auteur, "comparaisons": comparaisons,
              "bilan_8_6_modele": bilan_8_6, "exclues": exclues}
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
        print(f"  {b['reference']} contre {a} : {c['critere_8_6']}")
    if b["bilan_8_6_modele"]:
        print("Bilan 8.6 du modèle : " + " ; ".join(f"{k} : {v.get('verdict')}" for k, v in b["bilan_8_6_modele"].items()))
