"""Outils communs aux scripts de la phase 1 (bibliothèque standard uniquement)."""
import csv
import hashlib
import json
import math
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RACINE = Path(__file__).resolve().parent.parent
PARIS = ZoneInfo("Europe/Paris")

# Variables d'état suivies en phase 1 (noyau, sections 7.1 et 8.1) : série mensuelle collectée,
# libellé, unité, délai habituel de publication en mois après la période.
VARIABLES = {
    "ecart_FR_DE_pb": {"nom": "écart de taux à 10 ans France-Allemagne (moyenne mensuelle, BCE)", "unite": "pb", "delai": 1,
                       "proxy": "ecart_FR_DE_journalier_pb"},
    "inflation_ipch_FR": {"nom": "inflation IPCH France sur un an", "unite": "%", "delai": 1},
    "chomage_FR": {"nom": "taux de chômage France (Eurostat, CVS)", "unite": "%", "delai": 1},
}
# Ancrage quotidien (cycle à blanc) : quand une série mensuelle publiée tard a un équivalent quotidien
# (« proxy »), le niveau de départ est la moyenne des 5 dernières observations quotidiennes, corrigée
# du décalage moyen entre la série mensuelle et la moyenne mensuelle du proxy sur les 12 derniers mois
# communs. Le mois de départ est celui de la dernière observation quotidienne.
HORIZONS = (1, 2, 3)          # mois après le mois du gel
QUANTILES = (20, 50, 80)      # seuils aux quantiles de la marche aléatoire (section 8.1)
HISTO_DEBUT = "2010-01"       # fenêtre d'estimation des variations (section 7.1)


def maintenant():
    return datetime.now(PARIS).isoformat(timespec="seconds")


def lire_json(chemin, defaut=None):
    p = RACINE / chemin
    return json.loads(p.read_text("utf-8")) if p.exists() else defaut


def ecrire_json(chemin, obj):
    p = RACINE / chemin
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), "utf-8")


def lire_jsonl(chemin):
    p = RACINE / chemin
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text("utf-8").splitlines() if l.strip()]


def serie(nom):
    """Série (période 'AAAA-MM', valeur) lue dans data/historique/<nom>.csv."""
    p = RACINE / "data" / "historique" / f"{nom}.csv"
    with p.open(encoding="utf-8") as f:
        return [(r["periode"], float(r["valeur"])) for r in csv.DictReader(f) if r["valeur"] not in ("", None)]


def ancrage_quotidien(mensuelle, quotidienne):
    """Renvoie (mois de départ, niveau estimé, correction) ou None si le proxy est inutilisable."""
    if len(quotidienne) < 30:
        return None
    moy = {}
    for p, v in quotidienne:
        moy.setdefault(p[:7], []).append(v)
    m = dict(mensuelle)
    communs = sorted(k for k in moy if k in m)[-12:]
    if len(communs) < 6:
        return None
    correction = sum(m[k] - sum(moy[k]) / len(moy[k]) for k in communs) / len(communs)
    niveau = sum(v for _, v in quotidienne[-5:]) / 5 + correction
    return quotidienne[-1][0][:7], niveau, correction


def mois_suivant(m, k=1):
    a, mm = int(m[:4]), int(m[5:7]) - 1 + k
    return f"{a + mm // 12:04d}-{mm % 12 + 1:02d}"


def ecart_mois(m1, m2):
    return (int(m2[:4]) - int(m1[:4])) * 12 + int(m2[5:7]) - int(m1[5:7])


def quantile(valeurs, q):
    v = sorted(valeurs)
    if not v:
        raise ValueError("série vide")
    pos = (len(v) - 1) * q / 100
    i, f = int(pos), pos - int(pos)
    return v[i] if i + 1 >= len(v) else v[i] * (1 - f) + v[i + 1] * f


def variations(s, pas, debut=HISTO_DEBUT):
    """Variations sur `pas` mois de la série, depuis `debut` (marche aléatoire empirique)."""
    d = dict(s)
    return [d[mois_suivant(m, pas)] - v for m, v in s if m >= debut and mois_suivant(m, pas) in d]


def proba_au_dessus(base, seuil, var):
    """P(base + variation ≥ seuil) selon la distribution empirique des variations."""
    return sum(1 for x in var if base + x >= seuil) / len(var)


def trimestre(periode):
    """'2026-11' ou '2026-11-15' → '2026-T4'."""
    return f"{periode[:4]}-T{(int(periode[5:7]) - 1) // 3 + 1}"


def empreinte(chemin):
    return hashlib.sha256((RACINE / chemin).read_bytes()).hexdigest()


def jours(d1, d2):
    return (date.fromisoformat(d2[:10]) - date.fromisoformat(d1[:10])).days


def borne(p, lo=0.02, hi=0.98):
    return min(max(p, lo), hi)


def log_score(p, y):
    """Score logarithmique (plus petit = meilleur), p probabilité de l'issue 1, bornée."""
    p = borne(p, 1e-4, 1 - 1e-4)
    return -math.log(p if y else 1 - p)
