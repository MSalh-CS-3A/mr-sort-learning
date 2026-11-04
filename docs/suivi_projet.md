# Suivi du projet SDP

Ce document rassemble les réponses détaillées aux questions du sujet, les choix techniques et l'avancement du projet. Il est complété au fil des jalons. Chaque jalon a son dossier à la racine du dépôt, avec son code, ses données, ses résultats et son compte rendu : [jalon1](../jalon1/), [jalon2](../jalon2/) et [jalon3](../jalon3/).

## État d'avancement

| Étape | État | Éléments disponibles |
| --- | --- | --- |
| Préliminaires | Réponses rédigées | Questions i à viii (1) et viii (2), détaillées ci-dessous. |
| Jalon 1 | Travail réalisé et rendu préparé | Modèle MILP, implémentation, tests, résultats et compte rendu. |
| Jalon 2 | Version officielle retenue | Version de Quentin dans le [README du jalon 2](../jalon2/README.md) : 91 % d'objets bien expliqués en moyenne sur les 72 CSV. Variante A0-A4 (audit, A0-A4, pilote de 120 exécutions) conservée dans `jalon2/variante_a0_a4/`. |
| Jalon 3 | Confirmation terminée, analyse et rapport rédigés | [Rapport LaTeX compilé](../output/pdf/rapport_jalon3.pdf), 840 évaluations confirmatoires auditées sur vingt graines ; diagnostics des catégories/groupes et coûts ; règle hybride exploratoire rejouée sur les mêmes candidats, sans nouvelle confirmation. 44 tests passent. Dépôt le 05/11/2026, soutenance le 06/11/2026. |

Exécution locale : le [lanceur par lots](../jalon3/docs/campagnes_locales.md) est
validé par 35 tests et des essais réels d'interruption/reprise, d'audit et de
regroupement. Le calibrage prévoit les 25 couples sur cinq nouvelles graines,
soit 400 évaluations. Les plans suivants comptent 2 400 puis 9 600 évaluations ;
leur présence dans le lanceur ne signifie pas qu'ils ont été exécutés.

Le premier calibrage local a calculé 400 décisions mais seuls 80 résultats ont
passé l'audit : des poids LINCS tous nuls entraînaient une division par zéro à la
conversion. La correction conserve le modèle constant de classe basse avec des
paramètres et marges finis. Cinq tests de régression couvrent ce cas, et le
simulateur refuse les modèles non finis avant de calculer leurs métriques. Le
[guide local](../jalon3/docs/campagnes_locales.md) documente la relance complète
dans `calibrage_local_v2`, distincte de la campagne initiale conservée.

Après réévaluation de l'énoncé et accord de l'utilisateur le 3 novembre, la
[confirmation ciblée](../jalon3/docs/confirmation_quatre_couples.md) porte sur
quatre couples : MR-Sort aléatoire / classe haute, chacun face au naïf et à Inv2
avec choix du plus grand groupe. Vingt nouvelles graines et N_A=300, 500, 1 000
donnent 840 évaluations, témoins inclus. Ce plan remplace la priorité donnée à
une extension exhaustive. Les 840 évaluations et les 60 lots ont été audités,
sans remplacement de stratégie après consultation. Les analyses supplémentaires
et le sélecteur hybride sont distingués comme exploratoires dans le rapport ;
la validation de ce nouveau sélecteur sur de nouvelles graines reste à faire.

## Préliminaires : admission d'étudiants

Cette partie répond à toutes les questions des préliminaires du [sujet du projet SDP](sujet.pdf), pages 1 et 2. Elle présente la règle d'admission puis la construction et la résolution d'un programme linéaire mixte pour apprendre simultanément les poids, le seuil de majorité et les frontières. Le sujet comporte deux questions numérotées **viii** : elles sont distinguées ci-dessous par **viii (1), résolution avec GUROBI**, et **viii (2), généralisation à plusieurs catégories**.

### Cadre et notations

Chaque étudiant est évalué dans quatre cours : mathématiques ($M$), physique ($P$), littérature ($L$) et histoire ($H$). Pour un étudiant $x$, on définit l'ensemble des cours dans lesquels il atteint le seuil de 12/20 :

$$
C(x)=\{j\in\{M,P,L,H\}:x_j\geq 12\}.
$$

À chaque cours correspond un poids $w_j\geq 0$, avec $\sum_j w_j=1$. Le score de concordance est la somme des poids des cours dont le seuil est atteint :

$$
s(x)=\sum_{j\in C(x)}w_j.
$$

L'étudiant est admis si et seulement si $s(x)\geq\lambda$ ; sinon, il est refusé. Ce score dépend du franchissement du seuil dans chaque cours : une fois 12 atteint, une meilleure note dans ce cours n'augmente plus sa contribution. Il ne s'agit donc pas d'une moyenne pondérée des notes.

### Question i - Admissions et demande de recorrection de Bob

Les paramètres sont, dans l'ordre $(M,P,L,H)$ :

$$
w=(0{,}25,\;0{,}15,\;0{,}20,\;0{,}40),
\qquad \lambda=0{,}66.
$$

La règle « au moins 12/20 » inclut les notes égales à 12.

| Étudiant | M | P | L | H | Cours avec une note ≥ 12 | Score de concordance | Décision |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| Alice | 11 | 12 | 13 | 12 | P, L, H | 0,15 + 0,20 + 0,40 = **0,75** | **Admise**, car 0,75 ≥ 0,66 |
| Bob | 13 | 12 | 15 | 10 | M, P, L | 0,25 + 0,15 + 0,20 = **0,60** | **Refusé**, car 0,60 < 0,66 |
| Charlie | 11 | 13 | 11 | 13 | P, H | 0,15 + 0,40 = **0,55** | **Refusé**, car 0,55 < 0,66 |
| David | 12 | 12 | 16 | 12 | M, P, L, H | 0,25 + 0,15 + 0,20 + 0,40 = **1,00** | **Admis**, car 1,00 ≥ 0,66 |

**Alice et David sont donc admis ; Bob et Charlie sont refusés.** Alice et Bob atteignent chacun le seuil dans trois cours, mais leurs décisions diffèrent : la majorité est définie par la somme des poids, et non par le seul nombre de cours.

**Bob ne peut pas améliorer sa décision d'admission par une hausse de sa note en physique.** Sa note actuelle est déjà égale à 12 : le poids de la physique, $0{,}15$, est donc entièrement compté. Toute nouvelle note en physique supérieure ou égale à 12 laisse son score à $0{,}60$, en dessous de $\lambda=0{,}66$. Même une note de 20/20 ne change pas son refus.

À notes inchangées dans les autres cours, seul le franchissement du seuil en histoire permettrait à Bob d'être admis : une note d'histoire d'au moins 12 ferait passer son score de $0{,}60$ à $1{,}00$.

### Question ii - Admission avec au moins trois cours sur quatre

Pour que chaque cours joue le même rôle dans le décompte, on choisit des poids égaux :

$$
w_M=w_P=w_L=w_H=\frac14,
\qquad \lambda=\frac34.
$$

Si $k$ cours satisfont le seuil de note, leur poids total vaut $k/4$. Ainsi :

$$
s(x)\geq\lambda
\iff \frac{k}{4}\geq\frac34
\iff k\geq 3.
$$

Deux cours représentent $0{,}50$ et ne suffisent pas ; trois cours représentent $0{,}75$ et suffisent ; quatre cours représentent $1$. Plus généralement, avec ces poids, tout seuil $\lambda\in\left]\frac12,\frac34\right]$ produit exactement la même règle d'admission.

**Précision sur le seuil de note.** La question ii parle d'une note « supérieure à 12 », tandis que la règle générale du sujet utilise « au moins 12 ». Les poids et $\lambda$ ci-dessus règlent le nombre de cours requis ; ils ne modifient pas le test effectué sur chaque note.

- Avec la convention générale $x_j\geq 12$, ces paramètres signifient : admission si et seulement si au moins trois notes sont **supérieures ou égales à 12**.
- Pour respecter littéralement la question ii, on utilise $C_{>}(x)=\{j:x_j>12\}$ dans la somme, avec les mêmes poids et le même $\lambda$ : l'admission exige alors au moins trois notes **strictement supérieures à 12**.

Changer uniquement les poids et $\lambda$, tout en conservant $x_j\geq 12$, ne permet pas de distinguer une note égale à 12 d'une note supérieure à 12. Si les notes sont entières, la version stricte peut aussi s'écrire avec une frontière de 13 dans chaque cours. Pour des notes réelles, aucune frontière fixe $12+\varepsilon$, avec $\varepsilon>0$, ne représente exactement toutes les notes strictement supérieures à 12.

### Question iii - Interprétation de deux jeux de poids avec trois cours

On note les trois cours $1$, $2$ et $3$. Un cours appartient à la coalition $C$ lorsque sa note atteint le seuil. On compare :

$$
w^{(a)}=(0{,}49,\;0{,}49,\;0{,}02),\quad\lambda=0{,}50,
$$

$$
w^{(b)}=\left(\frac13,\;\frac13,\;\frac13\right),\quad\lambda=0{,}50.
$$

#### Premier jeu : $(0{,}49,0{,}49,0{,}02)$

Aucun cours ne suffit seul : même les deux plus grands poids, pris séparément, valent $0{,}49<0{,}50$. En revanche, toute paire de cours suffit :

$$
w_1+w_2=0{,}98\geq 0{,}50,
\qquad w_1+w_3=w_2+w_3=0{,}51\geq 0{,}50.
$$

La règle est donc : **être admis si et seulement si au moins deux des trois cours atteignent le seuil**. Malgré son faible poids, le troisième cours peut être décisif : associé à un seul des deux autres cours, il transforme un refus en admission.

#### Deuxième jeu : $(1/3,1/3,1/3)$

Un cours seul a un poids $1/3<0{,}50$, tandis que deux cours ont un poids $2/3\geq 0{,}50$. On retrouve donc exactement la même règle : **au moins deux cours sur trois**.

#### Comparaison de toutes les coalitions

| Cours atteignant le seuil | Score avec $(0,49 ; 0,49 ; 0,02)$ | Score avec $(1/3 ; 1/3 ; 1/3)$ | Décision dans les deux modèles |
| --- | ---: | ---: | --- |
| Aucun | 0 | 0 | Refus |
| 1 | 0,49 | 1/3 | Refus |
| 2 | 0,49 | 1/3 | Refus |
| 3 | 0,02 | 1/3 | Refus |
| 1 et 2 | 0,98 | 2/3 | Admission |
| 1 et 3 | 0,51 | 2/3 | Admission |
| 2 et 3 | 0,51 | 2/3 | Admission |
| 1, 2 et 3 | 1 | 1 | Admission |

**Conclusion.** Les deux jeux de paramètres définissent les mêmes coalitions gagnantes et classent donc de manière identique tous les étudiants, à seuils de notes identiques. Les poids numériques ne suffisent pas, pris isolément, à mesurer l'influence d'un cours sur la décision : celle-ci dépend aussi de $\lambda$ et des coalitions possibles. Ici, les trois cours ont le même rôle dans la règle finale, malgré les poids inégaux du premier jeu.

Cette équivalence illustre également la **non-unicité des paramètres de MR-Sort** : même en connaissant les décisions pour toutes les coalitions, on ne peut pas identifier un unique vecteur de poids. Dans la suite du projet, apprendre un modèle qui restitue les classifications n'implique donc pas de retrouver exactement les poids du modèle ayant généré les données.

### Question iv - Apprentissage des poids et du seuil avec une frontière connue

L'objectif est d'apprendre les poids $w_i$ et le seuil de majorité $\lambda$ à partir d'un ensemble d'objets acceptés $A^*$ et d'un ensemble d'objets refusés $R^*$. La frontière $b=(b_1,\ldots,b_n)$ est connue et reste fixe.

#### Données et coefficients calculés à l'avance

On note $N=\{1,\ldots,n\}$ l'ensemble des critères et $L=A^*\cup R^*$ l'ensemble d'apprentissage. Les performances $x_i$ et les classes de chaque objet sont connues. Pour chaque objet $x\in L$ et chaque critère $i\in N$, on calcule :

$$
a_i(x)=
\begin{cases}
1 & \text{si }x_i\geq b_i,\\
0 & \text{si }x_i<b_i.
\end{cases}
$$

Les $a_i(x)$ sont des **constantes**, et non des variables de décision, puisque les performances et la frontière sont connues. Le score de concordance s'écrit alors :

$$
s_w(x)=\sum_{i=1}^{n}a_i(x)w_i.
$$

Cette expression est linéaire en $w_i$. Il n'est donc pas nécessaire d'introduire des variables binaires dans cette question.

#### Variables de décision

- $w_i\geq 0$, pour chaque $i\in N$ : poids du critère $i$, avec $\sum_i w_i=1$.
- $\lambda\in[0,1]$ : seuil de majorité à apprendre.
- $\xi_x\geq 0$, pour chaque $x\in L$ : variable d'écart permettant de relâcher la contrainte associée à cet objet si les données ne peuvent pas toutes être reproduites.

Toutes les variables sont continues. La normalisation des poids conserve leur interprétation comme parts d'une majorité et fixe l'échelle du modèle. Elle implique $0\leq s_w(x)\leq 1$, ce qui motive le choix de $\lambda\in[0,1]$ conformément au cadre des préliminaires.

#### Contraintes de classification et traitement du refus strict

Sans écarts, reproduire les classes demanderait :

$$
s_w(x)\geq\lambda\quad\forall x\in A^*,
\qquad
s_w(x)<\lambda\quad\forall x\in R^*.
$$

La seconde inégalité est stricte : un objet dont le score vaut exactement $\lambda$ est admis. Un programme linéaire standard utilise des inégalités larges. On fixe donc une petite marge $\varepsilon>0$ et on impose aux objets refusés $s_w(x)\leq\lambda-\varepsilon$, avant d'introduire les écarts.

On obtient les contraintes assouplies suivantes :

$$
s_w(x)+\xi_x\geq\lambda
\qquad\forall x\in A^*,
$$

$$
s_w(x)-\xi_x\leq\lambda-\varepsilon
\qquad\forall x\in R^*.
$$

Un écart nul garantit le respect de la classe observée ; pour un refus, il garantit aussi une distance d'au moins $\varepsilon$ au seuil. Une marge trop grande peut empêcher une restitution parfaite pourtant possible avec des refus stricts : $\varepsilon$ est un paramètre fixé, à choisir suffisamment petit et en tenant compte de la précision numérique du solveur.

#### Programme linéaire proposé

Pour donner un sens précis à « correspondre au mieux », on choisit de **minimiser la somme des amplitudes des violations des contraintes de classification** :

$$
\boxed{
\begin{aligned}
\min_{w,\lambda,\xi}\quad
&\sum_{x\in L}\xi_x\\[2mm]
\text{sous contraintes}\quad
&\sum_{i=1}^{n}a_i(x)w_i+\xi_x\geq\lambda
&&\forall x\in A^*,\\
&\sum_{i=1}^{n}a_i(x)w_i-\xi_x\leq\lambda-\varepsilon
&&\forall x\in R^*,\\
&\sum_{i=1}^{n}w_i=1,\\
&w_i\geq 0
&&\forall i\in N,\\
&0\leq\lambda\leq 1,\\
&\xi_x\geq 0
&&\forall x\in L.
\end{aligned}
}
$$

Les écarts rendent le programme réalisable même si les classes d'apprentissage sont incompatibles avec un modèle MR-Sort à frontière fixée. Pour des valeurs données de $w$ et $\lambda$, leurs valeurs minimales sont :

$$
\xi_x=
\begin{cases}
\max\{0,\lambda-s_w(x)\} & \text{si }x\in A^*,\\
\max\{0,s_w(x)-\lambda+\varepsilon\} & \text{si }x\in R^*.
\end{cases}
$$

La valeur optimale est nulle si et seulement si toutes les classes sont reproduites avec la marge de refus imposée. Si elle est positive, le modèle minimise l'amplitude totale des violations. Un écart positif sur un objet refusé peut signaler soit une mauvaise classification, soit une marge inférieure à $\varepsilon$ alors que le score reste strictement sous $\lambda$.

**Portée de l'objectif.** La somme des écarts ne compte pas directement le nombre d'objets mal classés : plusieurs petites violations peuvent être préférées à une seule grande violation. Minimiser exactement le nombre d'erreurs nécessiterait généralement des variables binaires, et conduirait à une formulation linéaire en nombres entiers. Le programme ci-dessus est une formulation entièrement continue qui pénalise les écarts aux classes observées.

#### Vérification sur les étudiants de la question i

Prenons $b=(12,12,12,12)$, $A^*=\{\text{Alice},\text{David}\}$ et $R^*=\{\text{Bob},\text{Charlie}\}$. Les contraintes de classification deviennent :

$$
\begin{aligned}
w_P+w_L+w_H+\xi_{\text{Alice}}&\geq\lambda,\\
w_M+w_P+w_L+w_H+\xi_{\text{David}}&\geq\lambda,\\
w_M+w_P+w_L-\xi_{\text{Bob}}&\leq\lambda-\varepsilon,\\
w_P+w_H-\xi_{\text{Charlie}}&\leq\lambda-\varepsilon.
\end{aligned}
$$

Les paramètres de la question i, $w=(0{,}25,0{,}15,0{,}20,0{,}40)$ et $\lambda=0{,}66$, satisfont toutes ces contraintes avec $\xi_x=0$ dès que $0<\varepsilon\leq 0{,}06$. Ils donnent donc une solution optimale de valeur zéro, puisque l'objectif est une somme de variables non négatives. Le programme peut retrouver une autre solution optimale : comme montré à la question iii, les paramètres reproduisant les classes ne sont pas nécessairement uniques.

#### Pourquoi minimiser les écarts plutôt que compter les erreurs ?

Il faut distinguer deux objectifs :

$$
\text{Amplitude totale des violations :}\quad \sum_{x\in L}\xi_x,
$$

$$
\text{Nombre de mauvaises classifications :}\quad
\sum_{x\in L}\mathbf{1}\{\widehat y(x)\neq y(x)\},
$$

où $y(x)$ est la classe observée et $\widehat y(x)$ la classe prédite par MR-Sort. Dans le second objectif, chaque erreur coûte 1, quelle que soit la distance du score au seuil. Le premier objectif donne davantage de poids à une grande violation qu'à une petite.

**Le choix du premier objectif vient de la demande explicite de la question iv : formuler un programme linéaire.** La somme des écarts conduit à un programme linéaire continu. Compter directement les erreurs est un objectif discontinu ; sa formulation usuelle introduit des variables binaires et produit un programme linéaire en nombres entiers. La somme des écarts est donc un critère de substitution, et non une garantie de maximiser le taux de bonnes classifications. L'énoncé ne précise pas que ce critère est l'unique interprétation attendue de « correspondre au mieux ».

**Une solution optimale peut-elle classer tous les objets incorrectement ? Oui, si les données sont incompatibles, cela peut même arriver à une solution optimale de ce programme.** Considérons un seul critère, $b_1=12$ et donc $w_1=1$, avec deux objets :

| Objet | Performance | Classe observée | Score |
| --- | ---: | --- | ---: |
| $u$ | 11 | Accepté | 0 |
| $v$ | 13 | Refusé | 1 |

Ces classes contredisent la monotonie de MR-Sort : améliorer une performance ne peut pas faire passer un objet d'accepté à refusé. Les contraintes donnent, pour tout $\lambda\in[0,1]$ :

$$
\xi_u\geq\lambda,
\qquad
\xi_v\geq 1-\lambda+\varepsilon,
\qquad
\xi_u+\xi_v\geq 1+\varepsilon.
$$

La borne $1+\varepsilon$ est atteinte pour tout $\lambda\in[0,1]$ en prenant les écarts à leur minimum. Avec $\lambda=0{,}5$, les deux prédictions sont fausses : $u$ est refusé et $v$ est accepté. Avec $\lambda=0$, $u$ est correctement accepté et $v$ reste incorrectement accepté. Ces deux modèles ont pourtant la même valeur optimale de l'objectif. Minimiser la somme des écarts ne permet donc pas de départager ces solutions selon leur nombre d'erreurs.

En revanche, si la valeur optimale vaut zéro, tous les objets d'apprentissage sont correctement classés avec la marge imposée aux refusés. Cela ne garantit pas la justesse des prédictions sur de nouveaux objets.

**Variante pour compter les violations.** Si l'objectif retenu est de maximiser le nombre de classes reproduites, on peut introduire $e_x\in\{0,1\}$, où $e_x=1$ autorise à ignorer la contrainte de l'objet $x$, et résoudre :

$$
\begin{aligned}
\min\quad &\sum_{x\in L}e_x\\
\text{sous contraintes}\quad
&s_w(x)\geq\lambda-B e_x
&&\forall x\in A^*,\\
&s_w(x)\leq\lambda-\varepsilon+B e_x
&&\forall x\in R^*,\\
&\sum_i w_i=1,\quad w_i\geq0,\quad 0\leq\lambda\leq1,\\
&e_x\in\{0,1\}
&&\forall x\in L,
\end{aligned}
$$

avec $B=1+\varepsilon$, suffisant puisque les scores et $\lambda$ sont dans $[0,1]$. Quand $e_x=0$, la classe et la marge requise sont respectées ; quand $e_x=1$, la contrainte correspondante est désactivée. L'objectif compte ainsi les contraintes de classification non satisfaites, plutôt que l'amplitude de leur violation.

Il s'agit d'un **programme linéaire mixte**, avec la même convention de marge que précédemment. Un refus correct mais situé à moins de $\varepsilon$ du seuil est encore compté comme une violation. Le nombre réel d'erreurs doit donc également être mesuré en appliquant la règle $s_w(x)\geq\lambda$ aux objets. Cette variante est adaptée si « au mieux » signifie restituer le plus de classes possible ; le programme continu reste la réponse proposée à la demande de programme linéaire de la question iv.

### Question v - Contraintes définissant les indicateurs avec une frontière inconnue

La frontière $b=(b_1,\ldots,b_n)$ devient une variable de décision. Pour chaque objet $x$ et chaque critère $i$, on introduit une variable binaire :

$$
\delta_i(x)\in\{0,1\},
\qquad
\delta_i(x)=1\iff x_i\geq b_i.
$$

Contrairement aux coefficients $a_i(x)$ de la question iv, ces indicateurs ne peuvent plus être calculés à l'avance, car $b_i$ est inconnu. Les performances $x_i$ restent des données fixes.

#### Formulation par une constante de grande valeur

On suppose que les performances et les frontières sont bornées :

$$
\ell_i\leq x_i\leq u_i,
\qquad
\ell_i\leq b_i\leq u_i.
$$

Dans le cas des notes, on prend $\ell_i=0$ et $u_i=20$. Pour exprimer le côté strict du refus du critère, on fixe une petite marge de performance $\eta>0$. Elle est distincte de $\varepsilon$, la marge sur le score de concordance utilisée à la question iv.

Avec $M_i=u_i-\ell_i+\eta$, on impose, pour chaque $i\in N$ et chaque $x\in L$ :

$$
\boxed{
\begin{aligned}
b_i-x_i&\leq M_i\bigl(1-\delta_i(x)\bigr),\\
b_i-x_i&\geq\eta-M_i\delta_i(x),\\
\delta_i(x)&\in\{0,1\}.
\end{aligned}
}
$$

Dans l'exemple d'admission, $M_i=20+\eta$ convient. Les bornes sur $b_i$ doivent être ajoutées au modèle.

#### Vérification des deux cas

**Si $\delta_i(x)=1$**, la première contrainte impose :

$$
b_i-x_i\leq0\iff x_i\geq b_i.
$$

La seconde devient $b_i-x_i\geq\eta-M_i=\ell_i-u_i$, ce qui est déjà garanti par les bornes. Le critère est donc atteint, et l'égalité $x_i=b_i$ est autorisée.

**Si $\delta_i(x)=0$**, la seconde contrainte impose :

$$
b_i-x_i\geq\eta\iff x_i\leq b_i-\eta<b_i.
$$

La première devient $b_i-x_i\leq M_i$, ce qui est déjà garanti par les bornes. Le critère n'est donc pas atteint.

Les implications réciproques suivent aussi : si $x_i\geq b_i$, la valeur $\delta_i(x)=0$ est impossible ; si $x_i\leq b_i-\eta$, la valeur $\delta_i(x)=1$ est impossible. En particulier, **une note égale à la frontière impose $\delta_i(x)=1$**, conformément au sujet.

#### Précision sur les valeurs réelles et l'inégalité stricte

La définition exacte comporte $x_i<b_i$. Pour des performances et des frontières réelles, une marge fixe $\eta>0$ remplace cette condition par $x_i\leq b_i-\eta$. Elle exclut donc les couples vérifiant $b_i-\eta<x_i<b_i$ : aucune valeur de $\delta_i(x)$ n'y satisfait les deux contraintes.

La formulation est ainsi exacte **sous une convention de séparation minimale $\eta$**, et constitue une approximation de la définition stricte sur des valeurs réelles sans séparation minimale. Il faut expliciter cette convention plutôt que prétendre représenter toute inégalité stricte par des contraintes larges.

Si les performances **et les frontières** sont contraintes à être entières, on peut prendre $\eta=1$ : $x_i<b_i$ équivaut alors exactement à $x_i\leq b_i-1$. Pour des valeurs réelles, on choisit une petite marge adaptée à leur précision et au solveur.

Ces contraintes définissent uniquement quels critères sont atteints. L'agrégation de leurs poids et la décision d'admission seront traitées dans les questions suivantes.

### Question vi - Linéarisation des contributions des critères et condition d'admission

Pour chaque objet $x$ et chaque critère $i$, on introduit une variable continue $w_i(x)$ représentant la contribution effective du critère à son score. Le poids $w_i$ est commun à tous les objets ; la contribution $w_i(x)$ dépend de l'objet.

On suppose que $\delta_i(x)\in\{0,1\}$ indique correctement si $x_i\geq b_i$, conformément à la question v et à sa convention de marge. Les poids vérifient $w_i\geq0$ et $\sum_i w_i=1$, donc $0\leq w_i\leq1$.

Les contraintes données dans le sujet sont :

$$
\boxed{
\begin{aligned}
0&\leq w_i(x)\leq w_i,\\
\delta_i(x)+w_i-1&\leq w_i(x)\leq\delta_i(x).
\end{aligned}
}
$$

#### Cas 1 : le critère n'est pas atteint

Si $\delta_i(x)=0$, les bornes $w_i(x)\geq0$ et $w_i(x)\leq\delta_i(x)=0$ imposent :

$$
\boxed{w_i(x)=0.}
$$

Les deux autres bornes sont compatibles avec cette valeur : $0\leq w_i$ et $w_i-1\leq0$, puisque $w_i\in[0,1]$. Un critère dont la performance est sous la frontière ne contribue donc pas au score.

#### Cas 2 : le critère est atteint

Si $\delta_i(x)=1$, la borne inférieure de la seconde ligne devient :

$$
w_i(x)\geq1+w_i-1=w_i.
$$

La première ligne impose simultanément $w_i(x)\leq w_i$. Par conséquent :

$$
\boxed{w_i(x)=w_i.}
$$

Les bornes restantes $0\leq w_i(x)\leq1$ sont satisfaites puisque $w_i\in[0,1]$. Un critère dont la performance atteint la frontière contribue donc avec la totalité de son poids.

Ces deux cas prouvent que les contraintes imposent exactement :

$$
w_i(x)=w_i\delta_i(x)=
\begin{cases}
w_i & \text{si }x_i\geq b_i,\\
0 & \text{sinon}.
\end{cases}
$$

Réciproquement, ces valeurs satisfont les quatre bornes. Les contraintes constituent donc une **linéarisation exacte du produit d'une variable continue bornée et d'une variable binaire**. Écrire directement $w_i(x)=w_i\delta_i(x)$ introduirait un produit de deux variables ; les quatre inégalités l'évitent.

Les contraintes de cette question relient $w_i(x)$, $w_i$ et $\delta_i(x)$ ; elles ne relient pas à elles seules $\delta_i(x)$ à $x_i$ et $b_i$. Les contraintes de la question v restent nécessaires pour garantir la signification des indicateurs.

#### Interprétation de la somme des contributions

La somme représente le poids total des critères sur lesquels l'objet atteint la frontière, c'est-à-dire son **score de concordance** :

$$
s(x)=\sum_{i=1}^{n}w_i(x)
=\sum_{i=1}^{n}w_i\delta_i(x)
=\sum_{i:x_i\geq b_i}w_i.
$$

Ce score appartient à $[0,1]$ et mesure si la coalition des critères atteints constitue une majorité suffisante. Il ne s'agit pas d'une somme pondérée des performances $x_i$.

#### Condition d'admission

La règle MR-Sort devient une contrainte linéaire sur les contributions :

$$
\boxed{x\in A\iff\sum_{i=1}^{n}w_i(x)\geq\lambda.}
$$

L'égalité au seuil implique l'admission. Pour garantir le refus, la condition exacte est $\sum_i w_i(x)<\lambda$ ; avec la convention de marge de la question iv, on impose $\sum_i w_i(x)\leq\lambda-\varepsilon$.

Par exemple, pour Bob avec les paramètres de la question i, les contributions dans l'ordre $(M,P,L,H)$ sont $(0{,}25,0{,}15,0{,}20,0)$ : leur somme vaut $0{,}60<0{,}66$, donc Bob est refusé. La contribution de l'histoire est nulle parce que sa note de 10 n'atteint pas la frontière de 12.

### Question vii - Programme d'apprentissage simultané de la frontière, des poids et du seuil

#### Nature du programme et choix de l'objectif

La question vii demande un « programme mathématique » qui apprend simultanément $b$, $w$ et $\lambda$. En combinant les questions v et vi, on obtient un **programme linéaire mixte en nombres entiers** (PLNE mixte, ou MILP) : ses contraintes sont linéaires, mais les indicateurs $\delta_i(x)$ sont binaires. Même en conservant la somme des écarts comme objectif, ce modèle ne serait donc plus un programme linéaire continu.

Nous retenons ici comme objectif principal la **minimisation du nombre de contraintes de classification non satisfaites**, avec la convention de marge pour les refusés. Ce choix traduit directement la recherche d'un modèle qui restitue le plus d'exemples possible. Ajouter une variable binaire d'erreur par objet est cohérent avec le modèle, qui comporte déjà des variables binaires pour apprendre la frontière.

Ce choix est une interprétation motivée de l'énoncé, qui ne donne pas explicitement la fonction objectif. Il correspond aussi au principe de la formulation MIP présentée dans la littérature MR-Sort : minimiser la perte 0/1, donc maximiser le nombre d'exemples compatibles avec le modèle. Voir Sobrie, Mousseau et Pirlot, [*Learning monotone preferences using a majority rule sorting model*, section 4.1](https://orbi.umons.ac.be/bitstream/20.500.12907/36336/1/LearningMonotoneIntTransOpRes2019.pdf).

#### Comparaison des formulations possibles

| Formulation | Critère optimisé | Intérêt | Limite pour ce projet |
| --- | --- | --- | --- |
| MILP de restitution parfaite | Objectif constant, avec toutes les classes imposées | Vérifier si les données peuvent être reproduites intégralement | Peut être irréalisable en présence de données incompatibles ou de marges trop grandes |
| MILP avec écarts continus | $\min\sum_x\xi_x$ | Prolongement direct de la question iv ; minimise l'amplitude des violations | Ne maximise pas nécessairement le nombre de bonnes classifications ; les indicateurs de frontière restent binaires |
| **MILP avec erreurs binaires** | **$\min\sum_x e_x$** | **Privilégie le nombre de classes reproduites ; formulation retenue pour vii** | Nécessite une résolution combinatoire et une convention pour les inégalités strictes |
| MILP avec objectifs hiérarchisés | D'abord $\min\sum_x e_x$, puis $\min\sum_x\xi_x$ | Départage les modèles sans sacrifier le meilleur nombre de contraintes satisfaites | Ajoute une étape d'optimisation et ne garantit pas une meilleure généralisation |
| Formulation directe avec produits | Utilise $w_i\delta_i(x)$ sans linéarisation | Écriture compacte | Introduit des contraintes bilinéaires alors que la question vi fournit une linéarisation exacte |
| Heuristique alternée | Alterne apprentissage des poids à frontière fixée et ajustement des frontières | Autre approche pour traiter des ensembles plus grands | Ne certifie pas l'optimalité ; le jalon 1 demande la résolution du programme avec GUROBI |

La distinction porte aussi sur la façon d'écrire les implications : les contraintes de grande valeur $M$ et les contraintes indicatrices natives de GUROBI sont deux encodages possibles des mêmes conditions. Elles ne définissent pas, à elles seules, un objectif d'apprentissage différent. La [documentation de GUROBI sur les contraintes indicatrices](https://docs.gurobi.com/projects/optimizer/en/current/concepts/modeling/constraints.html) décrit la forme « variable binaire fixée à une valeur ⇒ contrainte linéaire active ».

L'heuristique alternée est notamment étudiée dans [Sobrie, Mousseau et Pirlot, sections 4.2 et suivantes](https://orbi.umons.ac.be/bitstream/20.500.12907/36336/1/LearningMonotoneIntTransOpRes2019.pdf). Elle est pertinente comme comparaison ou pour la suite du projet ; la formulation explicite issue de v et vi est le choix retenu ici pour le jalon 1.

#### Données et constantes

- $N=\{1,\ldots,n\}$ : critères, dont les performances sont à maximiser.
- $L=A^*\cup R^*$ : objets d'apprentissage et leurs classes connues.
- $x_i$ : performance connue de l'objet $x$ sur le critère $i$.
- $\ell_i,u_i$ : bornes des performances et de la frontière ; pour des notes, $\ell_i=0$ et $u_i=20$.
- $\eta>0$ : marge de performance pour les critères non atteints, comme en v.
- $\varepsilon>0$ : marge sur le score pour les objets refusés, comme en iv.
- $M_i=u_i-\ell_i+\eta$ et $B=1+\varepsilon$ : constantes de désactivation des contraintes.

Les marges sont fixées avant la résolution. Elles n'ont pas la même unité : $\eta$ porte sur les performances, tandis que $\varepsilon$ porte sur un score compris dans $[0,1]$.

#### Variables de décision

| Variable | Domaine | Rôle |
| --- | --- | --- |
| $b_i$ | $[\ell_i,u_i]$ | Frontière inconnue sur le critère $i$ |
| $w_i$ | $[0,1]$ | Poids inconnu du critère $i$ |
| $\lambda$ | $[0,1]$ | Seuil de majorité inconnu |
| $\delta_i(x)$ | $\{0,1\}$ | Indique si l'objet atteint la frontière sur le critère $i$ |
| $w_i(x)$ | $[0,1]$ | Contribution effective du critère à l'objet |
| $e_x$ | $\{0,1\}$ | Autorise à désactiver la contrainte de classe de l'objet |

On conserve la notation du sujet $w_i(x)$, même s'il s'agit d'une variable distincte du poids global $w_i$. Le score $s(x)=\sum_i w_i(x)$ est une expression linéaire et n'exige pas de variable supplémentaire.

#### Programme complet retenu

$$
\boxed{
\begin{aligned}
\min_{b,w,\lambda,\delta,w(\cdot),e}\quad
&\sum_{x\in L}e_x\\[2mm]
\text{sous contraintes}\quad
&\sum_{i=1}^{n}w_i=1,\\
&0\leq w_i\leq1
&&\forall i\in N,\\
&0\leq\lambda\leq1,\\
&\ell_i\leq b_i\leq u_i
&&\forall i\in N,\\[1mm]
&b_i-x_i\leq M_i(1-\delta_i(x))
&&\forall i\in N,\ x\in L,\\
&b_i-x_i\geq\eta-M_i\delta_i(x)
&&\forall i\in N,\ x\in L,\\[1mm]
&0\leq w_i(x)\leq w_i
&&\forall i\in N,\ x\in L,\\
&\delta_i(x)+w_i-1\leq w_i(x)\leq\delta_i(x)
&&\forall i\in N,\ x\in L,\\[1mm]
&\sum_{i=1}^{n}w_i(x)\geq\lambda-B e_x
&&\forall x\in A^*,\\
&\sum_{i=1}^{n}w_i(x)\leq\lambda-\varepsilon+B e_x
&&\forall x\in R^*,\\[1mm]
&\delta_i(x)\in\{0,1\}
&&\forall i\in N,\ x\in L,\\
&e_x\in\{0,1\}
&&\forall x\in L.
\end{aligned}
}
$$

Toutes les expressions sont linéaires : $x_i$, $M_i$, $B$, $\eta$ et $\varepsilon$ sont des constantes. Le produit $w_i\delta_i(x)$ est remplacé par les contraintes de vi.

#### Pourquoi les variables d'erreur fonctionnent

Lorsque $e_x=0$, la classe observée est imposée : le score est au moins $\lambda$ pour un objet accepté et au plus $\lambda-\varepsilon$ pour un objet refusé.

Lorsque $e_x=1$, la contrainte de classe devient automatiquement satisfaite :

- Pour un objet accepté, $\lambda-B\leq0$ et le score est non négatif.
- Pour un objet refusé, $\lambda-\varepsilon+B=\lambda+1\geq1$ et le score est au plus 1.

Les contraintes de frontière et de contribution restent actives pour tous les objets, y compris ceux dont $e_x=1$. Un objet autorisé à violer sa classe garde donc une prédiction MR-Sort bien définie.

À l'optimum, si la contrainte de classe d'un objet est satisfaite, $e_x$ peut être ramené à zéro sans modifier les autres variables et en améliorant l'objectif. Les $e_x$ comptent donc exactement les violations des contraintes de classe **avec les marges imposées**, sous réserve d'une résolution à l'optimalité.

Si $E^*=\sum_x e_x$ est la valeur optimale, le modèle restitue $|L|-E^*$ classes avec les conditions de marge. Comme en iv, un refus correct mais situé à moins de $\varepsilon$ du seuil est compté comme une violation. Il faut donc distinguer ce compte du nombre de mauvaises prédictions selon la règle originale $s(x)\geq\lambda$. La marge $\eta$ restreint également les positions possibles des frontières, comme expliqué en v.

#### Variante avec objectifs hiérarchisés

Pour départager les modèles obtenant le même meilleur compte, on peut procéder en deux résolutions :

1. Résoudre le MILP ci-dessus et obtenir le nombre minimal $E^*$ de violations.
2. Ajouter $\sum_x e_x=E^*$, introduire les écarts $\xi_x$ et les contraintes de iv avec $s(x)=\sum_i w_i(x)$, puis minimiser $\sum_x\xi_x$.

Le nombre de violations reste prioritaire ; leur amplitude ne sert qu'à départager les solutions. Ce choix évite le compromis implicite d'une simple somme pondérée des deux objectifs. GUROBI propose également des [objectifs hiérarchisés](https://docs.gurobi.com/projects/optimizer/en/current/features/multiobjective.html) ; pour imposer exactement le meilleur compte obtenu, la contrainte $\sum_xe_x=E^*$ rend la priorité explicite.

Cette variante constitue une amélioration facultative. La réponse principale à vii est le MILP de minimisation du compte des violations, qui suffit pour décrire la modélisation et préparer son implémentation.

#### Lecture du résultat et validation

Après résolution, le modèle appris est défini par $(b^*,w^*,\lambda^*)$. Pour prédire la classe d'un nouvel objet, on applique directement :

$$
\widehat y(x)=
\begin{cases}
A & \text{si }\displaystyle\sum_{i:x_i\geq b_i^*}w_i^*\geq\lambda^*,\\
R & \text{sinon}.
\end{cases}
$$

La variable $e_x$ sert uniquement pendant l'apprentissage. Elle n'intervient pas dans la prédiction. Le taux réel de restitution sur $L$ doit être recalculé à partir de cette règle, puis la qualité doit être mesurée sur l'ensemble test indépendant prévu dans le sujet. Maximiser la restitution de l'apprentissage ne garantit pas, à lui seul, le meilleur taux de bonnes classifications sur des données nouvelles.

Pour un ensemble généré par un modèle MR-Sort appartenant au domaine choisi et compatible avec les marges, la valeur attendue est $E^*=0$. Si la résolution est arrêtée avant la preuve d'optimalité, il faut rapporter la meilleure solution obtenue et l'écart d'optimalité ; on ne peut pas affirmer que le nombre de violations est minimal.

### Question viii (1) - Implémentation et résolution avec GUROBI

#### Choisir la formulation et comprendre l'algorithme de résolution

Nous choisissons le MILP de vii et son objectif $\min\sum_x e_x$. Le moteur d'optimisation est fourni par GUROBI : il n'est pas nécessaire de programmer nous-mêmes un algorithme de recherche des paramètres.

Pour ce MILP, le solveur utilise une recherche **branch-and-cut**, qui combine séparation et évaluation, coupes et heuristiques. Après un prétraitement du modèle, il résout sa relaxation linéaire, dans laquelle les variables binaires peuvent provisoirement prendre des valeurs dans $[0,1]$. La relaxation fournit une borne inférieure de l'objectif de minimisation. Des heuristiques cherchent des solutions admissibles binaires et donnent une borne supérieure.

Si les bornes ne suffisent pas à prouver l'optimalité, GUROBI ajoute des coupes valides et explore des sous-problèmes, par exemple en fixant une variable binaire à 0 ou à 1. Les branches irréalisables ou qui ne peuvent pas améliorer la meilleure solution sont éliminées. La résolution se termine avec une preuve d'optimalité, ou avec un autre statut, par exemple si la limite de temps est atteinte. Voir la [documentation du journal MIP de GUROBI](https://docs.gurobi.com/projects/optimizer/en/current/concepts/logging/mip.html).

Le **simplexe** et la **méthode de points intérieurs**, dite barrière, sont des méthodes pour résoudre les problèmes continus et les relaxations du MILP. Ils ne remplacent pas l'exploration nécessaire pour obtenir des variables binaires. Nous laissons GUROBI choisir automatiquement les méthodes des relaxations, les coupes et les heuristiques. Voir la [documentation des méthodes continues](https://docs.gurobi.com/projects/optimizer/en/current/concepts/numericguide/numeric_parameters.html).

Les paramètres explicites du programme sont la limite de temps, la graine et le nombre de threads. Par défaut, ils valent 60 secondes, 0 et 1. Les tolérances d'écart d'optimalité relatif et absolu sont fixées à zéro afin de demander une preuve d'optimalité ; la limite de temps reste active. Le statut, la borne et l'écart obtenus sont enregistrés avec le résultat.

#### Résolution directe du cas à deux catégories de vii

Le cas $p=2$ correspond exactement au modèle de vii : une frontière inconnue, un vecteur de poids et un seuil. Il est vérifié avec les quatre étudiants de i, en prenant Alice et David comme acceptés (classe 2), Bob et Charlie comme refusés (classe 1), des bornes $[0,20]$ et $\eta=\varepsilon=10^{-4}$.

L'appel à GUROBI via `train` dans [mrsort.py](../jalon1/mrsort.py) donne **`OPTIMAL`**, une valeur d'objectif **0**, un écart d'optimalité **0** et les prédictions $(2,1,1,2)$ dans l'ordre Alice, Bob, Charlie, David. Le modèle construit comporte 37 variables et 65 contraintes. Les quatre classes sont donc restituées sans relâcher de contrainte. Ce cas est également couvert par le test `test_binary_training_restores_known_model`.

La frontière est apprise, conformément à vii ; elle n'est pas fixée à 12 comme dans iv. Plusieurs jeux de paramètres peuvent reproduire ces quatre classes. Le résultat prouve la restitution optimale des exemples, sans garantir la récupération des paramètres de i.

#### Adaptation aux catégories du jeu de données

Le fichier fourni `dataset0.txt` contient **60 objets, 5 critères et 3 catégories**. Les catégories sont interprétées dans l'ordre $C^1<C^2<C^3$. Pour traiter ces données, le programme accepte $p\geq2$ catégories, avec $p-1$ frontières et les mêmes poids et le même seuil de majorité pour toutes les frontières.

On impose, pour chaque critère, l'ordre des frontières :

$$
b_i^1\leq b_i^2\leq\cdots\leq b_i^{p-1}.
$$

Pour un objet observé dans la catégorie $C^c$, une seule variable $e_x$ relâche les conditions suivantes :

$$
\sum_i w_i^{c-1}(x)\geq\lambda-B e_x\quad\text{si }c>1,
$$

$$
\sum_i w_i^c(x)\leq\lambda-\varepsilon+B e_x\quad\text{si }c<p.
$$

Les variables $w_i^h(x)$ désignent les contributions par rapport à la frontière $b^h$. Elles sont définies par les contraintes de v et vi, appliquées à chaque comparaison nécessaire. Pour une catégorie extrême, une seule condition suffit ; pour une catégorie intermédiaire, il faut franchir la frontière inférieure et ne pas franchir la frontière supérieure.

L'ordre des frontières rend les scores de concordance décroissants lorsque $h$ augmente. Les conditions concernant les autres frontières suivent donc de celles des frontières adjacentes. Le programme crée seulement les variables nécessaires à ces dernières. Il partage aussi les indicateurs et contributions des objets ayant une même performance sur un même critère et pour une même frontière. Ces réductions sont exactes et diminuent la taille du MILP.

#### Fichiers et exécution

- [mrsort.py](../jalon1/mrsort.py) : lecture du jeu de données, construction du MILP, résolution, extraction du modèle et prédiction.
- [test_mrsort.py](../jalon1/test_mrsort.py) : tests fonctionnels, y compris des données contradictoires.
- [benchmark.py](../jalon1/benchmark.py) : protocole aléatoire d'apprentissage et de test du jalon 1.
- [README du jalon 1](../jalon1/README.md) : installation, explication du solveur et commandes.
- [requirements.txt](../requirements.txt) : version vérifiée de `gurobipy`, 13.0.3.

Commande de résolution du jeu fourni, depuis la racine du projet :

```bash
.venv/bin/python jalon1/mrsort.py jalon1/data/dataset0.txt --log --output jalon1/results/resultat_dataset0.json --export-lp jalon1/results/modele_dataset0.lp
```

Le modèle transmis à GUROBI est consultable dans [modele_dataset0.lp](../jalon1/results/modele_dataset0.lp). Les paramètres appris, classes prédites et diagnostics sont enregistrés dans [resultat_dataset0.json](../jalon1/results/resultat_dataset0.json). La précision est recalculée à partir du modèle extrait ; elle est distinguée du compte des violations de marge.

#### Résultats obtenus sur Dataset0

Avec les bornes $[0,100]$, les marges $\eta=\varepsilon=10^{-4}$ et un thread :

| Mesure | Résultat |
| --- | --- |
| Variables | 742, dont 393 binaires |
| Contraintes linéaires | 1 756 |
| Statut | `OPTIMAL` |
| Objectif | 0 objet relâché |
| Classes reproduites | 60 sur 60, soit 100 % |
| Écart d'optimalité | 0 |
| Nœuds explorés lors de l'exécution enregistrée | 145 |
| Temps de résolution lors de cette exécution | Environ 0,49 seconde |

Le journal de GUROBI montre des solutions heuristiques successives, la relaxation linéaire, les coupes et l'exploration des nœuds. Le temps mesuré dépend de la machine et n'est pas une garantie de performance sur d'autres données.

La solution obtenue possède notamment les poids approximatifs $(0{,}0001,0{,}3333,0{,}3332,0{,}0001,0{,}3333)$ et $\lambda=0{,}6667$. Les paramètres peuvent différer de ceux du modèle ayant produit les données : l'objectif certifie ici la restitution optimale des classes, et non l'identification de paramètres uniques.

#### Vérifications et test indépendant

Les **9 tests fonctionnels** passent. Ils couvrent notamment les égalités aux seuils, les catégories ordonnées, les formats du fichier, la restitution du cas d'admission et la minimisation du nombre d'erreurs lorsque des objets identiques ont des classes contradictoires.

Le protocole suivant a également été exécuté :

```bash
.venv/bin/python jalon1/benchmark.py --runs 20 --output jalon1/results/resultat_benchmark.json
```

Pour chaque répétition, on tire un modèle MR-Sort de référence à 3 critères et 2 catégories, 30 objets d'apprentissage et 200 objets de test indépendants. Les graines sont 42 à 61. Les résultats détaillés sont conservés dans [resultat_benchmark.json](../jalon1/results/resultat_benchmark.json).

| Mesure sur les 20 répétitions | Résultat |
| --- | --- |
| Résolutions prouvées optimales | 20 sur 20 |
| Précision moyenne sur l'apprentissage | 100 % |
| Précision moyenne sur les objets de test | 93,025 % |
| Écart-type de la précision de test entre répétitions | Environ 3,576 points de pourcentage |

Ces résultats concernent ce protocole synthétique et ces tailles d'échantillons. Ils illustrent la différence entre restitution de l'apprentissage et généralisation, sans établir une garantie sur d'autres distributions ou sur Dataset0 hors apprentissage.

### Question viii (2) - Généralisation à p catégories ordonnées

Cette section répond séparément à la seconde question numérotée viii dans le sujet. Nous généralisons le modèle de vii à $p\geq2$ catégories $C^1<\cdots<C^p$, la catégorie $C^1$ étant la plus basse et $C^p$ la plus haute.

#### Frontières et règle d'affectation

On apprend **$p-1$ frontières internes** $b^1,\ldots,b^{p-1}$. La frontière $b^h$ sépare $C^h$ de $C^{h+1}$. Pour une catégorie intermédiaire $C^h$, $b^{h-1}$ est la frontière inférieure et $b^h$ la frontière supérieure. Les catégories extrêmes n'ont qu'une frontière interne : $C^1$ n'a pas de frontière inférieure à apprendre et $C^p$ n'a pas de frontière supérieure à apprendre.

Les frontières doivent respecter l'ordre des catégories sur chaque critère :

$$
\ell_i\leq b_i^1\leq b_i^2\leq\cdots\leq b_i^{p-1}\leq u_i
\qquad\forall i\in N.
$$

Les poids $w_i$ et le seuil $\lambda$ sont **communs à toutes les frontières**. On définit le score par rapport à la frontière $b^h$ :

$$
s^h(x)=\sum_{i:x_i\geq b_i^h}w_i.
$$

La règle de classification est :

$$
\boxed{
\begin{aligned}
x\in C^1
&\iff s^1(x)<\lambda,\\
x\in C^h
&\iff s^{h-1}(x)\geq\lambda\ \text{et}\ s^h(x)<\lambda
&&\text{pour }2\leq h\leq p-1,\\
x\in C^p
&\iff s^{p-1}(x)\geq\lambda.
\end{aligned}
}
$$

Il faut donc atteindre la majorité par rapport à la frontière inférieure de sa catégorie et ne pas l'atteindre par rapport à la frontière supérieure. Une égalité du score à $\lambda$ franchit la frontière et place l'objet du côté des catégories supérieures.

#### Indicateurs et contributions par frontière

Pour chaque comparaison nécessaire, on introduit :

$$
\delta_i^h(x)\in\{0,1\},\qquad
\delta_i^h(x)=1\iff x_i\geq b_i^h,
$$

$$
w_i^h(x)=w_i\delta_i^h(x).
$$

La définition des indicateurs reprend les contraintes de v avec la frontière $b_i^h$ et la marge $\eta$. Le produit est linéarisé exactement par les contraintes de vi. Le score s'écrit alors $s^h(x)=\sum_i w_i^h(x)$ pour les comparaisons modélisées.

Pour chaque objet $x$, la catégorie observée $c_x\in\{1,\ldots,p\}$ est une donnée. Les comparaisons nécessaires à sa restitution sont indexées par :

$$
\mathcal I=
\{(x,c_x-1):x\in L,\ c_x>1\}
\cup
\{(x,c_x):x\in L,\ c_x<p\}.
$$

Les variables $\delta_i^h(x)$ et $w_i^h(x)$ ne sont nécessaires que pour $(x,h)\in\mathcal I$, comme dans l'implémentation. Les scores aux autres frontières peuvent toujours être calculés directement à partir de $b$, $w$ et des performances.

#### Programme linéaire mixte complet

On conserve une variable binaire $e_x$ par objet, qui autorise à relâcher les contraintes de sa catégorie, et l'objectif de vii. Avec $M_i=u_i-\ell_i+\eta$ et $B=1+\varepsilon$, le programme est :

$$
\boxed{
\begin{aligned}
\min\quad
&\sum_{x\in L}e_x\\[2mm]
\text{sous contraintes}\quad
&\sum_{i=1}^{n}w_i=1,\\
&0\leq w_i\leq1
&&\forall i\in N,\\
&0\leq\lambda\leq1,\\
&\ell_i\leq b_i^h\leq u_i
&&\forall i\in N,\ h=1,\ldots,p-1,\\
&b_i^h\leq b_i^{h+1}
&&\forall i\in N,\ h=1,\ldots,p-2,\\[1mm]
&b_i^h-x_i\leq M_i(1-\delta_i^h(x))
&&\forall i\in N,\ (x,h)\in\mathcal I,\\
&b_i^h-x_i\geq\eta-M_i\delta_i^h(x)
&&\forall i\in N,\ (x,h)\in\mathcal I,\\[1mm]
&0\leq w_i^h(x)\leq w_i
&&\forall i\in N,\ (x,h)\in\mathcal I,\\
&\delta_i^h(x)+w_i-1\leq w_i^h(x)\leq\delta_i^h(x)
&&\forall i\in N,\ (x,h)\in\mathcal I,\\[1mm]
&\sum_{i=1}^{n}w_i^{c_x-1}(x)\geq\lambda-B e_x
&&\forall x\in L:\ c_x>1,\\
&\sum_{i=1}^{n}w_i^{c_x}(x)\leq\lambda-\varepsilon+B e_x
&&\forall x\in L:\ c_x<p,\\[1mm]
&\delta_i^h(x)\in\{0,1\}
&&\forall i\in N,\ (x,h)\in\mathcal I,\\
&e_x\in\{0,1\}
&&\forall x\in L.
\end{aligned}
}
$$

Quand $e_x=0$, les conditions de la catégorie observée sont imposées. Quand $e_x=1$, les contraintes de classe de cet objet sont désactivées, mais les contraintes définissant les indicateurs et contributions restent actives. Une même variable relâche les deux conditions d'une catégorie intermédiaire : l'objectif compte des **objets**, et non séparément les violations de frontière.

Comme pour vii, l'objectif compte les violations **avec la marge de score imposée**. Le taux de bonnes prédictions selon la règle originale doit être recalculé séparément. La convention de marge sur les performances conserve également les limites expliquées en v.

#### Pourquoi les frontières adjacentes suffisent

Puisque $b_i^h\leq b_i^{h+1}$, atteindre le critère $i$ à la frontière $h+1$ implique l'atteindre à la frontière $h$. Avec des poids non négatifs :

$$
s^1(x)\geq s^2(x)\geq\cdots\geq s^{p-1}(x).
$$

Si un objet de classe intermédiaire $C^{c_x}$ franchit $b^{c_x-1}$, il franchit donc toutes les frontières inférieures. S'il ne franchit pas $b^{c_x}$, il ne franchit aucune frontière supérieure. Les deux conditions adjacentes suffisent à déterminer sa classe, et l'ordre des frontières empêche des affectations incohérentes.

Pour classer un nouvel objet, on peut utiliser la formule équivalente :

$$
\boxed{\widehat c(x)=1+\sum_{h=1}^{p-1}\mathbf1\{s^h(x)\geq\lambda\}.}
$$

Le nombre de frontières franchies détermine sa catégorie. Pour $p=2$, il n'y a qu'une frontière : les contraintes et la règle d'affectation se réduisent exactement au cas accepté/refusé de vii.

#### Exemple avec trois catégories et lien avec le programme

Avec $p=3$, on apprend deux frontières $b^1\leq b^2$ :

| Classe observée | Conditions imposées lorsque $e_x=0$ |
| --- | --- |
| $C^1$ | $s^1(x)\leq\lambda-\varepsilon$ |
| $C^2$ | $s^1(x)\geq\lambda$ et $s^2(x)\leq\lambda-\varepsilon$ |
| $C^3$ | $s^2(x)\geq\lambda$ |

C'est la généralisation implémentée dans [mrsort.py](../jalon1/mrsort.py) et exécutée sur Dataset0 dans la réponse à viii (1). Le résultat de 60 classes reproduites sur 60 valide donc aussi cette formulation à trois catégories.

## Jalon 1 : bilan

Le [compte rendu du jalon 1](../jalon1/README.md) synthétise le modèle MR-Sort retenu, son implémentation avec GUROBI et l'analyse des résultats. Les réponses détaillées aux préliminaires restent dans ce document.

- Validation sur le [jeu du cours](../jalon1/data/dataset0.txt) : 60 classes restituées sur 60 et objectif nul.
- Évaluation sur vingt jeux aléatoires : précision moyenne de test de 93,025 %.
- [Résultats enregistrés](../jalon1/results/) : diagnostics, paramètres et modèle LP.
- [Rendu préparé](../jalon1/rendu/LIRE_MOI.md) : PDF et archive existants. Leur présence ne confirme pas un dépôt sur Edunao.

## Jalon 2 : suivi

> **Version officielle :** celle de Quentin, décrite dans le [README du jalon 2](../jalon2/README.md). La suite de cette section concerne la variante A0-A4, rangée dans `jalon2/variante_a0_a4/`.
>
> La branche `jalon2/simplifie` prépare maintenant une version pédagogique en trois fichiers, décrite dans le [guide courant](../jalon2/variante_a0_a4/docs/guide.md). Les résultats et tests relatés ci-dessous appartiennent à la version complète de référence sur `jalon2/salhmed` ; ils n'ont pas été réexécutés avec la simplification.

La variante A0-A4 implémente Inv-2-MR-Sort dans `jalon2/variante_a0_a4/`, en conservant les scripts du jalon 1. Le [guide d'utilisation](../jalon2/variante_a0_a4/docs/guide.md) décrit les méthodes, interfaces, budgets et commandes. Le [rapport d'audit](../jalon2/variante_a0_a4/docs/audit.md) décrit les 72 CSV et leurs dépendances.

### Objectifs et questions

Apprendre conjointement une partition en deux groupes non vides et deux modèles MR-Sort, avec pour objectif le nombre total de mauvaises classifications. Le nombre de catégories est fourni par le problème ; il ne correspond pas au nombre de modèles.

Les méthodes principales sont A0 (essais indépendants), A1 (transferts faux-vers-vrai), A2-random (exploration des cas ambigus), A3 (recherche locale après réentraînement) et A4 (perturbations). Les initialisations uniforme et GMM sont indépendantes de la recherche. L'apprentissage à partition fixée utilise lincs/WPB avec un garde-fou conservant l'ancien modèle s'il est meilleur sur le nouveau groupe. Le MILP conjoint reste un programme distinct avec affectations libres.

### Expérimentations et résultats

Les sorties se trouvent dans `jalon2/variante_a0_a4/results/version_complete/` : audit, essai court, pilote, modèles, affectations et traces. Le pilote cible douze CSV, cinq méthodes et deux graines : 120 exécutions de dix secondes nominales chacune. La configuration est conservée dans `configs/pilot.toml` ; chaque résultat enregistre aussi sa configuration exacte, ses sous-graines, versions, empreintes et dépassements de budget.

La vérification comprend 29 nouveaux tests de correction et les neuf tests historiques, tous passants. Les neuf combinaisons A0-A4/initialisation et le diagnostic à un modèle ont produit des résultats valides lors des essais courts. Le MILP retrouve les optima connus sur de petites instances. Après une première détection de licence limitée, une licence liée à la machine a permis un essai n0300 hors du bac à sable : LG = 56/300 après trente secondes, sans preuve d'optimalité.

Le pilote est terminé : 119 solutions validées après rechargement et une tentative sans solution complète après épuisement du budget pendant le premier appel WPB. A1-GMM obtient le plus faible taux d'erreur médian de ce pilote (16,08 %). Les effectifs, quartiles, comparaisons appariées et limites figurent dans le [compte rendu du jalon 2](../jalon2/variante_a0_a4/docs/compte_rendu.md). Les 120 identités d'exécution ont été vérifiées lors d'une reprise avec le code archivé du pilote, sans nouvel apprentissage.

### Décisions et prochaines étapes

Les expériences s'exécutent séquentiellement sur CPU, avec un thread par bibliothèque lorsque configurable. La campagne minimale reste une commande explicite : 1 800 exécutions de trente secondes, soit quinze heures nominales avant surcoûts. La reprise ne réutilise que les résultats terminés dont les données, configuration et environnement correspondent.

Le MILP utilise une marge de rejet documentée de `1e-4`, avec tolérances de `1e-8`. Sa preuve éventuelle concerne la formulation à marge ; aucune exactitude du problème continu sans marge n'est annoncée. Les limites de licence sont enregistrées sans interrompre les autres expériences.

Les types A et B de même nom partagent les mêmes performances, avec des catégories différentes : ils ne sont pas indépendants. Type B désigne une difficulté annoncée supérieure à A. Le mécanisme du bruit et les sources cachées ne sont pas connus. Les métriques portent sur la reconstruction des CSV complets. Les variantes géométriques et exhaustives restent hors de cette livraison.
