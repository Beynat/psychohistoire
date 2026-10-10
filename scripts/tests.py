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
    """Feuille de route v0, bloc 2, et étape 2 : une définition dont la fenêtre s'ouvre dans moins de 7 jours est
    refusée ; un jalon indice observé relève, dans le registre fantôme calculé par le moteur, l'issue qu'il favorise."""
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
        # Registre fantôme par le moteur unique (étape 2) : J-001 (49.3 sur le budget, indice sur la censure d'ici
        # fin 2026) observé relève EV-15 par rapport à la référence, calculée sans les indices.
        r = subprocess.run([sys.executable, "scripts/jalons.py", "statut"], cwd=tmp, env=env, capture_output=True, text=True,
                           input=json.dumps({"jalon": "J-001", "statut": "observé", "date": j0, "source": "s", "agent": "a"}) + chr(10))
        assert r.returncode == 0, r.stderr[-300:]
        (tmp / "data/cycles/t").mkdir(parents=True, exist_ok=True)
        (tmp / "data/cycles/t/questions.json").write_text(json.dumps({"questions": [
            {"id": "Q-EV-15", "type": "evenement", "details": {"evenement": "EV-15"}, "issues": ["oui", "non"],
             "fenetre": {"debut": "2026-10-10", "fin": "2026-12-31"}}]}))
        ligne = {"question": "Q-EV-15", "probabilites": {"oui": 30.0, "non": 70.0}, "piste": "v0", "auteur": "réseau v0",
                 "origine": "cycle t", "donnees": "t"}
        subprocess.run([sys.executable, "scripts/registre.py", "registre/essai_j.jsonl"], cwd=tmp, env=env, check=True,
                       capture_output=True, text=True, input=json.dumps(ligne) + chr(10))
        run("scripts/jalons.py", "fantome", "registre/essai_j.jsonl", "--tirages", "20", "--trajectoires", "100")
        f = [json.loads(l) for l in (tmp / "registre/fantome.jsonl").read_text().splitlines() if l.strip()]
        assert f[-1]["question"] == "Q-EV-15" and "J-001" in f[-1]["jalons"], f[-1]
        assert f[-1]["probabilites"]["oui"] > f[-1]["reference"]["oui"] + 3, f[-1]
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
    """Feuille de route v0, blocs 2 et 8, et étape 2 : décision sur un fait imprévu (sens opposés refusés, allégation
    sans effet, indice plafonné puis réduit par k = 0,5, fait qui tranche appliqué tel quel), quantile de Student du
    critère de direction."""
    import faits, direction
    oppose = faits.decider({"fait": "f", "noeud": "N", "issues": ["oui", "non"],
                            "avis": [{"p": {"oui": 0.6, "non": 0.3}}, {"p": {"oui": 0.2, "non": 0.4}}]})
    assert not oppose["retenu"] and "sens" in oppose["motifs"][0]
    alleg = faits.decider({"fait": "f", "noeud": "N", "issues": ["oui", "non"], "stade": "allégation",
                           "avis": [{"p": {"oui": 0.9, "non": 0.01}}] * 5})
    assert not alleg["retenu"] and alleg["classe"] == "allégation"
    fort = faits.decider({"fait": "f", "noeud": "N", "issues": ["oui", "non"], "avis": [{"p": {"oui": 0.9, "non": 0.1}}] * 5})
    assert fort["retenu"] and fort["classe"] == "indice" and abs(fort["vraisemblances"]["non"] - (1 / 3) ** 0.5) < 0.01, fort
    tranche = faits.decider({"fait": "f", "noeud": "N", "issues": ["oui", "non"], "avis": [{"p": {"oui": 0.9, "non": 0.01}}] * 3})
    assert tranche["classe"] == "tranche" and tranche["vraisemblances"]["non"] < 0.02, tranche
    assert direction.quantile_student_90(4) == 1.533 and direction.quantile_student_90(40) == 1.2816


def test_moteur_etape1():
    """Feuille de route, étape 1 (bogues du moteur, revues du 10 octobre 2026). Chaque cas est discriminant : il
    échoue avec l'ancien comportement (contrôles par mutation consignés au journal)."""
    import reseau
    tout = lambda e: {m: e for m in reseau.MOIS}
    fen = ["2026-10-10", "2028-09-30"]
    survenue = lambda n: {"caracteristique": {"type": "survenue", "noeud": n}, "table": {"oui": 100, "non": 0}}
    q = lambda e, f: {"id": f"Q-{e}", "evenement": e, "issues": ["oui", "non"], "fenetre": f}
    try:
        # 1. Parent daté pas encore tranché : moyenne des multiplicateurs sous sa loi a priori (0,2 × 1 + 0,8 × 0,1
        # = 0,28), et non l'état de référence (× 1). Fenêtre close avant la date du parent.
        S = {"variables_etat": [], "mesures": {"EV-H": survenue("PV-H")},
             "pivots": [{"id": "PV-D", "nature": "daté", "date": "2027-06-30", "issues": ["a", "b"], "parents": []},
                        {"id": "PV-H", "nature": "à tout moment", "fenetre": fen, "parents": ["PV-D"]}]}
        T = {"noeuds": {"PV-D": {"base": {"a": 0.2, "b": 0.8}}, "PV-H": {"p_fenetre": 0.8, "multiplicateurs": {"PV-D": {"b": {"oui": 0.1}}}}}}
        p = reseau.prevoir(S, T, {}, [q("EV-H", ["2026-10-10", "2027-05-31"])], 30, 200)["Q-EV-H"]["oui"]
        # sans le parent : h = 1 - 0,2^(1/24) par mois sur 8 mois, soit 41 % ; avec × 0,28 sur la fenêtre : 0,224 → 8 %
        assert p < 15, p
        # 2. Multiplicateur demandé sur la probabilité de fenêtre : 0,6 relevé × 3 donne 82 % (rapport de cotes), et
        # non 94 % (risque mensuel multiplié) ; abaissé × 0,5 donne 30 %.
        S = {"variables_etat": [{"id": "VE-X", "etats": ["r", "s"], "reference": "r", "parents": []}], "mesures": {"EV-H": survenue("PV-H")},
             "pivots": [{"id": "PV-H", "nature": "à tout moment", "fenetre": fen, "parents": ["VE-X"]}]}
        T = {"noeuds": {"VE-X": {"reference": "r", "transition": {"r": {"r": 1, "s": 0}, "s": {"r": 0, "s": 1}}},
                        "PV-H": {"p_fenetre": 0.6, "sigma": 0.01, "multiplicateurs": {"VE-X": {"s": {"oui": 3.0}}}}}}
        reseau.SIGMA_PLANCHER, plancher = 0.01, reseau.SIGMA_PLANCHER
        try:
            p = reseau.prevoir(S, T, {"VE-X": tout("s")}, [q("EV-H", fen)], 5, 2000)["Q-EV-H"]["oui"]
            assert 78 < p < 86, p
            T["noeuds"]["PV-H"]["multiplicateurs"]["VE-X"]["s"]["oui"] = 0.5
            p = reseau.prevoir(S, T, {"VE-X": tout("s")}, [q("EV-H", fen)], 5, 2000)["Q-EV-H"]["oui"]
            assert 26 < p < 34, p
        finally:
            reseau.SIGMA_PLANCHER = plancher
        # 3. Déclencheur : un parent « à tout moment » survenu en cours de fenêtre agit sur le reste de la fenêtre
        # (censure en avril → 96 % de départ en avril-mai, et non 55 % en étalant la probabilité sur huit mois).
        S = {"variables_etat": [], "mesures": {"EV-G": survenue("PV-G")},
             "pivots": [{"id": "PV-C", "nature": "à tout moment", "fenetre": ["2027-04-01", "2027-04-30"], "parents": []},
                        {"id": "PV-G", "nature": "à tout moment", "fenetre": ["2026-10-10", "2027-05-02"], "parents": ["PV-C"]}]}
        T = {"noeuds": {"PV-C": {"p_fenetre": 0.999999}, "PV-G": {"p_fenetre": 0.1, "multiplicateurs": {"PV-C": {"oui": {"oui": 200.0}}}}}}
        p = reseau.prevoir(S, T, {}, [q("EV-G", ["2027-04-01", "2027-05-02"])], 20, 200)["Q-EV-G"]["oui"]
        assert p > 85, p
        # 4. Verrou daté (article 12) : aucune dissolution dans les douze mois qui suivent la précédente.
        S = {"variables_etat": [], "mesures": {"EV-B": survenue("PV-B")},
             "verrous": [{"si": "PV-A", "interdit": ["PV-B"], "duree_mois": 12}],
             "pivots": [{"id": "PV-A", "nature": "à tout moment", "fenetre": ["2026-10-10", "2026-12-31"], "parents": []},
                        {"id": "PV-B", "nature": "à tout moment", "fenetre": ["2027-05-03", "2028-09-30"], "parents": []}]}
        T = {"noeuds": {"PV-A": {"p_fenetre": 0.999999}, "PV-B": {"p_fenetre": 0.9}}}
        r = reseau.prevoir(S, T, {}, [q("EV-B", ["2027-05-03", "2027-10-31"]), {**q("EV-B", ["2028-01-01", "2028-09-30"]), "id": "Q-T"}], 20, 200)
        assert r["Q-EV-B"]["oui"] < 1 and r["Q-T"]["oui"] > 20, r
        # Même mois : dissolution le mois où s'ouvre la fenêtre suivante (verrou compté dès le mois du fait).
        S["pivots"][0]["fenetre"], S["pivots"][1]["fenetre"] = ["2027-05-01", "2027-05-02"], ["2027-05-03", "2027-06-30"]
        S["pivots"][1]["parents"] = ["PV-A"]
        r = reseau.prevoir(S, T, {}, [q("EV-B", ["2027-05-03", "2027-06-30"])], 10, 200)
        assert r["Q-EV-B"]["oui"] < 1, r
        # 5. Extinction d'un fait : sans objet depuis l'étape 2 (les faits sont des preuves, sans multiplicateur
        # appliqué de mois en mois ; voir test_preuves).
        # 6. Contrôle de cohérence sur toutes les issues d'une question à plusieurs issues (EV-05).
        _, a = reseau.ecart_direct({"Le Pen": 51.3, "Philippe": 20.4, "autre": 28.3}, {"Le Pen": 43, "Philippe": 31.9, "autre": 25.1})
        assert a == 1
        assert reseau.ecart_direct({"oui": 50, "non": 50}, 45) == ("  évaluateurs 45", 0)
        # 7. Observation du mois en cours d'une variable « maximum du mois » : un minimum, pas un état.
        S = {"variables_etat": [{"id": "VE-M", "etats": ["calme", "modérée", "forte"], "reference": "calme", "parents": []}],
             "pivots": [], "mesures": {"EV-M": {"caracteristique": {"type": "etat_max", "noeud": "VE-M"}, "table": {"calme": 0, "modérée": 0, "forte": 100}}}}
        T = {"noeuds": {"VE-M": {"reference": "calme", "transition": {e: {"calme": 0.2, "modérée": 0.4, "forte": 0.4} for e in ("calme", "modérée", "forte")}}}}
        p = reseau.prevoir(S, T, {"VE-M": {"2026-10": {"au_moins": "modérée"}}}, [q("EV-M", ["2026-10-01", "2026-10-31"])], 20, 200)["Q-EV-M"]["oui"]
        assert 45 < p < 55, p    # forte 0,4 / (0,4 + 0,4) = 50 % ; un état fixé donnerait 0 %, un tirage libre 40 %
        # 8. Intervalle à 80 % sans le bruit de simulation : à peu près le même avec 20 ou 400 trajectoires par tirage.
        S = {"variables_etat": [], "mesures": {"EV-H": survenue("PV-H")},
             "pivots": [{"id": "PV-H", "nature": "à tout moment", "fenetre": fen, "parents": []}]}
        T = {"noeuds": {"PV-H": {"p_fenetre": 0.5}}}
        l = lambda n: (lambda i: i[1] - i[0])(reseau.prevoir(S, T, {}, [q("EV-H", fen)], 200, n, graine=3)["Q-EV-H"]["i80"])
        petit, grand = l(20), l(400)
        assert 0.75 < petit / grand < 1.3, (petit, grand)
    finally:
        pass


def test_preuves():
    """Feuille de route, étape 2 : moteur de preuve unique. Une preuve sur un enfant remonte vers son parent et
    descend vers l'aval ; un fait qui tranche s'applique sans réduction ; un pivot tranché met à jour ses parents ;
    une combinaison rare est signalée et un pivot tranché trop rare est imposé ; classes des jalons."""
    import reseau, preuves
    survenue = lambda n: {"caracteristique": {"type": "survenue", "noeud": n}, "table": {"oui": 100, "non": 0}}
    issue = lambda n: {"caracteristique": {"type": "issue", "noeud": n}, "table": "identite"}
    S = {"variables_etat": [], "mesures": {"EV-P": issue("PV-P"), "EV-E": issue("PV-E"), "EV-A": issue("PV-A")},
         "pivots": [{"id": "PV-P", "nature": "daté", "date": "2026-12-31", "issues": ["x", "y"], "parents": []},
                    {"id": "PV-E", "nature": "daté", "date": "2027-03-31", "issues": ["u", "v"], "parents": [],
                     "conditionnelle": "PV-P"},
                    {"id": "PV-A", "nature": "daté", "date": "2027-06-30", "issues": ["s", "t"], "parents": [],
                     "conditionnelle": "PV-E"}]}
    S["pivots"][1]["parents"] = ["PV-P"]
    S["pivots"][2]["parents"] = ["PV-E"]
    T = {"noeuds": {"PV-P": {"base": {"x": 0.5, "y": 0.5}},
                    "PV-E": {"base": {"u": 0.9, "v": 0.1}, "conditionnelle": {"x": {"u": 0.9, "v": 0.1}, "y": {"u": 0.1, "v": 0.9}}},
                    "PV-A": {"base": {"s": 0.8, "t": 0.2}, "conditionnelle": {"u": {"s": 0.8, "t": 0.2}, "v": {"s": 0.2, "t": 0.8}}}}}
    f = ["2026-10-10", "2027-06-30"]
    qs = [{"id": f"Q-{e}", "evenement": e, "issues": i, "fenetre": f} for e, i in (("EV-P", ["x", "y"]), ("EV-E", ["u", "v"]), ("EV-A", ["s", "t"]))]
    sans = reseau.prevoir(S, T, {}, qs, 10, 300)
    tr = {"id": "J", "noeud": "PV-E", "classe": "tranche", "vraisemblances": {"u": 0.02, "v": 0.9}}
    avec = reseau.prevoir(S, T, {}, qs, 10, 300, preuves=[tr])
    # amont : P(y | v observé) = 0,45 / 0,5 = 90 % ; aval : P(t) passe de 32 % à environ 77 %
    assert sans["Q-EV-P"]["y"] < 60 and avec["Q-EV-P"]["y"] > 80, (sans["Q-EV-P"], avec["Q-EV-P"])
    assert avec["Q-EV-A"]["t"] > 65, avec["Q-EV-A"]
    assert avec["__pivots__"]["PV-E"]["v"] > 80 and 0.1 < avec["__ess__"]["part"] < 0.7, (avec["__pivots__"], avec["__ess__"])
    # Fait qui tranche : vraisemblances appliquées telles quelles (J-026, « Attal renonce », « les deux » à 0,01).
    v = {"noeud": "PV-BLOC", "etat_reseau": None, "vraisemblances": {"les deux": 0.01, "Philippe seul": 0.601, "Attal seul": 0.014, "aucun des deux": 0.069}}
    assert preuves.classe_jalon(v) == "tranche" and preuves.preuve_jalon("J-026", v, "observé")["vraisemblances"]["les deux"] == 0.01
    assert preuves.preuve_jalon("J-026", v, "manqué")["classe"] == "indice"
    ind = {"noeud": "PV-X", "etat_reseau": None, "vraisemblances": {"oui": 0.6, "non": 0.3}}
    assert preuves.classe_jalon(ind) == "indice" and abs(preuves.preuve_jalon("J", ind, "observé")["vraisemblances"]["oui"] - 0.6 ** 0.5) < 1e-9
    # Pivot tranché : preuve sur l'enfant, pas état imposé ; le parent est mis à jour.
    o = reseau.prevoir(S, T, {"PV-E": {"2027-03": "v"}}, qs, 10, 300)
    assert o["Q-EV-P"]["y"] > 80 and not o["__ess__"].get("imposes"), (o["Q-EV-P"], o["__ess__"])
    # Combinaison rare : un pivot tranché presque impossible a priori est imposé (intervention), signalé.
    T2 = json.loads(json.dumps(T))
    T2["noeuds"]["PV-P"]["base"] = {"x": 0.999, "y": 0.001}
    T2["noeuds"]["PV-E"]["conditionnelle"]["x"] = {"u": 0.999, "v": 0.001}
    o = reseau.prevoir(S, T2, {"PV-E": {"2027-03": "v"}}, qs, 5, 200)
    assert o["__ess__"].get("imposes") == ["PV-E"] and o["Q-EV-E"]["v"] == 100, o["__ess__"]
    rare = reseau.prevoir(S, T2, {}, qs, 5, 200, preuves=[{"id": "R", "noeud": "PV-E", "classe": "tranche", "vraisemblances": {"u": 0.0, "v": 1.0}}])
    assert rare["__ess__"]["alerte"], rare["__ess__"]


def test_calendrier():
    """Feuille de route, étape 3 : chaque pivot daté renvoie à une entrée sourcée du calendrier, à la même date ; les
    fenêtres des questions concordent avec les dates et fenêtres des nœuds qui les mesurent ; un profil de risque
    reproduit la probabilité de fenêtre et la concentre sur les mois de poids fort."""
    import reseau
    racine = Path(__file__).resolve().parent.parent
    cal = json.loads((racine / "modele/reseau/calendrier.json").read_text())
    S = json.loads((racine / "modele/reseau/structure_v0.json").read_text())
    ev = {e["id"]: e for e in json.loads((racine / "modele/evenements.json").read_text())["evenements"]}
    E = {e["id"]: e for e in cal["entrees"]}
    for e in cal["entrees"]:
        assert e["source"]["rang"] in ("PO", "I", "MR", "S", "calcul"), e
        assert e["source"].get("url") or e["source"].get("texte"), e
    for p in S["pivots"]:
        if p["nature"] == "daté":
            assert p.get("calendrier") in E, (p["id"], p.get("calendrier"))
            assert E[p["calendrier"]]["date"] == p["date"], (p["id"], p["date"], E[p["calendrier"]]["date"])
        if isinstance(p.get("profil"), str):
            assert p["profil"] in cal["profils"], p["id"]
    noeuds = {n["id"]: n for n in S["pivots"]}
    for q, m in S["mesures"].items():
        c = m["caracteristique"]
        els = c.get("elements", [c])
        for x in els:
            n = noeuds.get(x.get("noeud"))
            if not n or q not in ev:
                continue
            fin = ev[q]["fenetre"]["fin"]
            if n["nature"] == "daté":
                assert n["date"] <= fin, (q, n["id"], n["date"], fin)   # le nœud est tranché avant la fin de la question
            elif x["type"] == "survenue":
                a, b = x.get("debut") or ev[q]["fenetre"]["debut"], min(x.get("fin") or fin, fin)
                assert n["fenetre"][0] <= b and a <= n["fenetre"][1], (q, n["id"])   # fenêtres qui se recouvrent
                if len(els) == 1:
                    assert n["fenetre"][1] >= b, (q, n["id"], n["fenetre"], b)        # le nœud couvre la question
    # Profil : P = 0,5 sur un an, tout le poids en mars 2027 (poids 0 ailleurs) : 50 % sur la fenêtre, 0 % hors mars.
    survenue = lambda d, f: {"caracteristique": {"type": "survenue", "noeud": "PV-N", "debut": d, "fin": f}, "table": {"oui": 100, "non": 0}}
    S2 = {"variables_etat": [], "pivots": [{"id": "PV-N", "nature": "à tout moment", "fenetre": ["2026-10-10", "2027-09-30"], "parents": [],
                                            "profil": {"poids": {"2027-03": 1.0}, "defaut": 0.0}}],
          "mesures": {"EV-A": survenue(None, None), "EV-B": survenue("2026-10-10", "2027-02-28")}}
    T2 = {"noeuds": {"PV-N": {"p_fenetre": 0.5}}}
    q = [{"id": "Q-A", "evenement": "EV-A", "issues": ["oui", "non"], "fenetre": ["2026-10-10", "2027-09-30"]},
         {"id": "Q-B", "evenement": "EV-B", "issues": ["oui", "non"], "fenetre": ["2026-10-10", "2027-09-30"]}]
    r = reseau.prevoir(S2, T2, {}, q, 20, 200)
    assert 42 < r["Q-A"]["oui"] < 58 and r["Q-B"]["oui"] == 0, r


def test_lois_par_cas():
    """Feuille de route, étape 4 : le moteur lit une table par cas (pivot « à tout moment », pivot daté dont un parent
    n'est pas tranché, variable d'état) ; les jokers d'un évaluateur couvrent les cas, le plus précis l'emporte ; les
    contrôles d'une ronde relèvent une justification vide et deux évaluateurs de sens opposés."""
    import reseau, tables
    tout = lambda e: {m: e for m in reseau.MOIS}
    survenue = lambda n: {"caracteristique": {"type": "survenue", "noeud": n}, "table": {"oui": 100, "non": 0}}
    issue = lambda n: {"caracteristique": {"type": "issue", "noeud": n}, "table": "identite"}
    fen = ["2026-10-10", "2027-09-30"]
    S = {"variables_etat": [{"id": "VE-X", "etats": ["a", "b"], "reference": "a", "parents": []}],
         "pivots": [{"id": "PV-H", "nature": "à tout moment", "fenetre": fen, "parents": ["VE-X"]},
                    {"id": "PV-P", "nature": "daté", "date": "2027-06-30", "issues": ["u", "v"], "parents": []},
                    {"id": "PV-D", "nature": "daté", "date": "2027-03-31", "issues": ["s", "t"], "parents": ["PV-P"]}],
         "mesures": {"EV-H": survenue("PV-H"), "EV-D": issue("PV-D")}}
    T = {"noeuds": {"VE-X": {"cas": {"prec=a": {"a": 1.0, "b": 0.0}, "prec=b": {"a": 0.0, "b": 1.0}}, "reference": "a"},
                    "PV-H": {"cas": {"VE-X=a": 0.1, "VE-X=b": 0.7}, "sigma": 0.01},
                    "PV-P": {"base": {"u": 0.25, "v": 0.75}, "sigma": 0.01},
                    "PV-D": {"cas": {"PV-P=u": {"s": 1.0, "t": 0.0}, "PV-P=v": {"s": 0.0, "t": 1.0}}, "sigma": 0.01}}}
    q = [{"id": "Q-H", "evenement": "EV-H", "issues": ["oui", "non"], "fenetre": fen},
         {"id": "Q-D", "evenement": "EV-D", "issues": ["s", "t"], "fenetre": fen}]
    plancher, reseau.SIGMA_PLANCHER = reseau.SIGMA_PLANCHER, 0.01
    try:
        r = reseau.prevoir(S, T, {"VE-X": tout("b")}, q, 5, 1000)
    finally:
        reseau.SIGMA_PLANCHER = plancher
    assert 65 < r["Q-H"]["oui"] < 75, r["Q-H"]             # cas VE-X = b pendant toute la fenêtre : 70 %
    assert 20 < r["Q-D"]["s"] < 30, r["Q-D"]               # parent pas encore tranché : mélange sous sa loi a priori
    assert tables.correspond("A=x|B=y", "A=x|B=*") == 1 and tables.correspond("A=x|B=y", "A=z|B=*") is None
    rep = {"noeuds": {"PV-H": {"cas": {"VE-X=*": {"loi": {"oui": 0.2}, "justification": "jugement : par défaut"},
                                       "VE-X=b": {"loi": {"oui": 0.6}, "justification": "jugement : cas aggravé"}}}}}
    cles = ["VE-X=a", "VE-X=b"]
    assert tables.lois_de(rep, "PV-H", cles) == {"VE-X=a": 0.2, "VE-X=b": 0.6}
    rep2 = json.loads(json.dumps(rep))
    rep2["noeuds"]["PV-H"]["cas"]["VE-X=b"]["justification"] = ""
    assert any("justification vide" in x for x in tables.verifier_cas({**rep2, "direct": {}}))
    a = {"noeuds": {"PV-H": {"cas": {"VE-X=a": {"poids_reseau": 0.8, "loi": {"oui": 0.2}}, "VE-X=b": {"poids_reseau": 0.2, "loi": {"oui": 0.5}}}}}}
    b = {"noeuds": {"PV-H": {"cas": {"VE-X=a": {"poids_reseau": 0.8, "loi": {"oui": 0.2}}, "VE-X=b": {"poids_reseau": 0.2, "loi": {"oui": 0.1}}}}}}
    import unittest.mock as um
    with um.patch.object(tables, "cas_du_noeud", lambda n, ns: cles), um.patch.object(tables, "_structure", lambda: S):
        so = tables.sens_opposes([a, b])
        assert so and so[0]["cas"] == "VE-X=b", so
        assert not tables.sens_opposes([a, a])
    # σ pondéré par la fréquence des cas : un cas sous verrou (poids nul) très dispersé ne gonfle pas l'incertitude.
    assert tables.sigma_pondere([(1.0, 0.1), (0.0, 5.0)]) == 0.3 and tables.sigma_pondere([(1.0, 0.8), (1.0, 0.4)]) == 0.6


def test_hypotheses():
    """Feuille de route, étape 5 : registre des hypothèses porteuses (nœuds existants, probabilité de rupture,
    au moins trois signaux) ; issue « autre candidat RN » : impossible si Le Pen est candidate, et le vainqueur RN
    est alors Le Pen, Bardella ou « autre » selon l'état des deux pivots ; le tri refuse une hypothèse inconnue."""
    import reseau
    racine = Path(__file__).resolve().parent.parent
    H = json.loads((racine / "modele/reseau/hypotheses.json").read_text())
    S = json.loads((racine / "modele/reseau/structure_v0.json").read_text())
    T = json.loads((racine / "modele/reseau/tables_v0.json").read_text())
    noeuds = reseau.noeuds_de(S)
    for h in H["hypotheses"]:
        assert set(h["noeuds"]) <= set(noeuds), (h["id"], h["noeuds"])
        assert 0 < h["probabilite_rupture"] < 1 and len(h["signaux"]) >= 3 and h["traitement"], h["id"]
    tab = T["mesures"]["EV-05"]
    assert reseau.chercher(tab, "RN|candidate|non") == {"Marine Le Pen": 100.0}
    assert reseau.chercher(tab, "RN|non candidate|non") == {"Jordan Bardella": 100.0}
    assert reseau.chercher(tab, "RN|non candidate|oui").get("autre") == 100.0
    import random
    reseau.PRIORS = reseau.lois_a_priori(S, T, reseau.observations(S), n=200)
    rng, params, vus = random.Random(3), {i: dict(x) for i, x in T["noeuds"].items()}, set()
    T2 = json.loads(json.dumps(T))
    T2["noeuds"]["PV-RNAUTRE"]["cas"]["PV-LEPEN=non candidate"] = {"non": 0.0, "oui": 1.0}   # pour voir la branche
    T2["noeuds"]["PV-RNAUTRE"]["cas"]["PV-LEPEN=candidate"] = {"non": 0.5, "oui": 0.5}       # l'exclusion doit primer
    params2 = {i: dict(x) for i, x in T2["noeuds"].items()}
    for _ in range(300):
        tr = reseau.simuler(S, params2, reseau.observations(S), rng)
        vus.add((tr["PV-LEPEN"][-1], tr["PV-RNAUTRE"][-1]))
    assert ("candidate", "oui") not in vus and ("non candidate", "oui") in vus, vus
    tmp, run = _copie()
    try:
        (tmp / "data/veille.json").write_text(json.dumps({"items": [{"source": "s", "titre": "t", "lien": "http://x/1", "date": "2026-10-09"}]}))
        import subprocess, os
        env = {**os.environ, "PYTHONPATH": str(tmp / "scripts")}
        l = {"lien": "http://x/1", "fait": "f", "decision": "non rattaché", "motif": "m", "hypotheses": ["H-99"]}
        r = subprocess.run([sys.executable, "scripts/tri.py", "ajouter"], cwd=tmp, env=env, capture_output=True, text=True, input=json.dumps(l) + chr(10))
        assert r.returncode != 0 and "H-99" in (r.stderr + r.stdout), r.stderr[-200:]
        l["hypotheses"] = ["H-01"]
        r = subprocess.run([sys.executable, "scripts/tri.py", "ajouter"], cwd=tmp, env=env, capture_output=True, text=True, input=json.dumps(l) + chr(10))
        assert r.returncode == 0, r.stderr[-300:]
        r = subprocess.run([sys.executable, "scripts/tri.py", "reprise"], cwd=tmp, env=env, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-300:]
        rep = json.loads((tmp / "data/reprise.json").read_text())
        assert rep["hypotheses"]["H-01"]["faits"] == ["f"], rep.get("hypotheses")
    finally:
        shutil.rmtree(tmp.parent)


def test_processus_etape6():
    """Feuille de route, étape 6 : questions rapides (jalons et variables, pool PR) générées, prévues par le moteur et
    résolues par script ; réseau témoin gelé une seule fois et protégé par empreintes ; gel de 48 heures avant un cycle."""
    import rapides, reseau
    import unittest.mock as um
    qs = rapides.generer("2026-11-01", "2026-11")
    assert any(q["details"]["rapide"] == "jalon" for q in qs) and sum(q["details"]["rapide"] == "variable" for q in qs) == 6
    assert all(q["pool"] == "PR" and q["type"] == "rapide" for q in qs)
    racine = Path(__file__).resolve().parent.parent
    S = json.loads((racine / "modele/reseau/structure_v0.json").read_text())
    T = json.loads((racine / "modele/reseau/tables_v0.json").read_text())
    jal = next(q for q in qs if q["details"].get("jalon") == "J-001")
    var = next(q for q in qs if q["details"].get("noeud") == "VE-POP")
    p = reseau.prevoir(S, T, reseau.observations(S), [{"id": q["id"], "rapide": q["details"], "issues": q["issues"]} for q in (jal, var)], 3, 60)
    assert 0 < p[jal["id"]]["oui"] < 100 and abs(sum(v for k, v in p[var["id"]].items() if k not in ("i80", "es")) - 100) < 0.5, p
    st = [{"jalon": "J-001", "statut": "observé", "date": "2026-11-20", "source": "s"}]
    with um.patch.object(rapides, "lire_jsonl", lambda f: st if "statuts" in f else []):
        assert rapides.resolution(jal)["issue"] == "oui"
    obs = {"etabli_le": "2026-12-02", "etats": {"VE-POP": {"2026-11": "< 25 %"}}}
    with um.patch.object(rapides, "lire_json", lambda f: obs):
        assert rapides.resolution(var)["issue"] == "< 25 %"
    obs["etabli_le"] = "2026-11-20"   # mois pas encore écoulé : pas de résolution
    with um.patch.object(rapides, "lire_json", lambda f: obs):
        assert rapides.resolution(var) is None
    tmp, run = _copie()
    try:
        import subprocess, os
        env = {**os.environ, "PYTHONPATH": str(tmp / "scripts")}
        shutil.rmtree(tmp / "modele/reseau/gele", ignore_errors=True)   # le dépôt réel est déjà gelé : on rejoue le gel sur la copie
        r = subprocess.run([sys.executable, "scripts/reseau.py", "--geler"], cwd=tmp, env=env, capture_output=True, text=True)
        assert r.returncode == 0 and (tmp / "modele/reseau/gele/manifeste.json").exists(), r.stderr[-300:]
        r = subprocess.run([sys.executable, "scripts/reseau.py", "--geler"], cwd=tmp, env=env, capture_output=True, text=True)
        assert r.returncode != 0, "second gel accepté"
        f = tmp / "modele/reseau/gele/tables_v0.json"
        f.write_text(f.read_text().replace('"sigma"', '"sigma" ', 1))
        r = subprocess.run([sys.executable, "-c", "import reseau; reseau.charger(True)"], cwd=tmp / "scripts", env=env, capture_output=True, text=True)
        assert r.returncode != 0 and "empreinte" in (r.stderr + r.stdout), r.stderr[-300:]
        for c in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "t"]):
            subprocess.run(["git", *c], cwd=tmp, check=True, capture_output=True)
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo
        (tmp / "data/cycles/9999-01/gel").mkdir(parents=True)
        for heures, attendu in ((1, True), (72, False)):
            g = (datetime.now(ZoneInfo("Europe/Paris")) + timedelta(hours=heures)).isoformat(timespec="seconds")
            (tmp / "data/cycles/9999-01/gel/manifeste.json").write_text(json.dumps({"gele_le": g}))
            r = subprocess.run([sys.executable, "-c", "import reseau; print(len(reseau.controle_gel_48h('9999-01')))"],
                               cwd=tmp / "scripts", env=env, capture_output=True, text=True)
            assert (r.stdout.strip() != "0") == attendu, (heures, r.stdout, r.stderr[-200:])
    finally:
        shutil.rmtree(tmp.parent)


def test_semantique_reseau():
    """Feuille de route, étape 7 (revue 2, section 5) : références valides (structure, indicateurs, jalons,
    hypothèses), feuilles et pivots sans mesure justifiés, sens attendus des liens respectés, invariants logiques
    du réseau réel (scénarios dorés) et erreur type de Monte-Carlo publiée."""
    import reseau, preuves
    racine = Path(__file__).resolve().parent.parent
    L = lambda f: json.loads((racine / f).read_text())
    S, T = L("modele/reseau/structure_v0.json"), L("modele/reseau/tables_v0.json")
    N = reseau.noeuds_de(S)
    anciens = S.get("anciens_identifiants", {})
    ref = lambda i: anciens.get(i, i)
    cites = {l["noeud"] for v in S["indicateurs"]["liens"].values() for l in v["liens"]}
    cites |= {ref(json.loads(l)["cible"]["noeud"]) for l in (racine / "modele/jalons/definitions.jsonl").read_text().splitlines() if l.strip()}
    cites |= {v["noeud"] for v in L("modele/jalons/vraisemblances_v2.json")["jalons"].values()}
    cites |= {n for h in L("modele/reseau/hypotheses.json")["hypotheses"] for n in h["noeuds"]}
    cites |= set(T["noeuds"])
    for m in S["mesures"].values():
        c = m["caracteristique"]
        cites |= {e["noeud"] for e in c.get("elements", [c])}
    assert cites <= set(N), sorted(cites - set(N))
    enfants = {reseau.pid(q) for n in N.values() for q in n.get("parents", [])}
    lus = {e["noeud"] for m in S["mesures"].values() for e in m["caracteristique"].get("elements", [m["caracteristique"]])}
    a_justifier = {i for i in N if i not in enfants} | {i for i in N if i.startswith("PV-") and i not in lus}
    assert a_justifier <= set(S.get("feuilles_assumees", {})), sorted(a_justifier - set(S.get("feuilles_assumees", {})))
    for n in N.values():
        for x in n.get("sens", []):
            a, b = reseau.effet_local(n, T["noeuds"][n["id"]], N, x["parent"], x["etat"], x["issue"])
            assert (b > a) if x["signe"] == "+" else (b < a), (n["id"], x, a, b)
    ev = {e["id"]: e for e in L("modele/evenements.json")["evenements"]}
    qs = [q for q in reseau.questions_banque(S, list(ev.values())) if q.get("evenement") in ("EV-02", "EV-05")]
    obs = reseau.observations(S)
    tr = lambda n, issue: {"id": f"T-{n}", "noeud": n, "classe": "tranche",
                           "vraisemblances": {i: (1.0 if i == issue else 0.0) for i in (N[n].get("issues") or ["oui", "non"])}}
    r = reseau.prevoir(S, T, obs, qs, 3, 150, preuves=[tr("PV-BLOC", "Philippe seul")])
    assert all(v == 0 for k, v in r["__pivots__"]["PV-DUEL"].items() if "ATT" in k.split("-")), r["__pivots__"]["PV-DUEL"]
    assert r["Q-EV-02"]["es"] is not None
    r = reseau.prevoir(S, T, obs, qs, 3, 150, preuves=[tr("PV-LEPEN", "non candidate")])
    assert r["Q-EV-05"]["Marine Le Pen"] == 0, r["Q-EV-05"]
    r = reseau.prevoir(S, T, obs, qs, 3, 150, preuves=[tr("PV-DISSOL1", "oui")])
    assert r["__pivots__"]["PV-DISSOL2a"].get("oui", 0) == 0, r["__pivots__"]["PV-DISSOL2a"]
    r = reseau.prevoir(S, T, obs, qs, 3, 150, preuves=[tr("PV-BUDGET", "publiée")])
    assert r["Q-EV-02"]["oui"] == 0, r["Q-EV-02"]
    v2 = L("modele/jalons/vraisemblances_v2.json")["jalons"]
    r = reseau.prevoir(S, T, obs, qs, 3, 150, preuves=[preuves.preuve_jalon("J-026", v2["J-026"], "observé")])
    assert r["__pivots__"]["PV-BLOC"]["les deux"] <= 3, r["__pivots__"]["PV-BLOC"]
    # Erreurs du 10 octobre : loi de base donnée pour la marginale (référence minoritaire), calage sur l'avis direct.
    import tables
    assert not tables.controle_tables(), tables.controle_tables()


def test_organigramme():
    """Feuille de route, étape 8 : données de l'organigramme cohérentes avec la structure (codes d'issues valides,
    une phrase par issue, vraisemblances des jalons alignées sur les issues de leur nœud), page assemblée avec son
    script et sans données en ligne pour la version publiée."""
    import organigramme
    d = organigramme.construire(tirages=2, trajectoires=20)
    assert len(d["codes"]) == 40 == len(d["poids"]) == len(d["variables_codes"])
    for i, p in enumerate(d["pivots"]):
        assert all(int(c[i]) < len(p["issues"]) for c in d["codes"]), p["id"]
        assert len(p["phrases"]) == len(p["issues"]) == len(p["libelles"]) and (p["k"] is None or p["k"] < len(p["issues"]))
    nv = len(d["variables"]) * len(d["mois"])
    assert all(len(c) == nv for c in d["variables_codes"])
    piv = {p["id"]: p for p in d["pivots"]}
    for j in d["jalons"]:
        assert len(j["L"]) == len(piv[j["noeud"]]["issues"]) and j["classe"] in ("tranche", "indice"), j["id"]
    j26 = next(j for j in d["jalons"] if j["id"] == "J-026")
    attendu = json.loads((Path(__file__).resolve().parent.parent / "modele/jalons/vraisemblances_v2.json").read_text())["jalons"]["J-026"]["vraisemblances"]
    assert j26["classe"] == "tranche" and dict(zip(piv["PV-BLOC"]["issues"], j26["L"])) == attendu, j26
    html = organigramme.page()
    assert "/*__DONNEES__*/null" in html and "ORGJS" not in html and "function poids(" in html


def test_chocs():
    """Feuille de route, étape 9 : choc imprévu comme intervention sur des points d'entrée déclarés. Les évaluateurs ne
    choisissent que les ports (majorité) ; l'intensité vient du barème par stade ; une allégation est sans effet ; le
    choc déplace la variable visée puis s'éteint quand une observation postérieure l'absorbe ; sur un pivot, il
    multiplie la cote de l'issue visée."""
    import faits, reseau
    S = {"variables_etat": [{"id": "VE-X", "etats": ["bas", "moyen", "haut"], "reference": "moyen", "parents": []}],
         "pivots": [{"id": "PV-D", "nature": "daté", "date": "2026-12-31", "issues": ["a", "b"], "parents": []}],
         "ports": [{"id": "P-X-BAISSE", "noeud": "VE-X", "sens": "baisse"}, {"id": "P-D", "noeud": "PV-D", "issues": ["b"], "sens": "hausse"}],
         "mesures": {"EV-X": {"caracteristique": {"type": "etat_max", "noeud": "VE-X", "debut": "2026-11-01", "fin": "2026-11-30"},
                              "table": {"bas": 100, "moyen": 0, "haut": 0}},
                     "EV-Y": {"caracteristique": {"type": "etat_max", "noeud": "VE-X", "debut": "2026-12-01", "fin": "2026-12-31"},
                              "table": {"bas": 100, "moyen": 0, "haut": 0}},
                     "EV-D": {"caracteristique": {"type": "issue", "noeud": "PV-D"}, "table": "identite"}}}
    B = {"points_par_unite": 4, "p_retrait_reference": 0.1,
         "stades": {"procédure engagée": {"points_intentions": -4, "points_popularite": -4, "p_retrait": 0.5, "duree_mois": 3}}}
    avis = [{"ports": ["P-X-BAISSE", "P-D"]}, {"ports": ["P-X-BAISSE"]}, {"ports": ["P-X-BAISSE", "P-D"]}]
    c = faits.choc({"id": "C", "fait": "f", "stade": "procédure engagée", "mois": "2026-10", "avis": avis}, S, B)
    assert c["retenu"] and c["ports"] == {"P-X-BAISSE": 1.0, "P-D": round(math.log(1) - math.log(0.1 / 0.9), 3)}, c
    assert not faits.choc({"id": "C", "fait": "f", "stade": "allégation", "mois": "2026-10", "avis": avis}, S, B)["retenu"]
    T = {"noeuds": {"VE-X": {"reference": "moyen", "transition": {e: {"bas": 0.2, "moyen": 0.6, "haut": 0.2} for e in ("bas", "moyen", "haut")}},
                    "PV-D": {"base": {"a": 0.8, "b": 0.2}}}}
    q = [{"id": "Q-X", "evenement": "EV-X", "issues": ["oui", "non"], "fenetre": ["2026-10-10", "2026-12-31"]},
         {"id": "Q-Y", "evenement": "EV-Y", "issues": ["oui", "non"], "fenetre": ["2026-10-10", "2026-12-31"]},
         {"id": "Q-D", "evenement": "EV-D", "issues": ["a", "b"], "fenetre": ["2026-10-10", "2026-12-31"]}]
    try:
        reseau.CHOCS = []
        sans = reseau.prevoir(S, T, {}, q, 10, 200)
        reseau.CHOCS = [c]
        avec = reseau.prevoir(S, T, {}, q, 10, 200)
        absorbe = reseau.prevoir(S, T, {"VE-X": {"2026-11": "moyen"}}, q, 10, 200)
    finally:
        reseau.CHOCS = None
    assert avec["Q-X"]["oui"] > sans["Q-X"]["oui"] + 8, (sans["Q-X"], avec["Q-X"])          # baisse en novembre
    assert avec["Q-D"]["b"] > sans["Q-D"]["b"] + 25, (sans["Q-D"], avec["Q-D"])              # cote de « b » × 9
    assert avec["Q-Y"]["oui"] > sans["Q-Y"]["oui"] + 8, (sans["Q-Y"], avec["Q-Y"])          # toujours actif en décembre
    assert abs(absorbe["Q-Y"]["oui"] - sans["Q-Y"]["oui"]) < 5, (sans["Q-Y"], absorbe["Q-Y"])  # absorbé par l'observation de novembre


def test_agregation_sans_veto():
    """Feuille de route, étape 1 : un zéro isolé chez un évaluateur ne fixe plus l'agrégat à zéro ; un zéro unanime
    reste un zéro."""
    import tables
    assert tables.moy_mult([0, 2, 2]) > 0.5 and tables.moy_mult([0, 0, 0]) == 0
    l = tables.moy_loi([{"a": 0.0, "b": 1.0}, {"a": 0.3, "b": 0.7}, {"a": 0.3, "b": 0.7}])
    assert l["a"] > 0.05, l
    assert tables.moy_loi([{"a": 0.0, "b": 1.0}] * 3)["a"] == 0


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
