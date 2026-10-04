"""Génère la banque de questions d'un cycle mensuel (noyau, sections 8.1 à 8.3).

Usage : python scripts/questions.py AAAA-MM-JJ [ETIQUETTE]   (date du gel ; étiquette du cycle, par défaut AAAA-MM)
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


def generer(gel, etiquette=None):
    mois = gel[:7]
    cycle = etiquette or mois
    gel_dir = RACINE / "data" / "cycles" / cycle / "gel" / "historique"
    lire = (lambda n: commun.serie(n)) if not gel_dir.exists() else (
        lambda n: [(p, float(v)) for p, v in (l.split(",") for l in (gel_dir / f"{n}.csv").read_text("utf-8").splitlines()[1:] if l)])
    resolues = {r["question"] for r in lire_jsonl("registre/resolutions.jsonl")}
    correspondances = lire_json("modele/correspondances_p1.json", {"correspondances": {}})["correspondances"]
    qs, ecartees = [], []

    for nom, meta in VARIABLES.items():
        s = lire(nom)
        publie, base_publiee = s[-1]
        dernier, base, ancrage = publie, base_publiee, None
        if meta.get("proxy"):
            try:
                a = commun.ancrage_quotidien(s, lire(meta["proxy"]))
            except FileNotFoundError:
                a = None
            if a and a[0] > publie:
                dernier, base = a[0], a[1]
                ancrage = {"proxy": meta["proxy"], "niveau_estime": round(a[1], 1), "correction": round(a[2], 1)}
        for h in HORIZONS:
            cible = mois_suivant(mois, h - 1)
            if cible <= publie:
                ecartees.append((f"{nom} {cible}", "valeur déjà publiée"))
                continue
            pas = max(1, ecart_mois(dernier, cible))
            var = variations(s, pas)
            for q in QUANTILES:
                seuil = arrondi(base + quantile(var, q), meta["unite"])
                qid = f"Q-{cycle}-{nom}-{cible}-q{q}"
                qs.append({
                    "id": qid, "type": "variable", "pool": correspondances.get(qid, {}).get("pool", "P2a"),
                    "grappe": f"{nom}-{trimestre(cible)}",
                    "texte": f"La valeur de « {meta['nom']} » pour {cible} est-elle supérieure ou égale à {seuil} {meta['unite']} ? (Dernière valeur publiée au gel : {base_publiee:g} {meta['unite']} pour {publie}"
                            + (f" ; niveau récent estimé d'après les données quotidiennes : {base:.0f} {meta['unite']})" if ancrage else ")"),
                    "issues": ["oui", "non"], "echeance": iso_fin_mois(mois_suivant(cible, meta["delai"])),
                    "details": {"serie": nom, "periode": cible, "seuil": seuil, "derniere_periode": dernier,
                                "derniere_valeur": round(base, 2), "pas": pas, "quantile": q, "n_variations": len(var),
                                "derniere_publiee": [publie, base_publiee], "ancrage_quotidien": ancrage},
                })

    # Banque gelée avec le cycle si elle existe (relecture 12) : un ajout fait après le gel vaut pour le
    # cycle suivant, et questions.py, comparateurs.py et dossier.py lisent la même banque.
    gel_ev = RACINE / "data" / "cycles" / cycle / "gel" / "evenements.json"
    evts = lire_json(str(gel_ev.relative_to(RACINE)) if gel_ev.exists() else "modele/evenements.json")["evenements"]
    # Grappe : l'événement ; ses sous-questions à fenêtres distinctes forment des grappes séparées
    # (noyau, section 8.3, relecture 9).
    fins = {}
    for e in evts:
        fins.setdefault(e["evenement"], set()).add(e["fenetre"]["fin"])
    # Les questions tranchées par un même acte officiel forment une grappe (relecture 12, K4).
    grappe = lambda e: e["acte"] if e.get("acte") else (e["id"] if len(fins[e["evenement"]]) > 1 else e["evenement"])
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
        # Une grappe par événement : la question de fenêtre et ses questions mensuelles sont corrélées
        # (relecture 8, souhaitable « grappes »).
        qs.append({**commun_e, "id": qid, "pool": correspondances.get(qid, {}).get("pool", e.get("pool", "P2b")),
                   "grappe": grappe(e),
                   "texte": (f"{e['nom']} : le critère est-il rempli ? (fenêtre du {debut} au {fin})"
                             if len(e["issues"]) == 2 else f"{e['nom']} : quelle issue, selon le critère ? (échéance : {fin})"),
                   "echeance": fin, "fenetre": {"debut": debut, "fin": fin}})
        if len(e["issues"]) == 2 and e.get("mensuelle", True) and ecart_mois(gel[:7], fin[:7]) > 3 and e["fenetre"]["debut"] <= gel:
            mid = f"Q-{e['id']}-{cycle}"
            qs.append({**commun_e, "id": mid, "pool": correspondances.get(mid, {}).get("pool", e.get("pool", "P2b")),
                       "grappe": grappe(e),
                       "texte": f"{e['nom']} : le critère est-il rempli au cours du mois {mois} ?",
                       "echeance": iso_fin_mois(mois), "fenetre": {"debut": gel, "fin": iso_fin_mois(mois)}})
    return {"cycle": cycle, "gel": gel, "genere_le": maintenant(), "questions": qs,
            "ecartees": [{"objet": o, "motif": m} for o, m in ecartees]}


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("usage : python scripts/questions.py AAAA-MM-JJ [ETIQUETTE]")
    banque = generer(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None)
    ecrire_json(f"data/cycles/{banque['cycle']}/questions.json", banque)
    n = len(banque["questions"])
    g = len({q["grappe"] for q in banque["questions"]})
    pools = {}
    for q in banque["questions"]:
        pools[q["pool"]] = pools.get(q["pool"], 0) + 1
    print(f"Cycle {banque['cycle']} : {n} questions, {g} grappes, pools {pools}, {len(banque['ecartees'])} écartées")
