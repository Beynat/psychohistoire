"""Tests des scripts de la phase 1 sur données fictives. Usage : python scripts/tests.py"""
import json
import random
import sys
import shutil
import tempfile
from pathlib import Path

import commun
import notation
import registre


def test_quantiles_et_marche():
    s = [(f"2010-{m:02d}", float(m)) for m in range(1, 13)]
    var = commun.variations(s, 1)
    assert var == [1.0] * 11
    assert commun.quantile([1, 2, 3, 4, 5], 50) == 3
    assert commun.proba_au_dessus(10, 11, var) == 1.0
    assert commun.mois_suivant("2026-11", 3) == "2027-02"
    assert commun.ecart_mois("2026-08", "2027-01") == 5
    assert commun.trimestre("2026-11-30") == "2026-T4"


def test_scores():
    assert abs(notation.brier({"oui": 70, "non": 30}, "oui") - 0.09) < 1e-9   # (p − y)², relecture 12, S1
    assert notation.brier({"a": 100, "b": 0, "c": 0}, "a") == 0
    m = notation.murphy([(0.9, True)] * 9 + [(0.9, False)] + [(0.1, False)] * 9 + [(0.1, True)])
    assert m["fiabilite"] == 0 and abs(m["incertitude"] - 0.25) < 1e-9


def test_grappes_sous_hypothese_nulle():
    rnd = random.Random(3)
    rejets = 0
    for _ in range(400):
        d = {g: [rnd.gauss(0, .1) for _ in range(5)] for g in range(30)}
        rejets += notation.test_grappes(d)["p_unilaterale"] < 0.10
    assert 0.05 < rejets / 400 < 0.15, rejets / 400


def test_brier_periode_commune():
    """Relecture 11, J1 : mêmes probabilités aux mêmes dates, plus deux prévisions anciennes pour A ;
    sur la période commune, les deux Brier pondérés sont égaux."""
    import notation
    commun_ = [{"emise": "2027-01-02T08:00:00+01:00", "probabilites": {"oui": 30, "non": 70}},
               {"emise": "2027-02-01T08:00:00+01:00", "probabilites": {"oui": 60, "non": 40}}]
    a = [{"emise": "2026-11-02T08:00:00+01:00", "probabilites": {"oui": 5, "non": 95}},
         {"emise": "2026-12-01T08:00:00+01:00", "probabilites": {"oui": 10, "non": 90}}] + commun_
    debut = max(a[0]["emise"][:10], commun_[0]["emise"][:10])
    ba = notation.brier_pondere(a, "oui", debut, "2027-03-31")
    bb = notation.brier_pondere(commun_, "oui", debut, "2027-03-31")
    assert abs(ba - bb) < 1e-12, (ba, bb)
    assert notation.brier_pondere(a, "oui", a[0]["emise"][:10], "2027-03-31") > ba  # l'artefact corrigé


def test_bout_en_bout():
    """Relecture 12, S15 : un cycle fictif de bout en bout sur une copie du dépôt (gel, questions,
    comparateurs, prévisions de deux auteurs, propositions, résolution, bilan). Vérifie : une seule
    grappe par événement (fenêtre et mensuelles), cycles d'essai ignorés, test de 8.6 limité à P2b et
    P2c, période commune sur le chemin du bilan, un avis par agent."""
    import subprocess
    racine = Path(__file__).resolve().parent.parent
    tmp = Path(tempfile.mkdtemp()) / "depot"
    shutil.copytree(racine, tmp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    try:
        env = {**__import__("os").environ, "PYTHONPATH": str(tmp / "scripts")}
        def run(*a):
            r = subprocess.run([sys.executable, *a], cwd=tmp, env=env, capture_output=True, text=True)
            assert r.returncode == 0, r.stderr[-2000:]
            return r
        (tmp / "modele/statut.json").write_text(json.dumps({"definitif": True}))
        run("scripts/geler.py", "2026-11-01", "2026-11", "--essai")
        run("scripts/questions.py", "2026-11-01", "2026-11")
        run("scripts/comparateurs.py", "2026-11", "registre/e2e.jsonl")
        banque = json.loads((tmp / "data/cycles/2026-11/questions.json").read_text())
        g = {q["id"]: q["grappe"] for q in banque["questions"]}
        assert g["Q-EV-15"] == g["Q-EV-15-2026-11"] == "EV-15" if "Q-EV-15-2026-11" in g else g["Q-EV-15"] == "EV-15"
        assert g["Q-EV-01"] == g["Q-EV-01-2026-11"]
        # Deux auteurs : l'ensemble prévoit dès novembre, le modèle à partir de décembre avec les mêmes valeurs.
        lignes = []
        for qid, pool_ok in (("Q-EV-15", True), ("Q-EV-30", False)):
            for auteur, dates in (("ensemble direct", ("2026-11-02", "2026-12-01")), ("modèle", ("2026-12-01",))):
                for k, d in enumerate(dates):
                    p = 30 if d == "2026-12-01" else 5
                    lignes.append({"question": qid, "probabilites": {"oui": p, "non": 100 - p}, "piste": "protocole", "phase": 1,
                                   "auteur": auteur, "origine": "cycle 2026-11", "donnees": "t",
                                   "emise": f"{d}T08:00:00+01:00"})
        with (tmp / "registre/e2e.jsonl").open("a", encoding="utf-8") as f:
            for l in lignes:
                f.write(json.dumps(l, ensure_ascii=False) + "\n")
        props = [{"proposition": True, "question": q, "issue": "non", "source": "s", "agent": a, "date_fait": "2026-12-31",
                  "emise": "2027-01-05T08:00:00+01:00"} for q in ("Q-EV-15", "Q-EV-30") for a in ("A", "A", "B")]
        (tmp / "registre/propositions_e2e.jsonl").write_text("\n".join(json.dumps(x) for x in props) + "\n")
        code = (
            "import json, resolution, notation\n"
            "r = resolution.resoudre('registre/e2e.jsonl', '2027-01-10')\n"
            # L'horloge réelle date la résolution d'aujourd'hui : on la recale au 10 janvier 2027 pour la notation.
            "import pathlib\n"
            "f = pathlib.Path('registre/resolutions_e2e.jsonl')\n"
            "L = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]\n"
            "f.write_text(''.join(json.dumps({**l, 'emise': '2027-01-10T08:00:00+01:00'}) + '\\n' for l in L))\n"
            "b = notation.bilan('registre/e2e.jsonl', 'ensemble direct', '2027-02-01')\n"
            "print(json.dumps({'r': r, 'c': b['comparaisons']['modèle']}, ensure_ascii=False))")
        out = json.loads(run("-c", code).stdout.strip().splitlines()[-1])
        res = {x["question"]: x for x in out["r"]}
        assert res["Q-EV-15"]["issue"] == res["Q-EV-30"]["issue"] == "non"
        assert all(res[q]["methode"] == "deux agents concordants" for q in ("Q-EV-15", "Q-EV-30"))
        # Q-EV-30 est en P2e : hors du critère ; Q-EV-15 : mêmes prévisions sur la période commune.
        c = out["c"]["critere_8_6"]
        assert c["grappes"] == 1 and c["t"] is None and c["verdict"] == "non concluant", c
    finally:
        shutil.rmtree(tmp.parent)


def _copie():
    """Copie du dépôt dans un dossier temporaire, et un lanceur de commandes Python dans cette copie."""
    import subprocess, os
    racine = Path(__file__).resolve().parent.parent
    tmp = Path(tempfile.mkdtemp()) / "depot"
    shutil.copytree(racine, tmp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    env = {**os.environ, "PYTHONPATH": str(tmp / "scripts")}

    def run(*a):
        r = subprocess.run([sys.executable, *a], cwd=tmp, env=env, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-2000:]
        return r.stdout
    return tmp, run


def test_regles_de_resolution():
    """Relecture 13, S4 : un cas discriminant par règle de résolution (un avis par agent et par passage,
    « non » prématuré refusé, annulation à 60 jours, première valeur collectée, réouverture par erratum)."""
    tmp, run = _copie()
    try:
        code = r"""
import json, resolution, registre
from pathlib import Path
R = Path('registre')
def props(L):
    (R / 'propositions_t.jsonl').write_text(''.join(json.dumps(x) + chr(10) for x in L))
def P(q, issue, agent, jour, df='2026-11-20'):
    return {"proposition": True, "question": q, "issue": issue, "source": "s", "agent": agent, "date_fait": df,
            "emise": jour + "T08:00:00+01:00"}
(R / 't.jsonl').write_text('')
out = {}
# 1. Même agent, même jour, « oui » deux fois : un seul avis, pas de résolution.
props([P("Q-EV-15", "oui", "A", "2026-11-20"), P("Q-EV-15", "oui", "A", "2026-11-20")])
out["doublon"] = [r["question"] for r in resolution.resoudre("registre/t.jsonl", "2026-11-21")]
(R / 'resolutions_t.jsonl').write_text('')
# 2. « non » sur un événement « survenue » avant son échéance : ignoré.
props([P("Q-EV-01", "non", "A", "2026-11-20"), P("Q-EV-01", "non", "B", "2026-11-20")])
out["non_premature"] = [r["question"] for r in resolution.resoudre("registre/t.jsonl", "2026-11-21")]
(R / 'resolutions_t.jsonl').write_text('')
# 3. Un seul avis, 61 jours après l'échéance : annulée ; sans aucun avis : pas d'annulation.
props([P("Q-EV-15", "oui", "A", "2027-01-05")])
r = resolution.resoudre("registre/t.jsonl", "2027-03-03")
out["annulation60"] = [(x["question"], x["issue"]) for x in r]
(R / 'resolutions_t.jsonl').write_text('')
props([])
out["sans_avis"] = [x["question"] for x in resolution.resoudre("registre/t.jsonl", "2027-03-03")]
# 5. Annulation à 30 jours : deux recherches vaines consignées (relecture 13, S13).
props([P("Q-EV-15", None, "A", "2027-01-10"), P("Q-EV-15", None, "B", "2027-01-10")])
out["annulation30"] = [(x["question"], x["issue"]) for x in resolution.resoudre("registre/t.jsonl", "2027-02-01")]
(R / 'resolutions_t.jsonl').write_text('')
# 6. « Non » prématuré déposé avant l'échéance : toujours ignoré après l'échéance (relecture 14, N1).
props([P("Q-EV-01", "non", "A", "2026-11-20"), P("Q-EV-01", "non", "B", "2026-11-20")])
out["non_premature_apres"] = [x["question"] for x in resolution.resoudre("registre/t.jsonl", "2028-10-01")]
(R / 'resolutions_t.jsonl').write_text('')
# 7. Réouverture par erratum : les propositions antérieures ne la referment pas (relecture 14, N1).
# Propositions datées avant l'erratum, que registre.py horodate à l'heure réelle.
props([P("Q-EV-15", "oui", "A", "2026-09-20"), P("Q-EV-15", "oui", "B", "2026-09-20")])
r1 = resolution.resoudre("registre/t.jsonl", "2026-11-21")
registre.ajouter("registre/resolutions_t.jsonl", [{"erratum": True, "objet": "Q-EV-15", "correction": {"rouverte": True}, "piste": "protocole"}])
r2 = resolution.resoudre("registre/t.jsonl", "2026-11-22")
out["reouverture"] = [[x["question"] for x in r1], [x["question"] for x in r2], "Q-EV-15" in resolution.resolutions_effectives("_t")]
print(json.dumps(out))
"""
        out = json.loads(run("-c", code).strip().splitlines()[-1])
        assert out["doublon"] == [], out
        assert "Q-EV-01" not in out["non_premature"], out
        assert ("Q-EV-15", None) in [tuple(x) for x in out["annulation60"]], out
        assert out["sans_avis"] == [], out
        assert ["Q-EV-15", None] in out["annulation30"], out
        assert "Q-EV-01" not in out["non_premature_apres"], out
        assert out["reouverture"] == [["Q-EV-15"], [], False], out
        # 4. Première valeur collectée (relecture 13, L1) : collectée, révisée, puis résolue.
        code2 = r"""
import json, resolution
from pathlib import Path
Path('data/premieres_valeurs.jsonl').write_text(json.dumps({"serie": "inflation_ipch_FR", "periode": "2099-11",
    "valeur": 3.4, "collecte_le": "2099-12-02T03:00:00+01:00"}) + chr(10))
Path('data/historique/inflation_ipch_FR.csv').write_text('periode,valeur' + chr(10) + '2099-11,3.3' + chr(10))
cyc = Path('data/cycles/2099-10'); cyc.mkdir(parents=True, exist_ok=True)
q = {"id": "Q-2099-10-inflation_ipch_FR-2099-11-q50", "type": "variable", "pool": "P2a", "grappe": "g", "texte": "t",
     "issues": ["oui", "non"], "echeance": "2099-12-31", "details": {"serie": "inflation_ipch_FR", "periode": "2099-11", "seuil": 3.4}}
(cyc / 'questions.json').write_text(json.dumps({"questions": [q]}))
Path('registre/v.jsonl').write_text(json.dumps({"question": q["id"], "probabilites": {"oui": 50, "non": 50}, "piste": "protocole",
    "phase": 1, "origine": "cycle 2099-10", "donnees": "t", "emise": "2099-10-01T08:00:00+02:00"}) + chr(10))
r = resolution.resoudre("registre/v.jsonl", "2100-01-01")
print(json.dumps([(x["issue"], x["valeur"], x["date_fait"]) for x in r]))
"""
        r = json.loads(run("-c", code2).strip().splitlines()[-1])
        assert r == [["oui", 3.4, "2099-12-02"]], r
    finally:
        shutil.rmtree(tmp.parent)


def test_regles_du_bilan():
    """Relecture 13, S4 : cycles d'essai exclus du registre noté, instantanés mensuels, grappe par acte."""
    tmp, run = _copie()
    try:
        run("scripts/geler.py", "2026-11-01", "2026-11", "--essai")
        run("scripts/questions.py", "2026-11-01", "2026-11")
        banque = json.loads((tmp / "data/cycles/2026-11/questions.json").read_text())
        g = {q["id"]: q["grappe"] for q in banque["questions"]}
        assert g["Q-EV-21"] == g["Q-EV-40a"] == g["Q-EV-20"], "grappe par acte"
        code = r"""
import json, resolution, notation
from pathlib import Path
# Le registre ne cite que le cycle 2026-11 : les banques d'essai (2026-10...) ne doivent pas être lues.
L = []
for auteur, lignes in (("ensemble direct", [("2026-11-02", 20, "cycle 2026-11")]),
                       ("modèle", [("2026-11-02", 20, "cycle 2026-11"), ("2026-11-15", 90, "fait imprévu MAJ-1")])):
    for d, p, o in lignes:
        L.append({"question": "Q-EV-15", "probabilites": {"oui": p, "non": 100 - p}, "piste": "protocole", "phase": 1,
                  "auteur": auteur, "origine": o, "donnees": "t", "emise": d + "T08:00:00+01:00"})
Path('registre/b.jsonl').write_text(''.join(json.dumps(x) + chr(10) for x in L))
Path('registre/resolutions_b.jsonl').write_text(json.dumps({"resolution": True, "question": "Q-EV-15", "issue": "non",
    "date_fait": "2026-12-31", "source": "s", "methode": "m", "emise": "2027-01-05T08:00:00+01:00"}) + chr(10))
qs = resolution.toutes_les_questions(resolution.cycles_du_registre('registre/b.jsonl'))
b = notation.bilan('registre/b.jsonl', 'ensemble direct', '2027-02-01')
c = b['comparaisons']['modèle']
print(json.dumps({"grappe": qs["Q-EV-15"]["grappe"], "t": c["critere_8_6"]["t"], "continu": c["mises_a_jour_continues_descriptif"]["t"]}))
"""
        out = json.loads(run("-c", code).strip().splitlines()[-1])
        assert out["grappe"] == "EV-15", out          # banque du cycle 2026-11, pas celle de l'essai
        assert out["t"] is None, out                  # instantanés mensuels identiques : écart nul
        assert out["continu"] is not None, out        # la mise à jour continue n'apparaît que dans le descriptif
    finally:
        shutil.rmtree(tmp.parent)


def test_registre():
    tmp = Path(tempfile.mkdtemp())
    ancien = registre.RACINE
    registre.RACINE = tmp
    try:
        registre.ajouter("registre/t.jsonl", [{"question": "Q", "probabilites": {"oui": 60, "non": 40},
                                               "piste": "protocole", "phase": 1, "origine": "test", "donnees": "test"}])
        l = json.loads((tmp / "registre/t.jsonl").read_text())
        assert l["emise"].endswith("+02:00") or l["emise"].endswith("+01:00")
        for mauvaise in ({"question": "Q", "probabilites": {"oui": 60, "non": 40}, "piste": "protocole", "origine": "o",
                          "donnees": "d"},                                   # phase manquante
                         {"question": "Q", "probabilites": {"oui": 60, "non": 30}, "piste": "exploratoire",
                          "origine": "o", "donnees": "d"},                   # somme ≠ 100
                         {"question": "Q", "probabilites": {"oui": 60, "non": 40}, "piste": "exploratoire",
                          "origine": "o", "donnees": "d", "emise": "2026-01-01T00:00:00+01:00"},  # horodatage fourni
                         {"proposition": True, "question": "Q", "issue": "oui", "source": "s", "agent": "a"},  # sans date du fait
                         {"proposition": True, "question": "Q", "issue": "oui", "source": "s", "agent": "a",
                          "date_fait": "3 novembre"}):                       # date du fait mal formée
            try:
                registre.valider(mauvaise)
                raise AssertionError(f"ligne acceptée à tort : {mauvaise}")
            except ValueError:
                pass
    finally:
        registre.RACINE = ancien
        shutil.rmtree(tmp)


if __name__ == "__main__":
    for nom, f in list(globals().items()):
        if nom.startswith("test_"):
            f()
            print(f"ok  {nom}")
