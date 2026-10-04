"""Relevé des marchés de prédiction pertinents pour la France, 2026-2028 (sans IA, bibliothèque standard).

Écrit data/cotes.json. Sources isolées : l'échec de l'une n'empêche pas l'autre.

Champs d'un marché :
- source, evenement (intitulé de l'événement), question (intitulé du marché), issue (« Yes » : la probabilité
  porte sur cette issue), libelle_issue (ex. nom du candidat ou échéance), theme ;
- probabilite : fraction 0-1 (prix de l'issue « Yes » donné par Gamma, milieu ou dernier échange) ;
- meilleure_offre (bestBid) et meilleure_demande (bestAsk) en fraction 0-1, ecart_offre_demande_pts en points ;
- volume_usd cumulé du marché (pas de l'événement), cloture, url, releve ;
- fiable (protocole 4.5) : true si volume >= 100 000 $ ET écart <= 3 points ; false si l'une des deux
  conditions connues est violée ; null si l'information manque sans qu'aucune condition connue soit violée.
  Le critère « même événement, résolu à un mois près » reste un jugement humain, non testé ici.

Metaculus : l'API exige un jeton. Si la variable d'environnement METACULUS_TOKEN est définie, elle est utilisée ;
sinon la source est notée « inaccessible » et rien n'est inventé.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "cotes.json"
UA = {"User-Agent": "psychohistoire-collecte/1.0 (+https://github.com/Beynat/psychohistoire)"}
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
SEUIL_VOLUME = 100_000
SEUIL_ECART_PTS = 3.0
MAX_APPELS_CLOB = 200

TAGS = ["france", "french-politics", "macron", "french-election", "france-politics"]
REQUETES = ["France presidential election 2027", "French presidential election", "France dissolution National Assembly",
            "France motion of no confidence", "France government", "French prime minister", "France credit rating",
            "France budget", "Macron", "Le Pen", "Bardella", "Lecornu", "France snap election", "France election"]
INCLUSION = re.compile(r"\b(france|french|macron|le[- ]pen|bardella|lecornu|national[- ]rally|elysee|matignon)\b", re.I)
EXCLUSION = re.compile(r"temperature|diesel|weather|counter-strike|\bbo[1-9]\b|tapestry|\bvs\. ", re.I)  # météo, énergie UE, sport, divers
THEMES = [
    ("presidentielle", re.compile(r"presidential|president of france|president of the national rally|nominee|primary|ballot|2nd round|second round|announce a run", re.I)),
    ("dissolution_elections", re.compile(r"dissol|snap|election called|legislative|referendum", re.I)),
    ("censure_gouvernement", re.compile(r"confidence|censure|prime minister|\bpm\b|lecornu|government|cabinet|out as|out by", re.I)),
    ("budget_souverain", re.compile(r"budget|rating|downgrade|moody|fitch|s&p|spread|oat|bund", re.I)),
    ("senat", re.compile(r"senate", re.I)),
]


def get(url, timeout=40, essais=2, headers=None):
    for n in range(essais):
        try:
            req = urllib.request.Request(url, headers={**UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8")
        except Exception:
            if n == essais - 1:
                raise


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def theme(texte):
    for nom, rx in THEMES:
        if rx.search(texte):
            return nom
    return "autre_france"


def fiable(volume, ecart_pts):
    """Règle du protocole 4.5 ; null si l'information manque sans condition violée."""
    if (volume is not None and volume < SEUIL_VOLUME) or (ecart_pts is not None and ecart_pts > SEUIL_ECART_PTS):
        return False
    if volume is None or ecart_pts is None:
        return None
    return True


# --- Polymarket -----------------------------------------------------------

def evenements_polymarket(erreurs):
    """Découverte par étiquettes puis par recherche ; renvoie {id: événement}, actifs et non clos."""
    vus = {}

    def ajouter(ev, via):
        if ev.get("closed") or not ev.get("active", True):
            return
        tags = {t.get("slug") for t in ev.get("tags") or []}
        texte = f"{ev.get('title', '')} {ev.get('slug', '')}"
        if EXCLUSION.search(texte):
            return
        if via == "recherche" and not (INCLUSION.search(texte) or tags & set(TAGS)):
            return
        vus[ev["id"]] = ev

    for tag in TAGS:
        for off in range(0, 400, 100):
            try:
                lot = json.loads(get(f"{GAMMA}/events?" + urllib.parse.urlencode(
                    {"tag_slug": tag, "active": "true", "closed": "false", "limit": 100, "offset": off})))
            except Exception as exc:
                erreurs.append(f"tag {tag}: {type(exc).__name__}: {exc}"[:200])
                break
            for ev in lot:
                ajouter(ev, "tag")
            if len(lot) < 100:
                break
    for q in REQUETES:
        for page in (1, 2, 3):
            try:
                j = json.loads(get(f"{GAMMA}/public-search?" + urllib.parse.urlencode(
                    {"q": q, "limit_per_type": 20, "page": page, "events_status": "active"})))
            except Exception as exc:
                erreurs.append(f"recherche '{q}' p{page}: {type(exc).__name__}: {exc}"[:200])
                break
            for ev in j.get("events") or []:
                ajouter(ev, "recherche")
            if not (j.get("pagination") or {}).get("hasMore"):
                break
    return vus


def carnet_clob(token):
    """Meilleure offre / demande depuis le carnet d'ordres CLOB, ou (None, None)."""
    try:
        b = json.loads(get(f"{CLOB}/book?token_id={token}", timeout=20, essais=1))
    except Exception:
        return None, None
    bids = [num(o.get("price")) for o in b.get("bids") or []]
    asks = [num(o.get("price")) for o in b.get("asks") or []]
    bids, asks = [x for x in bids if x is not None], [x for x in asks if x is not None]
    return (max(bids) if bids else None), (min(asks) if asks else None)


def polymarket(releve):
    erreurs = []
    evs = evenements_polymarket(erreurs)
    marches, appels = [], 0
    for ev in evs.values():
        for m in ev.get("markets") or []:
            if m.get("closed") or m.get("active") is False:
                continue
            try:
                prix = json.loads(m.get("outcomePrices") or "[]")
                issues = json.loads(m.get("outcomes") or "[]")
                tokens = json.loads(m.get("clobTokenIds") or "[]")
            except (TypeError, ValueError):
                continue
            if not prix or not issues:
                continue
            p = num(prix[0])
            bid, ask = num(m.get("bestBid")), num(m.get("bestAsk"))
            source_ecart = "gamma"
            if (bid is None or ask is None) and tokens and m.get("enableOrderBook") and appels < MAX_APPELS_CLOB:
                appels += 1
                bid, ask = carnet_clob(tokens[0])
                source_ecart = "clob"
            ecart = round((ask - bid) * 100, 2) if bid is not None and ask is not None else None
            vol = num(m.get("volumeNum")) if m.get("volumeNum") is not None else num(m.get("volume"))
            texte = f"{ev.get('title', '')} {m.get('question', '')}"
            marches.append({
                "source": "Polymarket",
                "evenement": ev.get("title"),
                "question": m.get("question"),
                "issue": issues[0],
                "libelle_issue": m.get("groupItemTitle") or None,
                "theme": theme(texte),
                "probabilite": p,
                "meilleure_offre": bid,
                "meilleure_demande": ask,
                "ecart_offre_demande_pts": ecart,
                "origine_ecart": source_ecart if ecart is not None else None,
                "volume_usd": vol,
                "cloture": m.get("endDate") or ev.get("endDate"),
                "url": f"https://polymarket.com/event/{ev.get('slug')}",
                "releve": releve,
                "fiable": fiable(vol, ecart),
            })
    marches.sort(key=lambda x: (x["theme"], -(x["volume_usd"] or 0)))
    return marches, {"evenements": len(evs), "appels_clob": appels, "erreurs_partielles": erreurs[:10]}


# --- Metaculus ------------------------------------------------------------

def metaculus(releve):
    jeton = os.environ.get("METACULUS_TOKEN")
    entetes = {"Authorization": f"Token {jeton}"} if jeton else {}
    marches, essais = [], {}
    for requete in ("France presidential", "France election", "French government", "France"):
        url = "https://www.metaculus.com/api/posts/?" + urllib.parse.urlencode(
            {"search": requete, "statuses": "open", "forecast_type": "binary", "limit": 50})
        try:
            j = json.loads(get(url, headers=entetes, essais=1))
        except urllib.error.HTTPError as exc:
            corps = exc.read().decode("utf-8", "replace")[:160]
            essais[requete] = f"HTTP {exc.code}: {corps}"
            if exc.code in (401, 403):
                return [], {"statut": "inaccessible", "jeton_fourni": bool(jeton), "erreur": essais[requete]}
            continue
        for p in j.get("results") or []:
            q = p.get("question") or {}
            titre = p.get("title") or ""
            if not INCLUSION.search(titre):
                continue
            dernier = ((q.get("aggregations") or {}).get("recency_weighted") or {}).get("latest") or {}
            centres = dernier.get("centers") or []
            marches.append({
                "source": "Metaculus", "evenement": titre, "question": titre, "issue": "Yes", "libelle_issue": None,
                "theme": theme(titre), "probabilite": num(centres[0]) if centres else None,
                "meilleure_offre": None, "meilleure_demande": None, "ecart_offre_demande_pts": None,
                "volume_usd": None, "cloture": q.get("scheduled_close_time") or p.get("scheduled_close_time"),
                "url": f"https://www.metaculus.com/questions/{p.get('id')}/", "releve": releve,
                "nb_previsionnistes": p.get("nr_forecasters"), "fiable": None,
            })
    return marches, {"statut": "ok", "jeton_fourni": bool(jeton), "essais": essais}


def main():
    releve = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sortie = {"releve": releve, "sources": {}, "marches": []}
    for nom, fn in (("polymarket", polymarket), ("metaculus", metaculus)):
        try:
            marches, info = fn(releve)
            info.setdefault("statut", "ok")
            info["marches"] = len(marches)
            sortie["sources"][nom] = info
            sortie["marches"] += marches
        except Exception as exc:
            sortie["sources"][nom] = {"statut": "echec", "erreur": f"{type(exc).__name__}: {exc}"[:300], "marches": 0}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(sortie, ensure_ascii=False, indent=1), "utf-8")
    ms = sortie["marches"]
    print(f"{len(ms)} marchés ; fiables: {sum(m['fiable'] is True for m in ms)} ; "
          f"non fiables: {sum(m['fiable'] is False for m in ms)} ; indéterminés: {sum(m['fiable'] is None for m in ms)}")
    for nom, info in sortie["sources"].items():
        print(f"- {nom}: {info.get('statut')} " + json.dumps({k: v for k, v in info.items() if k != 'statut'}, ensure_ascii=False)[:400])
    return 0 if any(i.get("statut") == "ok" and i.get("marches") for i in sortie["sources"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
