"""Contrôle des registres à la poussée (noyau, sections 0, 8.8 et 12). Exécuté par le workflow
« Contrôle des registres » ; exécutable en local sur un dépôt Git (tests).

Usage : python scripts/controle_registres.py   (dans la racine d'un dépôt Git)
Variables d'environnement :
- JOURNAL_CONTROLES : chemin d'une copie du journal des contrôles (branche « controles », fichier
  controles.jsonl), lue pour le dernier commit contrôlé et les empreintes déjà inscrites ; absent = journal vide.
- JOURNAL_NOUVEAU : fichier où écrire les entrées à ajouter au journal (le workflow les pousse sur la branche).
- AVANT : github.event.before, utilisé seulement si le journal ne contient encore aucun repère.
- POUSSE_LE : heure de la poussée (github.event.repository.pushed_at, horodatage Unix ou ISO) ; à défaut, maintenant.
- POUSSES : fichier JSON de l'activité du dépôt (API GitHub, poussées sur main : before, after, timestamp). Une plage
  recontrôlée est découpée par poussée, et chaque ligne jugée à l'heure de la poussée qui l'a apportée (troisième
  audit v1.27, défaut 2). Sans cette information, une ligne venue d'une poussée antérieure n'est pas jugée sur la
  fenêtre (anomalie signalée), mais l'est sur le fuseau et la lisibilité.
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import ligne_valide   # noqa: E402

PARIS = ZoneInfo("Europe/Paris")
ECRITS_PAR_WORKFLOW = {"data/premieres_valeurs.jsonl": "collecte-psychohistoire"}
SUIVIS = ("registre/", "modele/jalons/", "data/tri/", "modele/banque/ajouts.jsonl", "data/premieres_valeurs.jsonl")


class ErreurGit(Exception):
    pass


def git(*a, octets=False, tolerer=False):
    r = subprocess.run(["git", *a], capture_output=True)
    if r.returncode and not tolerer:
        raise ErreurGit(f"git {' '.join(a)} : {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout if octets else r.stdout.decode("utf-8", errors="replace")


def ancetre(a, b):
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b], capture_output=True).returncode == 0


def empreinte(brut):
    """Empreinte SHA-256 d'une ligne brute (octets, sans le saut de ligne final, retour chariot compris)."""
    return hashlib.sha256(brut if isinstance(brut, bytes) else brut.encode("utf-8")).hexdigest()


def lire_journal():
    """Lecture tolérante du journal : une ligne illisible ou incomplète est ignorée."""
    chemin = os.environ.get("JOURNAL_CONTROLES")
    sortie = []
    if chemin and os.path.exists(chemin):
        for brut in open(chemin, "rb").read().split(b"\n"):
            try:
                x = json.loads(brut)
            except Exception:
                continue
            if isinstance(x, dict):
                sortie.append(x)
    return sortie


def base_controlee(journal):
    """Repère « controle_jusqua » le plus avancé parmi ceux qui sont des ancêtres de HEAD (une relance d'une
    exécution ancienne ne fait pas reculer le contrôle) ; à défaut, AVANT, puis le commit racine."""
    meilleurs = []
    for e in journal:
        sha = e.get("controle_jusqua")
        if isinstance(sha, str) and ancetre(sha, "HEAD"):
            meilleurs.append((int(git("rev-list", "--count", f"{sha}..HEAD").strip()), sha))
    if meilleurs:
        return min(meilleurs)[1]
    avant = os.environ.get("AVANT", "")
    if avant and set(avant) != {"0"} and ancetre(avant, "HEAD"):
        print("::warning::Aucun repère au journal des contrôles : contrôle depuis github.event.before.")
        return avant
    return git("rev-list", "--max-parents=0", "HEAD").split()[0]


def heure(v):
    v = str(v or "")
    if v.isdigit():
        return datetime.fromtimestamp(int(v), timezone.utc)
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except Exception:
        return None


def segments(base):
    """Plages (début, fin, heure de poussée) qui couvrent base..HEAD, une par poussée sur main."""
    pousse = heure(os.environ.get("POUSSE_LE")) or datetime.now(timezone.utc)
    activite = []
    if os.environ.get("POUSSES") and os.path.exists(os.environ["POUSSES"]):
        try:
            activite = json.load(open(os.environ["POUSSES"], encoding="utf-8"))
        except Exception:
            activite = []
    pousses = []
    for a in activite if isinstance(activite, list) else []:
        apres, t = a.get("after"), heure(a.get("timestamp"))
        if isinstance(apres, str) and t and apres != base and ancetre(base, apres) and ancetre(apres, "HEAD"):
            pousses.append((t, apres))
    sortie, prec = [], base
    for t, apres in sorted(pousses):
        if prec != apres and ancetre(prec, apres):
            sortie.append((prec, apres, t))
            prec = apres
    tete = git("rev-parse", "HEAD").strip()
    if prec != tete:
        avant = os.environ.get("AVANT", "")
        if not pousses and avant and avant != prec and ancetre(prec, avant) and ancetre(avant, "HEAD"):
            sortie.append((prec, avant, None))   # poussées antérieures d'heure inconnue
            prec = avant
        sortie.append((prec, tete, pousse))
    return sortie


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


def fichiers_modifies(a, b):
    """(statut, chemin) sans guillemets ni échappement (-z)."""
    champs = git("diff", "--no-renames", "--name-status", "-z", a, b).split("\0")
    return [(champs[i], champs[i + 1]) for i in range(0, len(champs) - 1, 2)]


def controler():
    journal = lire_journal()
    base = base_controlee(journal)
    erreurs, hors = [], []
    detecte = heure(os.environ.get("POUSSE_LE")) or datetime.now(timezone.utc)

    # 6. Fichiers écrits par les workflows : seuls leurs commits les modifient ; le journal vit sur sa branche.
    if os.path.exists("registre/controles.jsonl"):
        erreurs.append("registre/controles.jsonl présent sur main : le journal des contrôles vit sur la branche « controles »")
    for f, bot in ECRITS_PAR_WORKFLOW.items():
        for l in git("log", "--format=%H%x09%an", f"{base}..HEAD", "--", f).splitlines():
            h, auteur = l.split("\t", 1)
            if auteur != bot:
                erreurs.append(f"{f} : modifié par le commit {h[:8]} ({auteur}), et non par le workflow")

    for debut_seg, fin_seg, t in segments(base):
        if t is None:
            erreurs.append(f"commits {debut_seg[:8]}..{fin_seg[:8]} : heure de poussée inconnue, fenêtre non vérifiée")
        for statut, f in fichiers_modifies(debut_seg, fin_seg):
            if re.match(r"data/cycles/[^/]+/", f) and not statut.startswith("A"):
                erreurs.append(f"{f} : fichier de cycle modifié ou supprimé")
                continue
            if not f.startswith(SUIVIS) or not f.endswith((".json", ".jsonl")):
                continue
            if statut.startswith("D"):
                erreurs.append(f"{f} : fichier supprimé ou renommé")
                continue
            diff = git("diff", "--text", "--no-renames", "--unified=0", debut_seg, fin_seg, "--", f, octets=True).split(b"\n")
            if [l for l in diff if l.startswith(b"-") and not l.startswith(b"---")]:
                erreurs.append(f"{f} : ligne(s) supprimée(s) ou réécrite(s)")
            ajoutees = [l[1:] for l in diff if l.startswith(b"+") and not l.startswith(b"+++")]
            avant = set(git("show", f"{debut_seg}:{f}", octets=True).split(b"\n")) if statut.startswith("M") else set()
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
                    if not isinstance(x, dict):
                        raise ValueError
                except Exception:
                    x = None
                if registre and (x is None or not ligne_valide(x)):
                    e, ecart, valeur = None, "illisible ou de types inattendus", None
                else:
                    valeur = x.get(champ) if x else None
                    e, ecart = date_conforme(valeur)
                if ecart is None and t is not None and not (t - timedelta(hours=2) <= e <= t + timedelta(minutes=5)):
                    ecart = f"hors de la fenêtre de poussée ({t.isoformat(timespec='seconds')})"
                if ecart:
                    erreurs.append(f"{f} : « {champ} » {valeur} {ecart}")
                    if registre:
                        x = x or {}
                        hors.append({"fichier": f, "empreinte": empreinte(brut), "question": str(x.get("question")),
                                     "auteur": str(x.get("auteur", "modèle")), "emise": str(x.get("emise")), "motif": ecart})

    # 5. Une seule prévision de cycle par auteur, question et cycle.
    nouvelles = {}
    for statut, f in fichiers_modifies(base, "HEAD"):
        if f.startswith("registre/") and f.endswith(".jsonl") and os.path.exists(f):
            diff = git("diff", "--text", "--unified=0", base, "HEAD", "--", f, octets=True).split(b"\n")
            nouvelles[f] = {l[1:] for l in diff if l.startswith(b"+") and not l.startswith(b"+++")}
    for f, nv in nouvelles.items():
        vus = set()
        for brut in open(f, "rb").read().split(b"\n"):
            try:
                x = json.loads(brut)
                if not isinstance(x, dict) or "probabilites" not in x or x.get("erratum") or not ligne_valide(x):
                    continue
                o = str(x.get("origine", "")).split()
                if len(o) < 2 or o[0] != "cycle":
                    continue
                cle = (x.get("auteur", "modèle"), x.get("question"), o[1].rstrip(","))
            except Exception:
                continue
            if cle in vus and brut in nv:
                erreurs.append(f"{f} : seconde prévision du cycle {cle[2]} pour {cle[0]}, {cle[1]}")
            vus.add(cle)

    # Entrées à ajouter au journal : lignes à écarter non encore inscrites, puis le repère de fin de contrôle.
    connues = {(j.get("fichier"), j.get("empreinte")) for j in journal}
    run = {"execution": os.environ.get("GITHUB_RUN_ID", ""), "tentative": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
           "detecte_le": detecte.isoformat(timespec="seconds")}
    nouveau, vues = [], set()
    for h in hors:
        if (h["fichier"], h["empreinte"]) not in connues | vues:
            nouveau.append({**h, **run})
            vues.add((h["fichier"], h["empreinte"]))
    nouveau.append({"controle_jusqua": git("rev-parse", "HEAD").strip(), "depuis": base, **run})
    if os.environ.get("JOURNAL_NOUVEAU"):
        with open(os.environ["JOURNAL_NOUVEAU"], "w", encoding="utf-8", newline="\n") as fj:
            fj.write("".join(json.dumps(x, ensure_ascii=True) + "\n" for x in nouveau))
    return erreurs, hors


def inscrire(chemin):
    """Ajoute au journal (fichier de la branche « controles ») les entrées de JOURNAL_NOUVEAU, en ajout seul,
    sans réinscrire une empreinte déjà présente (une relance n'inscrit rien deux fois)."""
    deja = open(chemin, encoding="utf-8", errors="replace", newline="").read() if os.path.exists(chemin) else ""
    cles = set()
    for l in deja.split("\n"):
        try:
            x = json.loads(l)
            cles.add((x.get("fichier"), x.get("empreinte")))
        except Exception:
            pass
    with open(chemin, "a", encoding="utf-8", newline="\n") as f:
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
    try:
        erreurs, hors = controler()
    except ErreurGit as exc:   # aucun repère n'est écrit : la plage sera recontrôlée
        print(f"::error::Contrôle interrompu : {exc}")
        sys.exit(2)
    for x in erreurs:
        print(f"::error::{x}")
    print("Contrôle conforme." if not erreurs else f"{len(erreurs)} anomalie(s), dont {len(hors)} ligne(s) de registre à inscrire au journal.")
    sys.exit(1 if erreurs else 0)
