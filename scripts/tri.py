"""Outils du tri de l'actualité (annexe, section 11.2 ; noyau, section 8.9).

Usage :
    python scripts/tri.py a-trier SORTIE.json
        Écrit dans SORTIE.json les titres de data/veille.json qui n'ont encore aucune décision de tri,
        et la liste des questions d'événement ouvertes (identifiant, nom, critère, fenêtre), seules
        cibles de rattachement en phases 1 et 2 (cas « donnée »). Affiche le nombre de titres.
    python scripts/tri.py ajouter < decisions.jsonl
        Ajoute les décisions à data/tri/AAAA-MM.jsonl (mois du passage), en ajout seul. Chaque ligne
        d'entrée porte les clés lien, fait, decision, motif ; « passage » est fixé ici, à partir de
        l'horloge système. Refuse une ligne incomplète, une clé inconnue ou un lien déjà trié.
        decision vaut l'identifiant d'une question (« Q-EV-08 ») ou « non rattaché ».
"""
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from commun import RACINE, lire_json

CLES = {"lien", "fait", "decision", "motif"}
TRI = RACINE / "data" / "tri"


def deja_tries():
    tries = set()
    for f in TRI.glob("*.json*"):
        if f.suffix == ".jsonl":
            tries |= {json.loads(l).get("lien") for l in f.read_text("utf-8").splitlines() if l.strip()}
        else:
            tries |= set(json.loads(f.read_text("utf-8")).get("decides", []))
    tries.discard(None)
    return tries


def questions_ouvertes():
    resolues = set()
    f = RACINE / "registre" / "resolutions.jsonl"
    if f.exists():
        resolues = {json.loads(l)["question"] for l in f.read_text("utf-8").splitlines() if l.strip()}
    return [{"question": f"Q-{e['id']}", "nom": e["nom"], "critere": e["critere"], "fenetre": e["fenetre"]}
            for e in lire_json("modele/evenements.json")["evenements"]
            if e["source_accessible"] and f"Q-{e['id']}" not in resolues]


def a_trier(sortie):
    tries = deja_tries()
    items = [{k: i[k] for k in ("source", "titre", "lien", "date")}
             for i in lire_json("data/veille.json")["items"] if i["lien"] not in tries]
    with open(sortie, "w", encoding="utf-8") as f:
        json.dump({"titres": items, "questions_ouvertes": questions_ouvertes()}, f, ensure_ascii=False, indent=1)
    print(f"{len(items)} titres à trier ; {len(questions_ouvertes())} questions d'événement ouvertes ; écrit dans {sortie}")


def ajouter():
    tries = deja_tries()
    valides = {q["question"] for q in questions_ouvertes()} | {"non rattaché"}
    passage = datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")
    lignes, vus = [], set()
    for n, l in enumerate(sys.stdin, 1):
        if not l.strip():
            continue
        d = json.loads(l)
        if set(d) != CLES:
            sys.exit(f"ligne {n} : clés {sorted(d)} au lieu de {sorted(CLES)}")
        if d["lien"] in tries or d["lien"] in vus:
            sys.exit(f"ligne {n} : lien déjà trié")
        if d["decision"] not in valides:
            sys.exit(f"ligne {n} : décision « {d['decision']} » inconnue (question ouverte ou « non rattaché »)")
        vus.add(d["lien"])
        lignes.append({"lien": d["lien"], "passage": passage, "fait": d["fait"], "decision": d["decision"], "motif": d["motif"]})
    f = TRI / f"{passage[:7]}.jsonl"
    with f.open("a", encoding="utf-8") as h:
        for x in lignes:
            h.write(json.dumps(x, ensure_ascii=False) + "\n")
    r = sum(x["decision"] != "non rattaché" for x in lignes)
    print(f"{len(lignes)} décisions ajoutées à {f.relative_to(RACINE)} ({r} rattachées), passage {passage}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "a-trier":
        a_trier(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "ajouter":
        ajouter()
    else:
        sys.exit(__doc__)
