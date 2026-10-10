"""Jalons du réseau v0 (annexe, section 10 ; feuille de route v0, bloc 2).

Usage :
    python scripts/jalons.py definir < jalons.jsonl     ajoute des définitions (defini_le fixé ici)
    python scripts/jalons.py statut < statuts.jsonl     ajoute des changements de statut (emise fixé ici)
    python scripts/jalons.py etat [AAAA-MM-JJ]          jalons ouverts, à venir, clos ; statut courant
    python scripts/jalons.py fantome REGISTRE [AAAA-MM-JJ]
                                                        registre fantôme : probabilités qu'aurait le réseau si
                                                        les jalons étaient actifs (registre/fantome.jsonl)

Journaux en ajout seul : modele/jalons/definitions.jsonl et modele/jalons/statuts.jsonl. Une définition porte :
id, lien (« PARENT → ENFANT »), observable (phrase vérifiable sans interprétation), indicateur {source, mesure,
seuil}, fenetre {debut, fin}, niveau (2 structurant, 3 fin), type (« amont », « transmission », « aval »), cible
{noeud, issue, question} (issue favorisée par l'observation, question de la banque dont la probabilité est ajustée
dans le registre fantôme), vraisemblances {a, b} (P(observé | hypothèse vraie), P(observé | hypothèse fausse)),
et optionnellement vraisemblances_si_precedent {observe: [a, b], manque: [a, b]} avec « precedent » (id).
Règles (annexe, section 10.7) : fenêtre ouverte au moins 7 jours après la définition ; aucun identifiant réutilisé.
Les jalons sont sans effet sur les probabilités du réseau (section 10.6) : le registre fantôme seul en tient compte,
avec le facteur de réduction k = 0,5 tant qu'il n'est pas estimé (section 10.4).
"""
import json
import math
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from commun import RACINE, lire_jsonl

DEFS = "modele/jalons/definitions.jsonl"
STATUTS = "modele/jalons/statuts.jsonl"
K = 0.5
CHAMPS = ("id", "lien", "observable", "indicateur", "fenetre", "niveau", "type", "cible", "vraisemblances")
STATUTS_PERMIS = ("observé", "manqué", "invalidé")


def maintenant():
    return datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")


def ecrire(chemin, lignes):
    f = RACINE / chemin
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("a", encoding="utf-8", newline="\n") as h:
        for l in lignes:
            h.write(json.dumps(l, ensure_ascii=True) + "\n")


def valider_definition(j, existants, jour):
    manque = [c for c in CHAMPS if c not in j]
    if manque:
        raise ValueError(f"{j.get('id')} : champs manquants {manque}")
    if j["id"] in existants:
        raise ValueError(f"{j['id']} : identifiant déjà défini")
    a, b = j["vraisemblances"]["a"], j["vraisemblances"]["b"]
    if not (0 < a < 1 and 0 < b < 1) or a == b:
        raise ValueError(f"{j['id']} : vraisemblances a et b dans ]0 ; 1[ et différentes")
    if j["type"] not in ("amont", "transmission", "aval") or j["niveau"] not in (2, 3):
        raise ValueError(f"{j['id']} : type ou niveau invalide")
    if date.fromisoformat(j["fenetre"]["debut"]) < jour + timedelta(days=7):
        raise ValueError(f"{j['id']} : fenêtre ouverte moins de 7 jours après la définition (annexe, section 10.7)")
    if j["fenetre"]["fin"] < j["fenetre"]["debut"]:
        raise ValueError(f"{j['id']} : fenêtre inversée")


def definir(lignes):
    existants = {j["id"] for j in lire_jsonl(DEFS)}
    t = maintenant()
    for j in lignes:
        valider_definition(j, existants, date.fromisoformat(t[:10]))
        existants.add(j["id"])
    ecrire(DEFS, [{**j, "defini_le": t} for j in lignes])
    return t


def statut(lignes):
    defs = {j["id"] for j in lire_jsonl(DEFS)}
    t = maintenant()
    for s in lignes:
        if s.get("jalon") not in defs or s.get("statut") not in STATUTS_PERMIS or not s.get("date") or not s.get("source"):
            raise ValueError(f"statut invalide : {s}")
    ecrire(STATUTS, [{**s, "emise": t} for s in lignes])
    return t


def etats(jour):
    """Statut courant de chaque jalon au jour donné (10.3) : attendu, en cours, ou le dernier statut consigné
    à cette date (observé, manqué, invalidé) ; une fenêtre close sans statut consigné est « à constater »."""
    consignes = {}
    for s in lire_jsonl(STATUTS):
        if s["emise"][:10] <= jour:
            consignes[s["jalon"]] = s
    out = {}
    for j in lire_jsonl(DEFS):
        if j["defini_le"][:10] > jour:
            continue
        f = j["fenetre"]
        if j["id"] in consignes:
            st = consignes[j["id"]]["statut"]
        elif jour < f["debut"]:
            st = "attendu"
        elif jour <= f["fin"]:
            st = "en cours"
        else:
            st = "à constater"
        out[j["id"]] = (j, st)
    return out


def rapport(j, st, jour):
    """Rapport de vraisemblance brut d'un jalon (10.4), selon son statut et l'avancement de sa fenêtre."""
    a, b = j["vraisemblances"]["a"], j["vraisemblances"]["b"]
    if st == "observé":
        return a / b
    if st == "manqué":
        return (1 - a) / (1 - b)
    if st == "en cours":
        d0, d1, t = (date.fromisoformat(x) for x in (j["fenetre"]["debut"], j["fenetre"]["fin"], jour))
        F = min(max((t - d0).days / max((d1 - d0).days, 1), 0), 1)
        return (1 - a * F) / (1 - b * F)
    return 1.0


def fantome(reg, jour):
    """Probabilités fantômes : pour chaque question cible, la dernière prévision du réseau dans REG, dont la
    cote de l'issue favorisée est multipliée par le produit des rapports des jalons, réduits par k."""
    from commun import lire_jsonl as lj
    derniere = {}
    for l in lj(reg):
        if l.get("auteur") == "réseau v0" and "probabilites" in l:
            derniere[l["question"]] = l
    lr = {}
    for jid, (j, st) in etats(jour).items():
        q = j["cible"]["question"]
        lr.setdefault(q, []).append((j, math.log(rapport(j, st, jour)) * K))
    lignes = []
    for q, liste in lr.items():
        base = derniere.get(q)
        if not base:
            continue
        issue = liste[0][0]["cible"]["issue"]
        p = base["probabilites"].get(issue)
        if p is None or not 0 < p < 100:
            continue
        lo = math.log(p / (100 - p)) + sum(x for _, x in liste)
        pf = 100 / (1 + math.exp(-lo))
        autres = {k: v for k, v in base["probabilites"].items() if k != issue}
        s = sum(autres.values()) or 1
        probas = {issue: round(pf, 1), **{k: round((100 - pf) * v / s, 1) for k, v in autres.items()}}
        lignes.append({"question": q, "probabilites": probas, "piste": "fantome", "auteur": "réseau v0 avec jalons (fantôme)",
                       "origine": f"fantôme {jour}", "donnees": f"jalons au {jour}, k = {K}",
                       "jalons": [j["id"] for j, _ in liste]})
    if lignes:
        from registre import ajouter
        ajouter("registre/fantome.jsonl", lignes)
    return lignes


if __name__ == "__main__":
    a = sys.argv[1:]
    jour = next((x for x in a if len(x) == 10 and x[4] == "-"), date.today().isoformat())
    if a[:1] == ["definir"]:
        lignes = [json.loads(x) for x in sys.stdin if x.strip()]
        print(f"{len(lignes)} jalon(s) défini(s) le {definir(lignes)}")
    elif a[:1] == ["statut"]:
        lignes = [json.loads(x) for x in sys.stdin if x.strip()]
        print(f"{len(lignes)} statut(s) consigné(s) le {statut(lignes)}")
    elif a[:1] == ["etat"]:
        for jid, (j, st) in sorted(etats(jour).items(), key=lambda x: x[1][0]["fenetre"]["debut"]):
            print(f"{jid:8} {st:12} {j['fenetre']['debut']} → {j['fenetre']['fin']}  {j['observable'][:90]}")
    elif a[:1] == ["fantome"] and len(a) >= 2:
        print(f"{len(fantome(a[1], jour))} ligne(s) ajoutée(s) à registre/fantome.jsonl")
    else:
        sys.exit(__doc__)
