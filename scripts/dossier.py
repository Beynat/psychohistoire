"""Dossier de données gelées remis aux prévisionnistes de l'ensemble direct (consigne v1.2).

Usage : python scripts/dossier.py ETIQUETTE [sortie.json]
Lit data/cycles/<ETIQUETTE>/gel/historique/*.csv et data/cycles/<ETIQUETTE>/questions.json.
Écrit data/cycles/<ETIQUETTE>/dossier.json (dernière valeur et valeurs 1, 3 et 12 mois plus tôt
pour chaque série) et, si une sortie est donnée, le fichier remis aux prévisionnistes : la liste
des questions (identifiant, texte, issues, échéance, critère) et le dossier. Rien d'autre : ni
prévision du projet, ni comparateur, ni cote.
"""
import csv
import sys
from datetime import date, timedelta

from commun import RACINE, ecrire_json, lire_json

LIBELLES = {
    "taux_10a_FR": ("Taux souverain 10 ans France, moyenne mensuelle (BCE)", "%"),
    "taux_10a_DE": ("Taux souverain 10 ans Allemagne, moyenne mensuelle (BCE)", "%"),
    "ecart_FR_DE_pb": ("Écart de taux 10 ans France-Allemagne, moyenne mensuelle (BCE)", "pb"),
    "ecart_FR_DE_journalier_pb": ("Écart de taux 10 ans France-Allemagne, quotidien (TEC 10 Banque de France moins Bund Bundesbank ; environ 9 pb sous la série BCE)", "pb"),
    "oat_tec10_journalier_FR": ("Taux de l'État à échéance constante 10 ans, quotidien (Banque de France)", "%"),
    "bund_10a_journalier_DE": ("Taux allemand 10 ans, quotidien (Bundesbank, courbe Svensson)", "%"),
    "inflation_ipch_FR": ("Inflation IPCH France sur un an", "%"),
    "chomage_FR": ("Taux de chômage France, mensuel CVS (Eurostat)", "%"),
    "dette_pib_FR": ("Dette publique France, % du PIB, trimestrielle", "%"),
    "pib_croissance_trim_FR": ("Croissance du PIB réel France sur un trimestre", "%"),
    "pib_croissance_ga_FR": ("Croissance du PIB réel France sur un an", "%"),
    "webstat_defaillances_12m_FR": ("Défaillances d'entreprises cumulées sur 12 mois, France", "nombre"),
    "webstat_climat_affaires_industrie": ("Climat des affaires, industrie manufacturière (Banque de France)", "indice"),
    "webstat_climat_affaires_services": ("Climat des affaires, services marchands (Banque de France)", "indice"),
    "webstat_teg_credit_habitat": ("Taux effectif global des nouveaux crédits à l'habitat", "%"),
    "webstat_oat_tec2_journalier": ("Taux de l'État à échéance constante 2 ans, quotidien", "%"),
    "webstat_oat_tec30_journalier": ("Taux de l'État à échéance constante 30 ans, quotidien", "%"),
    "webstat_pente_FR_2_10_pb": ("Pente de la courbe française 10 ans moins 2 ans, quotidienne", "pb"),
    "webstat_taux_10a_IT_mensuel": ("Taux 10 ans Italie, mensuel (Banque de France)", "%"),
    "webstat_taux_10a_DE_mensuel": ("Taux 10 ans Allemagne, mensuel (Banque de France)", "%"),
    "webstat_ecart_IT_DE_pb": ("Écart de taux 10 ans Italie-Allemagne, mensuel", "pb"),
    "webstat_eur_usd_journalier": ("Cours de l'euro en dollars, quotidien", "USD"),
    "brent_journalier": ("Prix spot du Brent, quotidien (EIA)", "$/baril"),
    "brent_mensuel": ("Prix spot du Brent, moyenne mensuelle (EIA)", "$/baril"),
    "inflation_energie_FR": ("Inflation IPCH énergie, France, sur un an (Eurostat)", "%"),
    "confiance_menages_FR": ("Indicateur synthétique de confiance des ménages (Insee, CVS)", "points"),
}


def date_de(p):
    if len(p) == 10:
        return date.fromisoformat(p)
    if "Q" in p:
        a, q = p.split("-Q")
        return date(int(a), 3 * int(q), 1)
    return date(int(p[:4]), int(p[5:7]), 1)


def avant(points, d, jours):
    cible = d - timedelta(days=jours)
    prec = [(p, v) for p, v in points if date_de(p) <= cible]
    return prec[-1] if prec else None


def construire(etiquette):
    dossier_gel = RACINE / "data" / "cycles" / etiquette / "gel" / "historique"
    series = []
    for f in sorted(dossier_gel.glob("*.csv")):
        nom = f.stem
        with f.open(encoding="utf-8") as h:
            pts = [(r["periode"], float(r["valeur"])) for r in csv.DictReader(h) if r["valeur"]]
        if not pts:
            continue
        lib, unite = LIBELLES.get(nom, (nom, ""))
        p, v = pts[-1]
        d = date_de(p)
        series.append({"serie": nom, "libelle": lib, "unite": unite, "derniere": {"periode": p, "valeur": v},
                       **{f"il_y_a_{k}": (lambda x: {"periode": x[0], "valeur": x[1]} if x else None)(avant(pts, d, j))
                          for k, j in (("1_mois", 30), ("3_mois", 91), ("12_mois", 365))}})
    manifeste = lire_json(f"data/cycles/{etiquette}/gel/manifeste.json")
    return {"cycle": etiquette, "gel": manifeste["date_gel"], "series": series,
            "note": "Données gelées du cycle, collectées sans IA. Les questions sur des séries se résolvent sur la série citée dans le texte de la question."}


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("usage : python scripts/dossier.py ETIQUETTE [sortie.json]")
    et = sys.argv[1]
    dos = construire(et)
    ecrire_json(f"data/cycles/{et}/dossier.json", dos)
    if len(sys.argv) == 3:
        banque = lire_json(f"data/cycles/{et}/questions.json")
        # Identifiants anonymisés (relecture 12, S7) : l'identifiant d'une question de variable contient
        # le quantile du seuil, dont on déduirait la probabilité du comparateur de persistance.
        # Ordre mélangé par une graine dérivée de l'étiquette du cycle, donc reproductible et journalisée : l'ordre
        # de la banque (trois seuils croissants d'une même série) révélerait le seuil médian (relecture 19, S5).
        import random
        ordre = list(banque["questions"])
        random.Random(f"psychohistoire-{et}").shuffle(ordre)
        anon = {f"Q{k + 1:03d}": q["id"] for k, q in enumerate(ordre)}
        reel = {v: k for k, v in anon.items()}
        ecrire_json(f"data/cycles/{et}/anonymisation.json", {"description": "Identifiant remis aux prévisionnistes → identifiant de la banque (relecture 12, S7) ; ordre mélangé, graine « psychohistoire-<étiquette> » (relecture 19, S5).", "correspondance": anon})
        qs = [{"id": reel[q["id"]], **{k: q[k] for k in ("texte", "issues", "echeance")}} | (
            {"critere": q["details"]["critere"]} if q["type"] in ("evenement", "conjointe") else {}) for q in ordre]
        import json
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            json.dump({"gel": dos["gel"], "questions": qs, "dossier_de_donnees": dos["series"]}, f, ensure_ascii=False, indent=1)
    print(f"Dossier du cycle {et} : {len(dos['series'])} séries" + (f" ; fichier des prévisionnistes : {sys.argv[2]}" if len(sys.argv) == 3 else ""))
