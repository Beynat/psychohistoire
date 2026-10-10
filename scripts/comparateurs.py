"""Prévisions des comparateurs naïfs d'un cycle (noyau, section 8.4).

Usage : python scripts/comparateurs.py AAAA-MM [registre/<fichier>.jsonl]
Par défaut, écrit dans registre/protocole.jsonl ; un cycle à blanc passe un autre registre.

- Persistance (variables) : probabilité que la marche aléatoire empirique (variations depuis 2010
  sur le même nombre de mois) dépasse le seuil.
- Taux de base (événements) : valeur « utilisee » de modele/taux_base.json. Pour un événement de
  nature « survenue », elle est ramenée à la fenêtre restante de la question par un risque constant : p = 1 − (1 − p_fenêtre)^(durée restante / durée
  de la fenêtre de l'événement). Pour un événement de nature « constat » (issue constatée à date
  fixe, relecture 9), elle n'est pas convertie. Distribution par issue inchangée pour une question à
  plusieurs issues.
- 50 % : probabilité uniforme sur les issues.
- Référence externe (noyau, section 8.4, point 3) : pour une question de fenêtre dont l'événement porte
  une « reference_externe » (modele/banque/criteres.json), prix Polymarket gelés (gel/cotes.json),
  renormalisés sur les issues ; le reste va à l'issue « reste ». La ligne indique si toutes les cotes
  utilisées au-dessus de 5 % sont fiables (section 4.5). Le pool d'une question est celui de la banque (EV-05 en P1) ; ce comparateur ne le change pas.
- Un événement marqué « taux_base_mode: uniforme » (EV-05, relecture 8) reçoit la loi uniforme comme taux de base.
Aucune probabilité n'est bornée (relecture 17, I3) ; les distributions sont seulement renormalisées.
"""
import sys

from commun import RACINE, jours, lire_json, proba_au_dessus, variations_question
import commun
from registre import ajouter


def lire_serie(cycle, nom):
    gel = RACINE / "data" / "cycles" / cycle / "gel" / "historique" / f"{nom}.csv"
    if gel.exists():
        return [(p, float(v)) for p, v in (l.split(",") for l in gel.read_text("utf-8").splitlines()[1:] if l)]
    return commun.serie(nom)


def normaliser(d):
    # Aucune borne (relecture 17, I3) : une borne appliquée à certains auteurs seulement les pénalise sur les
    # événements rares ; le score logarithmique borne lui-même ses probabilités (commun.log_score).
    b = {k: max(float(v), 0.0) for k, v in d.items()}
    s = sum(b.values())
    return {k: round(v * 100 / s, 1) for k, v in b.items()}


def reference_externe(q, e, cotes):
    ref = e.get("reference_externe")
    if not ref or q["id"] != f"Q-{e['id']}":
        return None
    marches = {m["libelle_issue"]: m for m in cotes if m["source"] == ref["source"] and m["evenement"] == ref["evenement"]}
    dist, fiable = {}, True
    for issue, lib in ref["issues"].items():
        m = marches.get(lib)
        if m is None:
            return None
        dist[issue] = m["probabilite"]
        if m["probabilite"] > 0.05 and not m.get("fiable"):
            fiable = False
    if "reste" in ref:
        dist[ref["reste"]] = max(1 - sum(dist.values()), 0.0)
    if len(q["issues"]) == 2 and set(dist) == {"oui"}:
        dist["non"] = 1 - dist["oui"]
    if set(dist) != set(q["issues"]):
        return None
    return dist, fiable


def previsions(cycle):
    banque = lire_json(f"data/cycles/{cycle}/questions.json")
    gel = f"data/cycles/{cycle}/gel"
    # Fichiers du gel seulement quand le cycle est gelé (audit interne, v1.24) : jamais de repli sur un fichier
    # courant, postérieur au gel. Le repli ne vaut que pour un cycle à blanc sans gel.
    gele = (RACINE / gel / "manifeste.json").exists()
    lire_gel = (lambda n, courant: lire_json(f"{gel}/{n}")) if gele else (lambda n, courant: lire_json(f"{gel}/{n}") or lire_json(courant))
    evts = {e["id"]: e for e in lire_gel("evenements.json", "modele/evenements.json")["evenements"]}
    cotes = (lire_gel("cotes.json", "data/cotes.json") or {"marches": []})["marches"]
    # Taux de base gelés avec le cycle (relecture 10, S5) ; à défaut (cycle d'essai sans gel), fichier courant.
    tb = lire_gel("taux_base.json", "modele/taux_base.json")["questions"]
    lignes, conj, tbq = [], [], {}
    for q in banque["questions"]:
        sortie = []
        if q["type"] == "variable":
            d = q["details"]
            p = proba_au_dessus(d["derniere_valeur"], d["seuil"], variations_question(lambda n: lire_serie(cycle, n), d))
            sortie.append(("persistance", {"oui": p, "non": 1 - p}))
        elif q["type"] == "rapide":
            pass   # questions rapides (étape 6) : seul le comparateur 50 %
        elif q["type"] == "conjointe":
            # Taux de base d'une conjointe : produit des taux de base de ses composantes (indépendance), calculé
            # après la boucle, une fois ceux-ci connus.
            conj.append(q)
            continue
        else:
            e = evts[q["details"]["evenement"]]
            u = ({k: 100 / len(e["issues"]) for k in e["issues"]} if e.get("taux_base_mode") == "uniforme"
                 else tb[e["id"]]["utilisee"])
            ref = reference_externe(q, e, cotes)
            if ref:
                sortie.append((f"référence externe {e['reference_externe']['source']}" + ("" if ref[1] else " (non fiable)"), ref[0]))
            if len(q["issues"]) > 2:
                sortie.append(("taux de base", {k: v / 100 for k, v in u.items()}))
            elif e.get("nature", "survenue") == "constat":
                # Issue constatée à date fixe : pas de conversion à la fenêtre restante (relecture 9, H1).
                sortie.append(("taux de base", {"oui": u["oui"] / 100, "non": u["non"] / 100}))
            else:
                p_f = u["oui"] / 100
                ratio = max(jours(q["fenetre"]["debut"], q["fenetre"]["fin"]), 1) / max(
                    jours(e["fenetre"]["debut"], e["fenetre"]["fin"]), 1)
                p = 1 - (1 - p_f) ** min(ratio, 1)
                sortie.append(("taux de base", {"oui": p, "non": 1 - p}))
        sortie.append(("50 %", {k: 1 / len(q["issues"]) for k in q["issues"]}))
        tbq[q["id"]] = dict(sortie).get("taux de base")
        for auteur, dist in sortie:
            lignes.append({"question": q["id"], "probabilites": normaliser(dist), "piste": "protocole", "phase": 1,
                           "auteur": f"comparateur : {auteur}", "origine": f"cycle {cycle}",
                           "donnees": f"gel du cycle {cycle}"})
    for q in conj:
        pa, pb = (tbq.get(x) for x in q["details"]["composantes"])
        sortie = [("50 %", {"oui": 0.5, "non": 0.5})]
        if pa and pb:
            p = pa["oui"] * pb["oui"]
            sortie.insert(0, ("taux de base", {"oui": p, "non": 1 - p}))
        for auteur, dist in sortie:
            lignes.append({"question": q["id"], "probabilites": normaliser(dist), "piste": "protocole", "phase": 1,
                           "auteur": f"comparateur : {auteur}", "origine": f"cycle {cycle}",
                           "donnees": f"gel du cycle {cycle}"})
    return lignes


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("usage : python scripts/comparateurs.py AAAA-MM [registre/<fichier>.jsonl]")
    cible = sys.argv[2] if len(sys.argv) == 3 else "registre/protocole.jsonl"
    # Rattrapage : une étape déjà faite n'est jamais rejouée (pas de lignes en double au registre).
    if any(l.get("auteur", "").startswith("comparateur") and l.get("origine") == f"cycle {sys.argv[1]}" for l in commun.lire_jsonl(cible, garder_inscrites=True)):
        sys.exit(f"Les lignes comparateurs du cycle {sys.argv[1]} sont déjà dans {cible} : étape déjà faite.")
    lignes = previsions(sys.argv[1])
    t = ajouter(cible, lignes)
    print(f"{len(lignes)} prévisions de comparateurs ajoutées à {cible}, émises le {t}")
