"""Diagnostic de l'accès Webstat avec WEBSTAT_KEY (n'affiche jamais la clé)."""
import json
import os
import urllib.parse
import urllib.request

K = os.environ.get("WEBSTAT_KEY", "").strip()
B = "https://webstat.banque-france.fr/api/explore/v2.1/catalog/datasets/observations"


def essai(nom, chemin):
    h = {"User-Agent": "psychohistoire-diag/1.0", "Authorization": f"Apikey {K}"}
    try:
        with urllib.request.urlopen(urllib.request.Request(B + chemin, headers=h), timeout=60) as r:
            print(f"[{nom}] HTTP {r.status} : {r.read().decode('utf-8')[:1500]}")
    except Exception as e:
        print(f"[{nom}] {type(e).__name__} {getattr(e, 'code', '')} {getattr(e, 'read', lambda: b'')()[:300]!r}")


essai("schéma", "?select=fields")
essai("un enregistrement", "/records?limit=1")
q = urllib.parse.quote('series_key="FM.D.FR.EUR.FR2.BB.FRMOYTEC10.HSTA"')
essai("TEC10 par series_key", f"/records?limit=3&where={q}&order_by=time_period%20desc")
q2 = urllib.parse.quote('search("FRMOYTEC10")')
essai("TEC10 par recherche", f"/records?limit=3&where={q2}")
