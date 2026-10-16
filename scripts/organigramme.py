"""Données de l'organigramme (feuille de route, étape 8) : écrit data/organigramme_v0.json, lu par reseau.html.

Usage : python scripts/organigramme.py [--tirages N] [--trajectoires N] [--sortie FICHIER] [--sans-instantane]
        python scripts/organigramme.py --page SORTIE.html [--apercu]     page (données en ligne avec --apercu)

La page recalcule elle-même toutes les probabilités à partir des trajectoires du moteur (scripts/reseau.py, mêmes
tables, observations et preuves que les prévisions du registre) : issue de chaque pivot et état mensuel de chaque
variable par trajectoire, et poids de chaque trajectoire (produit des vraisemblances des preuves notées). Le mode
« et si » de la page multiplie ces poids par la vraisemblance des faits cochés (jalon observé ou manqué, issue
fixée) : c'est le calcul du moteur de preuve (scripts/preuves.py), donc tout l'organigramme bouge, vers l'aval et
vers l'amont. Rien n'est écrit au registre : l'organigramme est une lecture du réseau, pas une prévision notée.

Codage : « codes », une chaîne par trajectoire, un caractère par pivot (rang de l'issue dans « issues ») ;
« variables », une chaîne par trajectoire, 24 caractères par variable dans l'ordre de « variables » (rang de
l'état, un par mois d'octobre 2026 à septembre 2028).

Évolution (16 octobre 2026, demande de Nathan) : chaque nuit, la loi des pivots et les faits du jour (observations,
preuves notées) sont conservés dans data/instantanes/AAAA-MM-JJ.json. La page compare chaque probabilité à
l'instantané le plus récent daté d'au moins 7 jours, et sépare l'écart en deux parts : « modèle » (le modèle courant
appliqué aux faits de ce jour-là, moins la valeur de ce jour-là) et « faits » (aujourd'hui moins ce contrefactuel).
Risques rares : un pivot dont l'issue affichée reste sous 3 % sort de l'organigramme pour un encart à part ; il reste
dans le moteur et dans le mode « et si ».
"""
import json
import random
import re
import sys
from datetime import date

import actualite
import preuves as pv
import reseau
from commun import RACINE, lire_json, lire_jsonl

M = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
dfr = lambda d: f"{int(d[8:10])} {M[int(d[5:7]) - 1]} {d[:4]}"
mfr = lambda d: f"{M[int(d[5:7]) - 1]} {d[:4]}"

# Titre (événement), issue affichée (rang, ou None pour un pivot à plusieurs issues) et libellé court.
TETE = {
 "PV-CENSURE1a": ("Censure du gouvernement d'ici fin 2026", 0, "censure fin 2026"),
 "PV-CENSURE1b": ("Censure entre janvier et mai 2027", 0, "censure au printemps"),
 "PV-BUDGET": ("Pas de loi de finances publiée au 31 décembre", 1, "pas de budget au 31 déc."),
 "PV-GOUV": ("Départ du Premier ministre avant le 2 mai 2027", 0, "départ du Premier ministre"),
 "PV-DISSOL1": ("Dissolution avant la présidentielle", 0, "dissolution avant l'élection"),
 "PV-AUDIENCE": ("Audience de cassation avant fin février 2027", 0, "audience tenue"),
 "PV-POURVOI": ("Arrêt de cassation sur le pourvoi de Marine Le Pen, au 12 mars 2027", None, "cassation"),
 "PV-ECOLO": ("Choix des écologistes pour 2027", None, "écologistes"),
 "PV-BLOC": ("Candidatures au centre (Philippe, Attal)", None, "centre"),
 "PV-GAUCHE": ("Nombre de candidats de gauche", None, "gauche"),
 "PV-LEPEN": ("Marine Le Pen sur la liste des candidats", 0, "Le Pen candidate"),
 "PV-DUEL": ("Duel du second tour", None, "2d tour"),
 "PV-VAINQ": ("Président élu", None, "élu"),
 "PV-DISSOL2a": ("Dissolution dans les deux mois suivant l'élection", 0, "dissolution en mai-juin 2027"),
 "PV-DISSOL2b": ("Dissolution de juillet 2027 à septembre 2028", 0, "dissolution plus tardive"),
 "PV-MAJOR": ("Majorité absolue pour le camp présidentiel", 0, "majorité absolue"),
 "PV-CENSURE2": ("Censure après la présidentielle", 0, "censure après l'élection"),
 "PV-NOTE": ("Dégradation de la note de la France", 0, "dégradation de la note"),
 "PV-PDE": ("Durcissement de la procédure pour déficit excessif", 0, "durcissement de la procédure"),
 "PV-TPI": ("Achats de dette française par la BCE (TPI)", 0, "achats de la BCE"),
}
SI = {
 "PV-CENSURE1a": ["le gouvernement est censuré d'ici fin 2026", "pas de censure d'ici fin 2026"],
 "PV-CENSURE1b": ["le gouvernement est censuré entre janvier et mai 2027", "pas de censure au printemps 2027"],
 "PV-BUDGET": ["la loi de finances est publiée au 31 décembre", "pas de loi de finances au 31 décembre"],
 "PV-GOUV": ["le Premier ministre part avant le 2 mai", "le Premier ministre reste"],
 "PV-DISSOL1": ["dissolution avant l'élection", "pas de dissolution avant l'élection"],
 "PV-AUDIENCE": ["l'audience de cassation se tient avant fin février", "pas d'audience avant fin février"],
 "PV-LEPEN": ["Marine Le Pen est candidate", "Marine Le Pen n'est pas candidate"],
 "PV-DISSOL2a": ["le nouveau président dissout en mai-juin 2027", "pas de dissolution en mai-juin 2027"],
 "PV-DISSOL2b": ["dissolution après juin 2027", "pas de dissolution après juin 2027"],
 "PV-MAJOR": ["le camp présidentiel a la majorité absolue", "pas de majorité absolue"],
 "PV-PDE": ["la procédure pour déficit est durcie", "procédure non durcie"],
 "PV-NOTE": ["la note est dégradée", "note maintenue"], "PV-TPI": ["la BCE achète de la dette française", "pas d'achats de la BCE"],
 "PV-CENSURE2": ["censure après l'élection", "pas de censure après l'élection"],
}
PREFIXE = {"PV-POURVOI": "l'arrêt de cassation est : ", "PV-ECOLO": "les écologistes choisissent : ", "PV-BLOC": "au centre : ",
           "PV-GAUCHE": "candidats de gauche : ", "PV-DUEL": "le second tour oppose ", "PV-VAINQ": "le président élu est "}
CAS = {
 "PV-POURVOI": {"rejet ou non-admission": "le pourvoi est rejeté", "cassation totale ou partielle": "la condamnation est cassée",
                "désistement": "Marine Le Pen se désiste de son pourvoi", "pas d'arrêt": "pas d'arrêt au 12 mars"},
 "PV-ECOLO": {"candidature autonome": "les écologistes ont leur propre candidat", "soutien à un autre candidat": "les écologistes soutiennent un autre candidat",
              "autre ou vote non tenu": "pas de choix tranché des écologistes"},
 "PV-BLOC": {"Philippe seul": "Philippe est seul candidat au centre", "les deux": "Philippe et Attal sont tous deux candidats",
             "Attal seul": "Attal est seul candidat au centre", "aucun des deux": "ni Philippe ni Attal ne sont candidats"},
}
VNOM = {"VE-POP": "Popularité du président", "VE-MOBIL": "Mobilisation sociale", "VE-ECART": "Écart de taux France-Allemagne",
        "VE-SOND": "Deuxième bloc dans les sondages", "VE-RN": "Intentions de vote RN", "VE-LYCEE": "Mobilisation lycéenne"}
VSI = {"VE-POP": "popularité ", "VE-MOBIL": "mobilisation ", "VE-ECART": "écart de taux ",
       "VE-SOND": "2e bloc : ", "VE-RN": "RN à ", "VE-LYCEE": "lycées : "}
THEME = {}
for th, ids in {"budget": ["PV-CENSURE1a", "PV-BUDGET", "PV-CENSURE1b", "PV-GOUV", "PV-DISSOL1"],
                "candidatures": ["PV-AUDIENCE", "PV-POURVOI", "PV-LEPEN", "PV-ECOLO", "PV-GAUCHE", "PV-BLOC"],
                "election": ["PV-DUEL", "PV-VAINQ"], "apres": ["PV-DISSOL2a", "PV-DISSOL2b", "PV-MAJOR", "PV-CENSURE2"],
                "dette": ["PV-NOTE", "PV-PDE", "PV-TPI"]}.items():
    for i in ids: THEME[i] = th
TETE["PV-RNAUTRE"] = ("Candidat du RN autre que Le Pen ou Bardella", 1, "autre candidat RN")
SI["PV-RNAUTRE"] = ["le candidat du RN est Le Pen ou Bardella", "le candidat du RN est une autre personne"]
THEME["PV-RNAUTRE"] = "candidatures"
TETE["PV-VACANCE"] = ("Vacance de la présidence avant mai 2027", 0, "vacance de la présidence")
SI["PV-VACANCE"] = ["la présidence devient vacante", "pas de vacance de la présidence"]
THEME["PV-VACANCE"] = "budget"
TETE["PV-CASSEURS"] = ("Loi « casseurs-payeurs » publiée avant avril 2027", 0, "loi casseurs-payeurs")
SI["PV-CASSEURS"] = ["la loi « casseurs-payeurs » est publiée", "la loi « casseurs-payeurs » n'est pas publiée"]
THEME["PV-CASSEURS"] = "budget"


def phrase(p, k):
    pid, l = p["id"], p["libelles"][k]
    if pid in CAS:
        return "Si " + CAS[pid].get(l, l)
    if pid == "PV-DUEL":
        return "Si le second tour oppose " + ("un autre duel" if l == "autre duel" else l.replace(" – ", " et ").replace("RN et", "le RN et"))
    if pid == "PV-VAINQ":
        return "Si le président élu est " + ("un autre candidat" if l == "autre" else "le candidat du RN" if l == "RN" else l)
    return "Si " + (SI[pid][k] if pid in SI else PREFIXE[pid] + l)


INSTANTANES = "data/instantanes"
SEUIL_RARE = 3      # pivot dont l'issue affichée reste sous 3 % : replié dans l'encart « risques rares »
RECUL_JOURS = 7     # évolution affichée : par rapport à l'instantané le plus récent daté d'au moins 7 jours


def simuler_lot(s, tables, obs, notees, tirages, trajectoires, graine):
    """Trajectoires du moteur : issue de chaque pivot, états mensuels des variables, poids des preuves."""
    # Nombres aléatoires communs : le contrefactuel de l'évolution (mêmes trajectoires, autres faits) et le jour
    # suivant ne diffèrent que par ce qui a changé, pas par le bruit des tirages.
    reseau.CRN = graine
    try:
        reseau.PRIORS = reseau.lois_a_priori(s, tables, obs)
    finally:
        reseau.CRN = None
    reseau.CHOCS = reseau.chocs_retenus()
    noeuds = reseau.noeuds_de(s)
    piv, ve = s["pivots"], s["variables_etat"]
    rng = random.Random(graine)
    reseau.CRN = graine
    codes, vcodes, poids = [], [], []
    for jt in range(tirages):
        params = reseau.perturber(tables, rng, reseau._rngs("p", jt))
        for jj in range(trajectoires):
            t = reseau.simuler(s, params, obs, rng, rngs=reseau._rngs("t", jt, jj))
            codes.append("".join(str(p["issues"].index(pv.issue_noeud(t, p["id"], p))) for p in piv))
            vcodes.append("".join(str(v["etats"].index(e)) for v in ve for e in t[v["id"]]))
            poids.append(round(pv.poids(notees, t, noeuds), 6) if notees else 1)
    reseau.CRN = None
    return codes, vcodes, poids


def marges(s, codes, poids):
    """Loi de chaque pivot (%), pondérée, à partir des codes de trajectoires."""
    W = sum(poids) or 1.0
    out = {}
    for i, p in enumerate(s["pivots"]):
        a = [0.0] * len(p["issues"])
        for c, w in zip(codes, poids):
            a[int(c[i])] += w
        out[p["id"]] = [round(100 * x / W, 1) for x in a]
    return out


def instantane(s, tables, jour, obs, notees, codes, poids, empreinte_):
    """Ce qui est conservé chaque jour pour afficher l'évolution : lois des pivots, et les faits de ce jour
    (observations et preuves) pour séparer ensuite l'effet du modèle de celui des faits."""
    return {"jour": jour, "empreinte": empreinte_, "version_structure": s.get("version"),
            "version_tables": tables.get("version"), "pivots": marges(s, codes, poids),
            "observations": obs, "preuves": notees}


def reference(jour, recul=RECUL_JOURS):
    """Instantané le plus récent daté d'au moins RECUL jours avant JOUR ; à défaut, le plus ancien."""
    d = RACINE / INSTANTANES
    fs = sorted(d.glob("????-??-??.json")) if d.exists() else []
    if not fs:
        return None
    from datetime import date as _d, timedelta
    limite = (_d.fromisoformat(jour) - timedelta(days=recul)).isoformat()
    avant = [f for f in fs if f.stem <= limite]
    f = avant[-1] if avant else fs[0]
    return None if f.stem >= jour else json.loads(f.read_text("utf-8"))


def tendance(s, tables, ref, marg_now, tirages, trajectoires, graine):
    """Évolution depuis l'instantané REF, séparée en deux parts : « modèle » (le modèle courant appliqué aux faits de
    REF, moins REF) et « faits » (aujourd'hui moins ce contrefactuel). Une issue absente de REF (structure changée)
    n'a pas d'évolution."""
    noeuds = reseau.noeuds_de(s)
    obs_ref = {n: d for n, d in (ref.get("observations") or {}).items() if n in noeuds}
    codes, _, poids = simuler_lot(s, tables, obs_ref, ref.get("preuves") or [], tirages, trajectoires, graine)
    cf = marges(s, codes, poids)
    out = {}
    for p in s["pivots"]:
        avant = ref["pivots"].get(p["id"])
        if avant is None or len(avant) != len(p["issues"]):
            continue
        out[p["id"]] = {"avant": avant, "contrefactuel": cf[p["id"]]}
    return {"reference": ref["jour"], "modele_change": ref.get("empreinte") != empreinte_courante(),
            "versions": [ref.get("version_tables"), tables.get("version")], "pivots": out}


def empreinte_courante():
    import derive
    return derive.empreinte()


def construire(tirages=100, trajectoires=40, graine=20261010, avec_tendance=True, ecrire_instantane=False):
    import carte
    s = lire_json("modele/reseau/structure_v0.json")
    tables = lire_json("modele/reseau/tables_v0.json")
    obs = reseau.observations(s)
    jour = date.today().isoformat()
    notees = pv.preuves_notees(jour)
    noeuds = reseau.noeuds_de(s)
    piv, ve = s["pivots"], s["variables_etat"]
    codes, vcodes, poids = simuler_lot(s, tables, obs, notees, tirages, trajectoires, graine)
    marg_now = marges(s, codes, poids)
    ref = reference(jour) if avec_tendance else None
    tend = tendance(s, tables, ref, marg_now, tirages, trajectoires, graine) if ref else None
    if ecrire_instantane:
        (RACINE / INSTANTANES).mkdir(parents=True, exist_ok=True)
        (RACINE / INSTANTANES / f"{jour}.json").write_text(
            json.dumps(instantane(s, tables, jour, obs, notees, codes, poids, empreinte_courante()), ensure_ascii=False), "utf-8")
    ve_ids = {v["id"] for v in ve}
    pivots = []
    for p in piv:
        titre, k, court = TETE[p["id"]]
        libs = [carte.libelle_issue(p["id"], i) for i in p["issues"]]
        q = {"id": p["id"], "titre": titre, "court": court, "k": k, "theme": THEME[p["id"]], "nature": p["nature"],
             "quand": f"le {dfr(p['date'])}" if p.get("date") else f"de {mfr(p['fenetre'][0])} à {mfr(p['fenetre'][1])}",
             "mois": reseau.idx(p["date"]) if p.get("date") else (reseau.idx(max(p["fenetre"][0], reseau.MOIS[0] + "-01")) + reseau.idx(p["fenetre"][1]) + 1) // 2,
             "issues": p["issues"], "libelles": libs}
        q["phrases"] = [phrase({**p, "libelles": libs}, j) for j in range(len(p["issues"]))]
        q["parents"] = [{"id": reseau.pid(x), "decalage": reseau.dec(x)} for x in p.get("parents", [])]
        q["ctx"] = [x["nom"].lower() for k_, v in sorted(s.get("indicateurs", {}).get("liens", {}).items())
                    for l in v["liens"] if l["noeud"] == p["id"] for x in [v]]
        sg = tables["noeuds"].get(p["id"], {}).get("sigma", .3)
        q["fiabilite"] = "bon" if sg <= .35 else "moyen" if sg <= .55 else "faible"
        pivots.append(q)
    interface = lire_json("data/interface_v1.json") or {"jalons": [], "questions": []}
    lib_j = {j["id"]: j for j in interface.get("jalons", [])}
    v2 = lire_json("modele/jalons/vraisemblances_v2.json")["jalons"]
    defs = {j["id"]: j for j in lire_jsonl("modele/jalons/definitions.jsonl")}
    import jalons as jl
    etats_j = jl.etats(jour)
    jal = []
    for jid, v in sorted(v2.items()):
        d = defs[jid]
        f = d["fenetre"]
        p = noeuds[v["noeud"]]
        jal.append({"id": jid, "lib": (lib_j.get(jid) or {}).get("libelle") or d["observable"][:60], "observable": d["observable"],
                    "quand": mfr(f["debut"]) if f["debut"][:7] == f["fin"][:7] else f"{mfr(f['debut'])} – {mfr(f['fin'])}",
                    "debut": f["debut"], "niveau": d["niveau"], "statut": etats_j.get(jid, (None, "attendu"))[1],
                    "noeud": v["noeud"], "classe": pv.classe_jalon(v),
                    "L": [v["vraisemblances"].get(i, 0.0) for i in p["issues"]],
                    "etat_reseau": p["issues"].index(v["etat_reseau"]["etat"]) if v.get("etat_reseau") else None})
    qs = {}
    for q in interface.get("questions", []):
        m = re.match(r"Q-(EV-[0-9a-zA-Z]+?)(?:-20\d\d-.*)?$", q["id"])
        if m:
            f = lambda a: (lambda x: None if not x else round(x["p"].get("oui", max(x["p"].values()))))(q["auteurs"].get(a))
            qs.setdefault(m.group(1), {"id": m.group(1), "texte": q["texte"], "reseau": f("réseau v0"), "ensemble": f("ensemble direct")})
    variables = []
    for v in ve:
        o = sorted(obs.get(v["id"], {}).items())
        lu = [q for q, mm in s["mesures"].items() if v["id"] in [e.get("noeud") for e in mm["caracteristique"].get("elements", [mm["caracteristique"]])]]
        variables.append({"id": v["id"], "titre": VNOM[v["id"]], "si": VSI[v["id"]], "etats": v["etats"], "definition": v.get("definition"),
                          "observe": [o[-1][0], o[-1][1] if isinstance(o[-1][1], str) else "au moins " + o[-1][1]["au_moins"]] if o else None,
                          "parents": [reseau.pid(x) for x in v.get("parents", [])], "questions": [qs[q] for q in lu if q in qs]})
    hyp = [{"id": h["id"], "enonce": h["enonce"], "rupture": h["probabilite_rupture"], "traitement": h["traitement"]}
           for h in (lire_json("modele/reseau/hypotheses.json") or {}).get("hypotheses", [])]
    return {"version_structure": s.get("version"), "version_tables": tables.get("version"), "etabli_le": jour,
            "mois": reseau.MOIS, "pivots": pivots, "variables": variables, "jalons": jal,
            "preuves_notees": [p["id"] for p in notees], "hypotheses": hyp,
            "hors": [{"id": e["id"], "nom": e["nom"]} for e in lire_json("modele/evenements.json")["evenements"] if e["id"] not in s["mesures"]],
            "k": pv.K, "seuil_ess": reseau.SEUIL_ESS, "seuil_rare": SEUIL_RARE, "tendance": tend,
            "actualite": actualite.liste(90, jour),
            "codes": codes, "variables_codes": vcodes, "poids": poids}


def page(donnees=None):
    """Page de l'organigramme : gabarit et script en ligne ; données en ligne (aperçu) ou lues dans
    data/organigramme_v0.json (page publiée, régénérée chaque nuit)."""
    d = RACINE / "modele/interface/organigramme"
    html = (d / "page.html").read_text("utf-8")
    js = (d / "organigramme.js").read_text("utf-8")
    html = html.replace('<script src="ORGJS"></script>', "<script>\n" + js + "\n</script>")
    if donnees is not None:
        html = html.replace("/*__DONNEES__*/null", json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    return html


def reconstituer():
    """Instantanés passés, reconstitués depuis git (une fois, 16 octobre 2026) : pour chaque jour, la dernière
    version publiée de data/carte_v0.json (mêmes trajectoires du moteur), les observations de ce commit et les
    preuves notées à cette date. Les jours sans nouvelle carte reprennent la précédente : rien n'a changé."""
    import subprocess
    import derive
    log = subprocess.run(["git", "log", "--format=%h %cI", "--", "data/carte_v0.json"], cwd=RACINE,
                         capture_output=True, text=True).stdout.split("\n")
    par_jour = {}
    for l in reversed([x for x in log if x.strip()]):
        h, t = l.split()
        from datetime import datetime
        par_jour[datetime.fromisoformat(t).astimezone().date().isoformat()] = h
    show = lambda h, f: json.loads(subprocess.run(["git", "show", f"{h}:{f}"], cwd=RACINE, capture_output=True,
                                                  text=True).stdout or "null")
    (RACINE / INSTANTANES).mkdir(parents=True, exist_ok=True)
    faits = []
    for jour, h in sorted(par_jour.items()):
        c = show(h, "data/carte_v0.json")
        s = show(h, "modele/reseau/structure_v0.json")
        fich = [show(h, f) for f in reseau.FICHIERS_RESEAU]
        piv = {}
        c["poids"] = c.get("poids") or [1] * len(c["codes"])
        W = sum(c["poids"]) or 1.0
        for i, p in enumerate(c["pivots"]):
            a = [0.0] * len(p["issues"])
            for code, w in zip(c["codes"], c["poids"]):
                x = code[i]
                k = int(x, 36) if p["nature"] == "daté" else p["issues"].index("non" if x == "-" else "oui")
                a[k] += w
            piv[p["id"]] = [round(100 * v / W, 1) for v in a]
        o = show(h, "modele/reseau/observations.json") or {}
        courant = (o.get("etabli_le") or "")[:7]
        maxima = {v["id"] for v in s["variables_etat"] if v.get("agregat") == "maximum"}
        obs = {n: {m: ({"au_moins": e} if n in maxima and courant and m >= courant and isinstance(e, str) else e)
                   for m, e in dd.items()} for n, dd in o.get("etats", {}).items()}   # même règle que reseau.observations
        d = {"jour": jour, "empreinte": derive.empreinte(fich), "version_structure": s.get("version"),
             "version_tables": c.get("version_tables"), "pivots": piv, "observations": obs,
             "preuves": pv.preuves_notees(jour), "reconstitue": f"git {h}"}
        f = RACINE / INSTANTANES / f"{jour}.json"
        if not f.exists():
            f.write_text(json.dumps(d, ensure_ascii=False), "utf-8")
            faits.append(jour)
    return faits


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--reconstituer" in a:
        print("instantanés reconstitués :", ", ".join(reconstituer()) or "aucun")
        sys.exit(0)
    if "--page" in a:
        # Page seule (données lues à l'exécution) ; avec --apercu, données en ligne.
        cible = a[a.index("--page") + 1]
        don = json.loads((RACINE / "data/organigramme_v0.json").read_text("utf-8")) if "--apercu" in a else None
        (RACINE / cible).write_text(page(don), "utf-8")
        print(f"{cible} écrit")
        sys.exit(0)
    nt = int(a[a.index("--tirages") + 1]) if "--tirages" in a else 100
    ntr = int(a[a.index("--trajectoires") + 1]) if "--trajectoires" in a else 40
    sortie = a[a.index("--sortie") + 1] if "--sortie" in a else "data/organigramme_v0.json"
    # L'instantané du jour n'est écrit que pour la sortie publiée (collecte nocturne), jamais pour un essai.
    d = construire(nt, ntr, ecrire_instantane=sortie == "data/organigramme_v0.json" and "--sans-instantane" not in a)
    (RACINE / sortie).write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), "utf-8")
    print(f"{sortie} : {len(d['codes'])} trajectoires, {len(d['pivots'])} pivots, {len(d['jalons'])} jalons")
