"""Construit modele/evenements.json (noyau, section 8.8).

Depuis la relecture 8 (4 octobre 2026), les critères viennent de modele/banque/criteres.json : un
critère propre par événement, seul transmis aux prévisionnistes. Le texte d'origine du balayage v1
(modele/v1/fusion.md, section 2, et modele/v1/balayage_C.md) est recopié mot pour mot dans le champ
« contexte_v1 », pour la trace ; il n'est jamais transmis (relecture 8, G1 : il contenait des cotes,
des sondages et des taux de base qui ancraient l'ensemble direct).
"""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RACINE = Path(__file__).resolve().parent.parent


def table(chemin, marqueur):
    lignes = (RACINE / chemin).read_text("utf-8").split(marqueur, 1)[1].splitlines()
    entete, rangs = None, []
    for l in lignes[1:]:
        if l.startswith("## "):
            break
        if not l.startswith("|"):
            continue
        cellules = [c.strip() for c in l.strip().strip("|").split(" | ")]
        if entete is None:
            entete = cellules
        elif not set(cellules[0]) <= set("-: "):
            rangs.append(dict(zip(entete, cellules)))
    return rangs


def contexte_v1():
    """Texte d'origine du balayage v1, par identifiant d'événement."""
    rangs = list(table("modele/v1/fusion.md", "## 2. Événements"))
    entete = None
    for l in (RACINE / "modele/v1/balayage_C.md").read_text("utf-8").splitlines():
        if l.startswith("| id | nom | domaine |"):
            entete = [c.strip() for c in l.strip().strip("|").split(" | ")]
        elif l.startswith("| EV-C") and entete:
            rangs.append(dict(zip(entete, [c.strip() for c in l.strip().strip("|").split(" | ")])))
    ctx = {}
    for r in rangs:
        if r.get("id", "").startswith("EV-") and r["id"] not in ctx:
            ctx[r["id"]] = {"critere": r.get("critère de résolution ou source de probabilité externe", ""),
                            "mesure": r.get("mesure et série", "")}
    return ctx


def construire():
    ref = json.loads((RACINE / "modele/banque/criteres.json").read_text("utf-8"))
    # Ajouts en cours de phase (noyau, section 8.8) : une ligne par événement, en ajout seul.
    f = RACINE / "modele/banque/ajouts.jsonl"
    ajouts = [json.loads(l) for l in f.read_text("utf-8").splitlines() if l.strip()] if f.exists() else []
    ctx = contexte_v1()
    evts = []
    for e in ref["evenements"] + ajouts:
        e.setdefault("accessible", True)
        e.setdefault("motif_inaccessible", None)
        d = {k: v for k, v in e.items() if k not in ("accessible",)}
        d["source_accessible"] = e["accessible"]
        if e["evenement"] in ctx:
            d["contexte_v1"] = ctx[e["evenement"]]
        evts.append(d)
    return evts, ref


if __name__ == "__main__":
    evts, ref = construire()
    sortie = {
        "description": "Banque d'événements (noyau, section 8.8). Générée par scripts/evenements.py depuis modele/banque/criteres.json. Seul le champ « critere » est transmis aux prévisionnistes.",
        "genere_le": datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds"),
        "premier_tour": ref["premier_tour"], "second_tour": ref["second_tour"],
        "evenements": evts,
    }
    (RACINE / "modele" / "evenements.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=1), "utf-8")
    n_ok = sum(e["source_accessible"] for e in evts)
    pools = {}
    for e in evts:
        if e["source_accessible"]:
            pools[e["pool"]] = pools.get(e["pool"], 0) + 1
    print(f"{len(evts)} questions d'événement ({len({e['evenement'] for e in evts})} événements), {n_ok} résolubles, {len(evts) - n_ok} non émises ; pools {pools}")
