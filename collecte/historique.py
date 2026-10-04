"""Historique long des séries d'état pour Psychohistoire (sans IA, bibliothèque standard).

Écrit data/historique/<serie>.csv (colonnes periode,valeur). Chaque série est isolée :
l'échec de l'une n'empêche pas les autres. Rapport final : points, première et dernière période.

Sources (toutes publiques, sans clé) :
- BCE, jeu IRS (taux à long terme pour la convergence, mensuel) ;
- Eurostat (HICP, dette trimestrielle, PIB, chômage) ;
- Bundesbank, série BBSIS (courbe des taux Svensson, 10 ans, journalière) : côté allemand seulement.

Écart OAT-Bund journalier : aucune source primaire gratuite sans clé n'a été trouvée pour la jambe
française (voir ecart_journalier_source()). Le script ne fabrique donc aucune série journalière d'écart.
"""
import csv
import io
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "data" / "historique"
UA = {"User-Agent": "psychohistoire-collecte/1.0 (+https://github.com/Beynat/psychohistoire)"}
EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def get(url, timeout=90, essais=3):
    for n in range(essais):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8-sig")
        except Exception:
            if n == essais - 1:
                raise


def eurostat(dataset, params):
    """Série complète (période, valeur), triée, pour un jeu Eurostat filtré sur une seule série."""
    q = urllib.parse.urlencode({**params, "format": "JSON", "lang": "EN"})
    j = json.loads(get(f"{EUROSTAT}/{dataset}?{q}"))
    if "error" in j:
        raise ValueError(str(j["error"])[:200])
    idx = j["dimension"]["time"]["category"]["index"]
    vals = j["value"]
    return sorted((p, float(vals[str(i)])) for p, i in idx.items() if str(i) in vals)


def bce(cle, debut="1990-01"):
    txt = get(f"https://data-api.ecb.europa.eu/service/data/{cle}?format=csvdata&startPeriod={debut}")
    rows = csv.DictReader(io.StringIO(txt))
    return sorted((r["TIME_PERIOD"], float(r["OBS_VALUE"])) for r in rows if r.get("OBS_VALUE"))


# --- Séries ---------------------------------------------------------------

def taux_fr():
    return bce("IRS/M.FR.L.L40.CI.0000.EUR.N.Z")


def taux_de():
    return bce("IRS/M.DE.L.L40.CI.0000.EUR.N.Z")


def inflation_fr():
    """Eurostat a changé de nomenclature (COICOP 2018) : on prend le jeu le plus récent, complété par l'ancien."""
    candidats = [("prc_hicp_minr", {"geo": "FR", "unit": "RCH_A", "coicop18": "TOTAL"}),
                 ("prc_hicp_manr", {"geo": "FR", "unit": "RCH_A", "coicop": "CP00"})]
    series = []
    for ds, p in candidats:
        try:
            series.append(eurostat(ds, p))
        except Exception:
            continue
    if not series:
        raise ValueError("aucun jeu HICP disponible")
    series.sort(key=lambda s: s[-1][0], reverse=True)
    fusion = {}
    for s in reversed(series):  # le plus récent écrase
        fusion.update(dict(s))
    return sorted(fusion.items())


def dette_fr():
    return eurostat("gov_10q_ggdebt", {"geo": "FR", "unit": "PC_GDP", "sector": "S13", "na_item": "GD"})


def pib_fr():
    """Variation trimestrielle du PIB en volume (chaînée, CVS-CJO), en %."""
    return eurostat("namq_10_gdp", {"geo": "FR", "unit": "CLV_PCH_PRE", "s_adj": "SCA", "na_item": "B1GQ"})


def pib_fr_ga():
    """Glissement annuel du PIB en volume (CVS-CJO), en %."""
    return eurostat("namq_10_gdp", {"geo": "FR", "unit": "CLV_PCH_SM", "s_adj": "SCA", "na_item": "B1GQ"})


def chomage_fr():
    return eurostat("une_rt_m", {"geo": "FR", "unit": "PC_ACT", "s_adj": "SA", "age": "TOTAL", "sex": "T"})


def bund_journalier():
    """Rendement 10 ans de la courbe Svensson des titres fédéraux (Bundesbank), journalier depuis 2010.
    Ce n'est pas le Bund benchmark coté mais une courbe lissée : à ne comparer qu'avec une jambe française de même nature."""
    cle = "BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A"
    txt = get(f"https://api.statistiken.bundesbank.de/rest/data/{cle}?format=csv&startPeriod=2010-01-01")
    out = []
    for ligne in txt.splitlines():
        c = ligne.split(";")
        if len(c) >= 2 and len(c[0]) == 10 and c[0][4] == "-" and c[1] not in (".", ""):
            out.append((c[0], float(c[1].replace(",", "."))))
    return sorted(out)


def ecart_journalier_source():
    """Cherche une jambe française journalière gratuite sans clé. Lève une exception documentant l'échec.
    Sondé le 2026-10-04 : Webstat (explore v2.1) expose les métadonnées du TEC10 mais aucune observation ;
    la nouvelle API Webstat répond 401 sans identifiants ; l'AFT est protégé par Cloudflare ;
    Eurostat irt_lt_mcby_d est indisponible ; la courbe BCE (YC) est celle de la zone euro, pas de la France."""
    base = "https://webstat.banque-france.fr/api/explore/v2.1/catalog/datasets/fm-d-fr-eur-fr2-mr-frfelt_tec10_005-idx"
    meta = json.loads(get(base))
    if meta.get("has_records"):
        raise NotImplementedError("Webstat expose maintenant des observations : le schéma est à câbler")
    raise ValueError("Webstat : jeu TEC10 sans observations (has_records=false) ; API officielle sous identifiants ; aucune jambe OAT journalière sans clé")


SERIES = {
    "taux_10a_FR": taux_fr,
    "taux_10a_DE": taux_de,
    "inflation_ipch_FR": inflation_fr,
    "dette_pib_FR": dette_fr,
    "pib_croissance_trim_FR": pib_fr,
    "pib_croissance_ga_FR": pib_fr_ga,
    "chomage_FR": chomage_fr,
    "bund_10a_journalier_DE": bund_journalier,
}


def ecrire(nom, serie):
    SORTIE.mkdir(parents=True, exist_ok=True)
    with open(SORTIE / f"{nom}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["periode", "valeur"])
        w.writerows(serie)


def main():
    rapport, obtenues = [], {}
    for nom, fn in SERIES.items():
        try:
            s = fn()
            if not s:
                raise ValueError("série vide")
            ecrire(nom, s)
            obtenues[nom] = s
            rapport.append((nom, "ok", len(s), s[0][0], s[-1][0], ""))
        except Exception as exc:
            rapport.append((nom, "echec", 0, "", "", f"{type(exc).__name__}: {exc}"[:250]))

    # Écart FR-DE mensuel en points de base, calculé sur les périodes communes
    try:
        de = dict(obtenues["taux_10a_DE"])
        ecart = [(p, round((v - de[p]) * 100)) for p, v in obtenues["taux_10a_FR"] if p in de]
        if not ecart:
            raise ValueError("aucune période commune")
        ecrire("ecart_FR_DE_pb", ecart)
        rapport.append(("ecart_FR_DE_pb", "ok", len(ecart), ecart[0][0], ecart[-1][0], ""))
    except Exception as exc:
        rapport.append(("ecart_FR_DE_pb", "echec", 0, "", "", f"{type(exc).__name__}: {exc}"[:250]))

    try:
        ecart_journalier_source()
        rapport.append(("ecart_OAT_Bund_journalier", "ok", 0, "", "", ""))
    except Exception as exc:
        rapport.append(("ecart_OAT_Bund_journalier", "indisponible", 0, "", "", f"{type(exc).__name__}: {exc}"[:250]))

    for nom, st, n, a, b, err in rapport:
        print(f"{nom}: {st}" + (f" | {n} points, {a} -> {b}" if st == "ok" and n else "") + (f" | {err}" if err else ""))
    # Le code de sortie ne signale que les séries qui doivent exister ; l'écart journalier est attendu indisponible.
    return 0 if all(st == "ok" for nom, st, *_ in rapport if nom != "ecart_OAT_Bund_journalier") else 1


if __name__ == "__main__":
    sys.exit(main())
