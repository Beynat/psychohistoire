"""Vérifie le fichier d'un prévisionniste de l'ensemble direct avant agrégation.

Usage : python scripts/verifier_reponse.py ETIQUETTE CHEMIN_DU_FICHIER
Contrôle : JSON lisible ; champs previsionniste, modele, recherches ; au moins 10 recherches
déclarées (consigne v1.1) ; une réponse à chaque question de data/cycles/<ETIQUETTE>/questions.json ;
issues exactement celles de la question (essai du 4 octobre 2026 : un prévisionniste avait répondu
oui/non à une question à cinq issues) ; pourcentages entre 0 et 100, de somme 100 à 1 point près ;
liste des adresses consultées (consigne v1.5), sans adresse du dépôt, de sa page publiée, ni d'un marché ou
agrégateur de prévisions (relecture 15, S1).
Code de sortie 0 si conforme, 1 sinon, avec la liste des défauts : le prévisionniste est alors
relancé une fois avec cette liste.
"""
import json
import re
import sys

from commun import lire_json


# Adresses interdites (consigne, « Interdits ») : le dépôt et sa page publiée, les marchés et agrégateurs.
INTERDITES = re.compile(r"(github\.com/beynat/psychohistoire|beynat\.github\.io/psychohistoire|"
                        r"raw\.githubusercontent\.com/beynat/psychohistoire|polymarket\.|kalshi\.|metaculus\.|"
                        r"manifold\.markets|predictit\.|api\.github\.com/repos/beynat/psychohistoire|"
                        # cotes de paris (relecture de suivi 16)
                        r"betfair\.|oddschecker\.|winamax\.|betclic\.|unibet\.|parionssport|zebet\.|bet365\.|"
                        r"paddypower\.|williamhill\.|smarkets\.)", re.I)


def defauts(etiquette, chemin):
    try:
        with open(chemin, encoding="utf-8") as f:
            r = json.load(f)
    except Exception as exc:
        return [f"fichier illisible : {type(exc).__name__}"]
    d = [f"champ « {c} » absent" for c in ("previsionniste", "modele", "recherches", "adresses", "previsions") if c not in r]
    if d:
        return d
    if not isinstance(r["recherches"], int) or r["recherches"] < 10:
        d.append(f"recherches déclarées : {r['recherches']} (minimum 10)")
    if not isinstance(r["adresses"], list) or not r["adresses"]:
        d.append("liste des adresses consultées vide ou mal formée")
    else:
        d += [f"adresse interdite consultée : {a}" for a in r["adresses"] if INTERDITES.search(str(a))]
    anon = (lire_json(f"data/cycles/{etiquette}/anonymisation.json") or {}).get("correspondance", {})
    previsions = {anon.get(k, k): v for k, v in r["previsions"].items()}   # identifiants remis → banque
    for q in lire_json(f"data/cycles/{etiquette}/questions.json")["questions"]:
        p = previsions.get(q["id"])
        if not p or "probabilites" not in p:
            d.append(f"{q['id']} : réponse absente")
            continue
        pr = p["probabilites"]
        if set(pr) != set(q["issues"]):
            d.append(f"{q['id']} : issues {sorted(pr)} au lieu de {q['issues']}")
            continue
        if any(not isinstance(v, (int, float)) or v < 0 or v > 100 for v in pr.values()):
            d.append(f"{q['id']} : pourcentage hors de 0-100")
        elif abs(sum(pr.values()) - 100) > 1:
            d.append(f"{q['id']} : somme {sum(pr.values()):g} au lieu de 100")
    return d


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage : python scripts/verifier_reponse.py ETIQUETTE CHEMIN_DU_FICHIER")
    d = defauts(sys.argv[1], sys.argv[2])
    print("conforme" if not d else "NON CONFORME :\n- " + "\n- ".join(d))
    sys.exit(1 if d else 0)
