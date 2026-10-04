"""Prévisions des comparateurs naïfs d'un cycle (noyau, section 8.4).

Usage : python scripts/comparateurs.py AAAA-MM [registre/<fichier>.jsonl]
Par défaut, écrit dans registre/protocole.jsonl ; un cycle à blanc passe un autre registre.

- Persistance (variables) : probabilité que la marche aléatoire empirique (variations depuis 2010
  sur le même nombre de mois) dépasse le seuil.
- Taux de base (événements) : valeur « utilisee » de modele/taux_base.json, ramenée à la fenêtre
  restante de la question par un risque constant : p = 1 − (1 − p_fenêtre)^(durée restante / durée
  de la fenêtre de l'événement). Distribution par issue inchangée pour une question à plusieurs issues.
- 50 % : probabilité uniforme sur les issues.
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


def previsions(cycle):
    banque = lire_json(f"data/cycles/{cycle}/questions.json")
    evts = {e["id"]: e for e in lire_json("modele/evenements.json")["evenements"]}
    tb = lire_json("modele/taux_base.json")["questions"]
    lignes = []
    for q in banque["questions"]:
        sortie = []
        if q["type"] == "variable":
            d = q["details"]
            p = proba_au_dessus(d["derniere_valeur"], d["seuil"], variations(lire_serie(cycle, d["serie"]), d["pas"]))
            sortie.append(("persistance", {"oui": p, "non": 1 - p}))
        else:
            e = evts[q["details"]["evenement"]]
            u = tb[e["id"]]["utilisee"]
            if len(q["issues"]) > 2:
                sortie.append(("taux de base", {k: v / 100 for k, v in u.items()}))
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
