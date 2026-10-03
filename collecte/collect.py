"""Collecte automatique des données ouvertes pour Psychohistoire.

Exécuté chaque nuit par GitHub Actions. Aucun appel à un modèle de langage :
le script interroge des API publiques et écrit data/collecte.json.
Chaque source est isolée : l'échec de l'une n'empêche pas les autres.
"""
import csv
import io
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "collecte.json"
UA = {"User-Agent": "psychohistoire-collecte/1.0 (+https://github.com/Beynat/psychohistoire)"}


def get(url, timeout=40, essais=2):
    for n in range(essais):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8")
        except Exception:
            if n == essais - 1:
                raise


def inflation_fr():
    """Eurostat a fait évoluer ses jeux HICP en 2026 : on garde la série la plus récente des candidats."""
    best = []
    for ds, p in [("prc_hicp_minr", {"geo": "FR", "unit": "RCH_A", "coicop18": "TOTAL"}),
                  ("prc_hicp_minr", {"geo": "FR", "unit": "RCH_A", "coicop": "CP00"}),
                  ("prc_hicp_manr", {"geo": "FR", "unit": "RCH_A", "coicop": "CP00"})]:
        try:
            s = eurostat_last(ds, p)
        except Exception:
            continue
        if s and (not best or s[-1][0] > best[-1][0]):
            best = s
    return best[-12:]


def eurostat_last(dataset, params):
    """Renvoie la série (période, valeur) d'un jeu Eurostat filtré sur une seule série."""
    q = urllib.parse.urlencode({**params, "format": "JSON", "lang": "FR"})
    j = json.loads(get(f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}?{q}"))
    time_index = j["dimension"]["time"]["category"]["index"]  # période -> position
    vals = j["value"]  # position (str) -> valeur
    serie = sorted(((p, vals[str(i)]) for p, i in time_index.items() if str(i) in vals), key=lambda x: x[0])
    return serie


def ecb_series(key, n=24):
    txt = get(f"https://data-api.ecb.europa.eu/service/data/{key}?format=csvdata&lastNObservations={n}")
    rows = list(csv.DictReader(io.StringIO(txt)))
    return [(r["TIME_PERIOD"], float(r["OBS_VALUE"])) for r in rows if r.get("OBS_VALUE")]


def polymarket(query):
    q = urllib.parse.urlencode({"q": query, "limit_per_type": 10})
    j = json.loads(get(f"https://gamma-api.polymarket.com/public-search?{q}"))
    out = []
    for ev in j.get("events", []) or []:
        for m in ev.get("markets", []) or []:
            if m.get("closed"):
                continue
            try:
                prices = json.loads(m.get("outcomePrices") or "[]")
                outcomes = json.loads(m.get("outcomes") or "[]")
            except (TypeError, ValueError):
                prices, outcomes = [], []
            out.append({
                "evenement": ev.get("title"),
                "marche": m.get("question"),
                "issues": dict(zip(outcomes, [round(float(p) * 100, 1) for p in prices])),
                "volume": m.get("volume"),
                "url": f"https://polymarket.com/event/{ev.get('slug')}",
            })
    return out[:15]


SOURCES = {
    "dette_trimestrielle_FR": {
        "nom": "Dette publique, % du PIB (trimestrielle)",
        "lie": "SI-01-01",
        "source": "Eurostat gov_10q_ggdebt",
        "fn": lambda: eurostat_last("gov_10q_ggdebt", {"geo": "FR", "unit": "PC_GDP", "sector": "S13", "na_item": "GD"})[-8:],
    },
    "taux_long_FR": {
        "nom": "Taux à long terme France (mensuel, critère de Maastricht)",
        "lie": "SI-01-05",
        "source": "BCE IRS.M.FR.L.L40.CI.0000.EUR.N.Z",
        "fn": lambda: ecb_series("IRS/M.FR.L.L40.CI.0000.EUR.N.Z"),
    },
    "taux_long_DE": {
        "nom": "Taux à long terme Allemagne (mensuel)",
        "lie": "SI-01-04",
        "source": "BCE IRS.M.DE.L.L40.CI.0000.EUR.N.Z",
        "fn": lambda: ecb_series("IRS/M.DE.L.L40.CI.0000.EUR.N.Z"),
    },
    "inflation_FR": {
        "nom": "Inflation harmonisée France, glissement annuel",
        "lie": None,
        "source": "Eurostat HICP (jeu le plus récent disponible)",
        "fn": inflation_fr,
    },
    "taux_depot_BCE": {
        "nom": "Taux de la facilité de dépôt de la BCE",
        "lie": None,
        "source": "BCE FM.D.U2.EUR.4F.KR.DFR.LEV",
        "fn": lambda: ecb_series("FM/D.U2.EUR.4F.KR.DFR.LEV", n=5),
    },
    "polymarket_presidentielle": {
        "nom": "Marchés de prédiction : présidentielle française",
        "lie": "Q-PV02-A",
        "source": "Polymarket (API publique)",
        "fn": lambda: polymarket("France presidential election 2027"),
    },
}


def main():
    previous = {}
    if OUT.exists():
        try:
            previous = json.loads(OUT.read_text("utf-8")).get("series", {})
        except ValueError:
            previous = {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = {"execution": now, "series": {}}
    ok = 0
    for key, meta in SOURCES.items():
        entry = {k: v for k, v in meta.items() if k != "fn"}
        try:
            data = meta["fn"]()
            if not data:
                raise ValueError("réponse vide")
            entry.update({"statut": "ok", "maj": now, "donnees": data})
            ok += 1
        except Exception as exc:  # une source en échec garde ses dernières données connues
            old = previous.get(key, {})
            entry.update({"statut": "echec", "erreur": f"{type(exc).__name__}: {exc}"[:300],
                          "maj": old.get("maj"), "donnees": old.get("donnees")})
        result["series"][key] = entry

    fr, de = result["series"]["taux_long_FR"].get("donnees"), result["series"]["taux_long_DE"].get("donnees")
    if fr and de:
        d = dict(de)
        result["series"]["ecart_FR_DE_mensuel"] = {
            "nom": "Écart de taux longs France – Allemagne (mensuel, pb)", "lie": "SI-01-04",
            "source": "Calcul à partir des séries BCE", "statut": "ok", "maj": now,
            "donnees": [(p, round((v - d[p]) * 100)) for p, v in fr if p in d],
        }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), "utf-8")
    print(f"{ok}/{len(SOURCES)} sources à jour")
    for k, v in result["series"].items():
        print(f"- {k}: {v['statut']}" + (f" ({v.get('erreur')})" if v["statut"] != "ok" else ""))
    return 0 if ok else 1



# --- Veille d'actualité (protocole v1.3, section 10.2) : titres seulement, sans IA ---
VEILLE = Path(__file__).resolve().parent.parent / "data" / "veille.json"
FLUX = {
    "franceinfo · politique": "https://www.francetvinfo.fr/politique.rss",
    "franceinfo · économie": "https://www.francetvinfo.fr/economie.rss",
    "franceinfo · société": "https://www.francetvinfo.fr/societe.rss",
    "Le Monde · politique": "https://www.lemonde.fr/politique/rss_full.xml",
    "Le Monde · économie": "https://www.lemonde.fr/economie/rss_full.xml",
}


def veille(jours=10, maxi=400):
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime
    old = []
    if VEILLE.exists():
        try:
            old = json.loads(VEILLE.read_text("utf-8")).get("items", [])
        except ValueError:
            old = []
    vus = {i["lien"] for i in old}
    statut, neufs = {}, []
    for nom, url in FLUX.items():
        try:
            root = ET.fromstring(get(url).encode("utf-8"))
            n = 0
            for it in root.iter("item"):
                lien = (it.findtext("link") or "").strip()
                if not lien or lien in vus:
                    continue
                try:
                    date = parsedate_to_datetime(it.findtext("pubDate")).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
                except Exception:
                    date = None
                neufs.append({"source": nom, "titre": (it.findtext("title") or "").strip(), "lien": lien,
                              "date": date, "trie": False})
                vus.add(lien)
                n += 1
            statut[nom] = f"ok ({n} nouveaux)"
        except Exception as exc:
            statut[nom] = f"echec: {type(exc).__name__}"
    limite = datetime.now(timezone.utc).timestamp() - jours * 86400
    def recent(i):
        try:
            return datetime.strptime(i["date"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc).timestamp() >= limite
        except Exception:
            return True
    items = sorted([i for i in old + neufs if recent(i) or not i.get("trie")],
                   key=lambda i: i.get("date") or "", reverse=True)[:maxi]
    VEILLE.write_text(json.dumps({"execution": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                  "flux": statut, "items": items}, ensure_ascii=False, indent=1), "utf-8")
    print("veille:", statut)


if __name__ == "__main__":
    code = main()
    try:
        veille()
    except Exception as exc:
        print("veille en échec:", exc)
    sys.exit(code)
