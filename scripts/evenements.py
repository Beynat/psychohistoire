"""Construit modele/evenements.json (noyau, section 8.8).

Reprend TOUS les événements du balayage v1 dotés d'un critère de résolution, sans sélection :
fusion A+B (modele/v1/fusion.md, section 2) et balayage C (modele/v1/balayage_C.md).
Le critère est recopié mot pour mot. Les seuls ajouts sont mécaniques et documentés ci-dessous :
- la fenêtre de résolution, lue dans le critère (dates explicites), sinon la fin de la période ;
- le découpage en sous-questions quand le critère prévoit lui-même des fenêtres séparées ;
- l'accessibilité de la source de résolution : une source qui exige un compte (ACLED) ou
  n'est pas publiée est marquée inaccessible ; ses questions seraient annulées (section 8.8),
  elles ne sont donc pas émises, avec motif.
"""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RACINE = Path(__file__).resolve().parent.parent
FIN = "2028-09-30"
SECOND_TOUR = "2027-05-02"  # à vérifier sur le décret de convocation (section 5.1)


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


# Fenêtre (début, fin), issues et accessibilité, lues dans chaque critère.
REGLES = {
    "EV-01": [("2026-10-03", FIN)],
    "EV-02": [("2026-10-03", "2026-12-31")],
    "EV-03": [("2028-03-01", "2028-04-30")],          # notification INSEE de mars 2028
    "EV-04": [("2026-10-03", FIN)],
    "EV-05": [("2026-10-03", SECOND_TOUR)],
    "EV-06": [("2026-10-03", "2028-07-31")],          # 1re estimation du T2 2028
    "EV-07": [("2026-10-03", FIN)],
    "EV-08": [("2026-10-03", FIN)],
    "EV-09": [("2027-06-01", FIN)],
    "EV-10": [("2026-10-03", "2026-11-15")],
    "EV-11": [("2026-10-03", FIN)],
    "EV-12": [("2026-10-03", FIN)],
    "EV-13": [("2026-10-03", "2026-12-31")],
    "EV-14": [("2026-10-03", FIN)],
    "EV-15": [("2026-10-03", "2026-12-31")],
    "EV-16": [("2026-10-03", SECOND_TOUR, "avant le second tour"), (SECOND_TOUR, FIN, "après le second tour")],
    "EV-17": [("2026-10-03", FIN)],
    "EV-C1": [("2026-10-03", FIN)],
    "EV-C2": [("2026-10-03", FIN)],
    "EV-C3": [("2026-10-03", "2026-12-31", "avant le 31/12/2026"), ("2026-10-03", FIN, "avant le 30/09/2028")],
    "EV-C4": [("2026-10-03", FIN)],
}
ISSUES = {"EV-05": ["RN", "bloc central", "gauche", "droite LR ou autre", "autre"],
          "EV-C4": ["avis rendu, compatible", "avis rendu, incompatible", "pas d'avis"]}
# Critères appréciés seulement en fin de fenêtre : pas de question mensuelle (cycle à blanc).
SANS_MENSUELLE = {"EV-17": "Le critère se juge à l'issue de législatives ou en fin de période, pas mois par mois.",
                  "EV-06": "Critère trimestriel, constaté aux publications de l'Insee : une question mensuelle n'a pas de sens (essai du 4 octobre 2026)."}
INACCESSIBLE = {
    "EV-12": "Résolution sur ACLED, qui exige un compte : source inaccessible au projet.",
    "EV-14": "Résolution sur ACLED, qui exige un compte : source inaccessible au projet.",
    "EV-11": "Le nombre de communes touchées n'est publié par le ministère de l'Intérieur qu'au cas par cas ; ACLED exige un compte.",
}


def construire():
    rangs = [(r, "fusion A+B") for r in table("modele/v1/fusion.md", "## 2. Événements")]
    texte_c = (RACINE / "modele/v1/balayage_C.md").read_text("utf-8").splitlines()
    entete = None
    for l in texte_c:
        if l.startswith("| id | nom | domaine |"):
            entete = [c.strip() for c in l.strip().strip("|").split(" | ")]
        elif l.startswith("| EV-C") and entete:
            rangs.append((dict(zip(entete, [c.strip() for c in l.strip().strip("|").split(" | ")])), "balayage C"))
    evts = []
    for r, origine in rangs:
        if True:
            if not r.get("id", "").startswith("EV-") or any(e["evenement"] == r["id"] for e in evts):
                continue
            critere = r.get("critère de résolution ou source de probabilité externe", "").strip()
            if not critere or critere in {"—", "-"}:
                continue
            for k, fen in enumerate(REGLES[r["id"]]):
                ident = r["id"] + ("" if len(REGLES[r["id"]]) == 1 else "abc"[k])
                evts.append({
                    "id": ident, "evenement": r["id"], "nom": r["nom"], "domaine": r["domaine"],
                    "critere": critere, "sous_question": fen[2] if len(fen) > 2 else None,
                    "source_resolution": r.get("mesure et série", ""),
                    "fenetre": {"debut": fen[0], "fin": fen[1]},
                    "issues": ISSUES.get(r["id"], ["oui", "non"]),
                    "source_accessible": r["id"] not in INACCESSIBLE,
                    "motif_inaccessible": INACCESSIBLE.get(r["id"]),
                    "origine": origine,
                    "mensuelle": r["id"] not in SANS_MENSUELLE,
                })
    return evts


if __name__ == "__main__":
    evts = construire()
    sortie = {
        "description": "Banque d'événements de la phase 1 (noyau, section 8.8). Générée par scripts/evenements.py ; ne change qu'à l'analyse trimestrielle, par ajout.",
        "genere_le": datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds"),
        "second_tour_a_verifier": SECOND_TOUR,
        "evenements": evts,
    }
    (RACINE / "modele" / "evenements.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=1), "utf-8")
    n_ok = sum(e["source_accessible"] for e in evts)
    print(f"{len(evts)} questions d'événement ({len({e['evenement'] for e in evts})} événements), {n_ok} résolubles, {len(evts) - n_ok} non émises (source inaccessible)")
