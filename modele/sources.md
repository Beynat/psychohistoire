# Fiabilité des sources — méthode, version 1.0 (4 octobre 2026)

Le projet s'appuie sur des sources lues par des agents : recherches des prévisionnistes, propositions de résolution, tri de l'actualité, rapports d'analyse. Une source engagée citée comme un fait établi fausse le travail sans que personne ne le voie. Cette méthode classe chaque source, fixe ce qu'elle peut appuyer et mesure la qualité d'un document.

Origine : le 4 octobre 2026, une date de procédure de la Cour internationale de justice a été citée d'après un média communautaire engagé, alors que l'ordonnance de la Cour était disponible.

## 1. Catégories

| Code | Catégorie | Exemples | Poids |
| --- | --- | --- | --- |
| PO | Primaire officielle : l'émetteur de la décision ou de la donnée | Journal officiel, Conseil constitutionnel, ministères, Insee, Banque de France, BCE, Eurostat, Commission et Conseil de l'UE, CIJ, ONU, gouvernements étrangers pour leurs propres décisions | 1,0 |
| I | Institut : statistique, sondage, recherche, organisation internationale technique | Instituts de sondage contrôlés par la Commission des sondages, Cevipof, AIE, Banque mondiale, laboratoires universitaires | 0,9 |
| MR | Média de référence : rédaction identifiée, charte, rectifications publiées | Agences (AFP, Reuters, AP), quotidiens nationaux, audiovisuel public, chaînes parlementaires | 0,75 |
| S | Spécialisée ou secondaire | Presse professionnelle, think tanks d'analyse, notes de cabinets | 0,5 |
| W | Tertiaire | Wikipédia, agrégateurs, sites sans rédaction identifiée | 0,25 |
| ME | Média engagé ou partisan | Ligne militante revendiquée, ou sanctions de l'Arcom pour manquement à l'honnêteté de l'information | 0,25 |
| MEE | Média d'État étranger | Rédaction financée ou contrôlée par un État hors de l'UE | 0,2 |
| PP | Partie prenante | Partis, candidats, syndicats, organisations de plaidoyer ou représentatives, entreprises, sondage commandité par une partie prenante | 0,2 |
| X | Non classée | | 0 |

Une ligne éditoriale marquée ne fait pas d'un média de référence un média engagé : Le Figaro et Libération restent MR pour les faits. Une révélation de presse d'investigation reste une allégation tant qu'une source primaire ne l'établit pas.

## 2. Critères de classement

Chaque classement repose sur des éléments vérifiables, consignés dans le motif :
- **Nature juridique et éditeur**, d'après les mentions légales.
- **Contrôle étatique** : financement ou tutelle d'un État ; liste des médias sous sanctions de l'UE.
- **Pratique éditoriale** : charte déontologique, rédaction identifiée, rectifications publiées, certification Journalism Trust Initiative.
- **Sanctions** : décisions de l'Arcom pour manquement à l'honnêteté ou au pluralisme de l'information.
- **Ligne revendiquée** : présentation du média par lui-même.

Le classement est écrit dans `modele/sources.json` : par domaine, avec catégorie et motif, plus des règles de suffixe (`gouv.fr`, `europa.eu`, etc.). Un classement fondé sur des indices incomplets porte la marque « à vérifier ». Un domaine non classé est classé au tri suivant par deux agents sur ces critères ; en cas de désaccord, la catégorie la plus basse est retenue. Le fichier est revu à chaque analyse trimestrielle, par ajout ou correction motivée.

## 3. Règles d'usage

1. **Résolution d'une question.** Seule une source PO résout une question ; une source I seulement si le critère cite cet institut. Une partie prenante ne fait foi que pour sa propre décision (résultat d'un vote interne d'un parti, par exemple), si le critère le prévoit.
2. **Fait chiffré ou daté dans un document du projet** (rapport, motif, page) : il doit s'appuyer sur une source PO, I ou MR. Un fait appuyé seulement par S, W, ME, MEE ou PP est marqué « non vérifié » ; il ne sert ni à fixer un seuil, ni à écrire une donnée.
3. **Position d'un acteur** : sa propre source (PP) suffit pour sa position, jamais pour un fait sur un tiers.
4. **Comptages** : un comptage de partie prenante (manifestants selon les organisateurs, actes recensés par une association) n'est jamais une donnée (noyau, section 8.9). Le chiffre officiel prime.

## 4. Indicateur

Pour un document ou un lot de sources (rapport d'analyse, motifs d'un prévisionniste, propositions d'un cycle), `python scripts/sources.py <fichiers>` calcule :
- la répartition des sources par catégorie ;
- la **part des sources de rang 1 à 3** (PO, I, MR), indicateur principal ;
- le **score moyen** (poids de la catégorie) ;
- la liste des domaines non classés ou classés à titre provisoire.

L'indicateur est publié pour chaque rapport d'analyse et, à partir de la consigne qui demandera aux prévisionnistes la liste de leurs sources, pour chaque prévisionniste et chaque cycle. Il ne note pas la justesse d'un document, seulement la solidité de ses appuis.

Premiers relevés (rapports du 4 octobre 2026) : sujets de campagne, 54 sources, 59 % de rang 1 à 3, score 0,63 ; moteurs internationaux, 104 sources, 60 % de rang 1 à 3, score 0,69.
