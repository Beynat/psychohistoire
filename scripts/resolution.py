"""Résolution des questions (noyau, section 8.8).

Usage : python scripts/resolution.py [registre/<fichier>.jsonl]   (défaut : registre/protocole.jsonl)
Les résolutions sont écrites dans registre/resolutions.jsonl (ou resolutions_<suffixe>.jsonl pour
un registre d'essai), en ajout seul, par scripts/registre.py.

- Variables : résolues par script dès que la période est publiée dans la série collectée.
- Événements : résolus à partir des propositions d'agents (registre/propositions.jsonl), chacune
  avec sa source primaire. Deux propositions concordantes résolvent la question. En cas de
  désaccord, une troisième tranche à la majorité. Si le désaccord persiste avec trois avis, ou si
  aucune proposition n'existe 30 jours après l'échéance, la question est annulée pour tous.
- Une prévision émise après la résolution publique de sa question est annulée pour son auteur ;
  ce contrôle est fait par scripts/notation.py, qui compare les dates.
"""
import sys
from datetime import date, timedelta

import commun
from commun import lire_json, lire_jsonl, RACINE
from registre import ajouter


def suffixe(reg):
    nom = reg.split("/")[-1].replace(".jsonl", "")
    return "" if nom == "protocole" else f"_{nom}"


def toutes_les_questions():
    """Questions de toutes les banques de cycle, plus la question de fenêtre de chaque événement
    (« Q-<id> »), pour pouvoir constater avant émission qu'un événement s'est déjà produit."""
    qs = {}
    for e in lire_json("modele/evenements.json")["evenements"]:
        qs[f"Q-{e['id']}"] = {"id": f"Q-{e['id']}", "type": "evenement", "issues": e["issues"], "pool": "P2b",
                              "grappe": f"{e['evenement']}", "echeance": e["fenetre"]["fin"], "avant_emission": True}
    for f in sorted((RACINE / "data" / "cycles").glob("*/questions.json")):
        for q in lire_json(str(f.relative_to(RACINE)))["questions"]:
            if qs.get(q["id"], {}).get("avant_emission"):
                del qs[q["id"]]
            qs.setdefault(q["id"], q)
    return qs


def resoudre(reg="registre/protocole.jsonl", aujourdhui=None):
    aujourdhui = aujourdhui or date.today().isoformat()
    sfx = suffixe(reg)
    deja = {r["question"] for r in lire_jsonl(f"registre/resolutions{sfx}.jsonl")}
    props = {}
    for p in lire_jsonl(f"registre/propositions{sfx}.jsonl"):
        props.setdefault(p["question"], []).append(p)
    emises = {l["question"] for l in lire_jsonl(reg) if "question" in l and "probabilites" in l}
    nouvelles, series = [], {}
    for qid, q in toutes_les_questions().items():
        if qid in deja or (qid not in emises and not (q.get("avant_emission") and qid in props)):
            continue
        if q["type"] == "variable":
            d = q["details"]
            s = series.setdefault(d["serie"], dict(commun.serie(d["serie"])))
            if d["periode"] in s:
                v = s[d["periode"]]
                nouvelles.append({"resolution": True, "question": qid, "issue": "oui" if v >= d["seuil"] else "non",
                                  "valeur": v, "source": f"data/historique/{d['serie']}.csv", "methode": "script"})
            continue
        avis = props.get(qid, [])
        issues = [a["issue"] for a in avis]
        if len(avis) >= 2 and issues[0] == issues[1]:
            nouvelles.append({"resolution": True, "question": qid, "issue": issues[0],
                              "source": " ; ".join(a["source"] for a in avis[:2]), "methode": "deux agents concordants"})
        elif len(avis) >= 3:
            maj = max(set(issues[:3]), key=issues[:3].count)
            if issues[:3].count(maj) >= 2:
                nouvelles.append({"resolution": True, "question": qid, "issue": maj,
                                  "source": " ; ".join(a["source"] for a in avis[:3]), "methode": "troisième agent, majorité"})
            else:
                nouvelles.append({"resolution": True, "question": qid, "issue": None, "source": "—",
                                  "methode": "annulée : désaccord persistant entre trois agents"})
        elif date.fromisoformat(q["echeance"]) + timedelta(days=30) < date.fromisoformat(aujourdhui) and not avis:
            nouvelles.append({"resolution": True, "question": qid, "issue": None, "source": "—",
                              "methode": "annulée : aucune source primaire 30 jours après l'échéance"})
    if nouvelles:
        ajouter(f"registre/resolutions{sfx}.jsonl", nouvelles)
    return nouvelles


if __name__ == "__main__":
    reg = sys.argv[1] if len(sys.argv) > 1 else "registre/protocole.jsonl"
    n = resoudre(reg)
    print(f"{len(n)} résolution(s) ajoutée(s)" + "".join(f"\n- {r['question']} : {r['issue']} ({r['methode']})" for r in n))
