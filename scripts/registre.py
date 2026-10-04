"""Ajout de lignes aux registres de prévisions (protocole, sections 0 et 12).

Seul ce script écrit dans registre/*.jsonl. Le champ « emise » est fixé ici, à partir de
l'horloge système, et jamais fourni par un agent : toute valeur « emise » en entrée est refusée.

Usage :
    python scripts/registre.py registre/exploratoire.jsonl < lignes.jsonl
Chaque ligne d'entrée est un objet JSON : une prévision (question, probabilites, piste, origine,
donnees, et phase pour la piste protocole ; auteur facultatif), un erratum (erratum: true, objet,
correction, piste), une proposition de résolution par un agent (proposition: true, question, issue,
source, agent) ou une résolution (resolution: true, question, issue, source, methode).
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RACINE = Path(__file__).resolve().parent.parent
PREVISION = {"question", "probabilites", "piste", "origine", "donnees"}
ERRATUM = {"erratum", "objet", "correction", "piste"}
RESOLUTION = {"resolution", "question", "issue", "source", "methode"}   # issue = null si la question est annulée
PROPOSITION = {"proposition", "question", "issue", "source", "agent"}


def horodatage():
    return datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")


def valider(l):
    if "emise" in l:
        raise ValueError("le champ « emise » est fixé par le script, pas fourni en entrée")
    if l.get("erratum"):
        manque = ERRATUM - l.keys()
    elif l.get("resolution"):
        manque = RESOLUTION - l.keys()
    elif l.get("proposition"):
        manque = PROPOSITION - l.keys()
    else:
        manque = PREVISION - l.keys()
        if l.get("piste") == "protocole" and "phase" not in l:
            manque.add("phase")
        if not manque:
            total = sum(l["probabilites"].values())
            if abs(total - 100) > 0.6:
                raise ValueError(f"{l['question']} : probabilités de somme {total}, pas 100")
    if manque:
        raise ValueError(f"champs manquants : {sorted(manque)}")


def ajouter(chemin, lignes):
    t = horodatage()
    for l in lignes:
        valider(l)
    cible = RACINE / chemin
    cible.parent.mkdir(parents=True, exist_ok=True)
    with cible.open("a", encoding="utf-8") as f:
        for l in lignes:
            f.write(json.dumps({**l, "emise": t}, ensure_ascii=False) + "\n")
    return t


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].startswith("registre/"):
        sys.exit("usage : python scripts/registre.py registre/<fichier>.jsonl < lignes.jsonl")
    entrees = [json.loads(x) for x in sys.stdin if x.strip()]
    print(f"{len(entrees)} ligne(s) ajoutée(s), émises le {ajouter(sys.argv[1], entrees)}")
