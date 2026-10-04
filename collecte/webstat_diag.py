"""Diagnostic de l'accès Webstat avec WEBSTAT_KEY (n'affiche jamais la clé)."""
import json
import os
import urllib.parse
import urllib.request

K = os.environ.get("WEBSTAT_KEY", "").strip()
B = "https://webstat.banque-france.fr/api/explore/v2.1"
D = "fm-d-fr-eur-fr2-bb-frmoytec10-hsta"


def essai(nom, url, entete=True):
    h = {"User-Agent": "psychohistoire-diag/1.0"}
    if entete:
        h["Authorization"] = f"Apikey {K}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r:
            corps = r.read().decode("utf-8")[:600]
            print(f"[{nom}] HTTP {r.status} : {corps.replace(K, '***') if K else corps}")
    except Exception as e:
        print(f"[{nom}] {type(e).__name__} {getattr(e, 'code', '')} {getattr(e, 'read', lambda: b'')()[:300]!r}")


print("clé présente :", bool(K), "longueur :", len(K))
essai("métadonnées avec clé", f"{B}/catalog/datasets/{D}?select=has_records,metas")
essai("records en-tête", f"{B}/catalog/datasets/{D}/records?limit=3")
essai("records paramètre", f"{B}/catalog/datasets/{D}/records?limit=3&apikey={urllib.parse.quote(K)}", entete=False)
essai("jeux avec données (clé)", f"{B}/catalog/datasets?limit=5&where=has_records%3Dtrue&select=dataset_id,metas.default.title,metas.default.records_count")
essai("recherche observations (clé)", f"{B}/catalog/datasets?limit=5&where=search(%22observations%22)%20and%20has_records%3Dtrue&select=dataset_id")
essai("compte utilisateur", "https://webstat.banque-france.fr/api/explore/v2.1/catalog/facets?facet=publisher")
