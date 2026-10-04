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
                    maintenant, mois_suivant, quantile, trimestre, variations_question, RACINE)
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
    from resolution import resolutions_effectives
    resolues = set(resolutions_effectives(""))   # errata de réouverture appliqués (relecture 13, S1)
    gel_corr = RACINE / "data" / "cycles" / cycle / "gel" / "correspondances_p1.json"
    correspondances = lire_json(str(gel_corr.relative_to(RACINE)) if gel_corr.exists() else "modele/correspondances_p1.json",
                                {"correspondances": {}})["correspondances"]
    qs, ecartees = [], []
    # Séries non collectées depuis plus de trois jours au gel (relecture 15, S6) : une publication a pu
    # échapper à la collecte, et la question serait émise alors que sa valeur est publique.
    etat_f = (gel_dir / "_collecte.json") if gel_dir.exists() else (RACINE / "data/historique/_collecte.json")
    etat = lire_json(str(etat_f.relative_to(RACINE)), {}) if etat_f.exists() else {}
    perimee = lambda n: n not in etat or (date.fromisoformat(gel) - date.fromisoformat(etat[n])).days > 3

    for nom, meta in VARIABLES.items():
        if perimee(nom) or (meta.get("proxy") and perimee(meta["proxy"])):
            ecartees.append((nom, "série non collectée depuis plus de trois jours au gel"))
            continue
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
                ancrage = {"proxy": meta["proxy"], "niveau_estime": round(a[1], 1), "correction": round(a[2], 1),
                           "date": a[3]}
        for h in HORIZONS:
            cible = mois_suivant(mois, h - 1)
            if cible <= publie:
                ecartees.append((f"{nom} {cible}", "valeur déjà publiée"))
                continue
            # Question ancrée : le pas peut être nul quand le point quotidien tombe dans le mois cible (loi « point
            # du jour J → moyenne du même mois ») ; sans ancrage, au moins un mois (relecture de suivi 16, N4).
            pas = ecart_mois(dernier, cible) if ancrage else max(1, ecart_mois(dernier, cible))
            # Ancrage quotidien : loi du point quotidien à la moyenne du mois cible (relecture 15, S5).
            var = variations_question(lire, {"serie": nom, "pas": pas, "ancrage_quotidien": ancrage})
            for q in QUANTILES:
                seuil = arrondi(base + quantile(var, q), meta["unite"])
                qid = f"Q-{cycle}-{nom}-{cible}-q{q}"
                qs.append({
                    "id": qid, "type": "variable", "pool": correspondances.get(qid, {}).get("pool", "P2a"),
                    "grappe": f"{nom}-{trimestre(cible)}",
                    "texte": f"La valeur de « {meta['nom']} » pour {cible} est-elle supérieure ou égale à {seuil} {meta['unite']} ? (Dernière valeur publiée au gel : {base_publiee:g} {meta['unite']} pour {publie}"
                            + (f" ; niveau récent estimé d'après les données quotidiennes : {base:.0f} {meta['unite']})" if ancrage else ")")
                            # Règle de résolution rappelée dans le texte (relecture 17, souhaitable 7).
                            + " Résolution sur la première valeur publiée et collectée pour cette période ; les révisions ultérieures ne comptent pas.",
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
    # Fenêtres disjointes : grappes distinctes ; fenêtres qui se chevauchent ou s'emboîtent (EV-C3a dans
    # EV-C3b) : même grappe (relecture 15, S10). Composantes connexes par chevauchement, au sein d'un événement.
    freres = {}
    for e in evts:
        freres.setdefault(e["evenement"], []).append(e)
    comp = {}
    for ev, liste in freres.items():
        groupes = []
        for e in sorted(liste, key=lambda x: x["fenetre"]["debut"]):
            f = e["fenetre"]
            g = next((g for g in groupes if any(f["debut"] <= x["fenetre"]["fin"] and x["fenetre"]["debut"] <= f["fin"] for x in g)), None)
            (g.append(e) if g is not None else groupes.append([e]))
        for g in groupes:
            nom_g = ev if len(groupes) == 1 else (g[0]["id"] if len(g) == 1 else ev + "-" + "-".join(x["id"].removeprefix(ev) for x in g))
            for x in g:
                comp[x["id"]] = nom_g
    # Les questions tranchées par un même acte officiel forment une grappe (relecture 12, K4).
    grappe = lambda e: e["acte"] if e.get("acte") else comp[e["id"]]
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
                       "texte": f"{e['nom']} : le critère est-il rempli entre le {gel} et le {iso_fin_mois(mois)} ?",
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
