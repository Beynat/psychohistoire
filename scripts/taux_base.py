"""Fusionne modele/taux_base/groupe_*.json en modele/taux_base.json (noyau, sections 7.3 et 8.4).

Règle mécanique ajoutée à la fusion : la probabilité utilisée par le comparateur « taux de base »
est bornée entre 2 % et 98 % (par issue, puis renormalisée), car une probabilité de 0 ou 100 %
rendrait le score logarithmique infini (section 8.4). La valeur brute retenue est conservée.
"""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RACINE = Path(__file__).resolve().parent.parent
BORNE = (2.0, 98.0)


def borner(p):
    return min(max(p, BORNE[0]), BORNE[1])


def utilisee(q):
    if q.get("issues"):
        b = {k: max(v, BORNE[0]) for k, v in q["issues"].items()}
        s = sum(b.values())
        return {k: round(v * 100 / s, 1) for k, v in b.items()}
    p = borner(q["retenue"]["probabilite"])
    return {"oui": round(p, 1), "non": round(100 - p, 1)}


if __name__ == "__main__":
    evts = {e["id"]: e for e in json.loads((RACINE / "modele/evenements.json").read_text("utf-8"))["evenements"]}
    sortie, manquants = {}, []
    # Les fichiers de la relecture 8 (suffixe _r8) passent en dernier : ils remplacent les estimations
    # des critères réécrits (EV-07, EV-09, EV-17).
    for f in sorted((RACINE / "modele/taux_base").glob("groupe_*.json"), key=lambda f: (f.stem.endswith("_r8"), f.name)):
        g = json.loads(f.read_text("utf-8"))
        for q in g["questions"]:
            sortie[q["id"]] = {**q, "groupe": g["groupe"], "utilisee": utilisee(q)}
    for i, e in evts.items():
        if e["source_accessible"] and i not in sortie and e.get("taux_base") != "uniforme":
            manquants.append(i)
    doc = {"description": "Taux de base des questions d'événement : au moins deux classes de référence, fourchette, classe retenue (sections 7.3 et 8.4). Probabilités en %. « utilisee » est la valeur du comparateur, bornée entre 2 et 98 %.",
           "fusionne_le": datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds"),
           "questions": sortie, "manquants": manquants}
    (RACINE / "modele/taux_base.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), "utf-8")
    print(f"{len(sortie)} questions, manquantes : {manquants or 'aucune'}")
    for i, q in sortie.items():
        print(f"{i:7} brut {q['retenue']['probabilite']:5} · utilisée {q['utilisee']}")
