# Calibrage local des 25 couples

Cette campagne comprend 400 évaluations : cinq attaques, cinq défenses, cinq
graines (100 à 104), N_A=300, six critères, trois classes, ratios H/A 0 / 0,25 /
0,5 / 1 et 10 000 objets de test par graine. Deux sous-processus calculent en
parallèle, avec un thread numérique chacun.

Le statut réel du lancement est dans [progression.json](progression.json). Le
lanceur effectue automatiquement les audits, le regroupement, les figures et
l'estimation de durée. Les lots incomplets restent exclus des statistiques.
Une campagne complète doit avoir cinq marqueurs `lots/*/termine.json` et un
`audit_campagne.json` portant `statut: ok` et `decisions_verifiees: 400`.

```bash
.venv/bin/python -m jalon3.campagne --sortie jalon3/results/calibrage_local_v1 --etat
```

À l'issue du calcul : `bilan.md`, `figures/`, `resume.csv`, `estimation.md` et les
audits des lots permettent d'examiner les résultats et le coût. `verification_lanceur/`
conserve les preuves des essais réels du lanceur (distincts des 400 évaluations).
Les 30 tests de `jalon3/tests` sont passés avant ce lancement.

La [documentation du lanceur](../../docs/campagnes_locales.md) décrit la reprise,
l'arrêt propre et les campagnes à 2 400 puis 9 600 évaluations. Les temps entre
défenses restent différents : ce calibrage ne démontre pas de supériorité à
budget égal. Les cinq graines servent au développement et au calibrage ; les
graines d'évaluation finale sont séparées.
