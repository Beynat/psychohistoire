"""Outils du tri de l'actualité (annexe, section 11.2 ; noyau, section 8.9).

Usage :
    python scripts/tri.py a-trier SORTIE.json
        Écrit dans SORTIE.json les titres de data/veille.json qui n'ont encore aucune décision de tri,
        et la liste des questions d'événement ouvertes (identifiant, nom, critère, fenêtre), seules
        cibles de rattachement en phases 1 et 2 (cas « donnée »). Affiche le nombre de titres.
    python scripts/tri.py ajouter < decisions.jsonl
        Ajoute les décisions à data/tri/AAAA-MM.jsonl (mois du passage), en ajout seul. Chaque ligne
        d'entrée porte les clés lien, fait, decision, motif, et facultativement concerne (questions
        dont le fait peut changer la probabilité, à titre descriptif) et caracterisation (nature,
        stade, appui : annexe, section 11.2) ; « passage » est fixé ici, à partir de l'horloge système.
        Refuse une ligne incomplète, une clé inconnue, une caractérisation hors liste ou un lien déjà
        trié. decision vaut l'identifiant d'une question qu'il pourrait résoudre (« Q-EV-08 ») ou
        « non rattaché ».
    python scripts/tri.py reprise
        Écrit data/reprise.json : pour chaque fait, sources distinctes, jours de présence, premier et
        dernier jour, questions concernées et caractérisation (annexe, section 11.2 ; descriptif).
"""
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from commun import RACINE, lire_json

CLES = {"lien", "fait", "decision", "motif"}
FACULTATIVES = {"concerne", "caracterisation"}
NATURES = {"pénal lié à la fonction", "pénal hors fonction", "manquement éthique ou politique",
           "vie privée", "décision ou déclaration publique", "autre"}
STADES = {"allégation", "procédure engagée", "mise en cause formelle", "décision"}
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
    titres = {i["lien"]: i for i in lire_json("data/veille.json")["items"]}
    valides = {q["question"] for q in questions_ouvertes()} | {"non rattaché"}
    passage = datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")
    lignes, vus = [], set()
    for n, l in enumerate(sys.stdin, 1):
        if not l.strip():
            continue
        d = json.loads(l)
        if not CLES <= set(d) <= CLES | FACULTATIVES:
            sys.exit(f"ligne {n} : clés {sorted(d)} ; attendues {sorted(CLES)}, facultatives {sorted(FACULTATIVES)}")
        c = d.get("caracterisation")
        if c is not None and (c.get("nature") not in NATURES or c.get("stade") not in STADES or "appui" not in c):
            sys.exit(f"ligne {n} : caractérisation invalide (nature dans {sorted(NATURES)}, stade dans {sorted(STADES)}, appui requis)")
        if d["lien"] in tries or d["lien"] in vus:
            sys.exit(f"ligne {n} : lien déjà trié")
        if d["decision"] not in valides:
            sys.exit(f"ligne {n} : décision « {d['decision']} » inconnue (question ouverte ou « non rattaché »)")
        vus.add(d["lien"])
        t = titres.get(d["lien"], {})
        lignes.append({"lien": d["lien"], "passage": passage, "fait": d["fait"], "decision": d["decision"], "motif": d["motif"],
                       **{k: d[k] for k in FACULTATIVES if k in d},
                       # Source et date du titre, conservées pour la mesure de reprise (la veille purge les titres triés).
                       "source": t.get("source"), "date_titre": t.get("date")})
    f = TRI / f"{passage[:7]}.jsonl"
    with f.open("a", encoding="utf-8") as h:
        for x in lignes:
            h.write(json.dumps(x, ensure_ascii=False) + "\n")
    r = sum(x["decision"] != "non rattaché" for x in lignes)
    print(f"{len(lignes)} décisions ajoutées à {f.relative_to(RACINE)} ({r} rattachées), passage {passage}")


def reprise():
    """Mesure descriptive de reprise par fait (annexe, section 11.2)."""
    titres = {i["lien"]: i for i in lire_json("data/veille.json")["items"]}
    faits = {}
    for f in sorted(TRI.glob("*.jsonl")):
        for l in f.read_text("utf-8").splitlines():
            if not l.strip():
                continue
            d = json.loads(l)
            if d["decision"] == "non rattaché" and not d.get("concerne"):
                continue
            x = faits.setdefault(d["fait"], {"sources": set(), "jours": set(), "liens": 0, "concerne": set(),
                                             "decision": set(), "caracterisation": None})
            t = titres.get(d["lien"], {})
            x["sources"].add((d.get("source") or t.get("source") or "?").split(" · ")[0])
            x["jours"].add((d.get("date_titre") or t.get("date") or d["passage"])[:10])
            x["liens"] += 1
            x["concerne"] |= set(d.get("concerne", []))
            if d["decision"] != "non rattaché":
                x["decision"].add(d["decision"])
            x["caracterisation"] = d.get("caracterisation") or x["caracterisation"]
    sortie = {k: {"sources_distinctes": len(v["sources"]), "sources": sorted(v["sources"]), "titres": v["liens"],
                  "jours": len(v["jours"]), "premier_jour": min(v["jours"]), "dernier_jour": max(v["jours"]),
                  "concerne": sorted(v["concerne"]), "peut_resoudre": sorted(v["decision"]),
                  "caracterisation": v["caracterisation"]} for k, v in faits.items()}
    (RACINE / "data" / "reprise.json").write_text(json.dumps(
        {"description": "Reprise des faits dans la veille (annexe, section 11.2) : descriptif, sans effet sur les probabilités. Limite : sept flux suivis (franceinfo, Le Monde, LCP, Public Sénat, Le Figaro, Libération, Mediapart).",
         "faits": sortie}, ensure_ascii=False, indent=1), "utf-8")
    print(f"{len(sortie)} faits suivis dans data/reprise.json")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "a-trier":
        a_trier(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "ajouter":
        ajouter()
    elif len(sys.argv) == 2 and sys.argv[1] == "reprise":
        reprise()
    else:
        sys.exit(__doc__)
