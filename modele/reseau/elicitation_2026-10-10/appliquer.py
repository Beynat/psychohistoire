"""Agrège E4-E6 et applique la chaîne présidentielle v0.4 à la structure et aux tables."""
import json, math, statistics, sys
sys.path.insert(0, 'scripts')
from tables import moy_loi, dispersion, lo
CH = '/tmp/claude-0/-home-claude-psychohistoire/23dfa29c-52e0-5c8e-bc30-47a4d773b38e/scratchpad/chantier/'
R = [json.load(open(CH + f'E{i}.json')) for i in (4, 5, 6)]
from tables import moy_mult as gm   # zéro isolé ramené au plancher (étape 1) ; aucun zéro isolé chez E4-E6
def loi(path):
    ls = []
    for r in R:
        x = r
        for k in path: x = x[k]
        ls.append({k: float(v) for k, v in x.items() if isinstance(v, (int, float))})
    return moy_loi(ls), dispersion(ls)
def mult(path):
    ms = []
    for r in R:
        x = r
        for k in path: x = x[k]
        ms.append(x)
    return {k: round(gm([float(m[k]) for m in ms]), 4) for k in ms[0] if isinstance(ms[0][k], (int, float))}
sp = 'modele/reseau/structure_v0.json'; tp = 'modele/reseau/tables_v0.json'
s = json.load(open(sp)); t = json.load(open(tp)); P = {p['id']: p for p in s['pivots']}
N = lambda k: [r['noeuds'][k] for r in R]
# audience
l = [lo(float(n['p_fenetre'])) for n in N('PV-AUDIENCE')]
t['noeuds']['PV-AUDIENCE'] = {"p_fenetre": round(1 / (1 + math.exp(-statistics.mean(l))), 4), "multiplicateurs": {}, "sigma": round(max(statistics.pstdev(l), .3), 3)}
# pourvoi : au 12 mars, loi selon l'audience
P['PV-POURVOI'].update(nom="Issue du pourvoi de Marine Le Pen au 12 mars 2027 (fin du dépôt des parrainages)", date="2027-03-12", conditionnelle="PV-AUDIENCE")
c, d = {}, []
for e in ("oui", "non"):
    c[e], dd = loi(['noeuds', 'PV-POURVOI', 'conditionnelle', 'PV-AUDIENCE', e]); d.append(dd)
t['noeuds']['PV-POURVOI'] = {"conditionnelle": c, "base": c["non"], "multiplicateurs": {}, "sigma": round(max(statistics.mean(d), .3), 3)}
# candidature
P['PV-LEPEN'].update(date="2027-03-26", date_note="liste officielle des candidats, au plus tard le 26 mars 2027", conditionnelle="PV-POURVOI")
c, d = {}, []
for e in P['PV-POURVOI']['issues']:
    c[e], dd = loi(['noeuds', 'PV-LEPEN', 'conditionnelle', 'PV-POURVOI', e]); d.append(dd)
m = {e: mult(['noeuds', 'PV-LEPEN', 'multiplicateurs', 'VE-RN (février 2027)', e]) for e in ("< 30 %", "> 35 %")}
t['noeuds']['PV-LEPEN'] = {"conditionnelle": c, "base": c["pas d'arrêt"], "multiplicateurs": {"VE-RN": m}, "sigma": round(max(statistics.mean(d), .3), 3)}
# duel
P['PV-DUEL']['conditionnelle'] = "PV-BLOC"
c, d = {}, []
for e in P['PV-BLOC']['issues']:
    c[e], dd = loi(['noeuds', 'PV-DUEL', 'conditionnelle', 'PV-BLOC', e]); d.append(dd)
t['noeuds']['PV-DUEL'] = {"conditionnelle": c, "base": c["Philippe seul"], "sigma": round(max(statistics.mean(d), .3), 3), "multiplicateurs": {
    "PV-LEPEN": {"non candidate": mult(['noeuds', 'PV-DUEL', 'multiplicateurs', 'PV-LEPEN', 'non candidate (Bardella candidat)'])},
    "VE-SOND": {e: mult(['noeuds', 'PV-DUEL', 'multiplicateurs', 'VE-SOND (avril 2027)', e]) for e in ("gauche", "droite")}}}
# vainqueur
P['PV-VAINQ']['parents'] = ["PV-DUEL", {"id": "VE-RN", "decalage": 1}, "PV-LEPEN"]
c, d = {}, []
for e in P['PV-DUEL']['issues']:
    x, dd = loi(['noeuds', 'PV-VAINQ', 'conditionnelle', 'PV-DUEL', e]); d.append(dd)
    c[e] = {k: x.get(k, 0.0) for k in P['PV-VAINQ']['issues']}
t['noeuds']['PV-VAINQ'] = {"conditionnelle": c, "base": c["RN-PHI"], "sigma": round(max(statistics.mean(d), .3), 3), "multiplicateurs": {
    "PV-LEPEN": {"non candidate": mult(['noeuds', 'PV-VAINQ', 'multiplicateurs', 'PV-LEPEN', 'non candidate (Bardella candidat)'])},
    "VE-RN": {e: mult(['noeuds', 'PV-VAINQ', 'multiplicateurs', 'VE-RN (mars 2027)', e]) for e in ("< 30 %", "> 35 %")}}}
# mesure EV-20 : issue au 31 mars si pas d'arrêt au 12 mars
x, _ = loi(['mesures', 'EV-20', 'table', "pas d'arrêt au 12 mars"])
t['mesures']['EV-20']["pas d'arrêt"] = {k: round(100 * v, 2) for k, v in x.items()}
s['mesures']['EV-20']['question'] = "si aucun arrêt n'est rendu au 12 mars 2027, loi de l'issue au 31 mars 2027"
# avis directs
t['direct']['EV-21'] = round(100 * statistics.median(float(r['direct']['EV-21']['p']) for r in R), 1)
t['direct']['EV-40a'] = round(100 * statistics.median(float(r['direct']['EV-40a']['p']) for r in R), 1)
t['direct']['EV-20'] = {k: round(100 * statistics.median(float(r['direct']['EV-20']['loi'][k]) for r in R), 1) for k in R[0]['direct']['EV-20']['loi']}
s['version'] = "structure v0.4 (10 octobre 2026, chaîne présidentielle réélicitée : pourvoi au 12 mars, liste au 26 mars, duel conditionnel aux candidatures du centre, vainqueur selon Le Pen ou Bardella)"
t['version'] = "tables v0.4 (E1, E2, E3 ; chaîne présidentielle par E4, E5 Opus et E6 Sonnet sur dossier sourcé, 10 octobre 2026) ; dissolution après l'élection découpée"
json.dump(s, open(sp, 'w'), ensure_ascii=False, indent=1); json.dump(t, open(tp, 'w'), ensure_ascii=False, indent=1)
for k in ('PV-AUDIENCE', 'PV-POURVOI', 'PV-LEPEN'): print(k, json.dumps(t['noeuds'][k], ensure_ascii=False)[:500])
print('direct', t['direct']['EV-21'], t['direct']['EV-40a'], t['direct']['EV-20'])
