"""Agrégation de l'ensemble direct (noyau, section 8.4).

Usage : python scripts/ensemble.py AAAA-MM [registre/<fichier>.jsonl]
Lit data/cycles/<AAAA-MM>/ensemble/*.json (un fichier par prévisionniste, format de
modele/consigne_ensemble.md). Écrit au registre chaque prévision individuelle (auteur
« ensemble : <identifiant> ») puis l'agrégat (auteur « ensemble direct ») : médiane par issue,
renormalisée, non extrémisée. Exige au moins cinq prévisionnistes et trois modèles (section 6.1),
une réponse à chaque question de la banque et au moins 10 recherches web déclarées par
prévisionniste (consigne v1.1).
"""
import statistics
import sys

from commun import RACINE, borne, lire_json
from registre import ajouter


def normaliser(d):
    b = {k: borne(v / 100) for k, v in d.items()}
    s = sum(b.values())
    return {k: round(v * 100 / s, 1) for k, v in b.items()}


def agreger(cycle, exiger_recherches=True):
    banque = lire_json(f"data/cycles/{cycle}/questions.json")
    fichiers = sorted((RACINE / "data" / "cycles" / cycle / "ensemble").glob("*.json"))
    prev = [lire_json(str(f.relative_to(RACINE))) for f in fichiers]
    if len(prev) < 5 or len({p["modele"] for p in prev}) < 3:
        raise SystemExit(f"Ensemble incomplet : {len(prev)} prévisionnistes, {len({p['modele'] for p in prev})} modèles (minimum 5 et 3).")
    faibles = [p["previsionniste"] for p in prev if p.get("recherches", 0) < 10]
    if faibles and exiger_recherches:
        raise SystemExit(f"Recherche insuffisante (moins de 10 recherches déclarées) : {faibles}. Relancer ces prévisionnistes une fois (consigne v1.1).")
    lignes = []
    for q in banque["questions"]:
        dists = []
        for p in prev:
            r = p["previsions"].get(q["id"])
            if not r or set(r["probabilites"]) != set(q["issues"]):
                raise SystemExit(f"{p['previsionniste']} : réponse absente ou issues incorrectes pour {q['id']}")
            d = normaliser(r["probabilites"])
            dists.append(d)
            lignes.append({"question": q["id"], "probabilites": d, "piste": "protocole", "phase": 1,
                           "auteur": f"ensemble : {p['previsionniste']}", "origine": f"cycle {cycle}",
                           "donnees": f"gel du cycle {cycle} et recherche web", "modele": p["modele"]})
        med = {k: statistics.median(d[k] for d in dists) for k in q["issues"]}
        lignes.append({"question": q["id"], "probabilites": normaliser(med), "piste": "protocole", "phase": 1,
                       "auteur": "ensemble direct", "origine": f"cycle {cycle}, médiane de {len(dists)}",
                       "donnees": f"gel du cycle {cycle}"})
    return lignes


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("usage : python scripts/ensemble.py AAAA-MM [registre/<fichier>.jsonl]")
    cible = sys.argv[2] if len(sys.argv) == 3 else "registre/protocole.jsonl"
    lignes = agreger(sys.argv[1])
    t = ajouter(cible, lignes)
    print(f"{len(lignes)} lignes de l'ensemble direct ajoutées à {cible}, émises le {t}")
