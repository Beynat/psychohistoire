"""Maquette d'organigramme v3 : titres en forme d'événement, effets des liens et des jalons en clair."""
import json, math, sys
C = json.load(open('data/carte_v0.json')); D = json.load(open('data/interface_v1.json'))
P = C['pivots']; N = len(C['codes']); IX = {p['id']: i for i, p in enumerate(P)}
VE = {"VE-POP": "popularité", "VE-MOBIL": "mobilisation", "VE-ECART": "écart OAT-Bund", "VE-SOND": "2e bloc des sondages", "VE-RN": "intentions RN", "VE-LYCEE": "lycées"}
M = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
dfr = lambda d: f"{int(d[8:10])} {M[int(d[5:7])-1]} {d[:4]}"
mfr = lambda d: f"{M[int(d[5:7])-1]} {d[:4]}"
# Titre (événement) et issue affichée ; None = pivot à plusieurs issues, toutes listées.
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
def phrase(a, s_):
    pid = P[a]['id']; l = P[a]['libelles'][s_]
    if pid in CAS: return "Si " + CAS[pid].get(l, l)
    if pid == "PV-DUEL": return "Si le second tour oppose " + ("un autre duel" if l == "autre duel" else l.replace(" – ", " et ").replace("RN et", "le RN et"))
    if pid == "PV-VAINQ": return "Si le président élu est " + ("un autre candidat" if l == "autre" else "le candidat du RN" if l == "RN" else l)
    return "Si " + (SI[pid][s_] if pid in SI else PREFIXE[pid] + P[a]['libelles'][s_])
S = json.load(open('modele/reseau/structure_v0.json')); TB = json.load(open('modele/reseau/tables_v0.json'))
VT = json.load(open('/tmp/claude-0/-home-claude-psychohistoire/23dfa29c-52e0-5c8e-bc30-47a4d773b38e/scratchpad/ve_traj.json'))
VDEF = {v['id']: v for v in S['variables_etat']}
VNOM = {"VE-POP": "Popularité du président", "VE-MOBIL": "Mobilisation sociale", "VE-ECART": "Écart de taux France-Allemagne",
        "VE-SOND": "Deuxième bloc dans les sondages", "VE-RN": "Intentions de vote RN", "VE-LYCEE": "Mobilisation lycéenne"}
VSI = {"VE-POP": "la popularité du président est ", "VE-MOBIL": "la mobilisation sociale est ", "VE-ECART": "l'écart de taux est ",
       "VE-SOND": "le 2e bloc dans les sondages est ", "VE-RN": "le RN est à ", "VE-LYCEE": "la mobilisation lycéenne est "}
MOIS = C['mois']
def mois_de(p):
    if p.get('date'): return min(MOIS.index(p['date'][:7]), len(MOIS) - 1)
    a, b = MOIS.index(max(p['fenetre'][0][:7], MOIS[0])), MOIS.index(min(p['fenetre'][1][:7], MOIS[-1]))
    return (a + b + 1) // 2
THEME = {}
for th, ids in {"budget": ["PV-CENSURE1a", "PV-BUDGET", "PV-CENSURE1b", "PV-GOUV", "PV-DISSOL1"],
                "candidatures": ["PV-AUDIENCE", "PV-POURVOI", "PV-LEPEN", "PV-ECOLO", "PV-GAUCHE", "PV-BLOC"],
                "election": ["PV-DUEL", "PV-VAINQ"], "apres": ["PV-DISSOL2a", "PV-DISSOL2b", "PV-MAJOR", "PV-CENSURE2"],
                "dette": ["PV-NOTE", "PV-PDE", "PV-TPI"]}.items():
    for i in ids: THEME[i] = th
def etat(i, t):
    ch = C['codes'][t][i]
    return int(ch) if P[i]['nature'] == 'daté' else (1 if ch == '-' else 0)
ET = [[etat(i, t) for t in range(N)] for i in range(len(P))]
MARG = [[100 * sum(1 for t in range(N) if ET[i][t] == k) / N for k in range(len(p['issues']))] for i, p in enumerate(P)]
TOP = [sorted(range(len(p['issues'])), key=lambda q: -MARG[i][q])[:3] for i, p in enumerate(P)]
def cond(c, k, a, s):
    ts = [t for t in range(N) if ET[a][t] == s]
    return (100 * sum(1 for t in ts if ET[c][t] == k) / len(ts), len(ts)) if ts else (None, 0)
def lib_tete(i):
    t = TETE[P[i]['id']]
    return t[2]
noeuds = []
for i, p in enumerate(P):
    titre, k, court = TETE[p['id']]
    quand = f"le {dfr(p['date'])}" if p.get('date') else f"de {mfr(p['fenetre'][0])} à {mfr(p['fenetre'][1])}"
    n = {"id": p['id'], "titre": titre, "court": court, "quand": quand, "theme": THEME[p['id']]}
    if k is not None:
        n["p"] = round(MARG[i][k], 1)
    else:
        d = sorted(((p['libelles'][j], round(v, 1)) for j, v in enumerate(MARG[i])), key=lambda x: -x[1])
        n["issues"] = [x for x in d if x[1] >= 3][:4]
        n["reste"] = round(sum(x[1] for x in d if x not in n["issues"]), 1)
    n["ctx"] = [VE[x['id']] for x in p['parents'] if x['id'] in VE] + [x['nom'].lower() for x in p.get('indicateurs', [])]
    # Ce qui pèse : effet de chaque pivot parent sur l'événement affiché
    eff = []
    for x in p['parents']:
        if x['id'] not in IX: continue
        a = IX[x['id']]; ta = TETE[x['id']]
        def ecart(j):
            vs = [cond(i, j, a, s_) for s_ in range(len(P[a]['issues']))]
            vs = [v for v, nn in vs if nn >= 60]
            return max(vs) - min(vs) if len(vs) > 1 else 0
        cible = k if k is not None else (max(range(len(p['issues'])), key=ecart) if ta[1] is not None else max(range(len(p['issues'])), key=lambda j: MARG[i][j]))
        cas = []
        for s_ in range(len(P[a]['issues'])):
            v, nn = cond(i, cible, a, s_)
            if nn >= 60:
                ts = [t for t in range(N) if ET[a][t] == s_]
                cas.append({"si": phrase(a, s_), "p": round(v), "freq": round(100 * nn / N), "pr": round(100 * nn / N, 2), "pv": v,
                            "dist": [round(100 * sum(1 for t in ts if ET[i][t] == q) / len(ts)) for q in TOP[i]]})
        if ta[1] is not None: cas.sort(key=lambda c: c['si'] != phrase(a, ta[1]))
        else: cas.sort(key=lambda c: -c['freq'])
        eff.append({"de": x['id'], "facteur": TETE[x['id']][0], "cible": None if k is not None else p['libelles'][cible], "cas": cas[:5]})
    for x in p['parents']:
        if x['id'] not in VDEF: continue
        v = x['id']; m = max(1, mois_de(p) - x.get('decalage', 0)); cible = k if k is not None else max(range(len(p['issues'])), key=lambda j: MARG[i][j])
        cas = []
        for s_, lib in enumerate(VDEF[v]['etats']):
            ts = [t for t in range(N) if VT[v][t][m] == str(s_)]
            if len(ts) >= 60:
                cas.append({"si": "Si " + VSI[v] + lib, "p": round(100 * sum(1 for t in ts if ET[i][t] == cible) / len(ts)), "freq": round(100 * len(ts) / N),
                            "pr": round(100 * len(ts) / N, 2), "pv": 100 * sum(1 for t in ts if ET[i][t] == cible) / len(ts),
                            "dist": [round(100 * sum(1 for t in ts if ET[i][t] == q) / len(ts)) for q in TOP[i]]})
        if len(cas) > 1:
            eff.append({"de": v, "facteur": VNOM[v] + f" ({M[int(MOIS[m][5:7]) - 1]} {MOIS[m][:4]})", "cible": None if k is not None else p['libelles'][cible], "cas": cas})
    n["ctx"] = [VE[x['id']] for x in p['parents'] if x['id'] in VE and not any(e['de'] == x['id'] for e in eff)] + [x['nom'].lower() for x in p.get('indicateurs', [])]
    for e in eff:
        e["couvert"] = round(sum(c_['pr'] for c_ in e['cas']), 1)
        e["ecart"] = max(c_['p'] for c_ in e['cas']) - min(c_['p'] for c_ in e['cas']) if e['cas'] else 0
    if k is None:
        n["top"] = [p['libelles'][q] for q in TOP[i]]
    sg = TB['noeuds'].get(p['id'], {}).get('sigma', .3)
    n["fiabilite"] = {"sigma": sg, "niveau": "bon" if sg <= .35 else "moyen" if sg <= .55 else "faible"}
    n["effets"] = eff
    n["jalons"] = []
    noeuds.append(n)
for v in S['variables_etat']:
    vid = v['id']; dist = [[round(100 * sum(1 for t in range(N) if VT[vid][t][m] == str(e)) / N) for e in range(len(v['etats']))] for m in range(len(MOIS))]
    ob = sorted((C['variables'][[x['id'] for x in C['variables']].index(vid)]['observe'] or {}).items())
    qs = [q for q, mm in S['mesures'].items() if vid in [mm['caracteristique'].get('noeud')] + [e.get('noeud') for e in mm['caracteristique'].get('elements', [])]]
    noeuds.append({"id": vid, "variable": True, "titre": VNOM[vid], "court": VNOM[vid].lower(), "etats": v['etats'], "dist": dist, "mois": MOIS,
                   "observe": ob[-1] if ob else None, "definition": v.get('definition'), "theme": "variable",
                   "parents": [(x if isinstance(x, str) else x['id']) for x in v.get('parents', [])], "questions": qs, "jalons": [], "effets": [], "ctx": []})
IXN = {n['id']: k for k, n in enumerate(noeuds)}
# Jalons : rangés sous le pivot qu'ils informent ; effet sur l'événement affiché (k = 0,5 en log, appliqué après validation).
o = lambda x: x / (1 - x); inv = lambda x: x / (1 + x)
def issue_cible(cible):
    nn = cible.get('noeud')
    if nn not in IX: return None
    p = P[IX[nn]]; v = cible['issue']
    if nn == 'PV-MAJOR' and v in ('oui', 'non'):   # EV-17 : « moins de 289 sièges » ; « non » = majorité absolue
        return (IX[nn], 1 if v == 'oui' else 0)
    k = p['issues'].index(v) if v in p['issues'] else (0 if v == 'oui' else len(p['issues']) - 1 if v == 'non' else
         next((k for k, l in enumerate(p['libelles']) if l in v), None))
    return None if k is None else (IX[nn], k)
V2 = json.load(open('modele/jalons/vraisemblances_v2.json'))['jalons']
def options_de(i, dist):
    kt = TETE[P[i]['id']][1]
    if kt is not None:
        return [[TETE[P[i]['id']][2], round(100 * MARG[i][kt] / 100 * 1, 0) if False else round(MARG[i][kt]), round(100 * dist[kt])]]
    ordre = sorted(range(len(dist)), key=lambda q: -MARG[i][q])
    return [[P[i]['libelles'][q], round(MARG[i][q]), round(100 * dist[q])] for q in ordre if MARG[i][q] >= 3][:4]
ENFANTS = {i: [c for c, pp in enumerate(P) if any(x['id'] == P[i]['id'] for x in pp['parents'])] for i in range(len(P))}
for j in D['jalons']:
    v2 = V2[j['id']]
    i = IX[v2['noeud']]
    quand = mfr(j['fenetre']['debut']) if j['fenetre']['debut'][:7] == j['fenetre']['fin'][:7] else f"{mfr(j['fenetre']['debut'])} – {mfr(j['fenetre']['fin'])}"
    e = {"id": j['id'], "lib": j['libelle'], "quand": quand, "debut": j['fenetre']['debut'], "statut": j['statut'], "niveau": j['niveau'], "observable": j['observable']}
    p0 = [v / 100 for v in MARG[i]]
    if v2['etat_reseau']:
        k = P[i]['issues'].index(v2['etat_reseau']['etat'])
        e["etat_reseau"] = P[i]['libelles'][k]
        e["pobs"] = round(MARG[i][k])
        apres = [1.0 if q == k else 0.0 for q in range(len(p0))]
        # conséquences dans le réseau : enfants sachant cet état
        cons = []
        ts = [t for t in range(N) if ET[i][t] == k]
        for c in ENFANTS[i]:
            kc = TETE[P[c]['id']][1]
            qs_ = [kc] if kc is not None else sorted(range(len(P[c]['issues'])), key=lambda q: -MARG[c][q])[:3]
            for q in qs_:
                av = MARG[c][q]; ap = 100 * sum(1 for t in ts if ET[c][t] == q) / len(ts) if ts else av
                if abs(ap - av) >= 3:
                    cons.append([TETE[P[c]['id']][2] + ("" if kc is not None else " : " + P[c]['libelles'][q]), round(av), round(ap)])
        e["consequences"] = cons
    else:
        L = [v2['vraisemblances'][iss] for iss in P[i]['issues']]
        e["pobs"] = round(100 * sum(p * l for p, l in zip(p0, L)))
        w = [p * l ** .5 for p, l in zip(p0, L)]; z = sum(w)
        apres = [x / z for x in w]
    e["options"] = options_de(i, apres)
    e["pivot_titre"] = TETE[P[i]['id']][0]
    noeuds[i]["jalons"].append(e)
for n in noeuds: n["jalons"].sort(key=lambda j: j['debut'])
# questions de la banque : prévisions du réseau et de l'ensemble
QS = {}
for q in D['questions']:
    import re as _re
    m_ = _re.match(r'Q-(EV-[0-9a-zA-Z]+?)(?:-20\d\d-.*)?$', q['id'])
    if m_:
        f = lambda a: (lambda v: None if not v else round(v['p'].get('oui', max(v['p'].values()))))(q['auteurs'].get(a))
        QS.setdefault(m_.group(1), {"texte": q['texte'], "echeance": q['echeance'], "reseau": f('réseau v0'), "ensemble": f('ensemble direct')})
for n in noeuds:
    if n.get('variable'): n['questions'] = [dict(id=q, **QS[q]) for q in n['questions'] if q in QS]
EVS = json.load(open('modele/evenements.json'))['evenements']
hors = [{"id": e['id'], "nom": e['nom'], "pool": e['pool']} for e in EVS if e['id'] not in S['mesures']]
liens = []
for c, p in enumerate(P):
    for x in p['parents']:
        if x['id'] in IX:
            ef = next(e for e in noeuds[c]['effets'] if e['de'] == x['id'])
            vs = [c_['p'] for c_ in ef['cas']]; d = max(vs) - min(vs) if len(vs) > 1 else 0
            if TETE[x['id']][1] is not None and len(vs) == 2:
                d2 = vs[0] - vs[1]; lab = f"{'+' if d2 >= 0 else '−'}{abs(d2)} pts"
            else:
                lab = f"jusqu'à {d} pts"
            liens.append({"de": x['id'], "vers": p['id'], "label": lab, "fort": d >= 10})
for n in noeuds:
    if n.get('variable'):
        for pa in n['parents']:
            liens.append({"de": pa, "vers": n['id'], "label": "", "fort": False, "variable": True})
for c, p in enumerate(P):
    for x in p['parents']:
        if x['id'] in VDEF:
            ef = next((e for e in noeuds[c]['effets'] if e['de'] == x['id']), None)
            vs = [c_['p'] for c_ in ef['cas']] if ef else []
            liens.append({"de": x['id'], "vers": p['id'], "label": "", "fort": bool(vs) and max(vs) - min(vs) >= 10, "variable": True})
json.dump({"noeuds": noeuds, "liens": liens, "hors": hors}, open(sys.argv[1], 'w'), ensure_ascii=False)
for n in noeuds: print(n['id'], n.get('p'), [(e['facteur'], e['cible'], [(c['si'], c['p']) for c in e['cas']]) for e in n['effets']])
