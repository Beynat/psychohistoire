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


def questions_banque(debut_p3="2027-01-01", butoir="2027-09-30"):
    """Questions de P2b réellement émises par scripts/questions.py à chaque cycle mensuel, du début de
    la phase 3 à la butée, et comptées dans le test de la section 8.6 : échéance passée à la butée,
    quelle que soit l'issue (relecture 10, I1). Chaque question porte une échelle 4p(1 − p), où p est
    son taux de base sur sa fenêtre (1 pour une question à plusieurs issues) : deux prévisions sur un
    événement rare ne peuvent différer que de peu en Brier (relecture 10, I2). Renvoie {grappe: [échelles]}."""
    import questions as gq
    from commun import lire_json, jours
    evts = {e["id"]: e for e in lire_json("modele/evenements.json")["evenements"]}
    tb = lire_json("modele/taux_base.json")["questions"]
    vues, G = set(), {}
    y, m = int(debut_p3[:4]), int(debut_p3[5:7])
    while f"{y:04d}-{m:02d}" <= butoir[:7]:
        banque = gq.generer(f"{y:04d}-{m:02d}-01", f"sim-{y:04d}-{m:02d}")
        for q in banque["questions"]:
            if q["type"] != "evenement" or q["pool"] != "P2b" or q["id"] in vues or q["echeance"] > butoir:
                continue
            vues.add(q["id"])
            e = evts[q["details"]["evenement"]]
            if len(q["issues"]) > 2 or e["id"] not in tb:
                ech = 1.0
            else:
                pf = tb[e["id"]]["utilisee"]["oui"] / 100
                if e.get("nature") == "survenue":
                    r = max(jours(q["fenetre"]["debut"], q["fenetre"]["fin"]), 1) / max(jours(e["fenetre"]["debut"], e["fenetre"]["fin"]), 1)
                    pf = 1 - (1 - pf) ** min(r, 1)
                ech = 4 * pf * (1 - pf)
            G.setdefault(q["grappe"], []).append(ech)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return G


def puissance_echelles(grappes, delta, rho, sigma, nsim, rnd):
    """Test de scripts/notation.py ; écart et dispersion de chaque question multipliés par son échelle
    (écart δ·e, écart-type σ·√e), effet de grappe commun de variance ρσ² × échelle moyenne."""
    ok = 0
    seuil = t_critique(len(grappes) - 1)
    for _ in range(nsim):
        D = []
        for ech in grappes:
            em = sum(ech) / len(ech)
            u = rnd.gauss(0, math.sqrt(rho * em) * sigma)
            D.append(sum(-delta * e + u + rnd.gauss(0, math.sqrt((1 - rho) * e) * sigma) for e in ech))
        ok += -sum(D) / math.sqrt(sum(d * d for d in D)) > seuil
    return ok / nsim


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
    # Démarrage tardif de la phase 3 (relecture 12, S10) : questions informatives restantes.
    tardif = {}
    for debut in ("2027-01-01", "2027-02-01", "2027-03-01", "2027-04-01", "2027-05-01"):
        G = questions_banque(debut_p3=debut)
        tardif[debut] = {"grappes_P2b": len(G), "questions_informatives": sum(1 for g in G.values() for e in g if e >= 0.5),
                         "puissance_0.04": round(puissance_echelles(list(G.values()), 0.04, 0.3, sigma, nsim, rnd), 3) if len(G) > 1 else None}
    # Banque réelle (relecture 10, I2) : questions effectivement émises, échéance passée à la butée,
    # écart proportionné à la probabilité de chaque question ; P2c compté de 0 à 15 grappes de
    # 3 questions d'échelle 1, faute de réseau défini.
    banque = []
    for butoir in ("2027-09-30", "2028-09-30"):
        G = questions_banque(butoir=butoir)
        for conj in (0, 15):
            # Questions conjointes « A et B » : plus rares qu'une issue à 50 % ; échelle d'une probabilité
            # de 10 % (relecture 12, S10).
            grappes = list(G.values()) + [[4 * 0.1 * 0.9] * 3] * conj
            for rho in (0.1, 0.3):
                for delta in (0.02, 0.04):
                    banque.append({"butee": butoir, "grappes_P2b": len(G), "grappes_P2c": conj,
                                   "questions": sum(len(g) for g in grappes),
                                   "questions_informatives": sum(1 for g in grappes for e in g if e >= 0.5),
                                   "rho": rho, "delta_brier": delta,
                                   "puissance": round(puissance_echelles(grappes, delta, rho, sigma, nsim, rnd), 3)})
    ecrire_json("data/puissance.json", {"etabli_le": maintenant(), "sigma": sigma, "simulations": nsim,
                                        "seuil": "unilatéral 10 %", "taux_fausse_alarme_delta_0": nulle, "table": lignes,
                                        "banque_reelle": banque, "demarrage_tardif": tardif})
    print("démarrage tardif :", tardif)
    for b in banque:
        print(f"butée {b['butee']} : {b['grappes_P2b']} + {b['grappes_P2c']} grappes, {b['questions']} questions ({b['questions_informatives']} informatives), ρ={b['rho']} δ={b['delta_brier']} → {b['puissance']:.2f}")
    print(f"σ = {sigma}, {nsim} simulations ; fausse alarme (δ = 0, ρ = 0,3, m = 6) : {nulle}")
    for l in lignes:
        if l["questions_par_grappe"] == 6:
            print(f"G={l['grappes']:3} ρ={l['rho']} δ={l['delta_brier']:.3f} → {l['puissance']:.2f}")
