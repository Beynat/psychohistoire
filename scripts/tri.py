"""Outils du tri de l'actualité (annexe, section 11.2 ; noyau, section 8.9).

Usage :
    python scripts/tri.py a-trier SORTIE.json
        Écrit dans SORTIE.json les titres de data/veille.json qui n'ont encore aucune décision de tri,
        la liste des questions d'événement ouvertes (identifiant, nom, critère, fenêtre) et la liste des
        faits déjà suivis (identifiant, jours, questions concernées, stade retenu), pour qu'un même fait
        garde son identifiant d'un passage à l'autre (relecture 11, S2). Affiche le nombre de titres.
    python scripts/tri.py ajouter < decisions.jsonl
        Ajoute les décisions à data/tri/AAAA-MM.jsonl (mois du passage), en ajout seul. Chaque ligne
        d'entrée porte les clés lien, fait, decision, motif, et facultativement concerne (questions
        dont le fait peut changer la probabilité, à titre descriptif) et caracterisation (nature,
        stade_propose, appui : annexe, section 11.2), contrôlée mais NON écrite dans le dépôt public
        (relecture 12, K6) ; « passage » est fixé ici, à partir de l'horloge système.
        Refuse une ligne incomplète, une clé inconnue, une caractérisation hors liste ou un lien déjà
        trié. decision vaut l'identifiant d'une question qu'il pourrait résoudre (« Q-EV-08 ») ou
        « non rattaché ».
    python scripts/tri.py etape < etapes.jsonl
        Ajoute à data/tri/etapes.jsonl, en ajout seul, la vérification d'une étape officielle d'un fait
        par un agent : fait, etape (liste ETAPES), source, date_fait, agent. Le stade d'un fait n'est
        relevé au-dessus de « allégation » que si deux agents distincts ont vérifié une étape de ce stade
        (annexe, section 11.2 ; relecture 11, J2).
    python scripts/tri.py reprise
        Écrit data/reprise.json : pour chaque fait, sources distinctes (total, sept premiers jours, sept
        derniers jours), jours de présence, questions concernées, caractérisation proposée, stade retenu,
        date de réexamen et statut (annexe, sections 11.2 et 11.3 ; descriptif).
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
STADES = ["allégation", "procédure engagée", "mise en cause formelle", "décision"]
# Étapes officielles (annexe, section 11.2) : actes de l'autorité elle-même ; une saisine ou un
# signalement par un tiers n'en est pas une (relecture 11, S4).
ETAPES = {
    "enquête ouverte par le parquet": "procédure engagée",
    "information judiciaire ouverte": "procédure engagée",
    "perquisition": "procédure engagée",
    "procédure ouverte par une autorité de contrôle": "procédure engagée",
    "commission d'enquête créée": "procédure engagée",
    "mise en examen": "mise en cause formelle",
    "témoin assisté": "mise en cause formelle",
    "renvoi devant une juridiction": "mise en cause formelle",
    "levée d'immunité": "mise en cause formelle",
    "jugement ou arrêt": "décision",
    "décision d'une autorité de contrôle": "décision",
    "décision de l'intéressé ou de son parti": "décision",
}
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
        rep = lire_json("data/reprise.json", {"faits": {}})["faits"]
        suivis = [{"fait": k, "premier_jour": v["premier_jour"], "dernier_jour": v["dernier_jour"],
                   "concerne": v["concerne"], "stade_retenu": v.get("stade_retenu")}
                  for k, v in rep.items() if v.get("statut") not in ("retombé",)]
        json.dump({"titres": items, "questions_ouvertes": questions_ouvertes(), "faits_suivis": suivis},
                  f, ensure_ascii=False, indent=1)
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
        if c is not None and (set(c) != {"nature", "stade_propose", "appui"} or c["nature"] not in NATURES
                              or c["stade_propose"] not in STADES):
            sys.exit(f"ligne {n} : caractérisation invalide : clés nature, stade_propose, appui ; nature dans "
                     f"{sorted(NATURES)} ; stade_propose dans {STADES} (le stade retenu reste « allégation » "
                     f"tant que deux agents n'ont pas vérifié une étape officielle)")
        if d["lien"] in tries or d["lien"] in vus:
            sys.exit(f"ligne {n} : lien déjà trié")
        if d["decision"] not in valides:
            sys.exit(f"ligne {n} : décision « {d['decision']} » inconnue (question ouverte ou « non rattaché »)")
        vus.add(d["lien"])
        t = titres.get(d["lien"], {})
        # La caractérisation proposée par l'agent de tri n'est pas écrite dans le dépôt, qui est public
        # (relecture 12, K6) : seul « concerne » est conservé. La nature n'est publiée qu'avec une étape
        # officielle vérifiée (data/tri/etapes.jsonl).
        lignes.append({"lien": d["lien"], "passage": passage, "fait": d["fait"], "decision": d["decision"], "motif": d["motif"],
                       **({"concerne": d["concerne"]} if "concerne" in d else {}),
                       # Seul le type est conservé (relecture 12, K5) : un fait public établi par la source
                       # de son auteur (décision, vote, accord publié) n'est pas une allégation.
                       **({"type_fait": "fait établi" if c["nature"] == "décision ou déclaration publique" else "mise en cause"}
                          if c is not None else {}),
                       # Source et date du titre, conservées pour la mesure de reprise (la veille purge les titres triés).
                       "source": t.get("source"), "date_titre": t.get("date")})
    f = TRI / f"{passage[:7]}.jsonl"
    with f.open("a", encoding="utf-8") as h:
        for x in lignes:
            h.write(json.dumps(x, ensure_ascii=False) + "\n")
    r = sum(x["decision"] != "non rattaché" for x in lignes)
    print(f"{len(lignes)} décisions ajoutées à {f.relative_to(RACINE)} ({r} rattachées), passage {passage}")


def etape():
    """Vérification d'une étape officielle par un agent (relecture 11, J2)."""
    f = TRI / "etapes.jsonl"
    passage = datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")
    lignes = []
    for n, l in enumerate(sys.stdin, 1):
        if not l.strip():
            continue
        d = json.loads(l)
        if not {"fait", "etape", "source", "date_fait", "agent"} <= set(d) <= {"fait", "etape", "source", "date_fait", "agent", "nature"}:
            sys.exit(f"ligne {n} : clés attendues fait, etape, source, date_fait, agent (nature facultative)")
        if "nature" in d and d["nature"] not in NATURES - {"vie privée"}:
            sys.exit(f"ligne {n} : nature hors liste ou « vie privée » (jamais publiée)")
        if d["etape"] not in ETAPES:
            sys.exit(f"ligne {n} : étape « {d['etape']} » hors liste {sorted(ETAPES)}")
        lignes.append({**d, "stade": ETAPES[d["etape"]], "verifie_le": passage})
    with f.open("a", encoding="utf-8") as h:
        for x in lignes:
            h.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"{len(lignes)} vérification(s) d'étape ajoutée(s) à {f.relative_to(RACINE)}")


def stades_retenus():
    """Stade retenu par fait : le plus élevé vérifié par au moins deux agents distincts, sinon « allégation »."""
    f = TRI / "etapes.jsonl"
    par = {}
    if f.exists():
        for l in f.read_text("utf-8").splitlines():
            if l.strip():
                d = json.loads(l)
                par.setdefault((d["fait"], d["stade"]), {}).setdefault(d["agent"], d["date_fait"])
    retenu = {}
    for (fait, stade), agents in par.items():
        if len(agents) >= 2 and STADES.index(stade) > STADES.index(retenu.get(fait, ("allégation", None))[0]):
            retenu[fait] = (stade, min(agents.values()))
    return retenu


def reprise(aujourdhui=None):
    """Mesure descriptive de reprise par fait, et statut du fait (annexe, sections 11.2 et 11.3)."""
    from datetime import date, timedelta
    auj = date.fromisoformat(aujourdhui) if aujourdhui else date.today()
    titres = {i["lien"]: i for i in lire_json("data/veille.json")["items"]}
    faits = {}
    for f in sorted(TRI.glob("*.jsonl")):
        if f.name == "etapes.jsonl":
            continue
        for l in f.read_text("utf-8").splitlines():
            if not l.strip():
                continue
            d = json.loads(l)
            if d["decision"] == "non rattaché" and not d.get("concerne"):
                continue
            x = faits.setdefault(d["fait"], {"obs": [], "concerne": set(), "decision": set(), "type": None})
            x["type"] = d.get("type_fait") or x["type"]
            t = titres.get(d["lien"], {})
            src = (d.get("source") or t.get("source") or "?").split(" · ")[0]
            x["obs"].append(((d.get("date_titre") or t.get("date") or d["passage"])[:10], src))
            x["concerne"] |= set(d.get("concerne", []))
            if d["decision"] != "non rattaché":
                x["decision"].add(d["decision"])
    stades = stades_retenus()
    natures = {}
    fe = TRI / "etapes.jsonl"
    if fe.exists():
        for l in fe.read_text("utf-8").splitlines():
            if l.strip() and "nature" in json.loads(l) and json.loads(l)["fait"] in stades:
                natures[json.loads(l)["fait"]] = json.loads(l)["nature"]
    sortie = {}
    for k, v in faits.items():
        jours = sorted({j for j, _ in v["obs"]})
        d0 = date.fromisoformat(jours[0])
        s7p = {s for j, s in v["obs"] if date.fromisoformat(j) < d0 + timedelta(days=7)}
        s7d = {s for j, s in v["obs"] if date.fromisoformat(j) > auj - timedelta(days=7)}
        stade, date_etape = stades.get(k, ("allégation", None))
        # Réexamen : 30 jours après l'entrée ; 14 jours si au moins cinq sources distinctes la première semaine
        # (constaté au septième jour). Table de décision de l'annexe, section 11.3.
        reex = d0 + timedelta(days=14 if len(s7p) >= 5 and auj >= d0 + timedelta(days=7) else 30)
        if v["type"] == "fait établi":
            statut, stade, reex = "fait établi", None, None
        elif date_etape and date_etape >= jours[0]:
            statut = "étape officielle vérifiée"
        elif auj < reex:
            statut = "en observation"
        elif auj < reex + timedelta(days=30) and len(s7d) >= len(s7p):
            statut, reex = "prolongé", reex + timedelta(days=30)
        else:
            statut = "retombé"
        sortie[k] = {"sources_distinctes": len({s for _, s in v["obs"]}), "sources": sorted({s for _, s in v["obs"]}),
                     "sources_7_premiers_jours": len(s7p), "sources_7_derniers_jours": len(s7d), "titres": len(v["obs"]),
                     "jours": len(jours), "premier_jour": jours[0], "dernier_jour": jours[-1],
                     "concerne": sorted(v["concerne"]), "peut_resoudre": sorted(v["decision"]),
                     "stade_retenu": stade, "nature_verifiee": natures.get(k),
                     "type_fait": v["type"], "date_reexamen": reex.isoformat() if reex else None, "statut": statut}
    (RACINE / "data" / "reprise.json").write_text(json.dumps(
        {"description": "Reprise et statut des faits (annexe, sections 11.2 et 11.3) : descriptif, sans effet sur les probabilités. Sept flux suivis (franceinfo, Le Monde, LCP, Public Sénat, Le Figaro, Libération, Mediapart). Stade retenu : « allégation » sauf étape officielle vérifiée par deux agents ; la nature n'est publiée qu'avec une étape vérifiée, jamais « vie privée ».",
         "etabli_le": auj.isoformat(), "faits": sortie}, ensure_ascii=False, indent=1), "utf-8")
    print(f"{len(sortie)} faits suivis dans data/reprise.json")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "a-trier":
        a_trier(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "ajouter":
        ajouter()
    elif len(sys.argv) == 2 and sys.argv[1] == "etape":
        etape()
    elif len(sys.argv) == 2 and sys.argv[1] == "reprise":
        reprise()
    else:
        sys.exit(__doc__)
