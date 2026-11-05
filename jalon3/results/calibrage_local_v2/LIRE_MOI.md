# Calibrage relancé après correction des poids nuls

Cette campagne recalcule les 400 évaluations du plan initial avec le code corrigé :
25 couples attaque/défense, cinq graines 100 à 104, N_A=300, six critères, trois
classes, ratios H/A 0 / 0,25 / 0,5 / 1 et test de 10 000 objets. Deux processus
travaillent en parallèle. Le plan et les distributions sont identiques à v1.

La conversion des poids LINCS tous nuls conserve maintenant une représentation
finie (poids nuls, seuil 1), avec exactement les prédictions natives de classe 0
et des marges finies. Les modèles et candidats non finis sont refusés dès la
décision de B ; les contrôles stricts de l'audit restent en place.

Avant cette relance : **35 tests passants**, puis **six décisions auditées** dans
un essai ciblé. Les 14 modèles de cet essai sont finis, dont quatre à poids nuls.
Les preuves sont conservées dans `verification_correction/` et `correction.json`.

`calibrage_local_v1` reste intact. Ses modèles ne sont pas réutilisés : les NaN
pouvaient fausser les réaffectations intermédiaires d'Inv-2.

```bash
.venv/bin/python -m jalon3.campagne --sortie jalon3/results/calibrage_local_v2 --etat
```

Le [statut](progression.json) indique les lots actifs, audités et en échec. La
commande ci-dessus compte aussi les décisions écrites dans les lots en cours.
Le lancement est terminé avec succès uniquement lorsque les cinq lots ont leur
marqueur `termine.json` et que `audit_campagne.json` indique `statut: ok` pour
400 décisions. Les tableaux, graphiques, audits et estimations sont produits
automatiquement. La [documentation](../../docs/campagnes_locales.md) décrit la
reprise et l'arrêt propre.
