"""Génère la banque de questions d'un cycle mensuel (noyau, sections 8.1 à 8.3).

Usage : python scripts/questions.py AAAA-MM-JJ   (date du gel, en général le 1er du mois)
Écrit data/cycles/<AAAA-MM>/questions.json. Lit les données gelées du cycle si elles existent
(data/cycles/<AAAA-MM>/gel/), sinon les données courantes.

Variables : pour chaque série, horizons 1 à 3 mois après le mois du gel, seuils aux quantiles 20,
50 et 80 de la marche aléatoire empirique (variations depuis 2010). Événements : une question sur
la fenêtre restante de chaque événement résoluble non encore résolu, et une question sur le mois
courant quand la fenêtre restante dépasse trois mois. Aucune question n'est émise si sa
résolution est déjà publique (section 8.2).
"""
import sys
from datetime import date

from commun import (HORIZONS, QUANTILES, VARIABLES, ecart_mois, ecrire_json, lire_json, lire_jsonl,
                    maintenant, mois_suivant, quantile, trimestre, variations, RACINE)
import commun


def fin_mois(m):
    return (date(int(m[:4]) + (m[5:7] == "12"), int(m[5:7]) % 12 + 1, 1).toordinal() - 1)


def iso_fin_mois(m):
    return date.fromordinal(fin_mois(m)).isoformat()


def arrondi(v, unite):
    return round(v) if unite == "pb" else round(v, 1)


def generer(gel):
    cycle = gel[:7]
    gel_dir = RACINE / "data" / "cycles" / cycle / "gel" / "historique"
    lire = (lambda n: commun.serie(n)) if not gel_dir.exists() else (
        lambda n: [(p, float(v)) for p, v in (l.split(",") for l in (gel_dir / f"{n}.csv").read_text("utf-8").splitlines()[1:] if l)])
    resolues = {r["question"] for r in lire_jsonl("registre/resolutions.jsonl")}
    correspondances = lire_json("modele/correspondances_p1.json", {"correspondances": {}})["correspondances"]
    qs, ecartees = [], []

    for nom, meta in VARIABLES.items():
        s = lire(nom)
        dernier, base = s[-1]
        for h in HORIZONS:
            cible = mois_suivant(cycle, h - 1)
            if cible <= dernier:
                ecartees.append((f"{nom} {cible}", "valeur déjà publiée"))
                continue
            pas = ecart_mois(dernier, cible)
            var = variations(s, pas)
            for q in QUANTILES:
                seuil = arrondi(base + quantile(var, q), meta["unite"])
                qid = f"Q-{cycle}-{nom}-{cible}-q{q}"
                qs.append({
                    "id": qid, "type": "variable", "pool": correspondances.get(qid, {}).get("pool", "P2a"),
                    "grappe": f"{nom}-{trimestre(cible)}",
                    "texte": f"La valeur de « {meta['nom']} » pour {cible} est-elle supérieure ou égale à {seuil} {meta['unite']} ? (Dernière valeur publiée au gel : {base:g} {meta['unite']} pour {dernier}.)",
                    "issues": ["oui", "non"], "echeance": iso_fin_mois(mois_suivant(cible, meta["delai"])),
                    "details": {"serie": nom, "periode": cible, "seuil": seuil, "derniere_periode": dernier,
                                "derniere_valeur": base, "pas": pas, "quantile": q, "n_variations": len(var)},
                })

    evts = lire_json("modele/evenements.json")["evenements"]
    for e in evts:
        if not e["source_accessible"]:
            ecartees.append((e["id"], e["motif_inaccessible"]))
            continue
        debut, fin = max(e["fenetre"]["debut"], gel), e["fenetre"]["fin"]
        if fin < gel:
            continue
        qid = f"Q-{e['id']}"
        if qid in resolues:
            ecartees.append((qid, "déjà résolue"))
            continue
        commun_e = {"type": "evenement", "issues": e["issues"], "details": {"evenement": e["id"], "critere": e["critere"]}}
        qs.append({**commun_e, "id": qid, "pool": correspondances.get(qid, {}).get("pool", "P2b"),
                   "grappe": f"{e['evenement']}-{trimestre(fin)}",
                   "texte": f"{e['nom']}{' (' + e['sous_question'] + ')' if e['sous_question'] else ''} : le critère est-il rempli entre le {debut} et le {fin} ?",
                   "echeance": fin, "fenetre": {"debut": debut, "fin": fin}})
        if len(e["issues"]) == 2 and e.get("mensuelle", True) and ecart_mois(gel[:7], fin[:7]) > 3 and e["fenetre"]["debut"] <= gel:
            mid = f"Q-{e['id']}-{cycle}"
            qs.append({**commun_e, "id": mid, "pool": correspondances.get(mid, {}).get("pool", "P2b"),
                       "grappe": f"{e['evenement']}-{trimestre(cycle)}",
                       "texte": f"{e['nom']} : le critère est-il rempli au cours du mois {cycle} ?",
                       "echeance": iso_fin_mois(cycle), "fenetre": {"debut": gel, "fin": iso_fin_mois(cycle)}})
    return {"cycle": cycle, "gel": gel, "genere_le": maintenant(), "questions": qs,
            "ecartees": [{"objet": o, "motif": m} for o, m in ecartees]}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage : python scripts/questions.py AAAA-MM-JJ")
    banque = generer(sys.argv[1])
    ecrire_json(f"data/cycles/{banque['cycle']}/questions.json", banque)
    n = len(banque["questions"])
    g = len({q["grappe"] for q in banque["questions"]})
    pools = {}
    for q in banque["questions"]:
        pools[q["pool"]] = pools.get(q["pool"], 0) + 1
    print(f"Cycle {banque['cycle']} : {n} questions, {g} grappes, pools {pools}, {len(banque['ecartees'])} écartées")
