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
{noeud, issue, question}, vraisemblances {a, b} (version 1, conservée dans le journal) et optionnellement
vraisemblances_si_precedent. Depuis le 10 octobre 2026, le calcul lit les vraisemblances par issue de la version 2
(modele/jalons/vraisemblances_v2.json) et passe par le moteur unique (scripts/preuves.py, scripts/reseau.py).
Règles (annexe, section 10.7) : fenêtre ouverte au moins 7 jours après la définition ; aucun identifiant réutilisé.
Les jalons indices sont sans effet sur les prévisions notées (section 10.6) : le registre fantôme seul en tient
compte, avec le facteur de réduction k = 0,5 tant qu'il n'est pas estimé (section 10.4). Un jalon « qui tranche »
observé est une observation : il entre dans les prévisions notées, sans réduction (feuille de route, étape 2).
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


def fantome(reg, jour, tirages=200, trajectoires=100):
    """Registre fantôme (feuille de route, étape 2) : prévisions qu'aurait le réseau si tous les jalons étaient
    actifs, calculées par le moteur unique (scripts/reseau.py) sur toutes les questions du dernier cycle du réseau
    dans REG. Chaque trajectoire est pondérée par les vraisemblances v2 des jalons observés, manqués ou en cours
    (scripts/preuves.py ; indices réduits par k). La ligne porte aussi la prévision de référence (jalons « qui
    tranche » observés et faits retenus seulement), pour lire l'apport des indices."""
    import preuves as pv
    import reseau
    from commun import lire_json, lire_jsonl as lj
    etiquette = None
    for l in lj(reg):
        if l.get("auteur") == reseau.VERSION and str(l.get("origine", "")).startswith("cycle "):
            etiquette = l["origine"].removeprefix("cycle ")
    if not etiquette:
        return []
    s = lire_json("modele/reseau/structure_v0.json")
    t = lire_json("modele/reseau/tables_v0.json")
    qs = reseau.questions_cycle(s, etiquette)
    obs = reseau.observations(s)
    pf, pn = pv.preuves_fantome(jour, K), pv.preuves_notees(jour, K)
    if not [p for p in pf if p["classe"] == "indice"]:
        return []
    f = reseau.prevoir(s, t, obs, qs, tirages, trajectoires, preuves=pf)
    r = reseau.prevoir(s, t, obs, qs, tirages, trajectoires, preuves=pn)
    lignes = [{"question": q["id"], "probabilites": {k: v for k, v in f[q["id"]].items() if k not in ("i80", "es")},
               "reference": {k: v for k, v in r[q["id"]].items() if k not in ("i80", "es")},
               "piste": "fantome", "auteur": "réseau v0 avec jalons (fantôme)", "origine": f"fantôme {jour}, cycle {etiquette}",
               "donnees": f"jalons au {jour}, k = {K}", "jalons": [p["id"] for p in pf if p["source"] == "jalon"],
               "trajectoires_effectives": f["__ess__"]["effectives"]} for q in qs]
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
        nt = int(a[a.index("--tirages") + 1]) if "--tirages" in a else 200
        ntr = int(a[a.index("--trajectoires") + 1]) if "--trajectoires" in a else 100
        print(f"{len(fantome(a[1], jour, nt, ntr))} ligne(s) ajoutée(s) à registre/fantome.jsonl")
    else:
        sys.exit(__doc__)
