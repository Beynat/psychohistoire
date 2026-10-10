"""Profils de risque des pivots « à tout moment » (feuille de route, étape 10).

Le risque mensuel constant est remplacé par une répartition dans le temps élicitée sur des tranches de dates réelles :
« si l'événement survient dans sa fenêtre, cas de référence (sans déclencheur), quelle part tombe dans chaque
tranche ? » (pourcentages de somme 100). Pour PV-NOTE, dont le profil suit déjà les revues programmées des agences
(calendrier.json), la question porte sur le poids d'un mois sans revue rapporté à un mois avec revue.

Conversion (exacte au cas de référence) : F(m) répartition cumulée du moment de survenue à la fin du mois m (linéaire
en jours dans une tranche), P probabilité de fenêtre de référence ; le moteur donne une survenue cumulée
1 - (1 - P)^(W_m / W), donc W_m / W = ln(1 - P F(m)) / ln(1 - P), et w_m = W_m - W_{m-1}. Pour P petit, w est
proportionnel à la densité élicitée ; pour P grand, la conversion corrige la concentration en début de fenêtre.

Usage : python scripts/profils.py gabarit SORTIE
        python scripts/profils.py controle REPONSE...       (contrôles d'une ronde ; rend 1 si un défaut)
        python scripts/profils.py agreger SORTIE REPONSE...  (moyenne des répartitions, moyenne géométrique du ratio)
        python scripts/profils.py appliquer AGREGAT           (écrit les profils dans la structure et le calendrier)
"""
import json
import math
import statistics
import sys
from datetime import date

from commun import RACINE, lire_json

# Tranches : (identifiant, début, fin inclus). Bornes alignées sur le calendrier du dossier profils_2026-10-10.md.
TRANCHES = {
    "PV-CENSURE1a": [("oct", "2026-10-10", "2026-10-31"), ("nov", "2026-11-01", "2026-11-30"),
                     ("dec", "2026-12-01", "2026-12-31")],
    "PV-CENSURE1b": [("jan", "2027-01-01", "2027-01-31"), ("fev", "2027-02-01", "2027-02-28"),
                     ("mar-mai", "2027-03-01", "2027-05-02")],
    "PV-GOUV": [("oct", "2026-10-10", "2026-10-31"), ("nov", "2026-11-01", "2026-11-30"), ("dec", "2026-12-01", "2026-12-31"),
                ("jan", "2027-01-01", "2027-01-31"), ("fev", "2027-02-01", "2027-02-28"), ("mar-mai", "2027-03-01", "2027-05-02")],
    "PV-DISSOL1": [("oct", "2026-10-10", "2026-10-31"), ("nov", "2026-11-01", "2026-11-30"), ("dec", "2026-12-01", "2026-12-31"),
                   ("jan", "2027-01-01", "2027-01-31"), ("fev", "2027-02-01", "2027-02-28"), ("mar-mai", "2027-03-01", "2027-05-02")],
    "PV-DISSOL2a": [("mai", "2027-05-03", "2027-05-31"), ("juin", "2027-06-01", "2027-06-30")],
    "PV-DISSOL2b": [("2027-T3", "2027-07-01", "2027-09-30"), ("2027-T4", "2027-10-01", "2027-12-31"),
                    ("2028-S1", "2028-01-01", "2028-06-30"), ("2028-T3", "2028-07-01", "2028-09-30")],
    "PV-CENSURE2": [("mai-juin", "2027-05-03", "2027-06-30"), ("2027-T3", "2027-07-01", "2027-09-30"),
                    ("2027-T4", "2027-10-01", "2027-12-31"), ("2028-S1", "2028-01-01", "2028-06-30"),
                    ("2028-T3", "2028-07-01", "2028-09-30")],
    "PV-PDE": [("2026-10-2027-01", "2026-10-10", "2027-01-31"), ("2027-02-05", "2027-02-01", "2027-05-31"),
               ("2027-06-07", "2027-06-01", "2027-07-31"), ("2027-08-10", "2027-08-01", "2027-10-31"),
               ("2027-11-2028-01", "2027-11-01", "2028-01-31"), ("2028-02-05", "2028-02-01", "2028-05-31"),
               ("2028-06-09", "2028-06-01", "2028-09-30")],
}

REFERENCE = {
    "PV-CENSURE1a": "Gouvernement Lecornu en place, sans choc imprévu ; censure adoptée d'ici fin 2026.",
    "PV-CENSURE1b": "Aucune censure en 2026, sans choc imprévu ; censure adoptée entre le 1er janvier et le 2 mai 2027.",
    "PV-GOUV": "Fin des fonctions de Sébastien Lecornu SANS censure adoptée (démission, remaniement, candidature, "
               "autre cause) ; le départ consécutif à une censure est traité à part (immédiat, article 50).",
    "PV-DISSOL1": "Dissolution avant le 2 mai 2027 SANS censure préalable ; la dissolution qui suit une censure est "
                  "traitée par un autre paramètre.",
    "PV-DISSOL2a": "Dissolution par le président élu en 2027, entre le 3 mai et le 30 juin 2027 (aucune dissolution "
                   "avant le 2 mai).",
    "PV-DISSOL2b": "Dissolution entre juillet 2027 et septembre 2028, aucune dissolution depuis juin 2024 (pas de verrou "
                   "de l'article 12 en cours).",
    "PV-CENSURE2": "Censure d'un gouvernement nommé par le président élu en 2027, entre le 3 mai 2027 et le 30 septembre 2028.",
    "PV-PDE": "Décision du Conseil visant la France au titre de l'article 126, paragraphe 8 ou 9, TFUE, entre le "
              "10 octobre 2026 et le 30 septembre 2028.",
}

QUESTION_NOTE = ("PV-NOTE (abaissement de la note de la France par Moody's, S&P ou Fitch) : rapport entre la "
                 "probabilité d'un abaissement pendant un mois SANS revue programmée de la France et pendant un mois "
                 "AVEC une revue programmée, toutes choses égales par ailleurs (nombre positif, par exemple 0,1 ou 0,5).")

SEUIL_ECART = 25   # points : avis isolé sur une tranche, signalé au retour de ronde


def jours(d0, d1):
    return date.fromisoformat(d1).toordinal() - date.fromisoformat(d0).toordinal() + 1


def gabarit():
    return {"lecture": "Pour chaque pivot, répartis 100 % entre les tranches : part de la survenue qui tombe dans "
                       "chaque tranche si l'événement survient dans sa fenêtre, dans le cas de référence indiqué. Ce "
                       "n'est pas la probabilité de l'événement, seulement sa répartition dans le temps. Justification "
                       "par tranche (URL ou « jugement : … »).",
            "evaluateur": "", "date": "",
            "pivots": {i: {"reference": REFERENCE[i],
                           "tranches": {t: {"du": a, "au": b, "pourcent": None, "justification": ""} for t, a, b in tr}}
                       for i, tr in TRANCHES.items()},
            "PV-NOTE": {"question": QUESTION_NOTE, "rapport_hors_revue": None, "justification": ""}}


def controle(r):
    defauts = []
    for i, tr in TRANCHES.items():
        d = r["pivots"].get(i)
        if not d:
            defauts.append(f"{i} : absent")
            continue
        vals = [d["tranches"].get(t, {}).get("pourcent") for t, _, _ in tr]
        if any(not isinstance(v, (int, float)) or v < 0 for v in vals):
            defauts.append(f"{i} : pourcentage manquant ou négatif")
            continue
        if abs(sum(vals) - 100) > 0.5:
            defauts.append(f"{i} : somme {sum(vals)} au lieu de 100")
        for t, _, _ in tr:
            if not (d["tranches"][t].get("justification") or "").strip():
                defauts.append(f"{i} {t} : justification vide")
    n = r.get("PV-NOTE", {})
    if not isinstance(n.get("rapport_hors_revue"), (int, float)) or not 0 < n["rapport_hors_revue"] <= 1.5:
        defauts.append("PV-NOTE : rapport hors revue manquant ou hors de ]0 ; 1,5]")
    if not (n.get("justification") or "").strip():
        defauts.append("PV-NOTE : justification vide")
    return defauts


def ecarts(reponses):
    """Avis isolés : sur une tranche, écart de plus de SEUIL_ECART points à la moyenne des autres évaluateurs."""
    out = []
    for i, tr in TRANCHES.items():
        for t, _, _ in tr:
            vs = {r["evaluateur"]: r["pivots"][i]["tranches"][t]["pourcent"] for r in reponses}
            for e, v in vs.items():
                autres = [x for f, x in vs.items() if f != e]
                if autres and abs(v - statistics.mean(autres)) > SEUIL_ECART:
                    out.append(f"{e} {i} {t} : {v} % contre {statistics.mean(autres):.0f} % en moyenne chez les autres")
    return out


def agreger(reponses):
    ag = {"evaluateurs": [r["evaluateur"] for r in reponses], "pivots": {}}
    for i, tr in TRANCHES.items():
        m = {t: statistics.mean(r["pivots"][i]["tranches"][t]["pourcent"] for r in reponses) for t, _, _ in tr}
        s = sum(m.values())
        ag["pivots"][i] = {t: round(100 * v / s, 2) for t, v in m.items()}
    ag["PV-NOTE"] = {"rapport_hors_revue": round(math.exp(statistics.mean(
        math.log(r["PV-NOTE"]["rapport_hors_revue"]) for r in reponses)), 3)}
    return ag


def cumul_mensuel(i, repartition, mois):
    """F(m) : part cumulée à la fin de chaque mois de `mois` (linéaire en jours dans chaque tranche)."""
    out = []
    for m in mois:
        a, mm = int(m[:4]), int(m[5:])
        fin = date(a + (mm == 12), mm % 12 + 1, 1).toordinal() - 1
        f = 0.0
        for t, d0, d1 in TRANCHES[i]:
            o0, o1 = date.fromisoformat(d0).toordinal(), date.fromisoformat(d1).toordinal()
            if fin >= o1:
                f += repartition[t]
            elif fin >= o0:
                f += repartition[t] * (fin - o0 + 1) / (o1 - o0 + 1)
        out.append(min(f / 100, 1.0))
    return out


def poids(i, repartition, p_ref, mois):
    """Poids mensuels du profil, exacts pour la probabilité de fenêtre p_ref (voir l'en-tête)."""
    F = cumul_mensuel(i, repartition, mois)
    p = min(max(p_ref, 1e-6), 0.999)
    W = [math.log(1 - p * f) / math.log(1 - p) for f in F]
    return [round(max(W[k] - (W[k - 1] if k else 0.0), 0.0), 6) for k in range(len(mois))]


def p_reference(structure, tables, n=1000):
    """Probabilité de fenêtre de chaque pivot à profil plat, au cas de référence de l'élicitation : trajectoires du
    moteur où aucun parent « à tout moment » n'est survenu."""
    import random
    import reseau
    s = json.loads(json.dumps(structure))
    for nd in s["pivots"]:
        if nd["id"] in TRANCHES:
            nd.pop("profil", None)
    reseau._PROFILS.clear()
    obs = reseau.observations(s)
    reseau.PRIORS = reseau.lois_a_priori(s, tables, obs)
    noeuds = {nd["id"]: nd for nd in s["pivots"]}
    # Cas de référence : aucun parent « à tout moment » survenu (ni déclencheur, ni verrou de l'article 12).
    declencheurs = {i: [reseau.pid(q) for q in noeuds[i].get("parents", [])
                        if noeuds.get(reseau.pid(q), {}).get("nature") == "à tout moment"] for i in TRANCHES}
    rng = random.Random(11)
    c, m = dict.fromkeys(TRANCHES, 0), dict.fromkeys(TRANCHES, 0)
    for _ in range(n):
        tr = reseau.simuler(s, tables["noeuds"], obs, rng)
        for i in TRANCHES:
            if not any("oui" in tr[d] for d in declencheurs[i]):
                m[i] += 1
                c[i] += "oui" in tr[i]
    reseau._PROFILS.clear()
    return {i: c[i] / max(m[i], 1) for i in TRANCHES}


def appliquer(ag, structure_f="modele/reseau/structure_v0.json", calendrier_f="modele/reseau/calendrier.json"):
    import reseau
    s = lire_json(structure_f)
    t = lire_json("modele/reseau/tables_v0.json")
    pref = p_reference(s, t)
    for nd in s["pivots"]:
        if nd["id"] in TRANCHES:
            w = poids(nd["id"], ag["pivots"][nd["id"]], pref[nd["id"]], reseau.MOIS)
            nd["profil"] = {"poids": dict(zip(reseau.MOIS, w)), "defaut": 0.0,
                            "repartition": ag["pivots"][nd["id"]], "p_reference": round(pref[nd["id"]], 3),
                            "source": f"élicitation du 10 octobre 2026 ({', '.join(ag['evaluateurs'])}), étape 10"}
    (RACINE / structure_f).write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n", "utf-8")
    c = lire_json(calendrier_f)
    c["profils"]["PV-NOTE"]["poids_hors_revue"] = ag["PV-NOTE"]["rapport_hors_revue"]
    c["profils"]["PV-NOTE"]["motif"] += (f" Rapport élicité à l'étape 10 ({', '.join(ag['evaluateurs'])}, moyenne "
                                         f"géométrique) : {ag['PV-NOTE']['rapport_hors_revue']}.")
    (RACINE / calendrier_f).write_text(json.dumps(c, ensure_ascii=False, indent=1) + "\n", "utf-8")
    return pref


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["gabarit"]:
        open(a[1], "w", encoding="utf-8").write(json.dumps(gabarit(), ensure_ascii=False, indent=1))
    elif a[:1] == ["controle"]:
        rs = [json.load(open(f, encoding="utf-8")) for f in a[1:]]
        ko = False
        for f, r in zip(a[1:], rs):
            d = controle(r)
            ko |= bool(d)
            print(f"{f} : " + ("conforme" if not d else "; ".join(d)))
        if len(rs) > 1 and not ko:
            for e in ecarts(rs):
                print("écart :", e)
        sys.exit(1 if ko else 0)
    elif a[:1] == ["agreger"]:
        ag = agreger([json.load(open(f, encoding="utf-8")) for f in a[2:]])
        open(a[1], "w", encoding="utf-8").write(json.dumps(ag, ensure_ascii=False, indent=1))
        print(json.dumps(ag, ensure_ascii=False))
    elif a[:1] == ["appliquer"]:
        print(appliquer(json.load(open(a[1], encoding="utf-8"))))
    else:
        sys.exit(__doc__)
