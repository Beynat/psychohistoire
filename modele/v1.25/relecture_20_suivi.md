# Relecture de suivi 20 — noyau v1.24, banque v1.8

Relecteur : celui de la relecture 19, même session. Relecture de suivi : elle vérifie les corrections et ne compte pas pour le critère d'arrêt (noyau, section 12). Date : 5 octobre 2026. Objet : commit b7df3fb (tag `protocole-v1.24`), réponse `v1.24/reponse_relecture_19.md`.

## Synthèse

Les corrections de B1 et I1 sont suffisantes. I1 est vérifié par simulation sur le nouveau code de `notation.bilan`.

Deux points de l'audit interne sont insuffisants :
- La correction de l'audit 1 introduit un défaut important (N1) : la procédure résout « oui » à l'annonce d'un acte, avant que le critère soit rempli.
- La correction de l'audit 4 ne fait pas ce que la réponse annonce (N2, souhaitable).

Les autres corrections sont suffisantes, ou leur report est justifié. La relecture de validation suivante, seule, fait foi pour le compteur.

## Vérification des corrections

| Point | Avis | Motif |
| --- | --- | --- |
| B1 | Suffisante | Le texte (8.8), l'étape 1 bis et le test couvrent EV-30 et EV-05 : avec la date du fait au jour du scrutin, une prévision du 2 mai 2027 est exclue. |
| I1 | Suffisante | Intersection des cycles dans `comparer`. Simulation sur le vrai `notation.bilan` (fichiers remplacés par des données synthétiques) : 400 questions, deux auteurs également bons mais différents (bruit indépendant de même variance), l'ensemble manquant avril. L'écart moyen par question vaut −0,0016 avec le cycle manqué, contre −0,0015 sans (6 tirages chacun) : le biais d'environ +0,013 a disparu. Avec des prévisions identiques, l'écart est nul. |
| Audit 1 | Fondé, correction insuffisante | La règle de date est juste, mais la procédure la sert par une résolution anticipée. Voir N1. |
| Audit 2 | Suffisante | Départ commun par cycle, au plus tardif des deux jours d'émission. Il reste toujours antérieur au fait, puisque les deux lignes sont filtrées sur leur date réelle avant l'alignement. |
| Audit 3 | Suffisante | `geler.py` échoue sur un fichier manquant ; `comparateurs.py` ne lit plus le fichier courant quand le cycle est gelé. Les replis de `questions.py` et de `lire_serie` restent dans le code, mais un gel complet les rend inatteignables. Les retirer serait plus net (souhaitable). |
| Audit 4 | Insuffisante | Voir N2 : un ajout qui chevauche une seule fenêtre d'un événement à fenêtres disjointes forme une grappe nouvelle au lieu de rejoindre l'existante. |
| Audit 5 | Non-correction acceptable, motif à préciser | La perte n'est pas seulement symétrique : elle sélectionne sur l'issue. Seules les questions nouvelles dont le fait tombe entre le gel et l'émission de l'ensemble sortent du test, donc uniquement des survenues. Le sens dépend de l'auteur le plus alarmiste et n'est pas déterminé ; l'effet est faible. Souhaitable : publier leur nombre dans le bilan. |
| Audit 6 | Suffisante | `fin <= gel`. |
| S1 | Suffisante pour le cas signalé | Restent deux trous, souhaitables. Le contrôle se fait par événement : un événement déjà en P1 au premier gel peut faire passer d'autres questions mensuelles en P1 sans être détecté. Les questions de variable ne sont pas couvertes, alors que les déplacer en P1 les retirerait du critère de persistance. |
| S2, S3 | Report acceptable | Inscrits à la liste de la phase 3, à traiter avant le démarrage. |
| S4 | Suffisante | Le texte, l'étape 5 et le code concordent : un « non » émis après l'échéance est accepté. |
| S5 | Suffisante | Le mélange est reproductible. Je corrige mon propre point : les trois seuils restent visibles dans les textes et révèlent le seuil médian quel que soit l'ordre. Sans effet sur un verdict : P2a n'oppose que le modèle à la persistance. |
| S6, S7, S10 | Suffisantes | |
| S8 | Rejet justifié | Écart mesuré inférieur à 4·10⁻⁶. |
| S9, S11, S12 | Report acceptable | |
| S13 | Non vérifiable ici | L'API GitHub reste fermée à cette session. L'instantané `regles_github.json` est pris comme déclaration. Indice faible : `protocole-v1.23` et `annexe-phase3-v1.7` pointent toujours sur les mêmes commits qu'hier. |

## Défauts introduits

### N1 — Important : résolution « oui » à l'annonce d'un acte, avant que le critère soit rempli

**Texte et procédure.** Section 8.8 : pour un « survenue » d'issue « oui », la date du fait est la plus précoce de l'acte et de son annonce. La règle est juste, mais elle n'a de sens qu'une fois l'issue acquise. Or `questions.py` ne retire une question que si elle est résolue. L'étape 1 bis demande donc aux agents de constater qu'un acte est « établi publiquement comme décidé », puis d'ajouter une proposition que `resolution.py` résout aussitôt : deux « oui » concordants suffisent, et rien n'écarte un « oui » émis avant l'échéance.

**Scénario.** EV-32, fenêtre jusqu'au 30 juin 2027. Le 15 mai 2027, le MOFCOM annonce des contrôles sur les aimants à base de terres rares, applicables au 1er août. Au cycle du 1er juin, deux agents constatent une décision annoncée et proposent « oui », daté du 15 mai : la question est résolue « oui ». Le critère exige pourtant que les contrôles « entrent en application pendant la fenêtre » : l'issue juste est « non ». Même risque sur EV-42 : une remise annoncée par le gouvernement dont le décret paraît après le 18 avril, ou jamais. « Décidé » sépare mal une annonce ferme d'une intention, ce qui laisse deux lectures raisonnables.

**Classement.** L'issue devient contestable entre deux lectures raisonnables, ce qui en fait un défaut important selon la grille. Le sens de l'erreur est déterminé : de faux « oui ». En P2b (EV-42), l'auteur le plus alarmiste est favorisé.

**Correction proposée.** Distinguer la non-émission de la résolution.
- Section 8.8 : « L'annonce fixe la date du fait d'une issue « oui » ; elle ne la résout pas. La question est résolue « oui » quand l'acte remplit le critère dans la fenêtre, avec la date de l'annonce si l'acte est celui qui a été annoncé ; sinon, la règle commune s'applique. »
- Section 8.2 : « Une question dont l'acte est annoncé comme décidé au gel n'est pas émise. »
- Code : un journal d'annonces en ajout seul (`registre/annonces.jsonl` : question, date de l'annonce, source, agent), lu par `questions.py` pour ne pas émettre, et jamais par `resolution.py`. Définir « décidé » : acte adopté, signé ou notifié par l'autorité compétente, dont seules la publication ou l'entrée en vigueur restent à venir.
- Test : une annonce sans acte dans la fenêtre résout « non » à l'échéance.

### N2 — Souhaitable : la grappe d'un ajout chevauchant n'est pas celle de l'événement existant

**Essai, sur une copie.**
1. Gel et questions du cycle 2026-11.
2. Ajout d'EV-15d (événement EV-15, censure entre le 1er janvier et le 31 mars 2027, emboîté dans EV-15b).
3. Gel et questions du cycle 2026-12.

Résultat : Q-EV-15b reste dans la grappe `EV-15b`, Q-EV-15d va dans une grappe nouvelle `EV-15-b-d`. Deux questions emboîtées se retrouvent dans deux grappes, contrairement à la section 8.3 et à ce qu'annonce la réponse (« un ajout rejoint une grappe existante »). Le cas d'un événement à fenêtre unique (EV-C3) fonctionne.

**Effet.** La dépendance entre questions est sous-estimée et le test devient un peu plus permissif dans les deux sens, sans sens déterminé.

**Correction proposée** : dans `questions.py`, une question nouvelle prend la grappe figée d'un événement déjà émis de sa composante.

```python
def grappe(e):
    if e["id"] in figees:
        return figees[e["id"]]
    if e.get("acte"):
        return e["acte"]
    voisins = sorted(figees[x] for x, g in comp.items() if g == comp[e["id"]] and x in figees)
    return voisins[0] if voisins else comp[e["id"]]
```

Si un ajout relie deux grappes déjà figées, on ne peut pas les fusionner sans renommer : le consigner et retenir la première, avec un test pour les deux cas.

## Exécuté

- `python scripts/tests.py` : 14 tests conformes.
- `python scripts/controle_banque.py` : conforme.
- Simulation de I1 sur `notation.bilan`.
- Essai d'ajouts chevauchants sur une copie (EV-C3c, puis EV-15d).
- La relecture 19 versée dans `v1.24/` est identique à celle remise, au retour à la ligne final près.