"""Rapport de dérive du réseau (16 octobre 2026, après la revue de Nathan : le duel RN – Philippe avait perdu
12 points entre les tables v0.4 et v0.10 sans que personne ne le voie).

Usage :
    python scripts/derive.py [REFERENCE] [--gele] [--seuil POINTS] [--tirages N] [--trajectoires N] [--decomposer]
        Compare toutes les sorties du réseau (loi de chaque pivot et questions de la banque rattachées) entre la
        référence (commit git, HEAD par défaut ; --gele : réseau témoin) et la copie de travail : même moteur, mêmes
        observations et preuves, même graine. Affiche les écarts d'au moins SEUIL points (5 par défaut).
        --decomposer : pour chaque nœud dont la structure ou la table a changé, effet de ce seul changement appliqué
        à la référence sur chacun des écarts (« d'où vient l'écart »).
    python scripts/derive.py [REFERENCE] --consigner "CAUSE" [mêmes options]
        Calcule le rapport et l'ajoute à modele/reseau/derives.jsonl (ajout seul), lié à l'empreinte de la copie de
        travail. Un écart d'au moins SEUIL points exige une cause écrite et la décomposition.

Règle (tests.py, test_derive) : toute version de la structure, des tables ou du calendrier a une entrée consignée
dans derives.jsonl ; un commit qui change le réseau sans rapport échoue aux tests.
"""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import preuves as pv
import reseau
from commun import RACINE, lire_json

JOURNAL = "modele/reseau/derives.jsonl"
SEUIL = 5.0


def empreinte(fichiers=None):
    """Empreinte de la structure, des tables et du calendrier (contenus JSON canoniques)."""
    fichiers = fichiers or [lire_json(f) for f in reseau.FICHIERS_RESEAU]
    h = hashlib.sha256()
    for d in fichiers:
        h.update(json.dumps(d, ensure_ascii=False, sort_keys=True).encode())
    return h.hexdigest()[:16]


def version(ref, chemin):
    if ref == "gele":
        return lire_json(f"{reseau.DOSSIER_GELE}/{Path(chemin).name}")
    r = subprocess.run(["git", "show", f"{ref}:{chemin}"], cwd=RACINE, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"{chemin} introuvable dans {ref}")
    return json.loads(r.stdout)


def observations_de(structure, o):
    """Observations au format du moteur (même règle que reseau.observations), à partir d'un observations.json."""
    o = o or {}
    courant = (o.get("etabli_le") or "")[:7]
    maxima = {v["id"] for v in structure["variables_etat"] if v.get("agregat") == "maximum"}
    return {n: {m: ({"au_moins": e} if n in maxima and courant and m >= courant and isinstance(e, str) else e)
                for m, e in d.items()} for n, d in o.get("etats", {}).items()}


def sorties(structure, tables, calendrier, qs, nt, ntr, obs_json=None):
    """Toutes les sorties comparables, à plat : {(objet, issue): %}. obs_json : observations.json à utiliser (à
    défaut, le fichier courant) ; une version de référence garde ses propres observations quand le format des états
    a changé (16 octobre 2026 : état « serré » de VE-SOND)."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(calendrier, f, ensure_ascii=False)
    reseau.CHEMIN_CALENDRIER, ancien = f.name, reseau.CHEMIN_CALENDRIER
    reseau._PROFILS.clear()
    reseau.CRN = 20261016    # nombres aléatoires communs : un nœud changé ne déplace pas les tirages des autres
    try:
        ids = {m for m in structure["mesures"]}
        q2 = [q for q in qs if q.get("evenement") in ids or ("composantes" in q and all(c[2:] in ids for c in q["composantes"]))]
        obs = observations_de(structure, obs_json) if obs_json is not None else reseau.observations(structure)
        p = reseau.prevoir(structure, tables, obs, q2, nt, ntr,
                           preuves=pv.preuves_notees(date.today().isoformat()))
    finally:
        reseau.CRN = None
        reseau.CHEMIN_CALENDRIER = ancien
        reseau._PROFILS.clear()
        Path(f.name).unlink()
    out = {}
    for k, d in p["__pivots__"].items():
        for i, v in d.items():
            if not (i == "non" and set(d) <= {"oui", "non"}):
                out[(k, i)] = v
    for k, d in p.items():
        if k.startswith("__"):
            continue
        for i, v in d.items():
            if i not in ("i80", "es", "non") and v is not None:
                out[(k, i)] = v
    return out


def ecarts(a, b, seuil):
    r = [(round(b[k] - a.get(k, 0.0), 1), k, a.get(k), b[k]) for k in b if abs(b[k] - a.get(k, 0.0)) >= seuil]
    r += [(round(-a[k], 1), k, a[k], None) for k in a if k not in b and a[k] >= seuil]
    return sorted(r, key=lambda x: -abs(x[0]))


def noeuds_changes(ref_fichiers, fichiers):
    """Nœuds dont la définition dans la structure ou la table a changé, et changement du calendrier."""
    (sa, ta, ca), (sb, tb, cb) = ref_fichiers, fichiers
    na, nb = reseau.noeuds_de(sa), reseau.noeuds_de(sb)
    out = []
    for i in sorted(set(na) | set(nb)):
        if na.get(i) != nb.get(i) or ta["noeuds"].get(i) != tb["noeuds"].get(i):
            out.append(i)
    if sa.get("mesures") != sb.get("mesures") or ta.get("mesures") != tb.get("mesures"):
        out.append("__mesures__")
    if ca != cb:
        out.append("__calendrier__")
    return out


def obs_compatibles(structure, o):
    """Observations de O dont l'état existe dans STRUCTURE (les autres sont retirées)."""
    N = reseau.noeuds_de(structure)
    out = {"etabli_le": (o or {}).get("etabli_le"), "etats": {}}
    for n, d in (o or {}).get("etats", {}).items():
        ok = N.get(n, {}).get("etats") or N.get(n, {}).get("issues") or ["oui", "non"]
        out["etats"][n] = {m: e for m, e in d.items() if (e if isinstance(e, str) else e.get("au_moins")) in ok}
    return out


def avec_changement(ref_fichiers, fichiers, i):
    """Référence où seul le nœud i (ou les mesures, ou le calendrier) prend sa version de la copie de travail."""
    (sa, ta, ca), (sb, tb, cb) = ref_fichiers, fichiers
    s, t, c = copy.deepcopy(sa), copy.deepcopy(ta), ca
    if i == "__calendrier__":
        return s, t, cb
    if i == "__mesures__":
        s["mesures"], t["mesures"] = copy.deepcopy(sb["mesures"]), copy.deepcopy(tb.get("mesures", {}))
        return s, t, c
    for cle in ("pivots", "variables_etat"):
        lb = {n["id"]: n for n in sb[cle]}
        if i in lb and any(n["id"] == i for n in s[cle]):
            s[cle] = [copy.deepcopy(lb[i]) if n["id"] == i else n for n in s[cle]]
        elif i in lb:
            s[cle].append(copy.deepcopy(lb[i]))
        else:
            s[cle] = [n for n in s[cle] if n["id"] != i]
    if i in tb["noeuds"]:
        t["noeuds"][i] = copy.deepcopy(tb["noeuds"][i])
    else:
        t["noeuds"].pop(i, None)
    return s, t, c


def rapport(ref="HEAD", nt=100, ntr=100, seuil=SEUIL, decomposer=False):
    refs = tuple(version(ref, f) for f in reseau.FICHIERS_RESEAU)
    cour = tuple(lire_json(f) for f in reseau.FICHIERS_RESEAU)
    qs = reseau.questions_banque(cour[0], lire_json("modele/evenements.json")["evenements"])
    o_ref = obs_compatibles(refs[0], version(ref, "modele/reseau/observations.json") if ref != "gele" else lire_json("modele/reseau/observations.json"))
    a = sorties(*refs, qs, nt, ntr, o_ref)
    b = sorties(*cour, qs, nt, ntr)
    e = ecarts(a, b, seuil)
    out = {"reference": ref, "empreinte_reference": empreinte(refs), "empreinte": empreinte(cour),
           "simulation": f"{nt} × {ntr}", "seuil": seuil,
           "ecarts": [{"objet": k[0], "issue": k[1], "avant": x, "apres": y, "ecart": d} for d, k, x, y in e],
           "noeuds_changes": noeuds_changes(refs, cour)}
    if decomposer and e:
        part = {}
        for i in out["noeuds_changes"]:
            try:
                sc = avec_changement(refs, cour, i)
                c = sorties(*sc, qs, nt, ntr, obs_compatibles(sc[0], lire_json("modele/reseau/observations.json")))
            except Exception as err:     # changement non séparable (issues ou parents modifiés ensemble)
                part[i] = f"non séparable ({type(err).__name__})"
                continue
            part[i] = {f"{k[0]} {k[1]}": round(c.get(k, 0.0) - a.get(k, 0.0), 1) for _, k, _, _ in e}
        out["decomposition"] = part
    return out


def afficher(r):
    print(f"Dérive entre {r['reference']} ({r['empreinte_reference']}) et la copie de travail ({r['empreinte']}), "
          f"{r['simulation']}, seuil {r['seuil']} points")
    print("Nœuds changés : " + (", ".join(r["noeuds_changes"]) or "aucun"))
    for x in r["ecarts"]:
        av = "absent" if x["avant"] is None else f"{x['avant']}"
        ap = "absent" if x["apres"] is None else f"{x['apres']}"
        print(f"  {x['objet']} {x['issue']} : {av} → {ap} ({x['ecart']:+.1f})")
    if not r["ecarts"]:
        print("  aucun écart au-dessus du seuil")
    for i, d in r.get("decomposition", {}).items():
        if isinstance(d, str):
            print(f"  {i} : {d}")
            continue
        fort = {k: v for k, v in d.items() if abs(v) >= 1}
        if fort:
            print(f"  part de {i} seul : " + ", ".join(f"{k} {v:+.1f}" for k, v in sorted(fort.items(), key=lambda x: -abs(x[1]))))


def consigner(r, cause):
    if r["ecarts"] and (not cause or len(cause.strip()) < 20):
        sys.exit("Écarts au-dessus du seuil : une cause écrite (20 caractères au moins) est exigée.")
    if r["ecarts"] and "decomposition" not in r:
        sys.exit("Écarts au-dessus du seuil : la décomposition est exigée (--decomposer).")
    r = {**r, "cause": cause, "emise": datetime.now(ZoneInfo("Europe/Paris")).isoformat(timespec="seconds")}
    with open(RACINE / JOURNAL, "a", encoding="utf-8") as f:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return r


def consignees():
    p = RACINE / JOURNAL
    return [json.loads(l) for l in p.read_text("utf-8").splitlines() if l.strip()] if p.exists() else []


if __name__ == "__main__":
    args = sys.argv[1:]
    val = lambda o, d: args[args.index(o) + 1] if o in args else d
    opts = {"--tirages", "--trajectoires", "--seuil", "--consigner"}
    libres = [x for k, x in enumerate(args) if not x.startswith("--") and (k == 0 or args[k - 1] not in opts)]
    ref = "gele" if "--gele" in args else (libres[0] if libres else "HEAD")
    r = rapport(ref, int(val("--tirages", 100)), int(val("--trajectoires", 100)), float(val("--seuil", SEUIL)),
                "--decomposer" in args or "--consigner" in args)
    afficher(r)
    if "--consigner" in args:
        consigner(r, val("--consigner", ""))
        print(f"consigné dans {JOURNAL}")
