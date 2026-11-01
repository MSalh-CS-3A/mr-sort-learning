#!/usr/bin/env bash
# À lancer depuis la racine ; choisir un nouveau dossier de sortie.
.venv/bin/projet \
  data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv \
  data/type_a/cr06_ca03/n0600_rep75-25_noise10.csv \
  data/type_a/cr08_ca04/n0300_rep50-50_noise10.csv \
  data/type_a/cr08_ca04/n1200_rep75-25_noise00.csv \
  data/type_a/cr10_ca05/n0600_rep75-25_noise10.csv \
  --methodes A1-uniforme A1-gmm A2-uniforme A2-gmm A3-uniforme A3-gmm A4-uniforme A4-gmm \
  --graines 0 --temps 10 --temps-appel 0.25 \
  --sortie results/simple/essai_5_type_a_graine0
