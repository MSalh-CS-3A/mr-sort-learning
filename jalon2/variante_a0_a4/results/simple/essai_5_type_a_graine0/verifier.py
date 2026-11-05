import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
os.environ.setdefault('MPLCONFIGDIR', '/tmp/projet-matplotlib')
import csv
import json
import math
from io import StringIO
from pathlib import Path
from statistics import mean

import numpy as np
from lincs import classification as lc
from projet.apprentissage import Donnees, charger, distances_categorie, predire

dossier = Path('results/simple/essai_5_type_a_graine0')
with (dossier / 'resultats.csv').open() as stream:
    lignes = list(csv.DictReader(stream))
assert len(lignes) == 40, len(lignes)
verifications = []
for ligne in lignes:
    assert ligne['statut'] == 'ok', ligne
    donnees = charger(ligne['fichier'])
    x_original, y_original = donnees.x.copy(), donnees.y.copy()
    details = dossier / ligne['details']
    with (details / 'problem.yml').open() as stream:
        probleme = lc.Problem.load(stream)
    modeles = []
    for groupe in (0, 1):
        with (details / f'modele_{groupe}.yml').open() as stream:
            modeles.append(lc.Model.load(probleme, stream))
    predictions = np.array([predire(donnees, modele) for modele in modeles])
    with (details / 'affectations.csv').open() as stream:
        affectations = list(csv.DictReader(stream))
    z = np.array([int(a['groupe']) for a in affectations])
    assert len(z) == len(donnees.y) and set(z) == {0, 1}
    categories = [c.name for c in probleme.ordered_categories]
    for i, affectation in enumerate(affectations):
        assert affectation['nom'] == donnees.noms[i]
        assert affectation['categorie_observee'] == categories[donnees.y[i]]
        for groupe in (0, 1):
            assert affectation[f'prediction_{groupe}'] == categories[predictions[groupe, i]]
    lg = int(np.count_nonzero(predictions[z, np.arange(len(z))] != donnees.y))
    assert lg == int(ligne['LG']), (ligne, lg)
    assert math.isclose(lg / len(z), float(ligne['taux_erreur']))
    for groupe in (0, 1):
        assert int((z == groupe).sum()) == int(ligne[f'taille_groupe_{groupe}'])
    with (details / 'trace.csv').open() as stream:
        trace = list(csv.DictReader(stream))
    assert trace
    temps = [float(t['temps']) for t in trace]
    scores = [int(t['meilleur_LG']) for t in trace]
    assert temps == sorted(temps)
    assert scores == sorted(scores, reverse=True)
    assert scores[-1] == lg
    assert np.array_equal(donnees.x, x_original) and np.array_equal(donnees.y, y_original)
    assert not donnees.x.flags.writeable and not donnees.y.flags.writeable
    verifications.append(dict(details=ligne['details'], LG_recharge=lg, conforme=True))

# Cas calculables : la distance doit respecter la coalition et atteindre la
# catégorie observée, même lorsqu'il faut franchir plusieurs profils.
probleme = charger('data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv').probleme
def modele(seuils, poids):
    texte = 'kind: ncs-classification-model\nformat_version: 1\naccepted_values:\n'
    texte += ''.join('  - kind: thresholds\n    thresholds: ' + json.dumps(seuils) + '\n' for _ in range(6))
    texte += 'sufficient_coalitions:\n'
    texte += ''.join('  - kind: weights\n    criterion_weights: ' + json.dumps(poids) + '\n' for _ in range(2))
    return lc.Model.load(probleme, StringIO(texte))

cas = [
    ('coalition_robuste', [.9, .9, .51], 2, [.5, .8], [.7, .4, .1, 0, 0, 0], .1),
    ('entree_intermediaire', [.9, .9, .51], 1, [.5, .8], [.7, .4, .1, 0, 0, 0], .1),
    ('sortie_profil_inferieur', [.51, .9, .9], 1, [.5, .8], [.7, .4, .1, 0, 0, 0], .01),
    ('atteindre_categorie_et_non_profil_suivant', [.9, .9, .51], 0, [.5, .8], [.7, .4, .1, 0, 0, 0], .4),
    ('entree_superieure', [.49, .9, .9], 2, [.5, .8], [.7, .4, .1, 0, 0, 0], .31),
    ('entree_inferieure', [.1, .1, .1], 1, [.5, .8], [.7, .4, .1, 0, 0, 0], .4),
    ('egalite_robustesse_nulle', [.5, .5, .5], 1, [.5, .8], [.7, .4, .1, 0, 0, 0], 0),
    ('categorie_vide', [.1, .1, .1], 1, [.5, .5], [.7, .4, .1, 0, 0, 0], math.inf),
    ('seuil_none', [.1, .1, .1], 2, [.5, None], [.7, .4, .1, 0, 0, 0], math.inf),
    ('decision_constante_robuste', [.9, .9, .9], 0, [.5, .8], [.7, 0, 0, 0, 0, 0], math.inf),
    ('decision_constante_inaccessible', [.9, .9, .9], 2, [.5, .8], [.7, 0, 0, 0, 0, 0], math.inf),
]
distances = []
for nom, valeurs, categorie, seuils, poids, attendu in cas:
    x = np.array([valeurs + [0, 0, 0]], dtype=np.float32).astype(float)
    y = np.array([categorie])
    donnees = Donnees(Path('cas_manuel'), probleme, ('x',), x, y)
    m = modele(seuils, poids)
    prediction = predire(donnees, m)
    distance = float(distances_categorie(donnees, m, prediction)[0])
    assert math.isclose(distance, attendu, abs_tol=1e-6), (nom, attendu, distance)
    distances.append(dict(cas=nom, conforme=True,
                          attendu=attendu if math.isfinite(attendu) else 'inf',
                          obtenu=distance if math.isfinite(distance) else 'inf'))

rapport = dict(executions=len(lignes), resultats_conformes=len(verifications),
               controles_distances=distances, rechargements=verifications)
(dossier / 'verification.json').write_text(json.dumps(rapport, indent=2, ensure_ascii=False) + '\n')
resume = []
for methode in ('A1', 'A2', 'A3', 'A4'):
    for initialisation in ('uniforme', 'gmm'):
        groupe = [r for r in lignes if r['methode'] == methode and r['initialisation'] == initialisation]
        resume.append(dict(methode=methode, initialisation=initialisation, fichiers=len(groupe),
                           taux_erreur_moyen=mean(float(r['taux_erreur']) for r in groupe),
                           temps_moyen=mean(float(r['temps_total']) for r in groupe),
                           temps_total=sum(float(r['temps_total']) for r in groupe)))
with (dossier / 'comparaison.csv').open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(resume[0]))
    writer.writeheader()
    writer.writerows(resume)
print(json.dumps(dict(executions=len(lignes), conformes=len(verifications),
                      controles_distance=len(distances), resume=resume), indent=2))
