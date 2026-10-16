"""Tables provisoires pour pondérer les cas du gabarit (16 octobre 2026) : états nouveaux sans loi élicitée.
VE-SOND : rester 70 %, le reste réparti également, quel que soit le cas ; enfants : cas « serré » = moyenne des cas
« centre » et « gauche » ; PV-SOUTIEN : loi uniforme sur les issues permises ; PV-DUEL : PV-SOUTIEN sans effet."""
import json, itertools, sys
sys.path.insert(0, '/home/claude/psychohistoire/scripts')
import tables, reseau
from commun import lire_json
S = lire_json('modele/reseau/structure_v0.json')
T = lire_json('modele/reseau/tables_v0.json')
N = reseau.noeuds_de(S)
moy = lambda a, b: {k: (a[k] + b[k]) / 2 for k in a} if isinstance(a, dict) else (a + b) / 2
def provisoire(nid):
    n = N[nid]
    cles = tables.cas_du_noeud(n, N)
    if nid == 'VE-SOND':
        out = {}
        for c in cles:
            prec = c.split('|')[0].split('=')[1]
            out[c] = {e: (.7 if e == prec else .1) for e in n['etats']}
        return out
    if nid == 'PV-SOUTIEN':
        out = {}
        for c in cles:
            eco = dict(x.split('=') for x in c.split('|'))['PV-ECOLO']
            ex = n['exclusions']['PV-ECOLO'].get(eco, [])
            ok = [i for i in n['issues'] if i not in ex]
            out[c] = {i: (1 / len(ok) if i in ok else 0.0) for i in n['issues']}
        return out
    old = T['noeuds'][nid]['cas']
    out = {}
    for c in cles:
        parts = [x for x in c.split('|') if not x.startswith('PV-SOUTIEN=')]
        k = '|'.join(parts)
        if k in old:
            out[c] = old[k]
        else:
            a = '|'.join(p.replace('VE-SOND=serré', 'VE-SOND=centre') for p in parts)
            b = '|'.join(p.replace('VE-SOND=serré', 'VE-SOND=gauche') for p in parts)
            out[c] = moy(old[a], old[b])
    return out
for nid in ['VE-SOND', 'PV-ECOLO', 'PV-BLOC', 'PV-GAUCHE', 'PV-SOUTIEN', 'PV-DUEL']:
    T['noeuds'][nid] = {**T['noeuds'].get(nid, {"sigma": .3}), 'cas': provisoire(nid)}
json.dump(T, open('/tmp/claude-0/elic16/tables_provisoires.json', 'w'), ensure_ascii=False)
_lire = tables.lire_json
tables.lire_json = lambda f: T if f.endswith('tables_v0.json') else _lire(f)
g = tables.gabarit_cas(['VE-SOND', 'PV-ECOLO', 'PV-BLOC', 'PV-GAUCHE', 'PV-SOUTIEN', 'PV-DUEL'])
g['lecture'] += (" Note du 16 octobre 2026 : l'état « serré » de VE-SOND et le nœud PV-SOUTIEN sont nouveaux ; les « poids_reseau » "
                 "sont calculés avec des lois provisoires neutres (VE-SOND : 70 % de maintien, le reste réparti également ; PV-SOUTIEN : "
                 "issues permises également probables), pas avec un avis : ils indiquent seulement quels cas existent et comptent.")
json.dump(g, open('/tmp/claude-0/elic16/gabarit_cas.json', 'w'), ensure_ascii=False, indent=1)
print({k: len(v['cas']) for k, v in g['noeuds'].items()}, list(g['direct']))
