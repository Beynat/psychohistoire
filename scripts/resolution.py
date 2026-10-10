"""Résolution des questions (noyau, section 8.8).

Usage : python scripts/resolution.py [registre/<fichier>.jsonl]   (défaut : registre/protocole.jsonl)
Les résolutions sont écrites dans registre/resolutions.jsonl (ou resolutions_<suffixe>.jsonl pour
un registre d'essai), en ajout seul, par scripts/registre.py.

- Variables : résolues par script dès que la période est publiée dans la série collectée.
- Événements : résolus à partir des propositions d'agents (registre/propositions.jsonl), chacune
  avec sa source primaire. Deux propositions concordantes résolvent la question. En cas de
  désaccord, une troisième tranche à la majorité. Si le désaccord persiste avec trois avis, la
  question est annulée pour tous. Sans avis : annulation à 30 jours après l'échéance si deux recherches
  vaines ont été consignées (agents ou passages distincts), à 60 jours si au moins un avis ou une recherche
  l'a été ; sans aucune recherche, la question reste ouverte (noyau, section 8.8).
- Une prévision émise après la résolution publique de sa question, ou à la date du fait ou après
  (champ date_fait des propositions, relecture 8, G2), est annulée pour son auteur ; ce contrôle est
  fait par scripts/notation.py, qui compare les dates.
"""
import sys
from datetime import date, timedelta

import commun
from commun import lire_json, lire_jsonl, RACINE
from registre import ajouter


def suffixe(reg):
    nom = reg.split("/")[-1].replace(".jsonl", "")
    return "" if nom == "protocole" else f"_{nom}"


def cycles_du_registre(reg):
    """Étiquettes des cycles dont le registre contient des prévisions (champ origine « cycle X ») :
    seules leurs banques de questions sont lues (relecture 12, K2 : un cycle d'essai ne doit pas entrer
    dans le bilan du registre du protocole)."""
    import re
    return {m.group(1) for l in lire_jsonl(reg) for m in [re.match(r"cycle ([^\s,]+)", str(l.get("origine", "")))] if m}


def toutes_les_questions(cycles=None):
    """Questions de toutes les banques de cycle, plus la question de fenêtre de chaque événement
    (« Q-<id> »), pour pouvoir constater avant émission qu'un événement s'est déjà produit."""
    qs = {}
    for e in lire_json("modele/evenements.json")["evenements"]:
        qs[f"Q-{e['id']}"] = {"id": f"Q-{e['id']}", "type": "evenement", "issues": e["issues"], "pool": "P2b",
                              "grappe": f"{e['evenement']}", "echeance": e["fenetre"]["fin"], "avant_emission": True}
    for f in sorted((RACINE / "data" / "cycles").glob("*/questions.json")):
        if cycles is not None and f.parent.name not in cycles:
            continue
        for q in lire_json(str(f.relative_to(RACINE)))["questions"]:
            if qs.get(q["id"], {}).get("avant_emission"):
                del qs[q["id"]]
            qs.setdefault(q["id"], q)
    return qs


_NATURES = None


def nature(qid, q):
    """Nature de l'événement d'une question (« survenue » ou « constat ») ; « survenue » par défaut."""
    global _NATURES
    if _NATURES is None:
        _NATURES = {e["id"]: e.get("nature", "survenue") for e in lire_json("modele/evenements.json")["evenements"]}
    ev = (q.get("details") or {}).get("evenement") or qid.removeprefix("Q-")
    return _NATURES.get(ev, "survenue")


def date_fait(proposition):
    """Date du fait (relecture 8, G2). Les propositions antérieures au 4 octobre 2026 n'en ont pas : on
    retient alors la date d'émission de la proposition, borne supérieure."""
    return proposition.get("date_fait") or proposition["emise"][:10]


def resolutions_effectives(sfx):
    """Résolutions avec les errata appliqués (relecture 12, S5) : une ligne d'erratum
    {erratum: true, objet: <question>, correction: {champs corrigés}, piste} remplace les champs
    indiqués de la résolution de cette question ; le dernier erratum l'emporte."""
    res = {}
    for r in lire_jsonl(f"registre/resolutions{sfx}.jsonl"):
        if r.get("resolution"):
            res.setdefault(r["question"], dict(r))
        elif r.get("erratum") and r.get("objet") in res and isinstance(r.get("correction"), dict):
            if r["correction"].get("rouverte"):
                # Erratum de réouverture (relecture 13, S1) : la question redevient ouverte.
                del res[r["objet"]]
                continue
            res[r["objet"]].update(r["correction"])
            res[r["objet"]]["corrigee_par_erratum"] = r.get("emise")
    return res


def resoudre(reg="registre/protocole.jsonl", aujourdhui=None):
    aujourdhui = aujourdhui or date.today().isoformat()
    sfx = suffixe(reg)
    deja = set(resolutions_effectives(sfx))
    # Dernière réouverture par erratum de chaque question (relecture 14, N1) : les propositions émises
    # avant elle ne comptent plus.
    reouv = {}
    for r in lire_jsonl(f"registre/resolutions{sfx}.jsonl"):
        if r.get("erratum") and isinstance(r.get("correction"), dict) and r["correction"].get("rouverte"):
            reouv[r["objet"]] = max(reouv.get(r["objet"], ""), r.get("emise", ""))
    props = {}
    for p in lire_jsonl(f"registre/propositions{sfx}.jsonl"):
        if p.get("emise", "") <= reouv.get(p["question"], ""):
            continue
        props.setdefault(p["question"], []).append(p)
    emises = {l["question"] for l in lire_jsonl(reg) if "question" in l and "probabilites" in l}
    nouvelles = []
    premieres = {}
    for l in lire_jsonl("data/premieres_valeurs.jsonl"):
        premieres.setdefault((l["serie"], l["periode"]), l)
    for qid, q in toutes_les_questions(cycles_du_registre(reg)).items():
        if qid in deja or (qid not in emises and not (q.get("avant_emission") and qid in props)):
            continue
        if q["type"] == "conjointe":
            continue   # résolue en seconde passe, à partir de ses composantes
        if q["type"] == "variable":
            d = q["details"]
            # Fait foi la première valeur collectée de la période, lue dans le journal en ajout seul
            # data/premieres_valeurs.jsonl ; sa date de collecte est la date du fait (relecture 13, L1).
            pv = premieres.get((d["serie"], d["periode"]))
            if pv:
                v = pv["valeur"]
                nouvelles.append({"resolution": True, "question": qid, "issue": "oui" if v >= d["seuil"] else "non",
                                  "valeur": v, "date_fait": pv["collecte_le"][:10], "publie_le": pv["collecte_le"],
                                  "source": "data/premieres_valeurs.jsonl (première valeur collectée)", "methode": "script"})
            continue
        # Une proposition par agent et par passage (relecture 12 ; relecture 13, S6) : deux propositions du
        # même agent le même jour ne valent qu'un avis. Une proposition « non » sur un événement « survenue »
        # avant son échéance est ignorée : l'événement peut encore survenir (relecture 13, S1). Une
        # proposition sans issue (issue null) consigne une recherche restée vaine (relecture 13, S13).
        avis, vus, vaines = [], set(), set()
        for a in props.get(qid, []):
            cle = (a["agent"], a.get("emise", "")[:10])
            if cle in vus:
                continue
            vus.add(cle)
            if a["issue"] is None:
                vaines.add(cle)   # par agent et par passage, comme les avis (relecture 19, S7)
                continue
            if a["issue"] == "non" and nature(qid, q) == "survenue" and a.get("emise", "")[:10] <= q["echeance"]:
                continue   # émise avant l'échéance : ignorée, même après l'échéance (relecture 14, N1)
            avis.append(a)
        issues = [a["issue"] for a in avis]
        def df(issue, avis_retenus):
            # Événement « survenue » et issue « non » : la date du fait est la fin de la fenêtre
            # (relecture 9). Événement « constat » : date de publication du constat, quelle que soit
            # l'issue (relecture 10, I1 c).
            if issue == "non" and nature(qid, q) == "survenue":
                return q["echeance"]
            return min(date_fait(a) for a in avis_retenus)
        if len(avis) >= 2 and issues[0] == issues[1]:
            nouvelles.append({"resolution": True, "question": qid, "issue": issues[0], "date_fait": df(issues[0], avis[:2]),
                              "source": " ; ".join(a["source"] for a in avis[:2]), "methode": "deux agents concordants"})
        elif len(avis) >= 3:
            maj = max(set(issues[:3]), key=issues[:3].count)
            if issues[:3].count(maj) >= 2:
                nouvelles.append({"resolution": True, "question": qid, "issue": maj,
                                  "date_fait": df(maj, [a for a in avis[:3] if a["issue"] == maj]),
                                  "source": " ; ".join(a["source"] for a in avis[:3]), "methode": "troisième agent, majorité"})
            else:
                nouvelles.append({"resolution": True, "question": qid, "issue": None, "source": "—",
                                  "methode": "annulée : désaccord persistant entre trois agents"})
        elif date.fromisoformat(q["echeance"]) + timedelta(days=30) < date.fromisoformat(aujourdhui) and not avis and len(vaines) >= 2:
            # Annulation à 30 jours seulement si deux agents ont consigné une recherche vaine (relecture 13, S13).
            nouvelles.append({"resolution": True, "question": qid, "issue": None, "source": "—",
                              "methode": "annulée : source introuvable pour deux agents, 30 jours après l'échéance"})
        elif date.fromisoformat(q["echeance"]) + timedelta(days=60) < date.fromisoformat(aujourdhui) and (avis or vaines):
            # Un seul avis, ou deux avis divergents sans troisième, 60 jours après l'échéance (relecture 12, S5).
            nouvelles.append({"resolution": True, "question": qid, "issue": None, "source": "—",
                              "methode": "annulée : pas de résolution concordante 60 jours après l'échéance"})
    # Questions conjointes (feuille de route v0, bloc 5) : « non » dès qu'une composante est « non » (date du fait :
    # la plus précoce) ; « oui » quand les deux sont « oui » (date du fait : la plus tardive) ; annulée si une
    # composante l'est.
    eff = {**resolutions_effectives(sfx), **{r["question"]: r for r in nouvelles}}
    for qid, q in toutes_les_questions(cycles_du_registre(reg)).items():
        if q["type"] != "conjointe" or qid in deja or qid not in emises:
            continue
        rs = [eff.get(c) for c in q["details"]["composantes"]]
        non = [r for r in rs if r and r.get("issue") == "non"]
        if non:
            nouvelles.append({"resolution": True, "question": qid, "issue": "non", "date_fait": min(r["date_fait"] for r in non),
                              "source": "composantes", "methode": "conjointe : une composante résolue « non »"})
        elif all(r and r.get("issue") == "oui" for r in rs):
            nouvelles.append({"resolution": True, "question": qid, "issue": "oui", "date_fait": max(r["date_fait"] for r in rs),
                              "source": "composantes", "methode": "conjointe : deux composantes résolues « oui »"})
        elif any(r and r.get("issue") is None for r in rs):
            nouvelles.append({"resolution": True, "question": qid, "issue": None, "source": "—",
                              "methode": "annulée : une composante annulée"})
    if nouvelles:
        ajouter(f"registre/resolutions{sfx}.jsonl", nouvelles)
    return nouvelles


if __name__ == "__main__":
    reg = sys.argv[1] if len(sys.argv) > 1 else "registre/protocole.jsonl"
    n = resoudre(reg)
    print(f"{len(n)} résolution(s) ajoutée(s)" + "".join(f"\n- {r['question']} : {r['issue']} ({r['methode']})" for r in n))
