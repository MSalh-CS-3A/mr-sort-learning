# Rapport du jalon 3

Le rapport présente la campagne confirmatoire des quatre couples, ses diagnostics
et une extension hybride explicitement exploratoire sur le même corpus.
Aucune confirmation indépendante de la règle hybride n'est revendiquée.

## Livrables

- `rapport_jalon3.pdf` : rapport compilé.
- `rapport_jalon3.tex` : source principale LaTeX, avec tableaux dans `tables/`.
- `figures/` : neuf figures vectorielles PDF et leurs aperçus PNG.
- `rapport_jalon3_sources.zip` : source autonome à compiler, tableaux et figures.
- `donnees_rapport.json` : empreintes des résultats utilisés pour les figures et tableaux.

## Compilation autonome

Dans ce dossier ou après extraction de l'archive :

```bash
sh compiler.sh
```

Le script utilise `latexmk`, sinon trois passes `pdflatex`, sinon `tectonic`.
Les paquets usuels LaTeX et le support du français sont nécessaires. Tectonic
peut télécharger les paquets manquants lors de sa première exécution.
Les figures et tableaux fournis suffisent : aucun nouvel apprentissage, résultat
CSV ou module Python du projet n'est nécessaire pour recompiler le document.

## Régénération des données du rapport

Depuis la racine du dépôt, avec les résultats complets encore présents :

```bash
.venv/bin/python -m output.pdf.preparer_rapport
```

Cette commande refait les tableaux et figures depuis les archives auditées,
sans apprentissage. Elle nécessite l'environnement Python du projet et LINCS.
Elle est distincte de la compilation autonome du document LaTeX.

Le désaccord de classe haute montré dans les nuages est un complément calculé
sur le diagnostic privé indépendant. Cette précision figure dans le rapport.

## Contrôles de livraison

La compilation, les références, les tableaux et le rendu des pages sont vérifiés.
Le document distingue bandes d'écart-type, intervalles de confiance appariés,
diagnostics oracle privés et décisions réellement accessibles à B. Les résultats
hybrides restent rétrospectifs et leur coût de sélection mesuré par rejeu n'est
pas présenté comme un nouveau benchmark d'apprentissage de bout en bout.
