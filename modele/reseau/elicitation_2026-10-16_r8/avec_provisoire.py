"""Lance un script de tables.py ou retours.py avec les tables provisoires (états nouveaux sans loi agrégée)."""
import json, runpy, sys
sys.path.insert(0, '/home/claude/psychohistoire/scripts')
import tables, commun
T = json.load(open('/tmp/claude-0/elic16/tables_provisoires.json'))
_l = commun.lire_json
def lire(f):
    return T if str(f).endswith('tables_v0.json') else _l(f)
tables.lire_json = lire
import reseau; reseau.lire_json = lire
script, sys.argv = sys.argv[1], sys.argv[1:]
runpy.run_path(script, run_name='__main__')
