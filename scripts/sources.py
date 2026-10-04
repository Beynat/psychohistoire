"""Indicateur de fiabilité des sources (méthode : modele/sources.md).

Usage :
    python scripts/sources.py FICHIER [FICHIER ...]
        Relève les adresses citées (texte, Markdown ou JSON), classe chaque domaine selon
        modele/sources.json et affiche, par fichier : nombre de sources, répartition par catégorie,
        part des sources de rang 1 à 3 (PO, I, MR), score moyen (poids de la catégorie), domaines
        non classés et classements provisoires.
    python scripts/sources.py --classer URL
        Affiche la catégorie d'une adresse et le motif.
"""
import json
import re
import sys
from collections import Counter
from urllib.parse import urlparse

from commun import lire_json

URL = re.compile(r"https?://[^\s)\]>\"'`]+")


def charger():
    return lire_json("modele/sources.json")


def domaine(url):
    return urlparse(url).netloc.lower().split(":")[0].removeprefix("www.")


def classer(url, ref=None):
    ref = ref or charger()
    h = domaine(url)
    if h in ref["domaines"]:
        d = ref["domaines"][h]
        return d["cat"], d["motif"], bool(d.get("a_verifier")), h
    for s, cat in sorted(ref["suffixes"].items(), key=lambda x: -len(x[0])):
        if h == s or h.endswith("." + s):
            return cat, f"règle de suffixe .{s}", False, h
    return "X", "domaine non classé", False, h


def indicateur(texte, ref=None):
    ref = ref or charger()
    urls = sorted(set(u.rstrip(".,;") for u in URL.findall(texte)))
    cl = [classer(u, ref) for u in urls]
    rep = Counter(c[0] for c in cl)
    n = len(cl)
    fiables = sum(rep[k] for k in ("PO", "I", "MR"))
    return {
        "sources": n,
        "repartition": dict(sorted(rep.items(), key=lambda x: ref["categories"][x[0]]["rang"])),
        "part_rang_1_3": round(fiables / n, 2) if n else None,
        "score": round(sum(ref["categories"][c[0]]["poids"] for c in cl) / n, 2) if n else None,
        "non_classes": sorted({c[3] for c in cl if c[0] == "X"}),
        "provisoires": sorted({c[3] for c in cl if c[2]}),
    }


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--classer":
        cat, motif, prov, h = classer(sys.argv[2])
        print(f"{h} : {cat} ({charger()['categories'][cat]['nom']}) — {motif}" + (" [provisoire]" if prov else ""))
    elif len(sys.argv) >= 2:
        for f in sys.argv[1:]:
            with open(f, encoding="utf-8") as h:
                r = indicateur(h.read())
            print(f"{f} : {json.dumps(r, ensure_ascii=False)}")
    else:
        sys.exit(__doc__)
