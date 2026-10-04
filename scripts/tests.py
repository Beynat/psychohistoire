"""Tests des scripts de la phase 1 sur données fictives. Usage : python scripts/tests.py"""
import json
import random
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
    assert abs(notation.brier({"oui": 70, "non": 30}, "oui") - 0.18) < 1e-9
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
