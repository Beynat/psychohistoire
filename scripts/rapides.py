"""Pool de questions rapides (feuille de route, étape 6 ; revues du 10 octobre 2026, C.5 et 4.4).

Questions qui se résolvent en quelques semaines, pour valider la méthode bien avant les 40 questions de la banque :
- jalons : « le jalon J-xxx est-il observé ? » pour chaque jalon dont la fenêtre se termine avant la fin du mois
  qui suit le gel et qui n'a pas encore de statut ; résolu par son statut (modele/jalons/statuts.jsonl) ;
- variables d'état : « quel est l'état de VE-xxx pour le mois du gel ? » ; résolu par modele/reseau/observations.json
  une fois le mois écoulé.

Pool « PR », type « rapide », une grappe par nœud du réseau : hors du test de la section 8.6 (pools P2b et P2c) et
hors du décompte du protocole ; ces questions sont prévues par le réseau et par l'ensemble direct, et notées à part.

Usage : python scripts/rapides.py AAAA-MM-JJ ETIQUETTE   ajoute les questions rapides à data/cycles/<ETIQUETTE>/
        questions.json (après scripts/questions.py, avant les comparateurs) ; refuse si elles y sont déjà.
"""
import json
import sys
from datetime import date

from commun import lire_json, lire_jsonl, RACINE


def fin_mois(m):
    a, mm = int(m[:4]), int(m[5:7])
    return (date(a + (mm == 12), mm % 12 + 1, 1).toordinal() - 1)


def iso(o):
    return date.fromordinal(o).isoformat()


def generer(gel, etiquette):
    mois = gel[:7]
    suivant = f"{int(mois[:4]) + (mois[5:] == '12'):04d}-{int(mois[5:]) % 12 + 1:02d}"
    borne = iso(fin_mois(suivant))
    defs = {j["id"]: j for j in lire_jsonl("modele/jalons/definitions.jsonl")}
    statuts = {s["jalon"] for s in lire_jsonl("modele/jalons/statuts.jsonl")}
    v2 = lire_json("modele/jalons/vraisemblances_v2.json")["jalons"]
    s = lire_json("modele/reseau/structure_v0.json")
    out = []
    for jid, j in sorted(defs.items()):
        f = j["fenetre"]
        if jid not in v2 or jid in statuts or not (gel < f["fin"] <= borne):
            continue
        out.append({"id": f"Q-{etiquette}-{jid}", "type": "rapide", "pool": "PR", "grappe": f"PR-{v2[jid]['noeud']}",
                    "texte": f"Le fait suivant est-il observé entre le {f['debut']} et le {f['fin']} ? {j['observable']}",
                    "issues": ["oui", "non"], "echeance": f["fin"],
                    "details": {"rapide": "jalon", "jalon": jid, "noeud": v2[jid]["noeud"],
                                "critere": f"{j['observable']} Source : {j['indicateur']['source']}. Fenêtre : du {f['debut']} au {f['fin']}."}})
    for v in s["variables_etat"]:
        out.append({"id": f"Q-{etiquette}-{v['id']}-{mois}", "type": "rapide", "pool": "PR", "grappe": f"PR-{v['id']}",
                    "texte": f"{v['nom']} : état pour le mois {mois} ({v['definition']}).",
                    "issues": v["etats"], "echeance": iso(fin_mois(mois) + 15),
                    "details": {"rapide": "variable", "noeud": v["id"], "mois": mois,
                                "critere": f"État de « {v['nom']} » pour {mois} : {v['definition']}. Issues : {', '.join(v['etats'])}."}})
    return out


def ajouter(gel, etiquette):
    f = RACINE / "data" / "cycles" / etiquette / "questions.json"
    banque = json.loads(f.read_text("utf-8"))
    if any(q["type"] == "rapide" for q in banque["questions"]):
        sys.exit(f"Questions rapides déjà présentes dans data/cycles/{etiquette}/questions.json")
    qs = generer(gel, etiquette)
    banque["questions"] += qs
    f.write_text(json.dumps(banque, ensure_ascii=False, indent=1), "utf-8")
    return qs


def resolution(q):
    """Résolution d'une question rapide par script, ou None si elle n'est pas encore établie."""
    d = q["details"]
    if d["rapide"] == "jalon":
        der = None
        for st in lire_jsonl("modele/jalons/statuts.jsonl"):
            if st["jalon"] == d["jalon"] and st["statut"] in ("observé", "manqué"):
                der = st
        if not der:
            return None
        return {"issue": "oui" if der["statut"] == "observé" else "non", "date_fait": der["date"],
                "source": f"modele/jalons/statuts.jsonl ({der.get('source')})"}
    if d["rapide"] == "variable":
        o = lire_json("modele/reseau/observations.json") or {}
        e = o.get("etats", {}).get(d["noeud"], {}).get(d["mois"])
        if not isinstance(e, str) or (o.get("etabli_le") or "")[:7] <= d["mois"]:
            return None   # mois pas encore écoulé à la dernière mise à jour des observations
        return {"issue": e, "date_fait": o["etabli_le"][:10], "source": "modele/reseau/observations.json"}
    return None


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) != 2:
        sys.exit(__doc__)
    print(f"{len(ajouter(a[0], a[1]))} questions rapides ajoutées au cycle {a[1]}")
