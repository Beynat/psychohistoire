"""Séries quotidiennes de la Banque de France (Webstat), avec la clé WEBSTAT_KEY (secret GitHub).

Sans IA, bibliothèque standard. La clé n'est jamais écrite ni affichée.
- OAT : « Taux de l'Echéance Constante - 10 ans » (TEC 10), quotidien, série
  FM.D.FR.EUR.FR2.BB.FRMOYTEC10.HSTA du jeu « observations » (visible avec une clé)
  → data/historique/oat_tec10_journalier_FR.csv
- Écart quotidien France-Allemagne en points de base : TEC 10 moins le taux allemand à 10 ans de la
  Bundesbank (courbe Svensson, data/historique/bund_10a_journalier_DE.csv), aux dates communes →
  data/historique/ecart_FR_DE_journalier_pb.csv. Les deux instruments diffèrent légèrement (taux
  à échéance constante contre courbe ajustée) : cet écart sert à caler les seuils et au modèle de
  la phase 2 ; les questions restent résolues sur la série mensuelle de la BCE.
- Séries complémentaires (SERIES ci-dessous), écrites dans data/historique/webstat_<nom>.csv, et
  deux séries dérivées : pente de la courbe française 2-10 ans (pb, quotidienne) et écart de taux
  Italie-Allemagne à 10 ans (pb, mensuel). Elles alimentent le dossier de données des
  prévisionnistes et, plus tard, le réseau de la phase 3 ; elles ne créent pas de question (gel).
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
TEC10 = "FM.D.FR.EUR.FR2.BB.FRMOYTEC10.HSTA"
# nom → (identifiant de jeu Webstat, libellé, unité). La clé de série est l'identifiant en majuscules,
# tirets remplacés par des points.
SERIES = {
    "defaillances_12m_FR": ("diren-m-fr-de-ul-df-03-n-zz-tt", "Défaillances d'entreprises cumulées sur 12 mois, France, brut", "nombre"),
    "climat_affaires_industrie": ("conj-m-n01-s-in-000cz-ica00000-10", "Climat des affaires, industrie manufacturière (Banque de France, CVS)", "indice"),
    "climat_affaires_services": ("conj-m-n01-s-sm-00nat-ica00000-10", "Climat des affaires, services marchands (Banque de France, CVS)", "indice"),
    "teg_credit_habitat": ("mir-m-fr-b-a2c-a-c-a-2250-eur-n", "Taux effectif global des nouveaux crédits à l'habitat aux ménages", "%"),
    "oat_tec2_journalier": ("fm-d-fr-eur-fr2-bb-frmoytec2-hsta", "Taux de l'État à échéance constante 2 ans", "%"),
    "oat_tec30_journalier": ("fm-d-fr-eur-fr2-bb-frmoytec30-hsta", "Taux de l'État à échéance constante 30 ans", "%"),
    "taux_10a_IT_mensuel": ("fm-m-it-eur-fr2-bb-it10yt_rr-yld", "Taux de l'emprunt phare à 10 ans, Italie", "%"),
    "taux_10a_DE_mensuel": ("fm-m-de-eur-fr2-bb-de10yt_rr-yld", "Taux de l'emprunt phare à 10 ans, Allemagne", "%"),
    "eur_usd_journalier": ("exr-d-usd-eur-sp00-a", "Cours de l'euro en dollars", "USD"),
}


def cle_serie(dataset):
    return dataset.upper().replace("-", ".")


def telecharger(serie, cle):
    url = f"{BASE}/observations/exports/json?" + urllib.parse.urlencode(
        {"where": f'series_key="{serie}"', "select": "time_period,obs_value", "order_by": "time_period", "limit": -1})
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
    obtenues = {"oat_tec10_journalier_FR": oat}
    for nom, (ds, _lib, _u) in SERIES.items():
        try:
            l2 = telecharger(cle_serie(ds), cle)
            pts = sorted((str(x["time_period"]), float(x["obs_value"])) for x in l2 if x.get("obs_value") not in (None, "", "NaN"))
            pts = [(p, x) for p, x in pts if p >= "2010"]
            if not pts:
                raise ValueError("aucune observation")
            ecrire(f"webstat_{nom}", pts)
            obtenues[nom] = pts
            print(f"{nom} : {len(pts)} points, de {pts[0][0]} à {pts[-1][0]}, dernière valeur {pts[-1][1]}")
        except Exception as exc:
            print(f"{nom} : échec ({type(exc).__name__})")
    if "oat_tec2_journalier" in obtenues:
        d2 = dict(obtenues["oat_tec2_journalier"])
        pente = [(p, round((x - d2[p]) * 100, 1)) for p, x in oat if p in d2]
        ecrire("webstat_pente_FR_2_10_pb", pente)
        print(f"pente 2-10 ans : {len(pente)} points, dernière {pente[-1] if pente else None}")
    if "taux_10a_IT_mensuel" in obtenues and "taux_10a_DE_mensuel" in obtenues:
        de = dict(obtenues["taux_10a_DE_mensuel"])
        it = [(p, round((x - de[p]) * 100, 1)) for p, x in obtenues["taux_10a_IT_mensuel"] if p in de]
        ecrire("webstat_ecart_IT_DE_pb", it)
        print(f"écart Italie-Allemagne : {len(it)} points, dernier {it[-1] if it else None}")
    bund_f = HISTO / "bund_10a_journalier_DE.csv"
    if bund_f.exists():
        bund = {r["periode"][:10]: float(r["valeur"]) for r in csv.DictReader(bund_f.open(encoding="utf-8")) if r["valeur"]}
        ecart = [(p, round((x - bund[p]) * 100, 1)) for p, x in oat if p in bund]
        ecrire("ecart_FR_DE_journalier_pb", ecart)
        print(f"Écart quotidien : {len(ecart)} points, dernier {ecart[-1] if ecart else None}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
