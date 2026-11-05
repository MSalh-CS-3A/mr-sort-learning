# Confirmation des quatre expériences

Plan fixé : deux attaques (MR-Sort aléatoire, classe haute), chacune face au naïf
et à Inv2 avec choix du plus grand groupe. Vingt nouvelles graines (1000 à 1019),
N_A=300, 500 et 1 000, ratios H/A 0 / 0,25 / 0,5 / 1, test de 10 000 objets.

**840 évaluations = 720 sous attaque + 120 témoins partagés.** Deux sous-processus
effectuent les 60 lots de 14 décisions. Les modèles et tests sont fixes par
graine ; les données sont emboîtées entre tailles et ratios. À ratio constant,
le nombre d'observations H augmente avec celui de A.

```bash
.venv/bin/python -m jalon3.campagne --sortie jalon3/results/confirmation_quatre_couples_v1 --etat
```

Le [statut du lanceur](progression.json) indique les lots actifs, terminés et en
échec. La commande compte aussi les décisions des lots en cours. La campagne est
réussie lorsque `audit_campagne.json` porte `statut: ok`, avec 840 décisions,
60 lots et un contrôle d'appariement réussi. Les résultats défavorables sont
conservés. Aucun changement de méthode n'est prévu après consultation des graines.

À la fin du calcul :

- `bilan.md` et `figures/` : graphiques des quatre couples et résultats détaillés ;
- `comparaisons_confirmation.md` et `.csv` : gain de défense, effet de l'attaque,
  différences appariées et intervalles à 95 % par bootstrap des graines ;
- `audit_appariement_tailles.json` : modèles fixes et préfixes sauvegardés vérifiés ;
- `resume.csv`, `resultats.csv`, `lots/` : statistiques, données et modèles ;
- `estimation.md`, `journaux/`, `configuration.json`, `sources/` : suivi et reproduction.

Le [plan d'analyse](../../docs/confirmation_quatre_couples.md) définit les deux
contrastes principaux et les analyses complémentaires avant le calcul. Les
bandes des graphiques usuels restent des écarts-types, distincts des IC des
contrastes. Les durées des méthodes diffèrent ; une fidélité supérieure ne prouve
pas une supériorité à calcul égal. Le résultat de cette confirmation reste à
interpréter ensemble.

`verification_pre_execution/` conserve les 40 tests passants et la vérification
du post-traitement sur les données de développement, distinctes des nouvelles
évaluations. La copie du code et du plan au moment du lancement est dans `sources/`.
