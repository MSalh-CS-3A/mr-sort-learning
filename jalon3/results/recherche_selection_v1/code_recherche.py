"""Développer un sélecteur hybride sur 5 anciennes graines, puis le décrire
sur les 20 graines déjà analysées. Aucune validation indépendante revendiquée.
"""

import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from threadpoolctl import threadpool_limits

from .analyse import identifiant, lire_resultats
from .analyse_approfondie import entropy, stats, write_csv
from .simulation import graine_derivee
from .validation_comparaisons import charger_modele

GRID = (0., .02, .05, .1, .2)


def choose(candidates, coefficient):
    """Features publiques seulement ; départager les égalités par la taille."""
    largest = int(np.argmax([c["taille_groupe"] for c in candidates]))
    scores = [1-c["erreur_melange"]+coefficient*c["entropie_publique"] for c in candidates]
    return 1-largest if scores[1-largest] > scores[largest]+1e-12 else largest


def development(source):
    rows = lire_resultats(source/"resultats.csv")
    rows = [r for r in rows if r["defense"]=="inv2_plus_grand" and
            r["hacker"] in ("aucun","classe_haute","mrsort_aleatoire")]
    assert len(rows)==35 and {r["graine"] for r in rows}==set(range(100,105))
    features=[]
    for row in rows:
        n,s,rho,h=(row[k] for k in ("taille","graine","ratio","hacker"))
        root=source/"lots"/f"6x3_n{n}_g{s:04d}"/"instances/6x3"/f"graine_{s:03d}"
        with np.load(root/"donnees.npz") as z:
            data={k:z[k] for k in z.files}
        case=root/f"taille_{n}"/f"ratio_{rho:g}"/identifiant(h)
        with np.load(case/"injection.npz") as z:
            x_h,y_h=z["x_h"],z["y_h"]
        # L'ordre ne change ni l'accord global ni l'entropie du modèle.
        x=np.vstack((data["x_a"][:n],x_h))
        y=np.r_[data["y_a"][:n],y_h]
        segment=np.load(case/f"{identifiant('inv2_plus_grand')}.segment.npy")
        public=np.random.default_rng(graine_derivee(s,"analyse_publique_v1",6,3)).uniform(size=(10000,6))
        for k in (0,1):
            m=charger_modele(case/f"{identifiant('inv2_plus_grand')}_modele_{k}.npz")
            pp=m.predict(public)
            pred=m.predict(data["x_test"])
            features.append(dict(taille=n,graine=s,ratio=rho,hacker=h,groupe=k,
                                 taille_groupe=int(np.sum(segment==k)),
                                 erreur_melange=float(np.mean(m.predict(x)!=y)),
                                 entropie_publique=entropy(np.bincount(pp,minlength=3)/len(pp)),
                                 fidelite=float(np.mean(pred==data["y_test"])),
                                 fidelite_equilibree=float(np.mean([np.mean(pred[data["y_test"]==c]==c) for c in range(3)]))))
    return features


def group_pairs(features):
    grouped=defaultdict(list)
    for r in features:
        grouped[r["taille"],r["graine"],r["ratio"],r["hacker"]].append(r)
    for pair in grouped.values():
        pair.sort(key=lambda x:x["groupe"])
        assert [p["groupe"] for p in pair]==[0,1]
    return grouped


def main(calibration, diagnostic, output):
    if output.exists() and any(output.iterdir()):
        raise ValueError("La sortie doit être nouvelle")
    output.mkdir(parents=True,exist_ok=True)
    dev=development(calibration)
    write_csv(output/"caracteristiques_developpement.csv",dev)
    pairs=group_pairs(dev)
    choices=[]
    for coefficient in GRID:
        conditions=defaultdict(list)
        for (n,s,rho,h),pair in pairs.items():
            selected=choose(pair,coefficient)
            base=int(np.argmax([c["taille_groupe"] for c in pair]))
            conditions[rho,h].append(pair[selected]["fidelite"]-pair[base]["fidelite"])
        admissible=all(np.mean(conditions[rho,h])>=-.01-1e-12 for rho,h in
                       ((0.,"aucun"),(.25,"mrsort_aleatoire"),(.5,"mrsort_aleatoire")))
        mean_gain=float(np.mean([np.mean(v) for v in conditions.values()]))
        choices.append(dict(coefficient=coefficient,admissible=admissible,gain_moyen=mean_gain,
                            gains_conditions={f"{h}/{rho:g}":float(np.mean(v)) for (rho,h),v in conditions.items()}))
    eligible=[r for r in choices if r["admissible"]]
    if not eligible:
        raise ValueError("Aucun coefficient admissible sur le développement")
    best=max(eligible,key=lambda r:(r["gain_moyen"],-r["coefficient"]))
    frozen=dict(coefficient=best["coefficient"],regle="accord_melange + lambda * entropie_publique",
                grille=list(GRID),reglage_graines=list(range(100,105)),paires_developpement=35,
                contrainte="Gain moyen >= -0,01 dans témoin et MR aléatoire aux ratios 0,25/0,5",
                objectif="Gain moyen, sept conditions également pondérées ; égalité au plus petit lambda",
                confirmation_independante=False,
                sha256_calibrage=hashlib.sha256((calibration/"resultats.csv").read_bytes()).hexdigest())
    # Écrit AVANT de lire les scores de transfert pour le critère hybride.
    (output/"regle_figee.json").write_text(json.dumps(frozen,ensure_ascii=False,indent=2)+"\n")
    write_csv(output/"reglage_developpement.csv",choices)
    print("Règle figée depuis le développement :",frozen["coefficient"],flush=True)
    with (diagnostic/"groupes.csv").open() as f:
        transfer=list(csv.DictReader(f))
    for row in transfer:
        for key in ("taille","graine","groupe","taille_groupe"):
            row[key]=int(row[key])
        for key in ("ratio","erreur_melange","entropie_publique","fidelite","fidelite_equilibree"):
            row[key]=float(row[key])
    records=[]
    for (n,s,rho,h),pair in group_pairs(transfer).items():
        base=int(np.argmax([c["taille_groupe"] for c in pair]))
        sel=choose(pair,frozen["coefficient"])
        globalfit=choose(pair,0.)
        for method,k in (("plus_grand",base),("accord_melange",globalfit),("hybride",sel)):
            records.append(dict(taille=n,graine=s,ratio=rho,hacker=h,selecteur=method,groupe=k,
                                changement=int(k!=base),fidelite=pair[k]["fidelite"],
                                fidelite_equilibree=pair[k]["fidelite_equilibree"],
                                gain=pair[k]["fidelite"]-pair[base]["fidelite"]))
    write_csv(output/"transfert_retroactif.csv",records)
    grouped=defaultdict(list)
    for r in records:
        grouped[r["taille"],r["ratio"],r["hacker"],r["selecteur"]].append(r)
    summaries=[]
    for key,rr in sorted(grouped.items()):
        rr.sort(key=lambda r:r["graine"])
        for metric in ("fidelite","fidelite_equilibree","gain","changement"):
            summaries.append(dict(zip(("taille","ratio","hacker","selecteur"),key),mesure=metric,
                                  **stats([r[metric] for r in rr],("recherche_selection",*key,metric))))
    write_csv(output/"resume_transfert.csv",summaries)
    # Unité d'incertitude pour l'agrégat : graine, jamais les 420 cellules.
    per_seed=defaultdict(list)
    for r in records:
        if r["selecteur"]=="hybride":
            per_seed[r["graine"]].append(r["gain"])
    overall=stats([np.mean(v) for s,v in sorted(per_seed.items())],"gain_moyen_21_conditions")
    audit=dict(statut="ok",**frozen,paires_transfert=len(records)//3,
               statut_transfert="Rétrospectif, graines déjà examinées ; pas de confirmation indépendante",
               gain_moyen_21_conditions=overall,
               sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (output/"audit_recherche.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(audit,ensure_ascii=False,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("calibrage",type=Path)
    parser.add_argument("diagnostic",type=Path)
    parser.add_argument("sortie",type=Path)
    args=parser.parse_args()
    with threadpool_limits(limits=1):
        main(args.calibrage,args.diagnostic,args.sortie)
