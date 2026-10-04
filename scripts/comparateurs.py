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
Toutes les probabilités sont bornées entre 2 et 98 % avant renormalisation.
"""
import sys

from commun import RACINE, borne, jours, lire_json, proba_au_dessus, variations
import commun
from registre import ajouter


def lire_serie(cycle, nom):
    gel = RACINE / "data" / "cycles" / cycle / "gel" / "historique" / f"{nom}.csv"
    if gel.exists():
        return [(p, float(v)) for p, v in (l.split(",") for l in gel.read_text("utf-8").splitlines()[1:] if l)]
    return commun.serie(nom)


def normaliser(d):
    b = {k: borne(v) for k, v in d.items()}
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
    evts = {e["id"]: e for e in (lire_json(f"{gel}/evenements.json") or lire_json("modele/evenements.json"))["evenements"]}
    cotes = (lire_json(f"{gel}/cotes.json") or lire_json("data/cotes.json") or {"marches": []})["marches"]
    # Taux de base gelés avec le cycle (relecture 10, S5) ; à défaut (cycle d'essai sans gel), fichier courant.
    tb = (lire_json(f"{gel}/taux_base.json") or lire_json("modele/taux_base.json"))["questions"]
    lignes = []
    for q in banque["questions"]:
        sortie = []
        if q["type"] == "variable":
            d = q["details"]
            p = proba_au_dessus(d["derniere_valeur"], d["seuil"], variations(lire_serie(cycle, d["serie"]), d["pas"]))
            sortie.append(("persistance", {"oui": p, "non": 1 - p}))
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
        for auteur, dist in sortie:
            lignes.append({"question": q["id"], "probabilites": normaliser(dist), "piste": "protocole", "phase": 1,
                           "auteur": f"comparateur : {auteur}", "origine": f"cycle {cycle}",
                           "donnees": f"gel du cycle {cycle}"})
    return lignes


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("usage : python scripts/comparateurs.py AAAA-MM [registre/<fichier>.jsonl]")
    cible = sys.argv[2] if len(sys.argv) == 3 else "registre/protocole.jsonl"
    lignes = previsions(sys.argv[1])
    t = ajouter(cible, lignes)
    print(f"{len(lignes)} prévisions de comparateurs ajoutées à {cible}, émises le {t}")
