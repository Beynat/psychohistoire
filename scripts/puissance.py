"""Puissance attendue du critère de la section 8.6 (noyau, section 8.3), publiée avant chaque phase.

Usage : python scripts/puissance.py [--sigma 0.12] [--simulations 4000]
Écrit data/puissance.json.

Modèle de simulation : pour chaque question i de la grappe g, la différence de Brier entre la
référence et le comparateur vaut d_ig = −δ + u_g + e_ig, avec u_g ~ N(0, ρσ²) commun à la grappe et
e_ig ~ N(0, (1 − ρ)σ²). Le test est celui de scripts/notation.py : somme des différences par grappe,
statistique t = ΣD_g / √(ΣD_g²), comparée au quantile unilatéral à 10 % d'une loi de Student à
G − 1 degrés de liberté. Hypothèses déclarées : σ, écart-type des différences de Brier par
question (0,12 par défaut), ρ, corrélation intra-grappe, m, questions par grappe.
"""
import math
import random
import sys

from commun import ecrire_json, maintenant

T10 = {4: 1.533, 5: 1.476, 9: 1.383, 11: 1.363, 14: 1.345, 19: 1.328, 24: 1.318, 39: 1.304, 59: 1.296, 79: 1.292}


def t_critique(dl):
    cles = sorted(T10)
    for c in cles:
        if dl <= c:
            return T10[c]
    return 1.2816


def puissance_banque(ms, delta, rho, sigma, nsim, rnd):
    """Même test, avec le nombre réel de questions résolues de chaque grappe (liste ms)."""
    ok = 0
    su, se = math.sqrt(rho) * sigma, math.sqrt(1 - rho) * sigma
    seuil = t_critique(len(ms) - 1)
    for _ in range(nsim):
        D = []
        for m in ms:
            u = rnd.gauss(0, su)
            D.append(sum(-delta + u + rnd.gauss(0, se) for _ in range(m)))
        ok += -sum(D) / math.sqrt(sum(d * d for d in D)) > seuil
    return ok / nsim


def grappes_banque(debut_p3="2027-01-01", butoir="2027-09-30", conjointes=0):
    """Grappes de P2b (une par événement, ou par sous-question à fenêtre distincte) ayant au moins une
    question émise après le début de la phase 3 et résolue avant la butée, avec leur nombre de
    questions : question de fenêtre close dans l'intervalle, plus une question mensuelle par cycle.
    Les grappes de questions conjointes (P2c, phase 3) sont ajoutées à part, à 3 questions chacune."""
    from commun import lire_json
    G = {}
    for e in lire_json("modele/evenements.json")["evenements"]:
        if not e["source_accessible"] or e.get("pool", "P2b") != "P2b":
            continue
        g = e["id"] if e["evenement"] in ("EV-16", "EV-C3") else e["evenement"]
        f, n = e["fenetre"]["fin"], 0
        if debut_p3 <= f <= butoir:
            n += 1
        if e.get("mensuelle"):
            y, mo = int(debut_p3[:4]), int(debut_p3[5:7])
            while f"{y:04d}-{mo:02d}" <= min(butoir[:7], f[:7]):
                n += 1
                y, mo = (y + 1, 1) if mo == 12 else (y, mo + 1)
        if n:
            G[g] = G.get(g, 0) + n
    return sorted(G.values()) + [3] * conjointes


def puissance(G, m, delta, rho, sigma, nsim, rnd):
    ok = 0
    su, se = math.sqrt(rho) * sigma, math.sqrt(1 - rho) * sigma
    seuil = t_critique(G - 1)
    for _ in range(nsim):
        D = []
        for _g in range(G):
            u = rnd.gauss(0, su)
            D.append(sum(-delta + u + rnd.gauss(0, se) for _ in range(m)))
        t = -sum(D) / math.sqrt(sum(d * d for d in D))
        ok += t > seuil
    return ok / nsim


if __name__ == "__main__":
    sigma = float(sys.argv[sys.argv.index("--sigma") + 1]) if "--sigma" in sys.argv else 0.12
    nsim = int(sys.argv[sys.argv.index("--simulations") + 1]) if "--simulations" in sys.argv else 4000
    rnd = random.Random(1)
    lignes = []
    for G in (12, 25, 40, 60):
        for m in (4, 6):
            for rho in (0.1, 0.3):
                for delta in (0.007, 0.02, 0.04):
                    lignes.append({"grappes": G, "questions_par_grappe": m, "rho": rho, "delta_brier": delta,
                                   "puissance": round(puissance(G, m, delta, rho, sigma, nsim, rnd), 3)})
    nulle = {G: round(puissance(G, 6, 0.0, 0.3, sigma, nsim, rnd), 3) for G in (12, 40)}
    # Banque réelle (relecture 9, H2) : butée intermédiaire du 30 septembre 2027 et butée finale du
    # 30 septembre 2028 ; P2c compté de 0 à 15 grappes, faute de réseau défini.
    banque = []
    for butoir in ("2027-09-30", "2028-09-30"):
        for conj in (0, 15):
            ms = grappes_banque(butoir=butoir, conjointes=conj)
            for rho in (0.1, 0.3):
                for delta in (0.02, 0.04):
                    banque.append({"butee": butoir, "grappes_P2b": len(ms) - conj, "grappes_P2c": conj,
                                   "questions": sum(ms), "rho": rho, "delta_brier": delta,
                                   "puissance": round(puissance_banque(ms, delta, rho, sigma, nsim, rnd), 3)})
    ecrire_json("data/puissance.json", {"etabli_le": maintenant(), "sigma": sigma, "simulations": nsim,
                                        "seuil": "unilatéral 10 %", "taux_fausse_alarme_delta_0": nulle, "table": lignes,
                                        "banque_reelle": banque})
    for b in banque:
        print(f"butée {b['butee']} : {b['grappes_P2b']} + {b['grappes_P2c']} grappes, {b['questions']} questions, ρ={b['rho']} δ={b['delta_brier']} → {b['puissance']:.2f}")
    print(f"σ = {sigma}, {nsim} simulations ; fausse alarme (δ = 0, ρ = 0,3, m = 6) : {nulle}")
    for l in lignes:
        if l["questions_par_grappe"] == 6:
            print(f"G={l['grappes']:3} ρ={l['rho']} δ={l['delta_brier']:.3f} → {l['puissance']:.2f}")
