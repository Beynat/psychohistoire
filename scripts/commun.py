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
    # Ajouts de la relecture 8 (4 octobre 2026) : énergie et confiance, canal prix → vote.
    "brent_mensuel": {"nom": "prix du Brent, moyenne mensuelle (EIA)", "unite": "$/baril", "delai": 1,
                      "proxy": "brent_journalier"},
    "inflation_energie_FR": {"nom": "inflation IPCH énergie France sur un an (Eurostat)", "unite": "%", "delai": 1},
    "confiance_menages_FR": {"nom": "indicateur synthétique de confiance des ménages (Insee, CVS)", "unite": "points", "delai": 1},
}
# Ancrage quotidien (cycle à blanc) : quand une série mensuelle publiée tard a un équivalent quotidien
# (« proxy »), le niveau de départ est la dernière observation quotidienne (moyenne des 5 dernières jusqu'à l'essai du 4 octobre 2026), corrigée
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


ILLISIBLES = []          # lignes illisibles rencontrées (chemin, numéro), publiées par la notation
_JOURNAL = {}


def journal_controles():
    """Journal des contrôles (noyau, sections 0 et 12) : entrées écrites par le workflow « Contrôle des registres »
    sur la branche « controles » (fichier controles.jsonl). Ordre de lecture : variable JOURNAL_CONTROLES (chemin
    d'un fichier) ; dans un dépôt Git, la branche distante « controles » (récupérée ; un échec de récupération est
    une erreur, jamais un journal vide) ; sinon registre/controles.jsonl (copies de test)."""
    import os
    import subprocess
    cle = str(RACINE)
    if cle in _JOURNAL:
        return _JOURNAL[cle]
    texte = ""
    if os.environ.get("JOURNAL_CONTROLES"):
        texte = Path(os.environ["JOURNAL_CONTROLES"]).read_text("utf-8")
    elif (RACINE / ".git").exists() and subprocess.run(["git", "remote"], cwd=RACINE, capture_output=True, text=True).stdout.strip():
        r = subprocess.run(["git", "ls-remote", "--exit-code", "origin", "controles"], cwd=RACINE, capture_output=True)
        if r.returncode == 0:
            f = subprocess.run(["git", "fetch", "-q", "origin", "controles:refs/remotes/origin/controles"], cwd=RACINE)
            if f.returncode:
                raise SystemExit("Journal des contrôles : récupération de la branche « controles » impossible.")
            texte = subprocess.run(["git", "show", "origin/controles:controles.jsonl"], cwd=RACINE,
                                   capture_output=True, text=True).stdout
        elif r.returncode != 2:
            raise SystemExit("Journal des contrôles : dépôt distant inaccessible.")
    elif (RACINE / "registre/controles.jsonl").exists():
        texte = (RACINE / "registre/controles.jsonl").read_text("utf-8")
    entrees = []
    for brut in texte.split("\n"):
        try:
            x = json.loads(brut)
        except Exception:
            continue
        if isinstance(x, dict):
            entrees.append(x)
    _JOURNAL[cle] = entrees
    return entrees


def empreintes_inscrites(chemin):
    """Empreintes des lignes de ce registre inscrites au journal des contrôles (poussées hors fenêtre)."""
    return {e["empreinte"] for e in journal_controles() if e.get("fichier") == chemin and e.get("empreinte")}


def lire_jsonl(chemin, empreintes=False, garder_inscrites=False):
    """Lignes d'un fichier JSONL, découpé sur « \\n » seulement (U+2028 et voisins restent dans la ligne). Une ligne
    illisible est écartée et consignée dans ILLISIBLES. Dans registre/, une ligne inscrite au journal des contrôles
    est écartée (audit interne v1.27 : annonces, propositions et résolutions comprises), sauf garder_inscrites.
    empreintes=True ajoute à chaque ligne l'empreinte SHA-256 de sa ligne brute (« _empreinte »)."""
    p = RACINE / chemin
    if not p.exists():
        return []
    inscrites = empreintes_inscrites(chemin) if chemin.startswith("registre/") and not garder_inscrites else set()
    sortie = []
    for n, brut in enumerate(p.read_text("utf-8", errors="replace").split("\n"), 1):
        if not brut.strip():
            continue
        try:
            x = json.loads(brut)
            if not isinstance(x, dict):
                raise ValueError
        except Exception:
            ILLISIBLES.append({"fichier": chemin, "ligne": n})
            continue
        e = hashlib.sha256(brut.encode("utf-8")).hexdigest()
        if e in inscrites:
            continue
        sortie.append({**x, "_empreinte": e} if empreintes else x)
    return sortie


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
    # Dernière valeur quotidienne plutôt que moyenne des 5 derniers jours : sur 2010-2026, elle prévoit
    # un peu mieux la moyenne mensuelle du mois suivant (erreur absolue moyenne 5,8 pb contre 5,9) et
    # ne retarde pas en période de tension (essai du 4 octobre 2026 : seuils jugés trop bas).
    niveau = quotidienne[-1][1] + correction
    return quotidienne[-1][0][:7], niveau, correction, quotidienne[-1][0]


def variations_ancrees(quotidienne, date_ancrage, pas, debut=HISTO_DEBUT):
    """Variations d'un point quotidien à la moyenne d'un mois cible (relecture 15, S5). Pour chaque mois M de
    l'historique, on prend la dernière observation quotidienne au plus tard au même jour du mois que la date
    d'ancrage, et on la compare à la moyenne du mois M + pas (mois complets seulement). C'est la loi de l'écart
    entre le niveau quotidien de départ et la moyenne mensuelle visée, plus étroite à l'horizon 1 que celle
    d'une variation de moyennes mensuelles."""
    jour = int(date_ancrage[8:10])
    moy, par_mois = {}, {}
    for p, v in quotidienne:
        moy.setdefault(p[:7], []).append(v)
        par_mois.setdefault(p[:7], []).append((p, v))
    dernier = max(moy)                      # mois en cours, incomplet : jamais pris comme cible
    sortie = []
    for m in sorted(par_mois):
        if m < debut:
            continue
        cible = mois_suivant(m, pas)
        if cible >= dernier or cible not in moy:
            continue
        avant = [v for p, v in par_mois[m] if int(p[8:10]) <= jour]
        if avant:
            sortie.append(sum(moy[cible]) / len(moy[cible]) - avant[-1])
    return sortie


def variations_question(lire, details):
    """Distribution de la variation utilisée pour une question de variable : depuis le point quotidien d'ancrage
    s'il y en a un, sinon marche aléatoire des valeurs mensuelles. lire(nom) renvoie une série."""
    a = details.get("ancrage_quotidien")
    if a and a.get("date"):
        return variations_ancrees(lire(a["proxy"]), a["date"], details["pas"])
    return variations(lire(details["serie"]), details["pas"])


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
