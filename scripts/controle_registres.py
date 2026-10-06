"""Contrôle des registres à la poussée (noyau, sections 0, 8.8 et 12). Exécuté par le workflow
« Contrôle des registres » ; exécutable en local sur un dépôt Git (tests).

Usage : python scripts/controle_registres.py   (dans la racine d'un dépôt Git)
Variables d'environnement :
- BASE : dernier commit déjà contrôlé (déterminé par le workflow à partir de l'historique de ses exécutions) ;
  à défaut, AVANT (github.event.before), puis HEAD~1.
- POUSSE_LE : heure de la poussée (horodatage Unix de github.event.repository.pushed_at) ; à défaut, maintenant.
- ECRIRE_JOURNAL=1 : inscrire les lignes hors fenêtre au journal des contrôles (première tentative d'une
  exécution déclenchée par une poussée seulement ; jamais pour une relance ni un déclenchement manuel).
- GITHUB_RUN_ID : numéro d'exécution, recopié dans le journal.

Vérifie, sur tous les commits de BASE à HEAD (y compris ceux qu'une poussée n'a pas fait contrôler :
« [skip ci] », poussée par un jeton de workflow) :
1. fichiers de cycle jamais modifiés ni supprimés ;
2. registres, jalons, décisions de tri, ajouts à la banque et premières valeurs en ajout seul ;
3. chaque nouvelle ligne de registre (« emise »), définition de jalon (« defini_le ») et ajout à la banque
   (« ajoute_le ») datée avec le décalage horaire de Paris à cet instant, dans les deux heures qui précèdent la
   poussée ; une ligne de registre hors fenêtre, sans fuseau, avec un autre décalage ou illisible est inscrite au
   journal des contrôles (registre/controles.jsonl), ce qui l'annule pour la notation ;
4. aucune ligne recopiée à l'identique d'une ligne déjà présente (elle n'est pas inscrite : seule la ligne
   nouvelle peut l'être, par son empreinte) ;
5. aucune seconde prévision d'un même cycle pour un auteur et une question (relecture 21, I1) ;
6. fichiers écrits par les workflows (registre/controles.jsonl, data/premieres_valeurs.jsonl) modifiés
   seulement par des commits de ces workflows.
Le contrôle est détectif : un échec est public.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")
JOURNAL = "registre/controles.jsonl"
ECRITS_PAR_WORKFLOW = {JOURNAL: "controle-psychohistoire", "data/premieres_valeurs.jsonl": "collecte-psychohistoire"}
SUIVIS = ("registre/", "modele/jalons/", "data/tri/", "modele/banque/ajouts.jsonl", "data/premieres_valeurs.jsonl")


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout


def empreinte(brut):
    return hashlib.sha256(brut.encode("utf-8")).hexdigest()


def lire_journal():
    """Lecture tolérante : une ligne illisible ou incomplète est ignorée (audit interne v1.27, B2)."""
    sortie = []
    if os.path.exists(JOURNAL):
        for brut in open(JOURNAL, encoding="utf-8").read().splitlines():
            try:
                x = json.loads(brut)
            except Exception:
                continue
            if isinstance(x, dict) and x.get("fichier") and x.get("empreinte"):
                sortie.append(x)
    return sortie


def date_conforme(valeur):
    """Renvoie (datetime, motif d'écart ou None). L'horodatage doit porter le décalage de Paris à cet instant."""
    try:
        e = datetime.fromisoformat(str(valeur))
    except Exception:
        return None, "illisible"
    if e.tzinfo is None:
        return e, "sans fuseau horaire"
    if e.utcoffset() != e.astimezone(PARIS).utcoffset():
        return e, f"décalage {e.utcoffset()} différent de celui de Paris"
    return e, None


def controler():
    base = os.environ.get("BASE") or os.environ.get("AVANT", "")
    if not base or set(base) == {"0"} or subprocess.run(["git", "cat-file", "-e", base + "^{commit}"],
                                                        capture_output=True).returncode:
        base = git("rev-parse", "HEAD~1").strip()
    pousse = os.environ.get("POUSSE_LE")
    debut = datetime.fromtimestamp(int(pousse), timezone.utc) if pousse else datetime.now(timezone.utc)
    erreurs, hors = [], []

    # 6. Fichiers écrits par les workflows : seuls leurs commits les modifient.
    for f, bot in ECRITS_PAR_WORKFLOW.items():
        for l in git("log", "--format=%H\t%an", f"{base}..HEAD", "--", f).splitlines():
            h, auteur = l.split("\t", 1)
            if auteur != bot:
                erreurs.append(f"{f} : modifié par le commit {h[:8]} ({auteur}), et non par le workflow")

    for ligne in git("diff", "--no-renames", "--name-status", base, "HEAD").splitlines():
        statut, f = ligne.split("\t", 1)
        if re.match(r"data/cycles/[^/]+/", f) and not statut.startswith("A"):
            erreurs.append(f"{f} : fichier de cycle modifié ou supprimé")
            continue
        if not f.startswith(SUIVIS) or not f.endswith((".json", ".jsonl")):
            continue
        if statut.startswith("D"):
            erreurs.append(f"{f} : fichier supprimé ou renommé")
            continue
        diff = git("diff", "--no-renames", "--unified=0", base, "HEAD", "--", f).splitlines()
        if [l for l in diff if l.startswith("-") and not l.startswith("---")]:
            erreurs.append(f"{f} : ligne(s) supprimée(s) ou réécrite(s)")
        ajoutees = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]
        avant = set(git("show", f"{base}:{f}").splitlines()) if statut.startswith("M") else set()
        registre = f.startswith("registre/") and f.endswith(".jsonl") and f != JOURNAL
        champ = "emise" if registre else "defini_le" if f == "modele/jalons/definitions.jsonl" else \
                "ajoute_le" if f == "modele/banque/ajouts.jsonl" else None
        for brut in ajoutees:
            if registre and brut in avant:
                erreurs.append(f"{f} : ligne recopiée à l'identique d'une ligne déjà présente")
                continue
            if not champ:
                continue
            try:
                x = json.loads(brut)
                valeur = x[champ]
            except Exception:
                x, valeur = {}, None
            e, ecart = date_conforme(valeur)
            if ecart is None and not (debut - timedelta(hours=2) <= e <= debut + timedelta(minutes=5)):
                ecart = f"hors de la fenêtre de poussée ({debut.isoformat(timespec='seconds')})"
            if ecart:
                erreurs.append(f"{f} : « {champ} » {valeur} {ecart}")
                if registre:
                    hors.append({"fichier": f, "empreinte": empreinte(brut), "question": x.get("question"),
                                 "auteur": x.get("auteur", "modèle"), "emise": x.get("emise"), "motif": ecart,
                                 "execution": os.environ.get("GITHUB_RUN_ID", ""),
                                 "detecte_le": debut.isoformat(timespec="seconds")})
        # 5. Une seule prévision de cycle par auteur, question et cycle.
        if registre:
            nouvelles, vus = set(ajoutees), set()
            for brut in open(f, encoding="utf-8").read().splitlines():
                try:
                    x = json.loads(brut)
                except Exception:
                    continue
                if not isinstance(x, dict) or "probabilites" not in x or x.get("erratum"):
                    continue
                o = str(x.get("origine", "")).split()
                if len(o) < 2 or o[0] != "cycle":
                    continue
                cle = (x.get("auteur", "modèle"), x.get("question"), o[1].rstrip(","))
                if cle in vus and brut in nouvelles:
                    erreurs.append(f"{f} : seconde prévision du cycle {cle[2]} pour {cle[0]}, {cle[1]}")
                vus.add(cle)

    if hors and os.environ.get("ECRIRE_JOURNAL") == "1":
        connues = {(j["fichier"], j["empreinte"]) for j in lire_journal()}
        with open(JOURNAL, "a", encoding="utf-8") as fj:
            for h in hors:
                if (h["fichier"], h["empreinte"]) not in connues:
                    fj.write(json.dumps(h, ensure_ascii=False) + "\n")
    return erreurs, hors


if __name__ == "__main__":
    erreurs, hors = controler()
    for x in erreurs:
        print(f"::error::{x}")
    print("Contrôle conforme." if not erreurs else f"{len(erreurs)} anomalie(s), dont {len(hors)} ligne(s) de registre à inscrire au journal.")
    sys.exit(1 if erreurs else 0)
