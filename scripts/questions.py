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


def generer(gel, etiquette=None, reg="registre/protocole.jsonl"):
    mois = gel[:7]
    cycle = etiquette or mois
    gel_dir = RACINE / "data" / "cycles" / cycle / "gel" / "historique"
    lire = (lambda n: commun.serie(n)) if not gel_dir.exists() else (
        lambda n: [(p, float(v)) for p, v in (l.split(",") for l in (gel_dir / f"{n}.csv").read_text("utf-8").splitlines()[1:] if l)])
    from resolution import resolutions_effectives, suffixe
    # Errata de réouverture appliqués (relecture 13, S1). Seules les résolutions dont le fait est établi au gel
    # écartent une question (section 8.2 ; relecture 22, N3) : à la reprise d'un cycle, un fait postérieur au
    # gel ne retire pas la question, ce qui ne retirerait que des « oui ».
    resolues = {q for q, r in resolutions_effectives(suffixe(reg)).items()
                if (r.get("date_fait") or str(r.get("emise", ""))[:10]) <= gel}
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
    # Grappe figée à la première émission d'un événement (audit interne, v1.24) : un ajout ultérieur rejoint une
    # grappe existante sans renommer celles des questions déjà émises.
    import re as _re
    figees = {}
    for f in sorted((RACINE / "data" / "cycles").glob("*/questions.json")):
        et = f.parent.name
        if _re.fullmatch(r"\d{4}-\d{2}", et) and "2026-11" <= et < cycle:   # cycles réels (premier : 2026-11)
            for q in lire_json(str(f.relative_to(RACINE)))["questions"]:
                ev = (q.get("details") or {}).get("evenement")
                if ev:
                    figees.setdefault(ev, q["grappe"])
    reliees = {}
    def grappe(e):
        # Un ajout rejoint la grappe figée d'un événement déjà émis de sa composante (relecture 20, N2) ; si
        # plusieurs grappes figées sont reliées par l'ajout, la première par ordre alphabétique est retenue.
        if e["id"] in figees:
            return figees[e["id"]]
        if e.get("acte"):
            return e["acte"]
        f = e["fenetre"]
        chevauche = lambda x: x["fenetre"]["debut"] <= f["fin"] and f["debut"] <= x["fenetre"]["fin"]
        # D'abord les événements dont la fenêtre chevauche directement celle de l'ajout (audit interne v1.25),
        # puis le reste de sa composante.
        directs = sorted({figees[x["id"]] for x in freres[e["evenement"]] if x["id"] in figees and chevauche(x)})
        if len(directs) > 1:
            reliees[e["id"]] = directs
        voisins = directs or sorted(figees[x] for x, g in comp.items() if g == comp[e["id"]] and x in figees)
        return voisins[0] if voisins else comp[e["id"]]
    # Actes annoncés comme décidés (relecture 20, N1) : la question n'est pas émise si deux agents distincts, ou
    # deux passages, ont consigné une annonce datée au plus tard du gel. L'annonce ne résout pas la question.
    vus_a = {}
    for a in lire_jsonl(f"registre/annonces{suffixe(reg)}.jsonl"):
        if a.get("annonce") and a["date_annonce"] <= gel:
            vus_a.setdefault(a["question"], set()).add((a["agent"], a["emise"][:10]))
    annoncees = {ev for ev, cles in vus_a.items() if len(cles) >= 2}
    for e in evts:
        if not e["source_accessible"]:
            ecartees.append((e["id"], e["motif_inaccessible"]))
            continue
        debut, fin = max(e["fenetre"]["debut"], gel), e["fenetre"]["fin"]
        if fin <= gel:   # échéance le jour du gel : issue en général déjà publique (audit interne, v1.24)
            continue
        qid = f"Q-{e['id']}"
        if e["id"] in annoncees:
            ecartees.append((qid, f"acte annoncé comme décidé avant le gel (registre/annonces{suffixe(reg)}.jsonl)"))
            continue
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
    # Questions conjointes (pool P2c, feuille de route v0, bloc 5) : émises quand les questions de fenêtre de leurs
    # deux événements le sont dans ce cycle ; grappe de A.
    fen = {q["details"]["evenement"]: q for q in qs if q["type"] == "evenement" and q["id"] == f"Q-{q['details']['evenement']}"}
    for c in (lire_json("modele/banque/conjointes.json") or {"conjointes": []})["conjointes"]:
        qa, qb = fen.get(c["a"]), fen.get(c["b"])
        if not (qa and qb and qa["issues"] == ["oui", "non"] and qb["issues"] == ["oui", "non"]):
            ecartees.append((f"Q-{c['id']}", "une des deux questions n'est pas émise dans ce cycle"))
            continue
        ea = next(e for e in evts if e["id"] == c["a"]); eb = next(e for e in evts if e["id"] == c["b"])
        qs.append({"id": f"Q-{c['id']}", "type": "conjointe", "pool": "P2c", "grappe": qa["grappe"], "issues": ["oui", "non"],
                   "texte": f"{c['nom']} : les deux critères sont-ils remplis, chacun dans sa fenêtre ? ({ea['nom']}, du {qa['fenetre']['debut']} au {qa['fenetre']['fin']} ; {eb['nom']}, du {qb['fenetre']['debut']} au {qb['fenetre']['fin']})",
                   "echeance": max(qa["echeance"], qb["echeance"]),
                   "fenetre": {"debut": gel, "fin": max(qa["echeance"], qb["echeance"])},
                   "details": {"conjointe": c["id"], "composantes": [qa["id"], qb["id"]],
                               "critere": f"« Oui » si et seulement si les deux questions sont résolues « oui ». (1) {ea['nom']} : {ea['critere']} (fenêtre du {qa['fenetre']['debut']} au {qa['fenetre']['fin']}). (2) {eb['nom']} : {eb['critere']} (fenêtre du {qb['fenetre']['debut']} au {qb['fenetre']['fin']})."}})
    for i, gs in reliees.items():
        ecartees.append((i, f"ajout reliant plusieurs grappes figées {gs} : grappe {gs[0]} retenue (consigné, non écarté)"))
    return {"cycle": cycle, "gel": gel, "genere_le": maintenant(), "questions": qs,
            "ecartees": [{"objet": o, "motif": m} for o, m in ecartees]}


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3, 4):
        sys.exit("usage : python scripts/questions.py AAAA-MM-JJ [ETIQUETTE] [registre/<fichier>.jsonl]")
    gel, etiquette = sys.argv[1], (sys.argv[2] if len(sys.argv) >= 3 else None)
    # Registre du cycle (vérificateur B, constat 2.1) : résolutions et annonces lues avec son suffixe.
    reg = sys.argv[3] if len(sys.argv) == 4 else "registre/protocole.jsonl"
    # Rattrapage (noyau, section 12) : un passage repris après le jour du gel garde la date du gel du
    # manifeste. Sinon le contrôle des séries périmées (plus de trois jours) écarterait les questions
    # de variables selon le jour de la reprise.
    manifeste = lire_json(f"data/cycles/{etiquette or gel[:7]}/gel/manifeste.json")
    if manifeste and manifeste["date_gel"] != gel:
        print(f"Date de gel du manifeste retenue : {manifeste['date_gel']} (et non {gel}).")
        gel = manifeste["date_gel"]
    # Une banque déjà écrite n'est jamais régénérée (audit interne v1.27, S3) : à la reprise, l'étape est faite.
    if (RACINE / "data" / "cycles" / (etiquette or gel[:7]) / "questions.json").exists():
        sys.exit(f"Les questions du cycle {etiquette or gel[:7]} existent déjà : étape déjà faite.")
    banque = generer(gel, etiquette, reg)
    ecrire_json(f"data/cycles/{banque['cycle']}/questions.json", banque)
    n = len(banque["questions"])
    g = len({q["grappe"] for q in banque["questions"]})
    pools = {}
    for q in banque["questions"]:
        pools[q["pool"]] = pools.get(q["pool"], 0) + 1
    print(f"Cycle {banque['cycle']} : {n} questions, {g} grappes, pools {pools}, {len(banque['ecartees'])} écartées")
