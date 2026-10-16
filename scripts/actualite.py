"""Fil d'actualité de l'application (16 octobre 2026, demande de Nathan) : un fait, son résumé, ses sources et son
effet sur les jalons. C'est une lecture, pas une preuve : rien ici n'entre dans les prévisions. Un jalon n'entre
dans le moteur que par son statut consigné (scripts/jalons.py statut, routine hebdomadaire).

Usage :
    python scripts/actualite.py ajouter < faits.jsonl    ajoute des faits (journal en ajout seul, horodaté ici)
    python scripts/actualite.py liste [JOURS]            faits des JOURS derniers jours (90 par défaut)

Une ligne : {"date": "AAAA-MM-JJ", "titre": "…", "resume": "…", "sources": ["https://…"],
             "jalons": [{"id": "J-0xx", "effet": "rapproche|éloigne|observé|manqué", "note": "…"}],
             "noeuds": [{"id": "PV-…", "note": "…"}]}   (noeuds : facultatif, effet sur un pivot sans jalon)
Au moins un jalon ou un nœud. Titre de 90 caractères au plus, résumé de 600, note de 160 : la carte doit se lire
d'un coup d'œil, le détail tient en quelques lignes, dans nos mots (jamais une citation d'article).
"""
import json
import re
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from commun import RACINE, lire_json, lire_jsonl

JOURNAL = "data/actualite.jsonl"
EFFETS = ("rapproche", "éloigne", "observé", "manqué")


def verifier(e, jalons, noeuds):
    """Défauts d'une ligne (liste vide si conforme)."""
    d = []
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(e.get("date", ""))):
        d.append("date AAAA-MM-JJ")
    if not e.get("titre") or len(e["titre"]) > 90:
        d.append("titre de 1 à 90 caractères")
    if not e.get("resume") or len(e["resume"]) > 600:
        d.append("résumé de 1 à 600 caractères")
    if not e.get("sources") or not all(str(s).startswith("https://") for s in e["sources"]):
        d.append("au moins une source https")
    js, ns = e.get("jalons") or [], e.get("noeuds") or []
    if not js and not ns:
        d.append("au moins un jalon ou un nœud")
    for j in js:
        if j.get("id") not in jalons:
            d.append(f"jalon inconnu : {j.get('id')}")
        if j.get("effet") not in EFFETS:
            d.append(f"effet de {j.get('id')} hors de {EFFETS}")
        if len(j.get("note", "")) > 160:
            d.append(f"note de {j.get('id')} trop longue")
    for n in ns:
        if n.get("id") not in noeuds:
            d.append(f"nœud inconnu : {n.get('id')}")
        if not n.get("note") or len(n["note"]) > 160:
            d.append(f"note de {n.get('id')} de 1 à 160 caractères")
    inconnus = set(e) - {"date", "titre", "resume", "sources", "jalons", "noeuds"}
    if inconnus:
        d.append(f"champs inconnus : {sorted(inconnus)}")
    return d


def ajouter(lignes):
    import reseau
    jalons = {j["id"] for j in lire_jsonl("modele/jalons/definitions.jsonl")}
    noeuds = set(reseau.noeuds_de(lire_json("modele/reseau/structure_v0.json")))
    existants = lire_jsonl(JOURNAL) if (RACINE / JOURNAL).exists() else []
    vus = {(x["date"], x["titre"]) for x in existants}
    out = []
    for l in lignes:
        if not l.strip():
            continue
        e = json.loads(l)
        d = verifier(e, jalons, noeuds)
        if d:
            sys.exit(f"{e.get('titre', '?')} : " + " ; ".join(d))
        if (e["date"], e["titre"]) in vus:
            continue    # déjà inscrit : reprise sans doublon
        n = sum(1 for x in existants + out if x["date"] == e["date"]) + 1
        out.append({"id": f"A-{e['date'].replace('-', '')}-{n}", **e,
                    "emise": datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")})
    with open(RACINE / JOURNAL, "a", encoding="utf-8") as f:
        for e in out:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return out


def liste(jours=90, jour=None):
    """Faits des JOURS derniers jours, du plus récent au plus ancien."""
    if not (RACINE / JOURNAL).exists():
        return []
    limite = ((date.fromisoformat(jour) if jour else date.today()) - timedelta(days=jours)).isoformat()
    xs = [x for x in lire_jsonl(JOURNAL) if x["date"] >= limite]
    return sorted(xs, key=lambda x: (x["date"], x["id"]), reverse=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "ajouter":
        r = ajouter(sys.stdin.read().splitlines())
        print(f"{len(r)} fait(s) ajouté(s) : " + ", ".join(x["id"] for x in r))
    elif a and a[0] == "liste":
        for x in liste(int(a[1]) if len(a) > 1 else 90):
            print(x["date"], x["id"], x["titre"], "|", ", ".join(f"{j['id']} {j['effet']}" for j in x.get("jalons", [])))
    else:
        sys.exit(__doc__)
