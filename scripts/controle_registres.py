"""Contrôle des registres à la poussée (noyau, sections 0, 8.8 et 12). Exécuté par le workflow
« Contrôle des registres » ; exécutable en local sur un dépôt Git (tests).

Usage : python scripts/controle_registres.py   (dans la racine d'un dépôt Git)
Variables d'environnement :
- JOURNAL_CONTROLES : chemin d'une copie du journal des contrôles (branche « controles », fichier
  controles.jsonl), lue pour le dernier commit contrôlé et les empreintes déjà inscrites ; absent = journal vide.
- JOURNAL_NOUVEAU : fichier où écrire les entrées à ajouter au journal (le workflow les pousse sur la branche).
- AVANT : github.event.before, utilisé seulement si le journal ne contient encore aucun repère.
- POUSSE_LE : heure de la poussée (github.event.repository.pushed_at, horodatage Unix ou ISO) ; à défaut, maintenant.
- GITHUB_RUN_ID, GITHUB_RUN_ATTEMPT : recopiés dans le journal.

Contrôle tous les commits depuis le dernier repère « controle_jusqua » du journal (le dernier commit contrôlé
jusqu'au bout), y compris ceux qu'une poussée n'a pas fait contrôler (« [skip ci] », jeton de workflow, exécution
en attente annulée, exécution échouée avant son inscription) :
1. fichiers de cycle jamais modifiés ni supprimés ;
2. registres, jalons, décisions de tri, ajouts à la banque et premières valeurs en ajout seul ;
3. chaque nouvelle ligne de registre (« emise »), définition de jalon (« defini_le ») et ajout à la banque
   (« ajoute_le ») porte le décalage horaire de Paris à cet instant et est datée dans les deux heures qui
   précèdent la poussée ; une ligne de registre hors fenêtre, sans fuseau, avec un autre décalage ou illisible est
   inscrite au journal par l'empreinte de sa ligne brute, ce qui l'écarte de toute lecture des registres ;
4. aucune ligne recopiée à l'identique d'une ligne déjà présente (elle n'est pas inscrite) ;
5. aucune seconde prévision d'un même cycle pour un auteur et une question (relecture 21, I1) ;
6. data/premieres_valeurs.jsonl modifié seulement par la collecte ; aucun fichier registre/controles.jsonl sur main.
Toute erreur de lecture d'une ligne la rend « illisible », sans interrompre le contrôle. En fin de contrôle, un
repère « controle_jusqua » est écrit, même en cas d'anomalie : la plage a été contrôlée et ses anomalies inscrites.
Le contrôle est détectif : un échec est public. Il ne protège pas contre une manœuvre délibérée de l'opérateur
(noyau, section 12, « Limites du contrôle »), qui reste visible dans l'historique public.
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
ECRITS_PAR_WORKFLOW = {"data/premieres_valeurs.jsonl": "collecte-psychohistoire"}
SUIVIS = ("registre/", "modele/jalons/", "data/tri/", "modele/banque/ajouts.jsonl", "data/premieres_valeurs.jsonl")


def git(*a):
    return subprocess.run(["git", *a], capture_output=True).stdout.decode("utf-8", errors="replace")


def empreinte(brut):
    return hashlib.sha256(brut.encode("utf-8")).hexdigest()


def lire_journal():
    """Lecture tolérante du journal : une ligne illisible ou incomplète est ignorée."""
    chemin = os.environ.get("JOURNAL_CONTROLES")
    sortie = []
    if chemin and os.path.exists(chemin):
        for brut in open(chemin, encoding="utf-8", errors="replace").read().split("\n"):
            try:
                x = json.loads(brut)
            except Exception:
                continue
            if isinstance(x, dict):
                sortie.append(x)
    return sortie


def base_controlee(journal):
    """Dernier repère « controle_jusqua » du journal qui est un ancêtre de HEAD ; à défaut, AVANT, puis HEAD~1."""
    for e in reversed(journal):
        sha = e.get("controle_jusqua")
        if sha and subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"], capture_output=True).returncode == 0:
            return sha
    avant = os.environ.get("AVANT", "")
    if avant and set(avant) != {"0"} and not subprocess.run(["git", "cat-file", "-e", avant + "^{commit}"],
                                                             capture_output=True).returncode:
        print("::warning::Aucun repère au journal des contrôles : contrôle depuis github.event.before.")
        return avant
    return git("rev-parse", "HEAD~1").strip()


def heure_poussee():
    v = os.environ.get("POUSSE_LE", "")
    if v.isdigit():
        return datetime.fromtimestamp(int(v), timezone.utc)
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def date_conforme(valeur):
    """Renvoie (datetime, motif d'écart ou None). L'horodatage doit porter le décalage de Paris à cet instant."""
    try:
        e = datetime.fromisoformat(str(valeur))
        if e.tzinfo is None:
            return e, "sans fuseau horaire"
        if e.utcoffset() != e.astimezone(PARIS).utcoffset():
            return e, f"décalage {e.utcoffset()} différent de celui de Paris"
        return e, None
    except Exception:   # chaîne illisible, année hors bornes (audit interne v1.27)
        return None, "illisible"


def controler():
    journal = lire_journal()
    base = base_controlee(journal)
    debut = heure_poussee()
    erreurs, hors = [], []

    # 6. Fichiers écrits par les workflows : seuls leurs commits les modifient ; le journal vit sur sa branche.
    if os.path.exists("registre/controles.jsonl"):
        erreurs.append("registre/controles.jsonl présent sur main : le journal des contrôles vit sur la branche « controles »")
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
        diff = git("diff", "--no-renames", "--unified=0", base, "HEAD", "--", f).split("\n")
        if [l for l in diff if l.startswith("-") and not l.startswith("---")]:
            erreurs.append(f"{f} : ligne(s) supprimée(s) ou réécrite(s)")
        ajoutees = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]
        avant = set(git("show", f"{base}:{f}").split("\n")) if statut.startswith("M") else set()
        registre = f.startswith("registre/") and f.endswith(".jsonl") and f != "registre/controles.jsonl"
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
                valeur = x[champ] if isinstance(x, dict) else None
                x = x if isinstance(x, dict) else {}
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
            for brut in open(f, encoding="utf-8", errors="replace").read().split("\n"):
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

    # Entrées à ajouter au journal : lignes hors fenêtre non encore inscrites, puis le repère de fin de contrôle.
    connues = {(j.get("fichier"), j.get("empreinte")) for j in journal}
    run = {"execution": os.environ.get("GITHUB_RUN_ID", ""), "tentative": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
           "detecte_le": debut.isoformat(timespec="seconds")}
    nouveau = [{**h, **run} for h in hors if (h["fichier"], h["empreinte"]) not in connues]
    nouveau.append({"controle_jusqua": git("rev-parse", "HEAD").strip(), "depuis": base, **run})
    if os.environ.get("JOURNAL_NOUVEAU"):
        with open(os.environ["JOURNAL_NOUVEAU"], "w", encoding="utf-8") as fj:
            fj.write("".join(json.dumps(x, ensure_ascii=True) + "\n" for x in nouveau))
    return erreurs, hors


def inscrire(chemin):
    """Ajoute au journal (fichier de la branche « controles ») les entrées de JOURNAL_NOUVEAU, en ajout seul,
    sans réinscrire une empreinte déjà présente (une relance n'inscrit rien deux fois)."""
    deja = open(chemin, encoding="utf-8", errors="replace").read() if os.path.exists(chemin) else ""
    cles = set()
    for l in deja.split("\n"):
        try:
            x = json.loads(l)
            cles.add((x.get("fichier"), x.get("empreinte")))
        except Exception:
            pass
    with open(chemin, "a", encoding="utf-8") as f:
        if deja and not deja.endswith("\n"):
            f.write("\n")
        for l in open(os.environ["JOURNAL_NOUVEAU"], encoding="utf-8").read().split("\n"):
            if l.strip():
                x = json.loads(l)
                if x.get("controle_jusqua") or (x.get("fichier"), x.get("empreinte")) not in cles:
                    f.write(l + "\n")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--inscrire":
        inscrire(sys.argv[2])
        sys.exit(0)
    erreurs, hors = controler()
    for x in erreurs:
        print(f"::error::{x}")
    print("Contrôle conforme." if not erreurs else f"{len(erreurs)} anomalie(s), dont {len(hors)} ligne(s) de registre à inscrire au journal.")
    sys.exit(1 if erreurs else 0)
