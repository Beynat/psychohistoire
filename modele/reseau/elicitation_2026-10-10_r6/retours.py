"""Retours de ronde 1 (IDEA) pour un lot : python3 retours11.py LOT E1 E2 E3"""
import json, sys
sys.path.insert(0, '/home/claude/psychohistoire/scripts')
import tables
lot, ids = sys.argv[1], sys.argv[2:]
D = '/tmp/claude-0/elic11'
R = {i: json.load(open(f'{D}/{i}.json')) for i in ids}
G = json.load(open(f'{D}/gabarit_{lot}.json'))
so = tables.sens_opposes(list(R.values()), G)
marg = {i: tables.ecarts_marginaux(R[i]) for i in ids}
bilan = []
for i in ids:
    autres = [j for j in ids if j != i]
    nom = {j: f"autre {n}" for n, j in enumerate(autres, 1)}
    out = {"evaluateur": i, "ronde": 2,
           "lecture": "Seconde ronde (protocole IDEA). (1) défauts de ta réponse ; (2) questions où la marginale impliquée par TES lois s'écarte de plus de 5 points de ton avis direct ; (3) cas où les évaluateurs donnent des sens opposés par rapport au cas le plus fréquent, avec les lois et justifications anonymes des autres ; (4) pour chaque nœud, les lois et justifications des autres sur les trois cas les plus fréquents. Corrige ou maintiens en écrivant pourquoi.",
           "defauts": tables.verifier_cas(R[i]), "marginales": marg[i], "sens_opposes": [], "noeuds": {}}
    for x in so:
        nid, c, ref = x["noeud"], x["cas"], x["reference"]
        out["sens_opposes"].append({"noeud": nid, "cas": c, "cas_reference": ref, "issue": x["issue"],
            "ta_loi_cas": tables.lois_de(R[i], nid)[c], "ta_loi_reference": tables.lois_de(R[i], nid)[ref],
            "autres": [{"evaluateur": nom[j], "loi_cas": tables.lois_de(R[j], nid)[c], "loi_reference": tables.lois_de(R[j], nid)[ref],
                        "justifications": {k: v.get("justification") for k, v in R[j]["noeuds"][nid]["cas"].items() if tables.correspond(c, k) is not None or tables.correspond(ref, k) is not None}} for j in autres]})
    for nid, nd in R[i]["noeuds"].items():
        cas = G["noeuds"][nid]["cas"]
        top = sorted(cas, key=lambda c: -cas[c].get("poids_reseau", 0))[:3]
        out["noeuds"][nid] = {c: {nom[j]: {"loi": tables.lois_de(R[j], nid).get(c),
                                           "justification": next((v.get("justification") for k, v in R[j]["noeuds"][nid]["cas"].items() if tables.correspond(c, k) is not None), None)}
                                  for j in autres} for c in top}
    json.dump(out, open(f'{D}/retour_{i}.json', 'w'), ensure_ascii=False, indent=1)
    bilan.append(f"{i}: {len(out['defauts'])} défauts, {len(marg[i])} marginales, {len(out['sens_opposes'])} sens opposés")
print("\n".join(bilan))
