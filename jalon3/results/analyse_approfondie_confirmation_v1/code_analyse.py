"""Diagnostics exploratoires de la confirmation, sans nouvel apprentissage.

Recharge les modèles et partitions, vérifie les métriques originales et produit
confusions, diagnostics des candidats, contrastes appariés et compromis de Pareto.
Les deux sélecteurs additionnels sont des explorations rétrospectives seulement.
"""

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/projet-jalon3-matplotlib")

import numpy as np
from threadpoolctl import threadpool_limits

from .analyse import identifiant, lire_resultats
from .simulation import graine_derivee
from .validation_comparaisons import charger_modele


BOOTSTRAPS = 10000
ANALYSIS_SEED = 20261104
ATTACKS = ("classe_haute", "mrsort_aleatoire")
DEFENSES = ("naif", "inv2_plus_grand")
LABELS = {"naif": "Naïf", "inv2_plus_grand": "Inv2, plus grand groupe",
          "classe_haute": "Classe haute", "mrsort_aleatoire": "MR-Sort aléatoire"}


def write_csv(path, rows):
    rows = list(rows)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                             for k, v in row.items()})


def stats(values, key):
    values = np.asarray(values, dtype=float)
    assert len(values) == 20 and np.isfinite(values).all(), (key, len(values))
    rng = np.random.default_rng(graine_derivee(ANALYSIS_SEED, str(key)))
    means = values[rng.integers(len(values), size=(BOOTSTRAPS, len(values)))].mean(axis=1)
    lo, hi = np.quantile(means, [.025, .975])
    return dict(n=len(values), moyenne=float(values.mean()), ecart_type=float(values.std(ddof=1)),
                ic95_bas=float(lo), ic95_haut=float(hi))


def entropy(probabilities):
    p = np.asarray(probabilities)
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)) / np.log(3))


def confusion(y, prediction):
    counts = np.bincount(3 * y + prediction, minlength=9).reshape(3, 3)
    assert (counts.sum(axis=1) > 0).all()
    return counts, counts / counts.sum(axis=1, keepdims=True)


def dominant(a, b):
    """All criteria maximize: weak inequalities and at least one strict."""
    a, b = np.asarray(a), np.asarray(b)
    return bool(np.all(a >= b) and np.any(a > b))


def load_diagnostics(source):
    original = lire_resultats(source / "resultats.csv")
    assert len(original) == 840 and all(r["statut"] == "ok" for r in original)
    details, groups, pairs, selectors = [], [], [], []
    loaded = {}
    for i, row in enumerate(original):
        n, seed, rho, attack, defense = (row[k] for k in ("taille", "graine", "ratio", "hacker", "defense"))
        key = n, seed
        root = source / "lots" / f"6x3_n{n}_g{seed:04d}" / "instances/6x3" / f"graine_{seed:03d}"
        if key not in loaded:
            with np.load(root / "donnees.npz") as archive:
                data = {k: archive[k] for k in archive.files}
            public = np.random.default_rng(graine_derivee(seed, "analyse_publique_v1", 6, 3)).uniform(size=(10000, 6))
            assert not np.array_equal(public, data["x_test"])
            loaded[key] = data, public
        data, public = loaded[key]
        case = root / f"taille_{n}" / f"ratio_{rho:g}" / identifiant(attack)
        name = identifiant(defense)
        model = charger_modele(case / f"{name}.npz")
        y = data["y_test"]
        pred = model.predict(data["x_test"])
        counts, matrix = confusion(y, pred)
        recalls = np.diag(matrix)
        fidelity = float(np.mean(pred == y))
        np.testing.assert_allclose(fidelity, row["fidelite"], atol=1e-12)
        np.testing.assert_allclose(recalls, json.loads(row["fidelites_categories"]), atol=1e-12)
        np.testing.assert_allclose(recalls.mean(), row["fidelite_equilibree"], atol=1e-12)
        np.testing.assert_allclose(row["temps"], row["temps_preparation"] + row["temps_selection"], atol=1e-9)
        base = dict(taille=n, graine=seed, ratio=rho, hacker=attack, defense=defense)
        record = dict(base, fidelite=fidelity, fidelite_equilibree=float(recalls.mean()),
                      temps=row["temps"], temps_preparation=row["temps_preparation"],
                      temps_selection=row["temps_selection"],
                      erreur_vers_haut=float(np.mean(pred > y)), erreur_vers_bas=float(np.mean(pred < y)),
                      desaccord=row["desaccord"])
        for c in range(3):
            record[f"rappel_{c}"] = float(recalls[c])
            record[f"frequence_vraie_{c}"] = float(np.mean(y == c))
            record[f"frequence_predite_{c}"] = float(np.mean(pred == c))
            for j in range(3):
                record[f"confusion_{c}_{j}"] = float(matrix[c, j])
                record[f"confusion_effectif_{c}_{j}"] = int(counts[c, j])
        details.append(record)
        if defense != "inv2_plus_grand":
            continue
        with np.load(case / "injection.npz") as archive:
            x_h, y_h, source_h = archive["x_h"], archive["y_h"], archive["source_h"]
        x = np.vstack((data["x_a"][:n], x_h))
        train_y = np.concatenate((data["y_a"][:n], y_h))
        order = np.random.default_rng(graine_derivee(seed, "melange")).permutation(len(train_y))
        x, train_y = x[order], train_y[order]
        np.testing.assert_array_equal(source_h, np.r_[np.zeros(n, dtype=bool), np.ones(len(y_h), dtype=bool)][order])
        segment = np.load(case / f"{name}.segment.npy")
        chosen = int(row["groupe_choisi"])
        assert chosen == int(np.argmax(np.bincount(segment, minlength=2)))
        candidates = []
        for k in (0, 1):
            m = charger_modele(case / f"{name}_modele_{k}.npz")
            p = m.predict(data["x_test"])
            public_p = m.predict(public)
            train_p = m.predict(x)
            inside, authentic = segment == k, (segment == k) & ~source_h
            probabilities = np.bincount(public_p, minlength=3) / len(public_p)
            assigned_counts = np.bincount(train_y[inside], minlength=3)
            train_margin = m.error_and_margin(x[inside], train_y[inside])[1]
            g = dict(base, groupe=k, choisi=int(chosen == k), taille_groupe=int(inside.sum()),
                     n_a=int(authentic.sum()), n_h=int(np.sum(inside & source_h)),
                     proportion_h=float(np.mean(source_h[inside])),
                     fidelite=float(np.mean(p == y)),
                     fidelite_equilibree=float(np.mean([np.mean(p[y == c] == c) for c in range(3)])),
                     erreur_groupe=float(np.mean(train_p[inside] != train_y[inside])),
                     marge_groupe=float(np.mean(train_margin)),
                     erreur_melange=float(np.mean(train_p != train_y)),
                     entropie_publique=entropy(probabilities), couverture_min_publique=float(probabilities.min()),
                     proportion_haut_publique=float(probabilities[2]),
                     taux_haut_test=float(np.mean(p == 2)),
                     poids=m.w.tolist(), profils=m.b.tolist(), seuil=float(m.lam))
            for c in range(3):
                g[f"n_a_classe_{c}"] = int(np.sum(authentic & (train_y == c)))
                g[f"n_etiquette_{c}"] = int(assigned_counts[c])
                g[f"proportion_publique_{c}"] = float(probabilities[c])
                g[f"rappel_{c}"] = float(np.mean(p[y == c] == c))
            candidates.append(g)
            groups.append(g)
        oracle = max(g["fidelite"] for g in candidates)
        regret = oracle - fidelity
        np.testing.assert_allclose([oracle, regret], [row["fidelite_oracle_a"], row["perte_selection"]], atol=1e-12)
        np.testing.assert_allclose(candidates[chosen]["fidelite"], fidelity, atol=1e-12)
        upper = int(np.argmax([g["proportion_haut_publique"] for g in candidates]))
        high, other = candidates[upper], candidates[1-upper]
        n_a_high = int(np.sum(data["y_a"][:n] == 2))
        pair = dict(base, groupe_choisi=chosen, groupe_plus_haut=upper,
                    fidelite=fidelity, fidelite_oracle=oracle, perte_selection=regret,
                    choix_sous_optimal=int(regret > 1e-12), choix_perte_sup_1_point=int(regret > .01),
                    choix_groupe_plus_haut=int(chosen == upper),
                    groupe_plus_haut_majoritaire=int(high["taille_groupe"] > other["taille_groupe"]),
                    proportion_a_haute=n_a_high/n,
                    construction_haut_majoritaire=int(len(y_h) + 2*n_a_high > n),
                    taille_haut_constructible=len(y_h) + n_a_high,
                    taille_haut_apprise=high["taille_groupe"],
                    n_a_haut_dans_groupe_haut=high["n_a_classe_2"],
                    n_a_nonhaut_dans_groupe_haut=high["n_a_classe_0"]+high["n_a_classe_1"],
                    n_h_dans_groupe_haut=high["n_h"],
                    part_a_haut_absorbee=high["n_a_classe_2"]/n_a_high if n_a_high else None,
                    part_h_groupe_haut=high["n_h"]/len(y_h) if len(y_h) else None,
                    part_a_nonhaut_groupe_haut=(high["n_a_classe_0"]+high["n_a_classe_1"])/(n-n_a_high)
                    if n_a_high<n else None,
                    fidelite_groupe_plus_haut=high["fidelite"], fidelite_autre_groupe=other["fidelite"],
                    prediction_haute_groupe_haut=high["proportion_haut_publique"],
                    prediction_haute_autre=other["proportion_haut_publique"],
                    entropie_groupe_haut=high["entropie_publique"], entropie_autre=other["entropie_publique"],
                    rejet_a=float(1-candidates[chosen]["n_a"]/n),
                    conservation_h=float(candidates[chosen]["n_h"]/len(y_h)) if len(y_h) else None)
        pairs.append(pair)
        # Public features only; no true A labels are consulted by these choices.
        eligible = [k for k in (0, 1) if candidates[k]["couverture_min_publique"] >= .005]
        cover = eligible[0] if len(eligible) == 1 else chosen
        choices = {"plus_grand_reference": chosen,
                   "couverture_005_sinon_plus_grand": cover,
                   "entropie_publique_max": int(np.argmax([g["entropie_publique"] for g in candidates]))}
        for selector, selected in choices.items():
            selectors.append(dict(base, selecteur=selector, groupe=selected, changement=int(selected != chosen),
                                  fidelite=candidates[selected]["fidelite"],
                                  fidelite_equilibree=candidates[selected]["fidelite_equilibree"],
                                  gain_sur_reference=candidates[selected]["fidelite"]-fidelity))
        if (i+1) % 140 == 0:
            print(f"Archives relues : {i+1}/840 décisions", flush=True)
    return details, groups, pairs, selectors


def summarise(records, keys, metrics):
    grouped = defaultdict(list)
    for r in records:
        grouped[tuple(r[k] for k in keys)].append(r)
    result = []
    for key, rows in sorted(grouped.items()):
        rows = sorted(rows, key=lambda r: r["graine"])
        for metric in metrics:
            values = [r[metric] for r in rows if r.get(metric) is not None]
            if not values:
                continue
            result.append(dict(zip(keys, key), mesure=metric, **stats(values, (*key, metric))))
    return result


def contrasts_and_dominance(details):
    index = {(r["taille"], r["graine"], r["ratio"], r["hacker"], r["defense"]): r for r in details}
    paired, dominance_rows = [], []
    seeds = sorted({r["graine"] for r in details})
    conditions = sorted({(r["taille"], r["ratio"], r["hacker"]) for r in details})
    for n, rho, attack in conditions:
        d = {method: [index[n, s, rho, attack, method] for s in seeds] for method in DEFENSES}
        for metric in ("fidelite", "fidelite_equilibree", "temps", "rappel_0", "rappel_1", "rappel_2"):
            values = [b[metric]-a[metric] for a, b in zip(d["naif"], d["inv2_plus_grand"])]
            paired.append(dict(taille=n, ratio=rho, hacker=attack, contraste="inv2_moins_naif", mesure=metric,
                               **stats(values, (n, rho, attack, metric, "defense"))))
        for dim in (2, 3):
            criteria = ["temps", "fidelite"] + (["fidelite_equilibree"] if dim == 3 else [])
            vectors = {method: np.array([[-r[k] if k == "temps" else r[k] for k in criteria]
                                         for r in rows]) for method, rows in d.items()}
            a, b = vectors["naif"], vectors["inv2_plus_grand"]
            dom_a, dom_b = dominant(a.mean(0), b.mean(0)), dominant(b.mean(0), a.mean(0))
            dominance_rows.append(dict(taille=n, ratio=rho, hacker=attack, dimensions=dim,
                                       dominant_moyennes="naif" if dom_a else "inv2_plus_grand" if dom_b else "aucun",
                                       proportion_graines_naif_domine=float(np.mean([dominant(x,y) for x,y in zip(a,b)])),
                                       proportion_graines_inv2_domine=float(np.mean([dominant(y,x) for x,y in zip(a,b)])),
                                       temps_naif=float(-a[:,0].mean()), temps_inv2=float(-b[:,0].mean()),
                                       fidelite_naif=float(a[:,1].mean()), fidelite_inv2=float(b[:,1].mean()),
                                       fidelite_equilibree_naif=float(np.mean([r["fidelite_equilibree"] for r in d["naif"]])),
                                       fidelite_equilibree_inv2=float(np.mean([r["fidelite_equilibree"] for r in d["inv2_plus_grand"]]))))
        if rho:
            for defense in DEFENSES:
                for metric in ("fidelite", "fidelite_equilibree", "rappel_0", "rappel_1", "rappel_2"):
                    values = [index[n,s,0.,"aucun",defense][metric] - index[n,s,rho,attack,defense][metric] for s in seeds]
                    paired.append(dict(taille=n, ratio=rho, hacker=attack, defense=defense,
                                       contraste="perte_depuis_sans_attaque", mesure=metric,
                                       **stats(values, (n,rho,attack,defense,metric,"temoin"))))
                    values = [index[n,s,rho,"mrsort_aleatoire",defense][metric] - index[n,s,rho,"classe_haute",defense][metric] for s in seeds]
                    if attack == "classe_haute":
                        paired.append(dict(taille=n, ratio=rho, hacker=attack, defense=defense,
                                           contraste="mr_aleatoire_moins_classe_haute", mesure=metric,
                                           **stats(values, (n,rho,defense,metric,"attaque"))))
    return paired, dominance_rows


def plots(output, details, groups, pairs, summary, pair_summary, dominance_rows, selector_summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FixedLocator, NullLocator, ScalarFormatter
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "savefig.dpi": 150})
    figures = output / "figures"
    figures.mkdir(exist_ok=True)
    saved = []
    def save(fig, name):
        for ext in ("png", "svg"):
            fig.savefig(figures / f"{name}.{ext}", bbox_inches="tight")
        plt.close(fig)
        saved.append(name)
    sizes, ratios = (300,500,1000), (0.,.25,.5,1.)
    si = {(r["taille"],r["ratio"],r["hacker"],r["defense"],r["mesure"]):r for r in summary}
    def get(n, rho, attack, defense, metric):
        return si[n,rho,"aucun" if rho == 0 else attack,defense,metric]
    for attack in ATTACKS:
        fig, axes = plt.subplots(2,3,figsize=(14,8),layout="constrained",sharex=True,sharey=True)
        for row, defense in enumerate(DEFENSES):
            for col, n in enumerate(sizes):
                ax=axes[row,col]
                for c, color in enumerate(("#377eb8","#ff7f00","#4daf4a")):
                    values = [get(n,r,attack,defense,f"rappel_{c}") for r in ratios]
                    ax.plot(ratios,[100*v["moyenne"] for v in values],"o-",color=color,label=("Basse","Moyenne","Haute")[c])
                    ax.fill_between(ratios,[100*v["ic95_bas"] for v in values],[100*v["ic95_haut"] for v in values],alpha=.12,color=color)
                ax.set_title(f"{LABELS[defense]} ; N_A={n}")
                ax.set(ylim=(0,101),xticks=ratios,xlabel="Ratio H/A",ylabel="Rappel (%)")
                ax.grid(alpha=.2)
        axes[0,0].legend()
        fig.suptitle(f"{LABELS[attack]} : rappels par catégorie\nMoyennes sur 20 graines ; bandes : IC bootstrap à 95 % individuels")
        save(fig,f"rappels_{attack}")
        fig,axes=plt.subplots(2,3,figsize=(12,8),layout="constrained")
        for row, defense in enumerate(DEFENSES):
            for col,n in enumerate(sizes):
                ax=axes[row,col]
                matrix=np.array([[get(n,1.,attack,defense,f"confusion_{c}_{j}")["moyenne"] for j in range(3)] for c in range(3)])
                ax.imshow(matrix,vmin=0,vmax=1,cmap="Blues")
                for c in range(3):
                    for j in range(3):
                        ax.text(j,c,f"{100*matrix[c,j]:.1f}",ha="center",va="center",color="white" if matrix[c,j]>.6 else "black")
                ax.set(title=f"{LABELS[defense]} ; N_A={n}",xticks=range(3),yticks=range(3),
                       xticklabels=["Basse","Moyenne","Haute"],yticklabels=["Basse","Moyenne","Haute"],
                       xlabel="Catégorie prédite par B",ylabel="Catégorie de A")
        fig.suptitle(f"{LABELS[attack]}, H/A=1 : matrices de confusion (%)\nNormalisation par vraie catégorie, puis moyenne égale des 20 graines")
        save(fig,f"confusions_{attack}_ratio1")
    ps={(r["taille"],r["ratio"],r["hacker"],r["mesure"]):r for r in pair_summary}
    fig,axes=plt.subplots(2,3,figsize=(14,8),layout="constrained",sharex=True,sharey=True)
    for row,attack in enumerate(ATTACKS):
        for col,n in enumerate(sizes):
            ax=axes[row,col]
            vals=lambda metric: [ps[n,r,"aucun" if r==0 else attack,metric]["moyenne"]*100 for r in ratios]
            oracle,actual=vals("fidelite_oracle"),vals("fidelite")
            ax.plot(ratios,oracle,"o-",color="#4daf4a",label="Meilleur candidat (oracle)")
            ax.plot(ratios,actual,"o-",color="#984ea3",label="Candidat choisi")
            ax.fill_between(ratios,actual,oracle,color="#984ea3",alpha=.13,label="Perte de sélection")
            ax.plot(ratios,[100*get(n,r,attack,"naif","fidelite")["moyenne"] for r in ratios],"o--",color="#377eb8",label="Naïf")
            ax.set(title=f"{LABELS[attack]} ; N_A={n}",ylim=(0,101),xticks=ratios,xlabel="Ratio H/A",ylabel="Fidélité (%)")
            ax.grid(alpha=.2)
    axes[0,0].legend(fontsize=8)
    fig.suptitle("Qualité des candidats et perte due au choix\nL'oracle est réservé au diagnostic ; aucun nouvel apprentissage")
    save(fig,"oracle_et_selection")
    # Public-high model = model with larger predicted-high volume, not a known H identity.
    example=[p for p in pairs if p["taille"]==1000 and p["ratio"]==1 and p["hacker"]=="classe_haute"]
    example.sort(key=lambda p:p["graine"])
    gi={(g["taille"],g["graine"],g["ratio"],g["hacker"],g["groupe"]):g for g in groups}
    fig,axes=plt.subplots(2,1,figsize=(15,8),layout="constrained",sharex=True,sharey=True)
    for panel in (0,1):
        ax=axes[panel]
        gr=[gi[1000,p["graine"],1.,"classe_haute",p["groupe_plus_haut"] if panel==0 else 1-p["groupe_plus_haut"]] for p in example]
        bottom=np.zeros(len(gr))
        for key,label,color in (("n_a_classe_0","A : basse","#377eb8"),("n_a_classe_1","A : moyenne","#ff7f00"),
                                ("n_a_classe_2","A : haute","#4daf4a"),("n_h","H : haute","#e41a1c")):
            vals=np.array([g[key] for g in gr])
            ax.bar(range(len(gr)),vals,bottom=bottom,color=color,label=label)
            bottom+=vals
        for x,g in enumerate(gr):
            if g["choisi"]:
                ax.text(x,bottom[x]+25,"★",ha="center",fontsize=12)
        ax.set(ylabel="Nombre de lignes",title="Modèle prédisant le plus souvent haut" if panel==0 else "Autre modèle")
        ax.axhline(1000,color="black",ls="--",lw=1,alpha=.4)
    axes[0].legend(ncol=4,loc="upper right")
    axes[1].set(xticks=range(len(example)),xticklabels=[p["graine"] for p in example],xlabel="Graine ; ★ : groupe choisi par B")
    fig.suptitle("Classe haute : composition réelle des deux groupes (N_A=N_H=1000)\nLa provenance est utilisée uniquement par l'évaluateur")
    save(fig,"composition_groupes_classe_haute")
    fig,axes=plt.subplots(2,3,figsize=(15,9),layout="constrained",sharey=True)
    markers={0.:"s",.25:"o",.5:"^",1.:"D"}
    colors={"naif":"#377eb8","inv2_plus_grand":"#984ea3"}
    for row,attack in enumerate(ATTACKS):
        for col,n in enumerate(sizes):
            ax=axes[row,col]
            for defense in DEFENSES:
                t=[get(n,r,attack,defense,"temps")["moyenne"] for r in ratios]
                f=[100*get(n,r,attack,defense,"fidelite")["moyenne"] for r in ratios]
                ax.plot(t,f,"--",color=colors[defense],alpha=.5)
                for r,x,y in zip(ratios,t,f):
                    st,sf=get(n,r,attack,defense,"temps"),get(n,r,attack,defense,"fidelite")
                    ax.errorbar(x,y,xerr=[[x-st["ic95_bas"]],[st["ic95_haut"]-x]],
                                yerr=[[y-100*sf["ic95_bas"]],[100*sf["ic95_haut"]-y]],
                                color=colors[defense],marker=markers[r],capsize=2,alpha=.85)
            ax.set(xscale="log",xlim=(3,110),ylim=(20,101),xlabel="Durée de décision de B (s, échelle log)",ylabel="Fidélité (%)",
                   title=f"{LABELS[attack]} ; N_A={n}")
            ax.xaxis.set_major_locator(FixedLocator([4,10,30,80]))
            ax.xaxis.set_major_formatter(ScalarFormatter())
            ax.xaxis.set_minor_locator(NullLocator())
            ax.grid(alpha=.2)
    legend=[Line2D([0],[0],color=colors[d],label=LABELS[d]) for d in DEFENSES]
    legend += [Line2D([0],[0],color="gray",ls="",marker=markers[r],label=f"ρ={r:g}") for r in ratios]
    axes[0,0].legend(handles=legend,fontsize=8,ncol=2)
    fig.suptitle("Compromis fidélité–temps : moyennes et IC bootstrap à 95 %\nComparer les défenses à ρ identique ; les trajectoires ne sont pas des frontières de Pareto")
    save(fig,"compromis_temps_fidelite")
    fig,axes=plt.subplots(2,3,figsize=(14,8),layout="constrained",sharex=True,sharey=True)
    for row,attack in enumerate(ATTACKS):
        for col,n in enumerate(sizes):
            ax=axes[row,col]
            for defense in DEFENSES:
                for r in ratios:
                    f=get(n,r,attack,defense,"fidelite")["moyenne"]*100
                    b=get(n,r,attack,defense,"fidelite_equilibree")["moyenne"]*100
                    t=get(n,r,attack,defense,"temps")["moyenne"]
                    ax.scatter(f,b,s=15+3*t,color=colors[defense],marker=markers[r],alpha=.6)
            ax.set(xlim=(20,101),ylim=(20,101),xlabel="Fidélité globale (%)",ylabel="Fidélité équilibrée (%)",
                   title=f"{LABELS[attack]} ; N_A={n}")
            ax.grid(alpha=.2)
    axes[0,0].legend(handles=legend,fontsize=8,ncol=2)
    fig.suptitle("Trois critères : globale, équilibrée, temps (surface des points)\nSymboles = ratio H/A ; comparer seulement les conditions identiques")
    save(fig,"trois_criteres")
    selidx={(r["taille"],r["ratio"],r["hacker"],r["selecteur"],r["mesure"]):r for r in selector_summary}
    fig,axes=plt.subplots(2,3,figsize=(14,8),layout="constrained",sharex=True,sharey=True)
    for row,attack in enumerate(ATTACKS):
        for col,n in enumerate(sizes):
            ax=axes[row,col]
            for selector,color,label in (("couverture_005_sinon_plus_grand","#4daf4a","Couverture minimale 0,5 %"),
                                         ("entropie_publique_max","#ff7f00","Entropie publique maximale")):
                vv=[selidx[n,r,"aucun" if r==0 else attack,selector,"gain_sur_reference"] for r in ratios]
                ax.plot(ratios,[100*v["moyenne"] for v in vv],"o-",color=color,label=label)
                ax.fill_between(ratios,[100*v["ic95_bas"] for v in vv],[100*v["ic95_haut"] for v in vv],color=color,alpha=.12)
            ax.axhline(0,color="black",lw=1)
            ax.set(title=f"{LABELS[attack]} ; N_A={n}",xlabel="Ratio H/A",ylabel="Gain sur le choix actuel (points)",xticks=ratios)
            ax.grid(alpha=.2)
    axes[0,0].legend(fontsize=8)
    fig.suptitle("Exploration rétrospective de sélecteurs : aucun résultat confirmatoire\nCaractéristiques publiques ; mêmes candidats ; nouvelles graines requises pour valider")
    save(fig,"selecteurs_exploratoires")
    return saved


def main(source, output, actualiser=False):
    source,output=source.resolve(),output.resolve()
    if output == source or source in output.parents:
        raise ValueError("La sortie doit être séparée de la campagne source")
    if output.exists() and any(output.iterdir()):
        if not actualiser:
            raise ValueError("Choisir un dossier vide ou --actualiser pour refaire les fichiers générés")
        audit=json.loads((output/"audit_analyse.json").read_text())
        if audit["source"] != str(source):
            raise ValueError("L'analyse existante utilise une autre source")
    output.mkdir(parents=True,exist_ok=True)
    before=hashlib.sha256((source/"resultats.csv").read_bytes()).hexdigest()
    details,groups,pairs,selectors=load_diagnostics(source)
    summary=summarise(details,("taille","ratio","hacker","defense"),
                      ("fidelite","fidelite_equilibree","temps","temps_preparation","temps_selection",
                       "rappel_0","rappel_1","rappel_2","frequence_vraie_2","frequence_predite_2",
                       "erreur_vers_haut","erreur_vers_bas",*[f"confusion_{c}_{j}" for c in range(3) for j in range(3)]))
    pair_metrics=[k for k in pairs[0] if k not in ("taille","graine","ratio","hacker","defense","groupe_choisi","groupe_plus_haut")]
    pair_summary=summarise(pairs,("taille","ratio","hacker"),pair_metrics)
    selector_summary=summarise(selectors,("taille","ratio","hacker","selecteur"),
                               ("fidelite","fidelite_equilibree","changement","gain_sur_reference"))
    contrasts,dominance_rows=contrasts_and_dominance(details)
    for name,rows in (("decisions_detaillees",details),("groupes",groups),("paires_candidats",pairs),
                      ("resume_metriques",summary),("resume_candidats",pair_summary),
                      ("contrastes_apparies",contrasts),("dominances",dominance_rows),
                      ("selecteurs_exploratoires",selectors),("resume_selecteurs",selector_summary)):
        write_csv(output/f"{name}.csv",rows)
    figures=plots(output,details,groups,pairs,summary,pair_summary,dominance_rows,selector_summary)
    assert hashlib.sha256((source/"resultats.csv").read_bytes()).hexdigest()==before
    metadata=dict(statut="ok",source=str(source),sha256_resultats_source=before,
                  sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  decisions_recalculees=len(details),candidats_recharges=len(groups),paires=len(pairs),
                  bootstraps=BOOTSTRAPS,graine_analyse=ANALYSIS_SEED,
                  statut_scientifique="Diagnostics et sélecteurs exploratoires postérieurs à la confirmation",
                  controle=["fidélités et rappels reconstitués", "confusions normalisées", "origines du mélange",
                            "choix du plus grand groupe", "oracle et perte de sélection", "comptabilité des temps",
                            "source CSV inchangée"],figures=figures)
    (output/"code_analyse.py").write_bytes(Path(__file__).read_bytes())
    (output/"audit_analyse.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(metadata,ensure_ascii=False,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path)
    parser.add_argument("sortie",type=Path)
    parser.add_argument("--actualiser",action="store_true",help="Refaire les fichiers générés de la même analyse, sans apprentissage")
    args=parser.parse_args()
    with threadpool_limits(limits=1):
        main(args.source,args.sortie,args.actualiser)
