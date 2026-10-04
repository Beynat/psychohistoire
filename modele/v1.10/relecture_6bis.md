# Relecture 6 bis (protocole v1.9, commit 9ffcb39)

Relecteur externe, reçue le 4 octobre 2026, transmise par Nathan dans le corps de son message. Texte intégral, non modifié. Sans défaut bloquant ni important, mais non comptée comme seconde relecture, sur recommandation du relecteur.

Je récupère la v1.9 et je regarde ce qui a changé depuis la v1.8, que j'ai relue juste avant.

**Verdict.** La v1.9 ne diffère de la v1.8 que par un point : le juge humain de la section 6.1 est remplacé par un contrôle par échantillon. Ma relecture de la v1.8, rendue juste avant ce message, reste valable en entier. Le changement n'introduit aucun défaut bloquant ni important, mais le contrôle de remplacement ne remplace rien.

J'ai vérifié les différences entre les tags `protocole-v1.8` et `protocole-v1.9` (commit `9ffcb39`) : huit lignes du noyau et une ligne du journal. L'annexe, les scripts, les workflows et les registres sont inchangés.

## 1. Suivi de la relecture 5

Sans changement par rapport à ma réponse précédente : F1, F2, la protection de branche, le seuil d'application, la cohérence et les simplifications sont suffisants.

**Remplacement du juge humain : retrait fondé, compensation sans objet.**
- **Retrait.** Fondé. L'échantillon de Nathan était un diagnostic publié, sans effet sur l'agrégat. Le retirer faute de compétence est une décision légitime, et la section 13 écrit la conséquence : les lignes conditionnelles n'ont plus aucun contrôle extérieur.
- **Compensation.** Le nouveau contrôle tire 10 sorties marginales et publie leur écart aux cotes quand une cote existe. Or tout nœud coté est déjà dans le pool P1, où cet écart est mesuré avant calage et publié pour tous les nœuds, à chaque bilan (sections 4.5 et 8.4). Le tirage n'est donc qu'un sous-ensemble de ce qui est déjà fait.

## 2. Scission

Sans changement : le noyau se lit seul pour les phases 1 et 2, avec les trois raccords déjà signalés (détection des données en 8.9, règle d'annulation absente de 8.8, « nœud » au lieu de « question » en phase 1).

## 3. Nouveaux défauts

Aucun bloquant, aucun important. Les souhaitables S1 à S8 de ma réponse précédente restent ouverts ; la v1.9 a été écrite avant leur réception. Deux s'y ajoutent.

**S9. Contrôle par échantillon redondant (noyau, 6.1).**
- **Constat et problème.** Voir section 1 : il double la section 8.4 sans rien couvrir de plus.
- **Correction.** Supprimer le paragraphe et garder la seule phrase de la section 13. Si Nathan veut conserver un regard hors famille sans avoir à estimer des probabilités, une option peu coûteuse existe : lui présenter des paires de lignes et lui demander laquelle doit être la plus haute. Un jugement d'ordre ne demande pas de compétence de prévisionniste, et les désaccords avec l'agrégat se publient de la même façon.

**S10. Le gel a été enfreint à sa première occasion (noyau, 12).**
- **Constat.** La section 12 n'autorise une nouvelle version que pour corriger un défaut relevé en relecture. La v1.9 vient d'une décision de Nathan, pas d'une relecture.
- **Problème.** Sans conséquence ici : aucune prévision n'existe encore, et le changement est journalisé avec son motif. Mais une règle de gel qui cède le jour même perd sa valeur d'engagement.
- **Correction.** Élargir la règle à ce cas précis : « ou retrait d'une exigence devenue inexécutable, sur décision humaine journalisée ». Tout ajout reste exclu.

## 4. Critère d'arrêt

Cette relecture est sans défaut bloquant ni important.

Je recommande pourtant de ne pas la compter comme la seconde. Elle porte sur le même texte que la précédente à huit lignes près, à dix minutes d'écart, par le même relecteur : elle n'apporte pas l'information qu'une seconde relecture est censée apporter. Le compteur reste donc à un, à mon avis. La seconde devrait porter sur une version qui a eu l'occasion de répondre à la première, par exemple une v1.10 traitant S2, S9, S10 et les raccords de la section 2. C'est votre règle, et la décision vous revient.
