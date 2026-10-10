"""Rejoue les trajectoires de scripts/carte.py (même graine) en gardant l'état mensuel des variables d'état."""
import json, random, sys
sys.path.insert(0, 'scripts')
import reseau
from commun import lire_json
s = lire_json("modele/reseau/structure_v0.json"); tables = lire_json("modele/reseau/tables_v0.json")
obs = reseau.observations(); reseau.FAITS = reseau.faits_retenus()
rng = random.Random(20261010); ve = [v['id'] for v in s['variables_etat']]
etats = {v['id']: v['etats'] for v in s['variables_etat']}
out = {v: [] for v in ve}
for _ in range(100):
    params = reseau.perturber(tables, rng)
    for _ in range(40):
        t = reseau.simuler(s, params, obs, rng)
        for v in ve:
            out[v].append("".join(str(etats[v].index(e)) for e in t[v]))
json.dump(out, open(sys.argv[1], 'w'))
print(len(out['VE-POP']))
