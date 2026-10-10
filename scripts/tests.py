"""Tests des scripts de la phase 1 sur données fictives. Usage : python scripts/tests.py"""
import json
import math
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


def test_brier_pondere_propre():
    """Relecture 17, I1 : sur des questions de fenêtre « survenue » à risque constant, la prévision honnête a le
    meilleur Brier pondéré moyen ; gonfler ou réduire les probabilités ne paie pas (mêmes trajectoires)."""
    from datetime import date, timedelta
    def moyenne(facteur, n=3000, h=0.1, mois=9, manques=()):
        rnd, tot = random.Random(1), 0.0
        debuts, ech = [date(2027, 1 + k, 1) for k in range(mois)], date(2027, 9, 30)
        for _ in range(n):
            fait = None
            for k in range(mois):
                if rnd.random() < h:
                    fin_m = debuts[k + 1] if k + 1 < mois else ech + timedelta(days=1)
                    fait = debuts[k] + timedelta(days=rnd.randrange((fin_m - debuts[k]).days))
                    break
            lignes = []
            for k in range(mois):
                if fait and debuts[k] >= fait:
                    break
                p = min(1.0, facteur * (1 - (1 - h) ** (mois - k)))
                if k in manques:
                    continue
                lignes.append({"emise": debuts[k].isoformat() + "T08:00:00+01:00",
                               "probabilites": {"oui": 100 * p, "non": 100 - 100 * p}})
            if lignes:
                tot += notation.brier_pondere(lignes, "oui" if fait else "non", "2027-01-01", ech.isoformat(),
                                              (fait or ech).isoformat())
        return tot / n
    honnete = moyenne(1.0)
    assert honnete < moyenne(1.25) and honnete < moyenne(0.8), honnete
    # Relecture de suivi 18 : manquer des cycles ne doit pas faire gagner un auteur, à prévisions égales.
    assert moyenne(1.0, manques=(3, 5)) >= honnete, (moyenne(1.0, manques=(3, 5)), honnete)


def test_bout_en_bout():
    """Relecture 12, S15 : un cycle fictif de bout en bout sur une copie du dépôt (gel, questions,
    comparateurs, prévisions de deux auteurs, propositions, résolution, bilan). Vérifie : une seule
    grappe par événement (fenêtre et mensuelles), cycles d'essai ignorés, test de 8.6 limité à P2b et
    P2c, période commune sur le chemin du bilan, un avis par agent."""
    import subprocess
    racine = Path(__file__).resolve().parent.parent
    tmp = Path(tempfile.mkdtemp()) / "depot"
    shutil.copytree(racine, tmp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    # Les essais gèlent au 1er novembre 2026 : les séries sont réputées collectées la veille (relecture 15, S6).
    etat = tmp / "data/historique/_collecte.json"
    etat.write_text(json.dumps({k: "2026-10-31" for k in json.loads(etat.read_text())}))
    try:
        env = {**__import__("os").environ, "PYTHONPATH": str(tmp / "scripts")}
        def run(*a):
            r = subprocess.run([sys.executable, *a], cwd=tmp, env=env, capture_output=True, text=True)
            assert r.returncode == 0, r.stderr[-2000:]
            return r
        (tmp / "modele/statut.json").write_text(json.dumps({"definitif": True, "premier_cycle_formel": "2026-11"}))
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
                                   "auteur": auteur, "origine": f"cycle {d[:7]}", "donnees": "t",
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
    # Les essais gèlent au 1er novembre 2026 : les séries sont réputées collectées la veille (relecture 15, S6).
    etat = tmp / "data/historique/_collecte.json"
    etat.write_text(json.dumps({k: "2026-10-31" for k in json.loads(etat.read_text())}))
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
        # Relecture 15, S10 : fenêtres emboîtées dans une grappe, fenêtres disjointes dans deux.
        assert g["Q-EV-C3a"] == g["Q-EV-C3b"] and g["Q-EV-16a"] != g["Q-EV-16b"], "grappes et fenêtres"
        # Relecture 15, S14 : la question mensuelle porte sur la période du gel à la fin du mois.
        assert any(q["texte"].endswith("entre le 2026-11-01 et le 2026-11-30 ?") for q in banque["questions"])
        # Relecture 15, S6 : une série non collectée depuis plus de trois jours n'est pas émise.
        assert not any("non collectée" in e["motif"] for e in banque["ecartees"])
        etat = tmp / "data/cycles/2026-11/gel/historique/_collecte.json"
        e = json.loads(etat.read_text()); e["brent_journalier"] = "2026-10-20"; etat.write_text(json.dumps(e))
        (tmp / "data/cycles/2026-11/questions.json").unlink()
        run("scripts/questions.py", "2026-11-01", "2026-11")
        b2 = json.loads((tmp / "data/cycles/2026-11/questions.json").read_text())
        assert {"objet": "brent_mensuel", "motif": "série non collectée depuis plus de trois jours au gel"} in b2["ecartees"]
        assert not any(q["id"].startswith("Q-2026-11-brent") for q in b2["questions"])
        etat.write_text(json.dumps({**e, "brent_journalier": "2026-10-31"}))
        (tmp / "data/cycles/2026-11/questions.json").unlink()
        run("scripts/questions.py", "2026-11-01", "2026-11")
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
print(json.dumps({"grappe": qs["Q-EV-15"]["grappe"], "t": c["critere_8_6"]["t"], "continu": c["mises_a_jour_continues_descriptif"]["t"],
                  "b86": sorted(b["bilan_8_6_modele"]), "va": b["bilan_8_6_modele"]["valeur_ajoutee"]["avec_ajouts"]["t"]}))
"""
        out = json.loads(run("-c", code).strip().splitlines()[-1])
        assert out["grappe"] == "EV-15", out          # banque du cycle 2026-11, pas celle de l'essai
        assert out["t"] is None, out                  # instantanés mensuels identiques : écart nul
        assert out["continu"] is not None, out        # la mise à jour continue n'apparaît que dans le descriptif
        assert out["b86"] == ["calibration", "valeur_ajoutee"] and out["va"] is None, out   # relecture 15, S3
    finally:
        shutil.rmtree(tmp.parent)


def test_calibration_questions_echues():
    """Relecture 15, I1 : la calibration ne retient que les questions échues à la date du test, quelle que soit
    leur issue ; une question de fenêtre longue résolue « oui » avant son échéance n'y entre pas seule."""
    tmp, run = _copie()
    try:
        run("scripts/geler.py", "2026-11-01", "2026-11", "--essai")
        run("scripts/questions.py", "2026-11-01", "2026-11")
        code = r"""
import json, notation
from pathlib import Path
evs = ["EV-01", "EV-04", "EV-07", "EV-08", "EV-17", "EV-C1", "EV-C2", "EV-39", "EV-29", "EV-43", "EV-45", "EV-16b", "EV-C3b"]
L, R = [], []
for e in evs:
    L.append({"question": "Q-" + e, "probabilites": {"oui": 20, "non": 80}, "piste": "protocole", "phase": 1,
              "auteur": "modèle", "origine": "cycle 2026-11", "donnees": "t", "emise": "2026-11-02T08:00:00+01:00"})
for e in evs[:3]:
    R.append({"resolution": True, "question": "Q-" + e, "issue": "oui", "date_fait": "2027-03-15", "source": "s",
              "methode": "m", "emise": "2027-03-16T08:00:00+01:00"})
Path('registre/c.jsonl').write_text(''.join(json.dumps(x) + chr(10) for x in L))
Path('registre/resolutions_c.jsonl').write_text(''.join(json.dumps(x) + chr(10) for x in R))
b = notation.bilan('registre/c.jsonl', 'ensemble direct', '2027-09-30')
print(json.dumps({"n": b["auteurs"]["modèle"]["calibration_8_6"]["questions"],
                  "n_sans": b["auteurs"]["modèle"]["calibration_8_6_sans_ajouts"]["questions"]}))
"""
        out = json.loads(run("-c", code).strip().splitlines()[-1])
        assert out == {"n": 0, "n_sans": 0}, out
        # Relecture 17, I2 : la prévision retenue est la première de cycle, pas la dernière avant résolution.
        code2 = r"""
import json, notation
from pathlib import Path
L = [{"question": "Q-EV-15", "probabilites": {"oui": p, "non": 100 - p}, "piste": "protocole", "phase": 1, "auteur": "modèle",
      "origine": "cycle " + c, "donnees": "t", "emise": d + "T08:00:00+01:00"} for p, c, d in ((30, "2026-11", "2026-11-02"), (10, "2026-12", "2026-12-01"))]
Path('registre/d.jsonl').write_text(''.join(json.dumps(x) + chr(10) for x in L))
Path('registre/resolutions_d.jsonl').write_text(json.dumps({"resolution": True, "question": "Q-EV-15", "issue": "non",
    "date_fait": "2026-12-31", "source": "s", "methode": "m", "emise": "2027-01-05T08:00:00+01:00"}) + chr(10))
b = notation.bilan('registre/d.jsonl', 'ensemble direct', '2027-01-15')
print(json.dumps(b["auteurs"]["modèle"]["calibration_8_6"]["p_moyenne"]))
"""
        assert json.loads(run("-c", code2).strip().splitlines()[-1]) == 0.3
    finally:
        shutil.rmtree(tmp.parent)


def test_verifier_reponse():
    """Relecture 15, S1 : une réponse sans liste d'adresses, ou qui cite le dépôt ou un marché, est rejetée.
    Consigne v1.6 : moins de 5 pages lues, ou un même motif sur plus d'un tiers des questions, est rejeté."""
    tmp, run = _copie()
    try:
        run("scripts/geler.py", "2026-11-01", "2026-11", "--essai")
        run("scripts/questions.py", "2026-11-01", "2026-11")
        code = r"""
import json, verifier_reponse as v
qs = json.load(open('data/cycles/2026-11/questions.json'))['questions']
prev = {q['id']: {'probabilites': {k: round(100 / len(q['issues']), 4) for k in q['issues']}} for q in qs}
prev = {k: {**v, 'motif': 'motif propre ' + k} for k, v in prev.items()}
base = {'previsionniste': 'p1', 'modele': 'm', 'recherches': 12, 'previsions': prev}
pages = ['https://www.lemonde.fr/' + c for c in 'abcde']
res = {}
generique = {k: {**v, 'motif': 'Taux de base et situation actuelle.'} for k, v in prev.items()}
json.dump({**base, 'adresses': pages, 'previsions': generique}, open('r_generique.json', 'w'))
res['generique'] = v.defauts('2026-11', 'r_generique.json')
sans_motif = {k: {'probabilites': x['probabilites']} for k, x in prev.items()}
json.dump({**base, 'adresses': pages, 'previsions': sans_motif}, open('r_sans_motif.json', 'w'))
res['sans_motif'] = v.defauts('2026-11', 'r_sans_motif.json')
for nom, adr in (('sans', None), ('propre', pages), ('peu_de_pages', pages[:2]),
                 ('depot', ['https://github.com/Beynat/psychohistoire/blob/main/data/x.json']),
                 ('marche', ['https://polymarket.com/event/x'])):
    r = dict(base) if adr is None else {**base, 'adresses': adr}
    json.dump(r, open('r_' + nom + '.json', 'w'))
    res[nom] = v.defauts('2026-11', 'r_' + nom + '.json')
print(json.dumps(res, ensure_ascii=False))
"""
        out = json.loads(run("-c", code).strip().splitlines()[-1])
        assert out["propre"] == [], out["propre"][:3]
        assert out["sans"] and out["depot"] and out["marche"], out
        # Consigne v1.6 (essai 2026-10-v0) : motifs génériques, motifs absents, trop peu de pages lues.
        assert any("motif identique" in x for x in out["generique"]), out["generique"]
        assert any("motif identique" in x for x in out["sans_motif"]), out["sans_motif"]
        assert any("pages lues" in x for x in out["peu_de_pages"]), out["peu_de_pages"]
    finally:
        shutil.rmtree(tmp.parent)


def test_ancrage_pas_nul():
    """Relecture de suivi 16, N4 : quand le point quotidien d'ancrage tombe dans le mois du gel, la question à
    horizon 1 (cible = ce mois) a un pas nul, et sa loi est celle du point du jour J à la moyenne du même mois."""
    tmp, run = _copie()
    try:
        code = r"""
import json, commun
a = commun.ancrage_quotidien(commun.serie('ecart_FR_DE_pb'), commun.serie('ecart_FR_DE_journalier_pb'))
print(json.dumps(a[3]))
"""
        jour = json.loads(run("-c", code).strip().splitlines()[-1])
        run("scripts/geler.py", jour, "essai-n4", "--essai")
        run("scripts/questions.py", jour, "essai-n4")
        qs = json.loads((tmp / "data/cycles/essai-n4/questions.json").read_text())["questions"]
        d = [q["details"] for q in qs if q["id"].startswith("Q-essai-n4-ecart_FR_DE_pb-" + jour[:7])]
        assert d and all(x["pas"] == 0 and x["ancrage_quotidien"] for x in d), d[:1]
        suiv = [q["details"]["pas"] for q in qs if q["id"].startswith("Q-essai-n4-ecart_FR_DE_pb-" + commun.mois_suivant(jour[:7]))]
        assert suiv and set(suiv) == {1}, suiv
    finally:
        shutil.rmtree(tmp.parent)


def test_symetrie_et_anteriorite():
    """Relecture 19. I1 : deux auteurs aux prévisions identiques, dont l'un manque un cycle, ont un écart nul
    (cycles communs seulement). B1 : une prévision émise après que l'issue d'un « constat » est établie
    publiquement (date du fait) est exclue, même avant la publication officielle."""
    tmp, run = _copie()
    try:
        run("scripts/geler.py", "2026-11-01", "2026-11", "--essai")
        run("scripts/questions.py", "2026-11-01", "2026-11")
        code = r"""
import json, notation
from pathlib import Path
L = []
for auteur, cycles in (("ensemble direct", (("2026-11", 20), ("2026-12", 30))),
                       ("modèle", (("2026-11", 20), ("2026-12", 30), ("2027-01", 60)))):
    for c, p in cycles:
        L.append({"question": "Q-EV-16a", "probabilites": {"oui": p, "non": 100 - p}, "piste": "protocole", "phase": 1,
                  "auteur": auteur, "origine": "cycle " + c, "donnees": "t", "emise": c + "-02T08:00:00+01:00"})
L.append({"question": "Q-EV-30", "probabilites": {"oui": 99, "non": 1}, "piste": "protocole", "phase": 1,
          "auteur": "modèle", "origine": "cycle 2026-12", "donnees": "t", "emise": "2026-12-01T08:00:00+01:00"})
Path('registre/s.jsonl').write_text(''.join(json.dumps(x) + chr(10) for x in L))
R = [{"resolution": True, "question": "Q-EV-16a", "issue": "oui", "date_fait": "2027-01-20", "source": "s", "methode": "m",
      "emise": "2027-01-21T08:00:00+01:00"},
     {"resolution": True, "question": "Q-EV-30", "issue": "oui", "date_fait": "2026-11-04", "source": "s", "methode": "m",
      "emise": "2026-12-15T08:00:00+01:00"}]
Path('registre/resolutions_s.jsonl').write_text(''.join(json.dumps(x) + chr(10) for x in R))
b = notation.bilan('registre/s.jsonl', 'ensemble direct', '2027-06-01')
# Mêmes prévisions émises le 1er par le modèle, le 5 par l'ensemble : départ commun, écart nul (audit, v1.24).
L2 = []
for auteur, jour in (("ensemble direct", "05"), ("modèle", "01")):
    for c, p in (("2026-11", 20), ("2026-12", 60), ("2027-01", 60)):
        L2.append({"question": "Q-EV-16a", "probabilites": {"oui": p, "non": 100 - p}, "piste": "protocole", "phase": 1,
                   "auteur": auteur, "origine": "cycle " + c, "donnees": "t", "emise": c + "-" + jour + "T08:00:00+01:00"})
Path('registre/u.jsonl').write_text(''.join(json.dumps(x) + chr(10) for x in L2))
Path('registre/resolutions_u.jsonl').write_text(json.dumps(R[0]) + chr(10))
b2 = notation.bilan('registre/u.jsonl', 'ensemble direct', '2027-06-01')
print(json.dumps({"t": b["comparaisons"]["modèle"]["critere_8_6"]["t"],
                  "exclue": any(e["question"] == "Q-EV-30" for e in b["exclues"]),
                  "t_dates": b2["comparaisons"]["modèle"]["critere_8_6"]["t"]}))
"""
        out = json.loads(run("-c", code).strip().splitlines()[-1])
        assert out == {"t": None, "exclue": True, "t_dates": None}, out
    finally:
        shutil.rmtree(tmp.parent)


def test_correspondances_figees():
    """Relecture 19, S1 : après le premier gel d'un événement, aucune de ses questions ne peut passer en P1."""
    tmp, run = _copie()
    try:
        st = tmp / "modele/statut.json"
        st.write_text(json.dumps({**json.loads(st.read_text()), "definitif": True, "premier_cycle_formel": "2026-11"}))
        run("scripts/geler.py", "2026-11-01", "2026-11", "--essai")
        assert "Banque conforme" in run("scripts/controle_banque.py")
        c = tmp / "modele/correspondances_p1.json"
        d = json.loads(c.read_text()); d["correspondances"]["Q-EV-16a-2027-01"] = {"pool": "P1"}
        c.write_text(json.dumps(d))
        import subprocess, os
        r = subprocess.run([sys.executable, "scripts/controle_banque.py"], cwd=tmp, capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": str(tmp / "scripts")})
        assert r.returncode != 0 and "EV-16a : correspondance" in r.stdout, r.stdout[-500:]
    finally:
        shutil.rmtree(tmp.parent)


def test_verrou_protocole():
    """Vérificateur B, 10 octobre 2026 : tant que le protocole n'est pas définitif, aucun script n'écrit dans
    registre/protocole.jsonl, même lancé sans registre d'essai ; une fois définitif, l'écriture passe."""
    tmp, run = _copie()
    try:
        import subprocess, os
        env = {**os.environ, "PYTHONPATH": str(tmp / "scripts")}
        run("scripts/geler.py", "2026-11-01", "2026-11", "--essai")
        run("scripts/questions.py", "2026-11-01", "2026-11")
        reg = tmp / "registre/protocole.jsonl"
        avant = reg.read_bytes() if reg.exists() else b""
        st = tmp / "modele/statut.json"
        st.write_text(json.dumps({**json.loads(st.read_text()), "definitif": False}))
        r = subprocess.run([sys.executable, "scripts/comparateurs.py", "2026-11"], cwd=tmp, env=env,
                           capture_output=True, text=True)
        assert r.returncode != 0 and "écriture refusée" in (r.stderr + r.stdout), (r.stdout + r.stderr)[-500:]
        assert (reg.read_bytes() if reg.exists() else b"") == avant
        st.write_text(json.dumps({**json.loads(st.read_text()), "definitif": True}))
        run("scripts/comparateurs.py", "2026-11")
        assert len(reg.read_bytes()) > len(avant)
    finally:
        shutil.rmtree(tmp.parent)


def test_conjointes():
    """Feuille de route v0, bloc 5 : une question conjointe est émise en P2c avec ses deux critères, reçoit un taux
    de base égal au produit de ceux de ses composantes, et se résout « non » dès qu'une composante l'est."""
    tmp, run = _copie()
    try:
        run("scripts/geler.py", "2026-11-01", "2026-11", "--essai")
        run("scripts/questions.py", "2026-11-01", "2026-11", "registre/v0.jsonl")
        qs = {q["id"]: q for q in json.loads((tmp / "data/cycles/2026-11/questions.json").read_text())["questions"]}
        c = qs["Q-CJ-01"]
        assert c["pool"] == "P2c" and c["details"]["composantes"] == ["Q-EV-15", "Q-EV-50"], c
        assert c["grappe"] == qs["Q-EV-15"]["grappe"]
        run("scripts/comparateurs.py", "2026-11", "registre/v0.jsonl")
        lignes = [json.loads(l) for l in (tmp / "registre/v0.jsonl").read_text().splitlines() if l.strip()]
        tb = {l["question"]: l["probabilites"]["oui"] for l in lignes if l["auteur"] == "comparateur : taux de base" and "oui" in l["probabilites"]}
        assert abs(tb["Q-CJ-01"] - tb["Q-EV-15"] * tb["Q-EV-50"] / 100) < 0.2, (tb["Q-CJ-01"], tb["Q-EV-15"], tb["Q-EV-50"])
        (tmp / "registre/resolutions_v0.jsonl").write_text(json.dumps({"resolution": True, "question": "Q-EV-15", "issue": "non",
            "date_fait": "2026-12-31", "source": "s", "methode": "m", "emise": "2027-01-05T08:00:00+01:00"}) + chr(10))
        code = "import resolution, json; print(json.dumps([r['question'] + ':' + str(r['issue']) for r in resolution.resoudre('registre/v0.jsonl', '2027-01-06')]))"
        out = json.loads(run("-c", code).strip().splitlines()[-1])
        assert "Q-CJ-01:non" in out and not any(x.startswith("Q-CJ-04") for x in out), out
    finally:
        shutil.rmtree(tmp.parent)


def test_emergence_du_tri():
    """Vérificateur A, A-04 : un fait sans question est suivi d'un passage à l'autre sous un seul identifiant, et
    signalé comme émergence à partir de 50 titres en sept jours."""
    tmp, run = _copie()
    try:
        from datetime import date as _d
        auj = _d.today().isoformat()
        lignes = [{"lien": f"https://exemple.fr/{i}", "passage": f"{auj}T10:00:00+02:00", "fait": "sujet-test",
                   "decision": "non rattaché", "motif": "m", "source": f"source{i % 3}", "date_titre": f"{auj}T09:00Z"}
                  for i in range(52)]
        (tmp / "data/tri/2099-01.jsonl").write_text("".join(json.dumps(x) + chr(10) for x in lignes))
        run("scripts/tri.py", "reprise")
        r = json.loads((tmp / "data/reprise.json").read_text())
        assert r["non_rattaches"]["sujet-test"]["titres"] == 52, r["non_rattaches"].get("sujet-test")
        assert "sujet-test" in r["emergences"], r["emergences"]
    finally:
        shutil.rmtree(tmp.parent)


def test_reseau_moteur():
    """Feuille de route v0, bloc 4 : la probabilité sur fenêtre donnée par les évaluateurs est retrouvée après
    conversion en risque mensuel ; un multiplicateur d'état parent déplace l'issue dans le bon sens ; un parent au
    mois précédent ne crée pas de cycle, un parent au même mois en crée un ; une exclusion annule une issue."""
    import reseau
    S = {"variables_etat": [{"id": "VE-A", "etats": ["bas", "haut"], "parents": [{"id": "PV-D", "decalage": 1}]}],
         "pivots": [{"id": "PV-H", "nature": "à tout moment", "fenetre": ["2026-10-10", "2027-05-02"], "parents": []},
                    {"id": "PV-D", "nature": "daté", "date": "2026-12-31", "parents": ["VE-A"],
                     "exclusions": {"VE-A": {"haut": ["z"]}}}],
         "mesures": {"EV-H": {"caracteristique": {"type": "survenue", "noeud": "PV-H"}, "table": {"oui": 100, "non": 0}},
                     "EV-D": {"caracteristique": {"type": "issue", "noeud": "PV-D"}, "table": "identite"}}}
    T = {"noeuds": {"VE-A": {"reference": "bas", "transition": {"bas": {"bas": 0.5, "haut": 0.5}, "haut": {"bas": 0.5, "haut": 0.5}}},
                    "PV-H": {"p_fenetre": 0.4},
                    "PV-D": {"base": {"x": 0.6, "y": 0.2, "z": 0.2}, "multiplicateurs": {"VE-A": {"haut": {"y": 5.0}}}}}}
    qs = [{"id": "Q-EV-H", "evenement": "EV-H", "issues": ["oui", "non"], "fenetre": ["2026-10-10", "2027-05-02"]},
          {"id": "Q-EV-D", "evenement": "EV-D", "issues": ["x", "y", "z"], "fenetre": ["2026-10-10", "2026-12-31"]}]
    p = reseau.prevoir(S, T, {}, qs, tirages=40, trajectoires=250)
    assert 34 <= p["Q-EV-H"]["oui"] <= 46, p["Q-EV-H"]
    assert p["Q-EV-D"]["y"] > 30 and p["Q-EV-D"]["z"] < 15, p["Q-EV-D"]   # y relevé, z exclu quand VE-A est haut
    reseau.ordre(S)   # le lien au mois précédent ne forme pas de cycle
    S2 = {"variables_etat": [{"id": "VE-A", "parents": ["VE-B"]}, {"id": "VE-B", "parents": ["VE-A"]}], "pivots": []}
    try:
        reseau.ordre(S2)
        assert False, "cycle non détecté"
    except SystemExit as e:
        assert "Cycle" in str(e)


def test_carte():
    """Feuille de route, bloc 10 : les trajectoires de la carte respectent les fenêtres des pivots, gardent un rang
    d'issue valide, codent la survenue (et non son absence) et conservent la dépendance du réseau (un départ du Premier ministre bien plus fréquent après une
    censure qu'en son absence)."""
    import carte
    import reseau
    d = carte.construire(tirages=10, trajectoires=40)
    P, B = d["pivots"], "0123456789abcdefghijklmnopqrstuvwxyz"
    assert len(d["codes"]) == 400 and all(len(c) == len(P) for c in d["codes"])
    for i, p in enumerate(P):
        for c in d["codes"]:
            if p["nature"] == "daté":
                assert int(c[i]) < len(p["issues"]), (p["id"], c[i])
            elif c[i] != "-":
                assert reseau.idx(p["fenetre"][0]) <= B.index(c[i]) <= reseau.idx(p["fenetre"][1]), (p["id"], c[i])
    ix = {p["id"]: i for i, p in enumerate(P)}
    a, g = ix["PV-CENSURE1a"], ix["PV-GOUV"]
    survenue = sum(c[a] != "-" for c in d["codes"]) / len(d["codes"])
    assert 0.12 < survenue < 0.5, survenue          # tables : 24 % de base, relevé par la mobilisation observée
    avec = [c[g] != "-" for c in d["codes"] if c[a] != "-"]
    sans = [c[g] != "-" for c in d["codes"] if c[a] == "-"]
    assert avec and sans and sum(avec) / len(avec) > sum(sans) / len(sans) + 0.3, (len(avec), len(sans))
    assert all(len(v["par_mois"]) == len(d["mois"]) for v in d["variables"])


def test_jalons():
    """Feuille de route v0, bloc 2 : une définition dont la fenêtre s'ouvre dans moins de 7 jours est refusée ; un
    jalon observé relève, dans le registre fantôme, l'issue qu'il favorise, avec la réduction k."""
    tmp, run = _copie()
    try:
        from datetime import date as _d, timedelta as _t
        j0 = (_d.today() + _t(days=10)).isoformat()
        j1 = (_d.today() + _t(days=40)).isoformat()
        base = {"lien": "PV-CENSURE1 → PV-GOUV", "observable": "o", "indicateur": {"source": "s", "mesure": "m", "seuil": "x"},
                "niveau": 3, "type": "amont", "cible": {"noeud": "PV-GOUV", "issue": "oui", "question": "Q-EV-50"},
                "vraisemblances": {"a": 0.6, "b": 0.2}}
        import subprocess, os
        env = {**os.environ, "PYTHONPATH": str(tmp / "scripts")}
        trop_tot = {**base, "id": "J-T", "fenetre": {"debut": (_d.today() + _t(days=3)).isoformat(), "fin": j1}}
        r = subprocess.run([sys.executable, "scripts/jalons.py", "definir"], cwd=tmp, env=env, capture_output=True, text=True,
                           input=json.dumps(trop_tot) + chr(10))
        assert r.returncode != 0 and "7 jours" in r.stderr, r.stderr[-300:]
        r = subprocess.run([sys.executable, "scripts/jalons.py", "definir"], cwd=tmp, env=env, capture_output=True, text=True,
                           input=json.dumps({**base, "id": "J-1", "fenetre": {"debut": j0, "fin": j1}}) + chr(10))
        assert r.returncode == 0, r.stderr[-300:]
        r = subprocess.run([sys.executable, "scripts/jalons.py", "statut"], cwd=tmp, env=env, capture_output=True, text=True,
                           input=json.dumps({"jalon": "J-1", "statut": "observé", "date": j0, "source": "s", "agent": "a"}) + chr(10))
        assert r.returncode == 0, r.stderr[-300:]
        ligne = {"question": "Q-EV-50", "probabilites": {"oui": 30.0, "non": 70.0}, "piste": "v0", "auteur": "réseau v0",
                 "origine": "cycle t", "donnees": "t"}
        subprocess.run([sys.executable, "scripts/registre.py", "registre/essai_j.jsonl"], cwd=tmp, env=env, check=True,
                       capture_output=True, text=True, input=json.dumps(ligne) + chr(10))
        run("scripts/jalons.py", "fantome", "registre/essai_j.jsonl")
        f = [json.loads(l) for l in (tmp / "registre/fantome.jsonl").read_text().splitlines() if l.strip()]
        attendu = 100 / (1 + math.exp(-(math.log(30 / 70) + 0.5 * math.log(3))))
        assert abs(f[-1]["probabilites"]["oui"] - attendu) < 0.2, (f[-1], attendu)
    finally:
        shutil.rmtree(tmp.parent)


def test_tables_du_reseau():
    """Feuille de route v0, bloc 4 : le gabarit couvre chaque nœud de la structure, un gabarit vide est refusé, et
    une loi qui ne somme pas à 1 est signalée."""
    import tables
    g = tables.gabarit()
    s = json.loads((Path(__file__).resolve().parent.parent / "modele/reseau/structure_v0.json").read_text())
    assert set(g["noeuds"]) == {n["id"] for n in s["variables_etat"] + s["pivots"]}
    assert tables.verifier(g), "gabarit vide accepté"
    i = next(k for k, x in g["noeuds"].items() if "base" in x and "conditionnelle" not in x)
    r = json.loads(json.dumps(g))
    r["noeuds"][i]["base"] = {c: 0.9 for c in r["noeuds"][i]["base"]}
    assert any(f"{i} base" in x and "somme" in x for x in tables.verifier(r))


def test_faits_et_direction():
    """Feuille de route v0, blocs 2 et 8 : seuil d'application d'un fait imprévu (signes opposés refusés, plafond
    puis réduction k = 0,5), application d'un fait retenu par le moteur, quantile de Student du critère de direction."""
    import faits, reseau, direction
    oppose = faits.decider({"fait": "f", "noeud": "N", "issues": ["oui", "non"],
                            "avis": [{"p": {"oui": 0.6, "non": 0.3}}, {"p": {"oui": 0.2, "non": 0.4}}]})
    assert not oppose["retenu"] and "signes" in oppose["motifs"][0]
    fort = faits.decider({"fait": "f", "noeud": "N", "issues": ["oui", "non"],
                          "avis": [{"p": {"oui": 0.9, "non": 0.1}}] * 5})
    assert fort["retenu"] and abs(fort["multiplicateurs"]["oui"] - 3 ** 0.5) < 0.01, fort
    S = {"variables_etat": [], "pivots": [{"id": "PV-H", "nature": "à tout moment", "fenetre": ["2026-10-10", "2027-05-02"], "parents": []}],
         "mesures": {"EV-H": {"caracteristique": {"type": "survenue", "noeud": "PV-H"}, "table": {"oui": 100, "non": 0}}}}
    T = {"noeuds": {"PV-H": {"p_fenetre": 0.3}}}
    q = [{"id": "Q", "evenement": "EV-H", "issues": ["oui", "non"], "fenetre": ["2026-10-10", "2027-05-02"]}]
    reseau.FAITS = {}
    sans = reseau.prevoir(S, T, {}, q, 30, 200)["Q"]["oui"]
    reseau.FAITS = {"PV-H": [("2026-10", {"oui": 3.0})]}
    avec = reseau.prevoir(S, T, {}, q, 30, 200)["Q"]["oui"]
    reseau.FAITS = None
    assert avec > sans + 15, (sans, avec)
    assert direction.quantile_student_90(4) == 1.533 and direction.quantile_student_90(40) == 1.2816


def test_cycles_v0():
    """Feuille de route v0, bloc 6 (vérificateur B, 2.1 et 4). Un gel AAAA-MM ne fige la banque qu'à partir du
    premier cycle formel ; un cycle v0 lit les résolutions et les annonces de son propre registre."""
    tmp, run = _copie()
    try:
        import subprocess, os
        env = {**os.environ, "PYTHONPATH": str(tmp / "scripts")}
        st = tmp / "modele/statut.json"
        base = json.loads(st.read_text())
        st.write_text(json.dumps({**base, "definitif": False, "v0": True, "premier_cycle_formel": None}))
        run("scripts/geler.py", "2026-11-01", "2026-11", "--essai")
        assert "Banque conforme" in run("scripts/controle_banque.py")
        st.write_text(json.dumps({**base, "definitif": False, "v0": True, "premier_cycle_formel": "2026-11"}))
        r = subprocess.run([sys.executable, "scripts/controle_banque.py"], cwd=tmp, env=env, capture_output=True, text=True)
        assert r.returncode != 0 and "pas déclaré définitif" in r.stdout, r.stdout[-300:]
        st.write_text(json.dumps({**base, "definitif": False, "v0": True, "premier_cycle_formel": None}))
        # Q-EV-42 résolue dans le registre v0 : écartée du cycle v0 suivant, émise dans un cycle d'un autre registre.
        (tmp / "registre/resolutions_v0.jsonl").write_text(json.dumps({"resolution": True, "question": "Q-EV-42",
            "issue": "oui", "date_fait": "2026-11-20", "source": "s", "methode": "m",
            "emise": "2026-11-21T08:00:00+01:00"}) + chr(10))
        run("scripts/geler.py", "2026-12-01", "2026-12", "--essai")
        run("scripts/questions.py", "2026-12-01", "2026-12", "registre/v0.jsonl")
        ids = {q["id"] for q in json.loads((tmp / "data/cycles/2026-12/questions.json").read_text())["questions"]}
        assert not any(i.startswith("Q-EV-42") for i in ids), sorted(i for i in ids if "EV-42" in i)
        run("scripts/geler.py", "2026-12-01", "essai-autre", "--essai")
        run("scripts/questions.py", "2026-12-01", "essai-autre", "registre/essai_autre.jsonl")
        ids = {q["id"] for q in json.loads((tmp / "data/cycles/essai-autre/questions.json").read_text())["questions"]}
        assert "Q-EV-42" in ids
    finally:
        shutil.rmtree(tmp.parent)


def test_mensuelle_sans_date_de_fin():
    """Essai 2026-10-v0, Q120 : le critère d'une question mensuelle n'écrit pas la fin de sa fenêtre, sinon
    l'énoncé du mois et le critère se contredisent."""
    tmp, run = _copie()
    try:
        import subprocess, os
        assert "Banque conforme" in run("scripts/controle_banque.py")
        c = tmp / "modele/banque/criteres.json"
        d = json.loads(c.read_text())
        for e in d["evenements"]:
            if e["id"] == "EV-16a":
                e["critere"] = e["critere"].replace("pendant la fenêtre.", "entre le début de la fenêtre et le 2 mai 2027.")
        c.write_text(json.dumps(d, ensure_ascii=False))
        run("scripts/evenements.py")
        r = subprocess.run([sys.executable, "scripts/controle_banque.py"], cwd=tmp, capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": str(tmp / "scripts")})
        assert r.returncode != 0 and "EV-16a : question mensuelle" in r.stdout, r.stdout[-500:]
    finally:
        shutil.rmtree(tmp.parent)


def test_annonces_et_grappes_d_ajout():
    """Relecture 20. N1 : un acte annoncé comme décidé (deux agents) n'est pas émis, mais l'annonce ne résout pas
    la question. N2 : un ajout emboîté dans une sous-question déjà émise rejoint sa grappe."""
    tmp, run = _copie()
    try:
        a = [{"annonce": True, "question": "EV-42", "date_annonce": "2026-10-20", "source": "s", "agent": ag,
              "emise": "2026-10-21T08:00:00+02:00"} for ag in ("agent-1", "agent-2")]
        (tmp / "registre/annonces.jsonl").write_text("".join(json.dumps(x) + chr(10) for x in a))
        run("scripts/geler.py", "2026-11-01", "2026-11", "--essai")
        run("scripts/questions.py", "2026-11-01", "2026-11")
        b = json.loads((tmp / "data/cycles/2026-11/questions.json").read_text())
        assert not any(q["id"].startswith("Q-EV-42") for q in b["questions"])
        run("scripts/resolution.py")
        res = (tmp / "registre/resolutions.jsonl")
        assert not res.exists() or "Q-EV-42" not in res.read_text()
        # N2 : ajout d'EV-15d (janvier-mars 2027), emboîté dans EV-15b.
        c = tmp / "modele/banque/criteres.json"
        d = json.loads(c.read_text())
        e15b = next(e for e in d["evenements"] if e["id"] == "EV-15b")
        d["evenements"].append({**e15b, "id": "EV-15d", "nom": "Censure du 1er janvier au 31 mars 2027",
                                "fenetre": {"debut": "2027-01-01", "fin": "2027-03-31"}})
        c.write_text(json.dumps(d, ensure_ascii=False))
        run("scripts/evenements.py")
        run("scripts/geler.py", "2026-12-01", "2026-12", "--essai")
        run("scripts/questions.py", "2026-12-01", "2026-12")
        g = {q["id"]: q["grappe"] for q in json.loads((tmp / "data/cycles/2026-12/questions.json").read_text())["questions"]}
        assert g["Q-EV-15d"] == g["Q-EV-15b"] == "EV-15b", (g.get("Q-EV-15d"), g.get("Q-EV-15b"))
        # Audit v1.25, D2 : EV-15e (15 déc.-15 janv.) relie EV-15 et EV-15b ; EV-15g (févr.-mars), emboîté dans
        # EV-15b seul, rejoint EV-15b et non la grappe de la liaison.
        d = json.loads(c.read_text())
        d["evenements"].append({**e15b, "id": "EV-15e", "nom": "Censure à cheval", "fenetre": {"debut": "2026-12-15", "fin": "2027-01-15"}})
        d["evenements"].append({**e15b, "id": "EV-15g", "nom": "Censure février-mars", "fenetre": {"debut": "2027-02-01", "fin": "2027-03-31"}})
        c.write_text(json.dumps(d, ensure_ascii=False))
        run("scripts/evenements.py")
        run("scripts/geler.py", "2027-01-01", "2027-01", "--essai")
        run("scripts/questions.py", "2027-01-01", "2027-01")
        b3 = json.loads((tmp / "data/cycles/2027-01/questions.json").read_text())
        g = {q["id"]: q["grappe"] for q in b3["questions"]}
        assert g["Q-EV-15g"] == "EV-15b", g.get("Q-EV-15g")
        assert any(e["objet"] == "EV-15e" and "reliant" in e["motif"] for e in b3["ecartees"]), b3["ecartees"][-3:]
        # Audit v1.25, D1 : coupure à la première annonce, quelle que soit l'issue (ici « non »).
        (tmp / "registre/annonces_v.jsonl").open("a").write(json.dumps({"annonce": True, "question": "EV-15", "date_annonce": "2026-11-02",
            "source": "s", "agent": "agent-1", "emise": "2026-11-03T08:00:00+01:00"}) + chr(10))
        code = r"""
import json, notation
from pathlib import Path
L = [{"question": "Q-EV-15", "probabilites": {"oui": p, "non": 100 - p}, "piste": "protocole", "phase": 1, "auteur": a,
      "origine": "cycle 2026-11", "donnees": "t", "emise": d + "T08:00:00+01:00"}
     for a, p, d in (("modèle", 20, "2026-11-01"), ("ensemble direct", 90, "2026-11-04"))]
Path('registre/v.jsonl').write_text(''.join(json.dumps(x) + chr(10) for x in L))
Path('registre/resolutions_v.jsonl').write_text(json.dumps({"resolution": True, "question": "Q-EV-15", "issue": "non",
    "date_fait": "2026-12-31", "source": "s", "methode": "m", "emise": "2027-01-05T08:00:00+01:00"}) + chr(10))
b = notation.bilan('registre/v.jsonl', 'ensemble direct', '2027-02-01')
print(json.dumps([e["auteur"] for e in b["exclues"] if e["question"] == "Q-EV-15"]))
"""
        assert json.loads(run("-c", code).strip().splitlines()[-1]) == ["ensemble direct"]
        # Vérificateur B (constat 2.1) : une annonce d'un autre registre ne coupe pas les prévisions de celui-ci.
        (tmp / "registre/annonces_v.jsonl").rename(tmp / "registre/annonces_autre.jsonl")
        assert json.loads(run("-c", code).strip().splitlines()[-1]) == []
        (tmp / "registre/annonces_autre.jsonl").rename(tmp / "registre/annonces_v.jsonl")
        # Audit interne v1.27, S1 : une annonce consignée après la résolution, même datée d'avant, ne coupe rien.
        (tmp / "registre/annonces_v.jsonl").write_text(json.dumps({"annonce": True, "question": "EV-15", "date_annonce": "2026-11-02",
            "source": "s", "agent": "agent-1", "emise": "2027-01-20T08:00:00+01:00"}) + chr(10))
        assert json.loads(run("-c", code).strip().splitlines()[-1]) == []
        # Audit interne v1.27 : une annonce inscrite au journal des contrôles (poussée hors fenêtre) est écartée.
        import hashlib
        brut = json.dumps({"annonce": True, "question": "EV-15", "date_annonce": "2026-11-02", "source": "s",
                           "agent": "agent-1", "emise": "2026-11-03T08:00:00+01:00"})
        (tmp / "registre/annonces_v.jsonl").write_text(brut + chr(10))
        assert json.loads(run("-c", code).strip().splitlines()[-1]) == ["ensemble direct"]
        (tmp / "registre/controles.jsonl").write_text(json.dumps({"fichier": "registre/annonces_v.jsonl",
            "empreinte": hashlib.sha256(brut.encode()).hexdigest()}) + chr(10))
        assert json.loads(run("-c", code).strip().splitlines()[-1]) == []
    finally:
        shutil.rmtree(tmp.parent)


def test_errata_et_unicite_du_cycle():
    """Relecture 21 et suivi 22. B1/N1 : une ligne inscrite au journal des contrôles n'est plus notée, même poussée
    douze jours après son émission et après le fait ; un erratum sans inscription au journal est ignoré et publié.
    I1 : une seconde prévision d'un même cycle est écartée, quelle que soit l'issue."""
    tmp, run = _copie()
    try:
        run("scripts/geler.py", "2026-11-01", "2026-11", "--essai")
        run("scripts/questions.py", "2026-11-01", "2026-11")
        ech = next(q["echeance"] for q in json.loads((tmp / "data/cycles/2026-11/questions.json").read_text())["questions"]
                   if q["id"] == "Q-EV-15")
        code = r"""
import json, sys, notation
from pathlib import Path
ech, cas = sys.argv[1], sys.argv[2]
P = lambda a, p, d, c="2026-11": {"question": "Q-EV-15", "probabilites": {"oui": p, "non": 100 - p}, "piste": "protocole",
    "phase": 1, "auteur": a, "origine": "cycle " + c, "donnees": "t", "emise": d + "T08:00:00+01:00"}
E = lambda d: {"erratum": True, "objet": {"question": "Q-EV-15", "auteur": "modèle", "emise": "2026-11-01T08:00:00+01:00"},
    "correction": {"annulee": True}, "motif": "poussée hors fenêtre", "piste": "protocole", "emise": d + "T09:00:00+01:00"}
if cas == "seconde":
    L = [P("modèle", 30, "2026-11-01"), P("ensemble direct", 30, "2026-11-03"), P("modèle", 1, "2026-11-28")]
    issue, fait = "non", ech
else:
    L = [P("modèle", 95, "2026-11-01"), P("ensemble direct", 30, "2026-11-03")] + ([E("2026-11-12")] if cas == "erratum_seul" else [])
    issue, fait = "oui", "2026-11-10"
    if cas in ("journal", "copie"):
        import hashlib
        brut = json.dumps(P("modèle", 95, "2026-11-01") if cas == "journal" else {**P("modèle", 95, "2026-11-01"), "probabilites": {"oui": 94, "non": 6}})
        if cas == "copie":   # copie tardive inscrite : elle ne doit pas annuler la ligne régulière (audit v1.27, B1)
            L.append(json.loads(brut))
        Path('registre/controles.jsonl').write_text("ligne illisible" + chr(10) + json.dumps({"fichier": "registre/v.jsonl",
            "empreinte": hashlib.sha256(brut.encode()).hexdigest(), "execution": "1"}) + chr(10))
Path('registre/v.jsonl').write_text(''.join(json.dumps(x) + chr(10) for x in L))
Path('registre/resolutions_v.jsonl').write_text(json.dumps({"resolution": True, "question": "Q-EV-15", "issue": issue,
    "date_fait": fait, "source": "s", "methode": "m", "emise": "2028-12-01T08:00:00+01:00"}) + chr(10))
b = notation.bilan('registre/v.jsonl', 'ensemble direct', '2028-12-31')
c = b["comparaisons"].get("modèle", {}).get("critere_8_6", {})
print(json.dumps({"auteurs": sorted(b["auteurs"]), "motifs": [e["motif"] for e in b["exclues"]], "t": c.get("t"),
                  "grappes": c.get("grappes")}))
"""
        r = lambda cas: json.loads(run("-c", code, ech, cas).strip().splitlines()[-1])
        o = r("journal")
        assert "modèle" not in o["auteurs"] and "annulée (journal des contrôles)" in o["motifs"], o
        o = r("copie")
        assert "modèle" in o["auteurs"], o
        (tmp / "registre/controles.jsonl").unlink()
        o = r("erratum_seul")
        assert "modèle" in o["auteurs"] and any("ignoré" in m for m in o["motifs"]), o
        o = r("seconde")
        assert "seconde prévision du cycle 2026-11" in o["motifs"] and o["grappes"] == 1 and o["t"] is None, o
    finally:
        shutil.rmtree(tmp.parent)


def test_controle_registres():
    """Suivi 22, N1, et audits internes v1.27 : contrôle à la poussée sur un dépôt Git jetable, journal sur fichier
    à part (branche « controles » en production), repère « controle_jusqua »."""
    import subprocess, os, hashlib
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    script = Path(__file__).resolve().parent / "controle_registres.py"
    tmp = Path(tempfile.mkdtemp())
    depot, journal, nouveau = tmp / "d", tmp / "controles.jsonl", tmp / "nouveau.jsonl"
    depot.mkdir()
    g = lambda *a, auteur="agent": subprocess.run(["git", "-c", f"user.name={auteur}", "-c", "user.email=a@b", *a], cwd=depot,
                                                  capture_output=True, text=True).stdout.strip()
    maintenant = datetime.now(ZoneInfo("Europe/Paris")).replace(microsecond=0)
    L = lambda q, t, auteur="modèle": json.dumps({"question": q, "probabilites": {"oui": 50, "non": 50}, "auteur": auteur,
                                                  "origine": "cycle 2026-11", "emise": t})
    def pousser(lignes, auteur="agent", f="registre/protocole.jsonl", binaire=False):
        (depot / f).parent.mkdir(parents=True, exist_ok=True)
        with (depot / f).open("ab") as h:
            h.write(lignes if binaire else "".join(x + "\n" for x in lignes).encode())
        g("add", "-A"); g("commit", "-qm", "c", auteur=auteur)
    def controler(avant="", pousses=None, pousse_le=None):
        env = {**os.environ, "AVANT": avant, "JOURNAL_CONTROLES": str(journal), "JOURNAL_NOUVEAU": str(nouveau),
               "GITHUB_RUN_ID": "7", "POUSSE_LE": str(int((pousse_le or maintenant).timestamp()))}
        if pousses is not None:
            (tmp / "pousses.json").write_text(json.dumps(pousses)); env["POUSSES"] = str(tmp / "pousses.json")
        r = subprocess.run([sys.executable, str(script)], cwd=depot, env=env, capture_output=True, text=True)
        subprocess.run([sys.executable, str(script), "--inscrire", str(journal)], cwd=depot, env=env, check=True)
        j = [json.loads(x) for x in journal.read_text().splitlines() if x.strip()]
        return r.returncode, r.stdout + r.stderr, [x for x in j if x.get("empreinte")]
    h = lambda x: hashlib.sha256(x.encode()).hexdigest()
    try:
        g("init", "-q")
        a_l_heure = L("Q1", maintenant.isoformat())
        pousser([a_l_heure]); b0 = g("rev-parse", "HEAD")
        pousser([L("Q2", maintenant.isoformat())])
        code, out, j = controler(b0)
        assert code == 0 and not j, out
        # Ligne tardive : inscrite par son empreinte. Copie d'une ligne régulière : signalée, non inscrite.
        tardive = L("Q3", (maintenant - timedelta(days=12)).isoformat())
        pousser([tardive, a_l_heure])
        code, out, j = controler()
        assert code == 1 and "recopiée" in out and [x["empreinte"] for x in j] == [h(tardive)], (out, j)
        # Inscription rejouée (journal lu avant une autre écriture, relance) : rien n'est inscrit deux fois.
        subprocess.run([sys.executable, str(script), "--inscrire", str(journal)], cwd=depot,
                       env={**os.environ, "JOURNAL_NOUVEAU": str(nouveau)}, check=True)
        j = [json.loads(x) for x in journal.read_text().splitlines() if x.strip()]
        assert [x["empreinte"] for x in j if x.get("empreinte")] == [h(tardive)], j
        # Décalage autre que celui de Paris, ou sans fuseau : inscrites, même dans la fenêtre.
        decalee = L("Q4", maintenant.astimezone(ZoneInfo("Pacific/Kiritimati")).isoformat())
        sans = L("Q5", maintenant.replace(tzinfo=None).isoformat())
        pousser([decalee, sans])
        code, out, j = controler()
        assert code == 1 and {h(decalee), h(sans)} <= {x["empreinte"] for x in j}, (out, j)
        # Commits non contrôlés (« [skip ci] », exécution interrompue) : couverts depuis le dernier repère.
        sautee = L("Q6", (maintenant - timedelta(hours=5)).isoformat())
        pousser([sautee]); pousser([L("Q7", maintenant.isoformat())])
        code, out, j = controler()
        assert h(sautee) in {x["empreinte"] for x in j}, (out, j)
        # Lignes « poison » (octet non UTF-8, année hors bornes) : illisibles, inscrites, sans interrompre le contrôle.
        poison = L("Q8", "9999-12-31T23:59:59-23:59")
        pousser(b"\xff\xfe{\n" + (poison + "\n").encode() + (L("Q9", (maintenant - timedelta(days=3)).isoformat()) + "\n").encode(), binaire=True)
        code, out, j = controler()
        assert "Traceback" not in out and h(poison) in {x["empreinte"] for x in j}, (out, j)
        # Troisième audit v1.27. Ligne de types inattendus : sans plantage, inscrite ; retour chariot et octet NUL :
        # l'empreinte est celle de la ligne brute, et le fichier reste contrôlé.
        typee = json.dumps({"question": ["EV-15", "EV-16"], "probabilites": {"oui": 50, "non": 50}, "origine": "cycle 2026-11",
                            "emise": maintenant.isoformat()})
        crlf = L("Q10", (maintenant - timedelta(days=2)).isoformat())
        pousser((typee + "\n" + crlf + "\r\n").encode() + b'{"question": "Q\x00", "emise": "x"}\n', binaire=True)
        code, out, j = controler()
        e = {x["empreinte"] for x in j}
        assert "Traceback" not in out and h(typee) in e and hashlib.sha256((crlf + "\r").encode()).hexdigest() in e, (out, j)
        assert hashlib.sha256(b'{"question": "Q\x00", "emise": "x"}').hexdigest() in e, (out, j)
        # Plage recontrôlée : chaque ligne est jugée à l'heure de la poussée qui l'a apportée (défaut 2) ; une relance
        # ancienne ne fait pas reculer le repère (défaut 3).
        bA = g("rev-parse", "HEAD")
        reguliere = L("Q12", (maintenant - timedelta(hours=6)).isoformat())
        pousser([reguliere]); bB = g("rev-parse", "HEAD")
        pousser([L("Q13", maintenant.isoformat())]); bC = g("rev-parse", "HEAD")
        pousses = [{"before": bA, "after": bB, "timestamp": (maintenant - timedelta(hours=6)).isoformat()},
                   {"before": bB, "after": bC, "timestamp": maintenant.isoformat()}]
        code, out, j = controler(pousses=pousses)
        assert h(reguliere) not in {x["empreinte"] for x in j}, (out, j)
        with journal.open("a") as fj:   # repère ancien écrit après coup (relance de l'exécution de bB)
            fj.write(json.dumps({"controle_jusqua": bB}) + "\n")
        tardive2 = L("Q14", (maintenant - timedelta(days=4)).isoformat())
        pousser([tardive2])
        code, out, j = controler(pousse_le=maintenant + timedelta(hours=5))
        assert h(L("Q13", maintenant.isoformat())) not in {x["empreinte"] for x in j}, (out, j)
        # Sans l'activité du dépôt, une poussée antérieure n'est pas jugée sur la fenêtre, et c'est signalé.
        bD = g("rev-parse", "HEAD")
        anterieure = L("Q15", (maintenant - timedelta(hours=6)).isoformat())
        pousser([anterieure]); bE = g("rev-parse", "HEAD"); pousser([L("Q16", maintenant.isoformat())])
        journal.write_text(journal.read_text() + json.dumps({"controle_jusqua": bD}) + "\n")
        code, out, j = controler(avant=bE)
        assert "heure de poussée inconnue" in out and h(anterieure) not in {x["empreinte"] for x in j}, (out, j)
        # Premières valeurs modifiées par un autre que la collecte ; journal présent sur main : signalés.
        pousser(['{"serie": "x"}'], f="data/premieres_valeurs.jsonl")
        pousser(['{"note": "x"}'], f="registre/controles.jsonl")
        code, out, j = controler()
        assert code == 1 and "et non par le workflow" in out and "branche « controles »" in out, out
    finally:
        shutil.rmtree(tmp)


def test_branche_du_journal():
    """Troisième audit v1.27, défaut 4 : branche « controles » absente ou recréée = erreur, jamais un journal vide."""
    import subprocess, os
    racine = Path(__file__).resolve().parent.parent
    tmp = Path(tempfile.mkdtemp())
    try:
        nu, depot = tmp / "nu.git", tmp / "depot"
        g = lambda cwd, *a: subprocess.run(["git", "-c", "user.name=a", "-c", "user.email=a@b", *a], cwd=cwd,
                                           capture_output=True, text=True)
        g(tmp, "init", "-q", "--bare", str(nu))
        shutil.copytree(racine, depot, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        g(depot, "init", "-q"); g(depot, "remote", "add", "origin", str(nu))
        code = "import commun; print(len(commun.journal_controles()))"
        env = {k: v for k, v in os.environ.items() if k != "JOURNAL_CONTROLES"}
        env["PYTHONPATH"] = str(depot / "scripts")
        run = lambda: subprocess.run([sys.executable, "-c", code], cwd=depot, env=env, capture_output=True, text=True)
        r = run()
        assert r.returncode != 0 and "introuvable" in (r.stdout + r.stderr), r.stdout + r.stderr   # branche absente
        j = tmp / "j"; g(tmp, "init", "-q", str(j)); (j / "controles.jsonl").write_text('{"controle_jusqua": "x"}\n')
        g(j, "add", "-A"); g(j, "commit", "-qm", "j"); g(j, "push", "-q", str(nu), "HEAD:refs/heads/controles")
        r = run()
        assert r.returncode != 0 and "recréée" in (r.stdout + r.stderr), r.stdout + r.stderr       # autre racine
        (depot / "modele/controles_racine.txt").write_text(g(j, "rev-parse", "HEAD").stdout)
        r = run()
        assert r.returncode == 0 and r.stdout.strip() == "1", r.stdout + r.stderr
    finally:
        shutil.rmtree(tmp)


def test_registre():
    tmp = Path(tempfile.mkdtemp())
    ancien = registre.RACINE
    registre.RACINE = tmp
    try:
        registre.ajouter("registre/t.jsonl", [{"question": "Q", "probabilites": {"oui": 60, "non": 40},
                                               "piste": "protocole", "phase": 1, "origine": "test", "donnees": "test"}])
        registre.valider({"erratum": True, "objet": {"question": "Q", "auteur": "modèle", "emise": "x"},
                          "correction": {"annulee": True}, "motif": "m", "piste": "protocole"})
        # Audit interne v1.27 : U+2028 dans un champ ne coupe pas la ligne à la relecture.
        registre.ajouter("registre/t.jsonl", [{"question": "Q", "probabilites": {"oui": 60, "non": 40}, "piste": "protocole",
                                               "phase": 1, "origine": "test", "donnees": "a\u2028b\u0085c"}])
        ancien_c = commun.RACINE
        commun.RACINE = tmp
        try:
            lues = commun.lire_jsonl("registre/t.jsonl")
        finally:
            commun.RACINE = ancien_c
        assert len(lues) == 2 and lues[1]["donnees"] == "a\u2028b\u0085c", lues
        # Ligne écrite avec un U+2028 littéral (sans échappement) : lue en une seule ligne.
        with (tmp / "registre/t.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"question": "Q", "source": "x\u2028y"}, ensure_ascii=False) + "\n")
        commun.RACINE = tmp
        try:
            lues = commun.lire_jsonl("registre/t.jsonl")
        finally:
            commun.RACINE = ancien_c
        assert len(lues) == 3 and lues[2]["source"] == "x\u2028y", lues
        # Troisième audit v1.27 : types inattendus refusés à l'écriture, écartés à la lecture.
        try:
            registre.valider({"proposition": True, "question": ["EV-15"], "issue": "oui", "source": "s", "agent": "a",
                              "date_fait": "2026-11-03"})
            raise AssertionError("question non textuelle acceptée")
        except ValueError:
            pass
        with (tmp / "registre/t.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"question": ["EV-15"], "probabilites": {"oui": 50, "non": 50}}) + "\r\n")
        commun.RACINE = tmp
        try:
            lues = commun.lire_jsonl("registre/t.jsonl")
        finally:
            commun.RACINE = ancien_c
        assert len(lues) == 3, lues
        l = json.loads((tmp / "registre/t.jsonl").read_text().split("\n")[0])
        assert l["emise"].endswith("+02:00") or l["emise"].endswith("+01:00")
        for mauvaise in ({"question": "Q", "probabilites": {"oui": 60, "non": 40}, "piste": "protocole", "origine": "o",
                          "donnees": "d"},                                   # phase manquante
                         {"question": "Q", "probabilites": {"oui": 60, "non": 30}, "piste": "exploratoire",
                          "origine": "o", "donnees": "d"},                   # somme ≠ 100
                         {"question": "Q", "probabilites": {"oui": 60, "non": 40}, "piste": "exploratoire",
                          "origine": "o", "donnees": "d", "emise": "2026-01-01T00:00:00+01:00"},  # horodatage fourni
                         {"erratum": True, "objet": {"question": "Q", "auteur": "modèle", "emise": "x"},
                          "correction": {"issue": "oui"}, "piste": "protocole", "motif": "m"},  # erratum de prévision non admis
                         {"erratum": True, "objet": {"question": "Q", "auteur": "modèle", "emise": "x"},
                          "correction": {"annulee": True}, "piste": "protocole"},             # sans motif
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


def test_rattrapage():
    """Passage manqué simulé (controle/phase1.md) : gel le 1er, reprise le 5 à la première étape non
    faite. La reprise garde la date du gel du manifeste (mêmes questions qu'un passage le 1er) et une
    étape déjà faite n'est pas rejouée (pas de lignes en double au registre)."""
    import subprocess
    racine = Path(__file__).resolve().parent.parent
    tmp = Path(tempfile.mkdtemp()) / "depot"
    shutil.copytree(racine, tmp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    etat = tmp / "data/historique/_collecte.json"
    etat.write_text(json.dumps({k: "2026-10-31" for k in json.loads(etat.read_text())}))
    try:
        env = {**__import__("os").environ, "PYTHONPATH": str(tmp / "scripts")}
        def run(*a):
            return subprocess.run([sys.executable, *a], cwd=tmp, env=env, capture_output=True, text=True)
        assert run("scripts/geler.py", "2026-11-01", "2026-11", "--essai").returncode == 0
        assert run("scripts/questions.py", "2026-11-01", "2026-11").returncode == 0
        q1 = json.loads((tmp / "data/cycles/2026-11/questions.json").read_text())
        # Reprise le 5 : le gel n'est pas refait ; une banque déjà écrite n'est pas régénérée (audit v1.27, S3) ;
        # si elle ne l'était pas, elle l'est à la date du gel du manifeste.
        assert run("scripts/geler.py", "2026-11-05", "2026-11", "--essai").returncode != 0
        assert run("scripts/questions.py", "2026-11-05", "2026-11").returncode != 0
        (tmp / "data/cycles/2026-11/questions.json").unlink()
        assert run("scripts/questions.py", "2026-11-05", "2026-11").returncode == 0
        q5 = json.loads((tmp / "data/cycles/2026-11/questions.json").read_text())
        assert q5["gel"] == "2026-11-01"
        assert [q["id"] for q in q5["questions"]] == [q["id"] for q in q1["questions"]], "questions écartées à la reprise"
        # Suivi 22, N3 : un fait postérieur au gel ne retire pas la question à la reprise ; un fait antérieur, si.
        ids = lambda: {q["id"] for q in json.loads((tmp / "data/cycles/2026-11/questions.json").read_text())["questions"]}
        assert "Q-EV-07" in ids()
        for jour, present in (("2026-11-03", True), ("2026-10-30", False)):
            (tmp / "registre/resolutions.jsonl").write_text(json.dumps({"resolution": True, "question": "Q-EV-07", "issue": "oui",
                "date_fait": jour, "source": "s", "methode": "m", "emise": "2026-11-04T08:00:00+01:00"}) + "\n")
            (tmp / "data/cycles/2026-11/questions.json").unlink()
            assert run("scripts/questions.py", "2026-11-05", "2026-11").returncode == 0
            assert ("Q-EV-07" in ids()) == present, (jour, present)
        (tmp / "registre/resolutions.jsonl").unlink()
        (tmp / "data/cycles/2026-11/questions.json").unlink()
        assert run("scripts/questions.py", "2026-11-05", "2026-11").returncode == 0
        reg = tmp / "registre/rattrapage.jsonl"
        assert run("scripts/comparateurs.py", "2026-11", "registre/rattrapage.jsonl").returncode == 0
        n = len(reg.read_text().splitlines())
        assert run("scripts/comparateurs.py", "2026-11", "registre/rattrapage.jsonl").returncode != 0
        assert len(reg.read_text().splitlines()) == n, "comparateurs rejoués à la reprise"
        ens = [{"question": "X", "probabilites": {"oui": 50, "non": 50}, "piste": "protocole", "phase": 1,
                "auteur": "ensemble direct", "origine": "cycle 2026-11, médiane de 5", "donnees": "d"}]
        reg.write_text(reg.read_text() + json.dumps({**ens[0], "emise": "2026-11-01T09:00:00+01:00"}) + "\n")
        r = run("scripts/ensemble.py", "2026-11", "registre/rattrapage.jsonl")
        assert r.returncode != 0 and "déjà" in (r.stderr + r.stdout), "ensemble rejoué à la reprise"
    finally:
        shutil.rmtree(tmp.parent)


if __name__ == "__main__":
    for nom, f in list(globals().items()):
        if nom.startswith("test_"):
            f()
            print(f"ok  {nom}")
