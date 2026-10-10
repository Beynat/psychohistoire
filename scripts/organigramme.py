"""Données de l'organigramme (feuille de route, étape 8) : écrit data/organigramme_v0.json, lu par reseau.html.

Usage : python scripts/organigramme.py [--tirages N] [--trajectoires N] [--sortie FICHIER]
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
"""
import json
import random
import re
import sys
from datetime import date

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
 "PV-POURVOI": ("Arrêt de cassation sur le pourvoi de Marine Le Pen, au 12 mars 2027", None, "arrêt de cassation"),
 "PV-ECOLO": ("Choix des écologistes pour 2027", None, "choix des écologistes"),
 "PV-BLOC": ("Candidatures au centre (Philippe, Attal)", None, "candidatures au centre"),
 "PV-GAUCHE": ("Nombre de candidats de gauche", None, "candidats de gauche"),
 "PV-LEPEN": ("Marine Le Pen sur la liste des candidats", 0, "Le Pen candidate"),
 "PV-DUEL": ("Duel du second tour", None, "duel du second tour"),
 "PV-VAINQ": ("Président élu", None, "président élu"),
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
VSI = {"VE-POP": "la popularité du président est ", "VE-MOBIL": "la mobilisation sociale est ", "VE-ECART": "l'écart de taux est ",
       "VE-SOND": "le 2e bloc dans les sondages est ", "VE-RN": "le RN est à ", "VE-LYCEE": "la mobilisation lycéenne est "}
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


def phrase(p, k):
    pid, l = p["id"], p["libelles"][k]
    if pid in CAS:
        return "Si " + CAS[pid].get(l, l)
    if pid == "PV-DUEL":
        return "Si le second tour oppose " + ("un autre duel" if l == "autre duel" else l.replace(" – ", " et ").replace("RN et", "le RN et"))
    if pid == "PV-VAINQ":
        return "Si le président élu est " + ("un autre candidat" if l == "autre" else "le candidat du RN" if l == "RN" else l)
    return "Si " + (SI[pid][k] if pid in SI else PREFIXE[pid] + l)


def construire(tirages=100, trajectoires=40, graine=20261010):
    import carte
    s = lire_json("modele/reseau/structure_v0.json")
    tables = lire_json("modele/reseau/tables_v0.json")
    obs = reseau.observations(s)
    reseau.PRIORS = reseau.lois_a_priori(s, tables, obs)
    reseau.CHOCS = reseau.chocs_retenus()
    jour = date.today().isoformat()
    notees = pv.preuves_notees(jour)
    noeuds = reseau.noeuds_de(s)
    piv, ve = s["pivots"], s["variables_etat"]
    rng = random.Random(graine)
    codes, vcodes, poids = [], [], []
    for _ in range(tirages):
        params = reseau.perturber(tables, rng)
        for _ in range(trajectoires):
            t = reseau.simuler(s, params, obs, rng)
            codes.append("".join(str(p["issues"].index(pv.issue_noeud(t, p["id"], p))) for p in piv))
            vcodes.append("".join(str(v["etats"].index(e)) for v in ve for e in t[v["id"]]))
            poids.append(round(pv.poids(notees, t, noeuds), 6) if notees else 1)
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
            "k": pv.K, "seuil_ess": reseau.SEUIL_ESS, "codes": codes, "variables_codes": vcodes, "poids": poids}


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


if __name__ == "__main__":
    a = sys.argv[1:]
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
    d = construire(nt, ntr)
    (RACINE / sortie).write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), "utf-8")
    print(f"{sortie} : {len(d['codes'])} trajectoires, {len(d['pivots'])} pivots, {len(d['jalons'])} jalons")
