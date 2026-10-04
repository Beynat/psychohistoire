"""Séries quotidiennes de la Banque de France (Webstat), avec la clé WEBSTAT_KEY (secret GitHub).

Sans IA, bibliothèque standard. La clé n'est jamais écrite ni affichée.
- OAT : « Taux de l'Echéance Constante - 10 ans » (TEC 10), quotidien, jeu
  fm-d-fr-eur-fr2-bb-frmoytec10-hsta → data/historique/oat_tec10_journalier_FR.csv
- Écart quotidien France-Allemagne en points de base : TEC 10 moins le taux allemand à 10 ans de la
  Bundesbank (courbe Svensson, data/historique/bund_10a_journalier_DE.csv), aux dates communes →
  data/historique/ecart_FR_DE_journalier_pb.csv. Les deux instruments diffèrent légèrement (taux
  à échéance constante contre courbe ajustée) : cet écart sert à caler les seuils et au modèle de
  la phase 2 ; les questions restent résolues sur la série mensuelle de la BCE.
"""
import csv
import io
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
HISTO = RACINE / "data" / "historique"
BASE = "https://webstat.banque-france.fr/api/explore/v2.1/catalog/datasets"
TEC10 = "fm-d-fr-eur-fr2-bb-frmoytec10-hsta"


def telecharger(dataset, cle):
    url = f"{BASE}/{dataset}/exports/json?" + urllib.parse.urlencode({"limit": -1})
    req = urllib.request.Request(url, headers={"Authorization": f"Apikey {cle}",
                                               "User-Agent": "psychohistoire-collecte/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def champs(lignes):
    """Repère le champ de date et le champ de valeur, quelle que soit leur casse."""
    cles = list(lignes[0].keys())
    date = next(k for k in cles if any(m in k.lower() for m in ("time_period", "date", "period")))
    valeur = next(k for k in cles if any(m in k.lower() for m in ("obs_value", "value", "valeur")) and k != date)
    return date, valeur, cles


def ecrire(nom, points):
    with (HISTO / f"{nom}.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["periode", "valeur"])
        w.writerows(points)


def main():
    cle = os.environ.get("WEBSTAT_KEY", "").strip()
    if not cle:
        print("WEBSTAT_KEY absent : série quotidienne de l'OAT non collectée.")
        return 0
    try:
        lignes = telecharger(TEC10, cle)
    except Exception as exc:
        print(f"Webstat en échec : {type(exc).__name__} {getattr(exc, 'code', '')}")
        return 0
    if not lignes:
        print("Webstat : aucune observation renvoyée.")
        return 0
    d, v, cles = champs(lignes)
    print(f"Webstat : {len(lignes)} lignes, champs {cles}, date = {d}, valeur = {v}")
    oat = sorted((str(l[d])[:10], float(l[v])) for l in lignes if l.get(v) not in (None, "", "NaN"))
    oat = [(p, x) for p, x in oat if p >= "2010-01-01"]
    ecrire("oat_tec10_journalier_FR", oat)
    print(f"OAT TEC 10 : {len(oat)} points, de {oat[0][0]} à {oat[-1][0]}, dernière valeur {oat[-1][1]}")
    bund_f = HISTO / "bund_10a_journalier_DE.csv"
    if bund_f.exists():
        bund = {r["periode"][:10]: float(r["valeur"]) for r in csv.DictReader(bund_f.open(encoding="utf-8")) if r["valeur"]}
        ecart = [(p, round((x - bund[p]) * 100, 1)) for p, x in oat if p in bund]
        ecrire("ecart_FR_DE_journalier_pb", ecart)
        print(f"Écart quotidien : {len(ecart)} points, dernier {ecart[-1] if ecart else None}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
