#!/usr/bin/env bash
set -uo pipefail
cd /home/mohamedsalh/Documents/CS/3A/SDP/projet
dossier="$PWD/results/simple/a2_72_fichiers_graine0_30s"
export PYTHONPATH="$dossier/source"
export PYTHONUNBUFFERED=1
export TZ=Europe/Paris
resultat_global=0
for type_donnees in type_a type_b; do
    printf 'EN_COURS %s\n' "$type_donnees" > "$dossier/statut.txt"
    date -Iseconds
    printf 'Début du lot %s\n' "$type_donnees"
    .venv/bin/python -m projet "data/$type_donnees" \
        --methodes A2-uniforme A2-gmm --graines 0 \
        --temps 30 --temps-appel 1 \
        --sortie "$dossier/$type_donnees"
    code=$?
    printf '%s=%s\n' "$type_donnees" "$code" >> "$dossier/codes_sortie.txt"
    if [ "$code" -ge 2 ]; then
        printf 'ECHEC %s code=%s\n' "$type_donnees" "$code" > "$dossier/statut.txt"
        exit "$code"
    fi
    if [ "$code" -ne 0 ]; then resultat_global=1; fi
    printf 'Fin du lot %s, code=%s\n' "$type_donnees" "$code"
done
printf 'TERMINE code=%s\n' "$resultat_global" > "$dossier/statut.txt"
date -Iseconds
exit "$resultat_global"
