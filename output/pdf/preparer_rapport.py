"""Préparer les tableaux et figures du rapport depuis les résultats audités.

Aucun apprentissage. Les calculs de confirmation ne sont jamais modifiés.
"""
import csv
import hashlib
import io
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR','/tmp/projet-jalon3-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, NullLocator, ScalarFormatter
import numpy as np
from lincs import classification as lc
from jalon2.jalon2_deux_mrsort import MRSort

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SOURCE=ROOT/'jalon3/results/confirmation_quatre_couples_v1'
DEEP=ROOT/'jalon3/results/analyse_approfondie_confirmation_v1'
RESEARCH=ROOT/'jalon3/results/recherche_selection_v1'

def read(path):
    with path.open() as f:return list(csv.DictReader(f))

def number(x, places=2):return f'{float(x):.{places}f}'.replace('.',',')
def condition(r):return int(r['taille']),float(r['ratio']),r['hacker']

def main():
    (OUT/'figures').mkdir(exist_ok=True)
    (OUT/'tables').mkdir(exist_ok=True)
    rows=read(SOURCE/'resume.csv')
    index={(*condition(r),r['defense']):r for r in rows}
    details=read(DEEP/'decisions_detaillees.csv')
    deep=read(DEEP/'resume_metriques.csv')
    di={(*condition(r),r['defense'],r['mesure']):r for r in deep}
    pairs=read(DEEP/'paires_candidats.csv')
    groups=read(DEEP/'groupes.csv')
    hybrid=read(RESEARCH/'resume_transfert.csv')
    hi={(*condition(r),r['selecteur'],r['mesure']):r for r in hybrid}
    conditions=[(n,r,h) for n in [300,500,1000] for r,h in
                [(0.,'aucun'),(.25,'mrsort_aleatoire'),(.5,'mrsort_aleatoire'),(1.,'mrsort_aleatoire'),
                 (.25,'classe_haute'),(.5,'classe_haute'),(1.,'classe_haute')]]
    hname={'aucun':'Sans','mrsort_aleatoire':'MR','classe_haute':'Haute'}
    resultats=[]; costs=[]; hybrides=[]
    for n,r,h in conditions:
        a,b=index[n,r,h,'naif'],index[n,r,h,'inv2_plus_grand']
        values=[str(n),number(r,2),hname[h],*[number(100*float(x[k])) for k in ['fidelite_moyenne','fidelite_equilibree_moyenne'] for x in [a,b]]]
        resultats.append(' & '.join(values)+r' \\')
        costs.append(' & '.join([str(n),number(r),hname[h],*[number(100*float(x['delta_attaque_moyenne'])) for x in [a,b]],
                                *[number(x['temps_moyenne']) for x in [a,b]]])+r' \\')
        v=hi[n,r,h,'hybride','fidelite'];g=hi[n,r,h,'hybride','gain']
        hybrides.append(' & '.join([str(n),number(r),hname[h],number(100*float(b['fidelite_moyenne'])),number(100*float(v['moyenne'])),
                                   number(100*float(g['moyenne'])),f"[{number(100*float(g['ic95_bas']))} ; {number(100*float(g['ic95_haut']))}]"])+r' \\')
    for name,lines in [('resultats_complets',resultats),('couts_complets',costs),('hybride_complet',hybrides)]:
        (OUT/'tables'/f'{name}.tex').write_text('\n'.join(lines)+'\n')
    # Le désaccord de classe haute est un diagnostic complémentaire explicite,
    # calculé sur le diagnostic privé indépendant, jamais fourni à une stratégie.
    disagreement={}
    for seed in range(1000,1020):
        p=SOURCE/'lots'/f'6x3_n300_g{seed}'/'instances/6x3'/f'graine_{seed}'/'donnees.npz'
        with np.load(p) as z:disagreement[seed]=float(np.mean(z['y_diagnostic_a']!=2))
    original=read(SOURCE/'resultats_apparies.csv')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.titlesize':9,
                         'axes.labelsize':8,'legend.fontsize':7,'xtick.labelsize':7.5,'ytick.labelsize':7.5,
                         'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':210})
    colors=['#1976a3','#d97919','#368f4b']
    defenses=['naif','inv2_plus_grand']; names={'naif':'Naïf','inv2_plus_grand':'Inv2, plus grand groupe'}
    attacks=['mrsort_aleatoire','classe_haute']; anames={'mrsort_aleatoire':'MR-Sort aléatoire','classe_haute':'Classe haute'}
    ratios=[0,.25,.5,1]
    def save(fig,name):
        fig.savefig(OUT/'figures'/f'{name}.pdf',bbox_inches='tight')
        fig.savefig(OUT/'figures'/f'{name}.png',bbox_inches='tight')
        plt.close(fig)
    for h in attacks:
        for b in defenses:
            fig,axes=plt.subplots(2,2,figsize=(6.55,4.05),layout='constrained')
            for j,n in enumerate([300,500,1000]):
                rr=[index[n,r,'aucun' if r==0 else h,b] for r in ratios]
                for ax,key in [(axes[0,0],'fidelite'),(axes[0,1],'delta_attaque'),(axes[1,0],'fidelite_equilibree')]:
                    mean=np.array([float(x[key+'_moyenne'])*100 for x in rr]);sd=np.array([float(x[key+'_ecart_type'])*100 for x in rr])
                    ax.plot(ratios,mean,'o-',ms=3,color=colors[j],label=f'$N_A={n}$')
                    lo,hi_=mean-sd,mean+sd
                    if key!='delta_attaque':lo=np.maximum(lo,0);hi_=np.minimum(hi_,100)
                    ax.fill_between(ratios,lo,hi_,color=colors[j],alpha=.12)
                    ax.set(xticks=ratios,xlabel='Ratio H/A');ax.grid(alpha=.18)
            axes[0,0].set(title='Fidélité globale',ylabel='Accord avec A (%)',ylim=(0,101))
            axes[0,1].set(title='Perte depuis le témoin',ylabel='Dégradation (points)')
            axes[0,1].axhline(0,color='black',lw=.7)
            axes[1,0].set(title='Fidélité équilibrée',ylabel='Rappel moyen (%)',ylim=(0,101))
            axes[0,0].legend(loc='lower left',ncol=1)
            selected=[r for r in original if r['hacker']==h and r['defense']==b and float(r['ratio'])>0]
            x=[100*(disagreement[int(r['graine'])] if h=='classe_haute' else float(r['desaccord'])) for r in selected]
            y=[100*float(r['delta_attaque']) for r in selected]
            sc=axes[1,1].scatter(x,y,c=[float(r['ratio']) for r in selected],s=8,cmap='viridis',vmin=0,vmax=1,alpha=.65,edgecolors='none')
            axes[1,1].axhline(0,color='black',lw=.7);axes[1,1].grid(alpha=.18)
            axes[1,1].set(title='Diagnostic descriptif',xlabel='Désaccord A/H (%)',ylabel='Dégradation (points)')
            bar=fig.colorbar(sc,ax=axes[1,1],fraction=.045,pad=.025);bar.set_label('H/A',fontsize=7)
            save(fig,f'couple_{h}_{b}')
    # Confusions ciblées : texte et chiffres restent lisibles à largeur de page.
    fig,axes=plt.subplots(1,2,figsize=(6.55,2.7),layout='constrained')
    for ax,b in zip(axes,defenses):
        matrix=np.array([[float(di[1000,1.,'classe_haute',b,f'confusion_{c}_{j}']['moyenne'])*100 for j in range(3)] for c in range(3)])
        ax.imshow(matrix,vmin=0,vmax=100,cmap='Blues')
        for c in range(3):
            for j in range(3):ax.text(j,c,number(matrix[c,j],1),ha='center',va='center',color='white' if matrix[c,j]>60 else 'black',fontsize=9)
        ax.set(title=names[b],xticks=range(3),yticks=range(3),xticklabels=['Basse','Moyenne','Haute'],yticklabels=['Basse','Moyenne','Haute'],xlabel='Catégorie prédite',ylabel='Catégorie de A')
    save(fig,'confusions_haute_1000')
    # Oracle et sélection, tous les N et attaques.
    fig,axes=plt.subplots(2,3,figsize=(6.55,4.5),layout='constrained',sharex=True,sharey=True)
    for row,h in enumerate(attacks):
        for col,n in enumerate([300,500,1000]):
            ax=axes[row,col]
            v=[];o=[]
            for r in ratios:
                pp=[p for p in pairs if int(p['taille'])==n and float(p['ratio'])==r and p['hacker']==('aucun' if r==0 else h)]
                v.append(100*np.mean([float(p['fidelite']) for p in pp]));o.append(100*np.mean([float(p['fidelite_oracle']) for p in pp]))
            ax.plot(ratios,o,'o-',ms=3,color='#368f4b',label='Oracle des candidats')
            ax.plot(ratios,v,'o-',ms=3,color='#8a4a99',label='Modèle choisi')
            ax.fill_between(ratios,v,o,color='#8a4a99',alpha=.12)
            ax.set(title=f'{anames[h]}\n$N_A={n}$',xticks=[0,.5,1],xlabel='Ratio H/A',ylabel='Fidélité (%)',ylim=(20,101));ax.grid(alpha=.18)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside upper center',ncol=2,frameon=False)
    save(fig,'oracle_selection')
    # Composition réelle : deux groupes, 20 graines, orientation publique.
    pp=sorted([r for r in pairs if r['taille']=='1000' and float(r['ratio'])==1 and r['hacker']=='classe_haute'],key=lambda r:int(r['graine']))
    gi={(int(g['graine']),int(g['groupe'])):g for g in groups if g['taille']=='1000' and float(g['ratio'])==1 and g['hacker']=='classe_haute'}
    fig,axes=plt.subplots(2,1,figsize=(6.55,4.2),layout='constrained',sharex=True,sharey=True)
    for panel,ax in enumerate(axes):
        gg=[gi[int(p['graine']),int(p['groupe_plus_haut']) if panel==0 else 1-int(p['groupe_plus_haut'])] for p in pp]
        bottom=np.zeros(20)
        for key,label,color in [('n_a_classe_0','A : basse','#1976a3'),('n_a_classe_1','A : moyenne','#d97919'),('n_a_classe_2','A : haute','#368f4b'),('n_h','H : haute','#c44242')]:
            v=np.array([int(g[key]) for g in gg]);ax.bar(range(20),v,bottom=bottom,color=color,label=label,width=.8);bottom+=v
        for i,g in enumerate(gg):
            if g['choisi']=='1':ax.plot(i,bottom[i]+35,'*',color='black',ms=4)
        ax.axhline(1000,color='black',ls='--',lw=.6,alpha=.4)
        ax.set(title='Modèle prédisant le plus souvent haut' if panel==0 else 'Autre modèle',ylabel='Effectif')
    axes[1].set(xticks=range(20),xticklabels=[str(int(p['graine'])-1000) for p in pp],xlabel='Graine = 1000 + indice ; étoile : groupe choisi')
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside upper center',ncol=4,fontsize=7,frameon=False)
    save(fig,'composition_groupes')
    # Trois critères affichés en deux vues, sans frontière entre difficultés.
    markers={0:'s',.25:'o',.5:'^',1:'D'};dc={'naif':'#1976a3','inv2_plus_grand':'#8a4a99'}
    fig,axes=plt.subplots(2,3,figsize=(6.55,4.6),layout='constrained',sharey=True)
    for row,h in enumerate(attacks):
        for col,n in enumerate([300,500,1000]):
            ax=axes[row,col]
            for b in defenses:
                rr=[index[n,r,'aucun' if r==0 else h,b] for r in ratios]
                tx=[float(z['temps_moyenne']) for z in rr];fy=[100*float(z['fidelite_moyenne']) for z in rr]
                ax.plot(tx,fy,'--',lw=.8,color=dc[b],alpha=.5)
                for r,t,f in zip(ratios,tx,fy):ax.scatter(t,f,color=dc[b],marker=markers[r],s=17)
            ax.set(xscale='log',xlim=(3,110),ylim=(20,101),title=f'{anames[h]}\n$N_A={n}$',xlabel='Temps (s, log)',ylabel='Fidélité (%)')
            ax.xaxis.set_major_locator(FixedLocator([4,20,80]));ax.xaxis.set_major_formatter(ScalarFormatter());ax.xaxis.set_minor_locator(NullLocator());ax.grid(alpha=.18)
    legend=[Line2D([0],[0],color=dc[b],label=names[b]) for b in defenses]+[Line2D([0],[0],color='gray',marker=markers[r],ls='',label=f'$\u03c1={r:g}$') for r in ratios]
    fig.legend(handles=legend,loc='outside upper center',ncol=3,frameon=False,fontsize=7)
    save(fig,'compromis_temps')
    fig,axes=plt.subplots(1,2,figsize=(6.55,2.65),layout='constrained',sharey=True)
    for ax,h in zip(axes,attacks):
        for method,color,label in [('plus_grand','#8a4a99','Plus grand groupe'),('accord_melange','#d97919','Accord seul'),('hybride','#368f4b','Hybride')]:
            vals=[100*float(hi[1000,r,'aucun' if r==0 else h,method,'fidelite']['moyenne']) for r in ratios]
            ax.plot(ratios,vals,'o-',ms=3,color=color,label=label)
        ax.set(title=anames[h],xlabel='Ratio H/A',ylabel='Fidélité (%)',xticks=ratios,ylim=(20,101));ax.grid(alpha=.18)
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside upper center',ncol=3,frameon=False,fontsize=7)
    save(fig,'hybride_retrospectif')
    # Exemple reproductible du hacker basique, choisi après observation pour illustrer.
    root=SOURCE/'lots/6x3_n300_g1001/instances/6x3/graine_1001'
    problem=lc.Problem.load(io.StringIO((root/'probleme.yml').read_text()))
    hfile=next((root/'taille_300/ratio_0.5').glob('mrsort_aleatoire*/modele_h.yml'))
    models={name:MRSort.from_lincs(lc.Model.load(problem,io.StringIO(path.read_text()))) for name,path in [('A',root/'modele_a.yml'),('H',hfile)]}
    params=[]
    for name,m in models.items():
        matrix=' \\\\ '.join(' & '.join(number(x,4) for x in profile) for profile in m.b)
        weights=';\\ '.join(number(x,4) for x in m.w)
        params.append(r'\paragraph{Modèle $M_'+name+r'$.}'+ '\n'+r'\[b_'+name+r'=\begin{pmatrix}'+matrix+r'\end{pmatrix}\]'+'\n'+r'\[w_'+name+r'=('+weights+r'),\qquad \lambda_'+name+'='+number(m.lam,4)+r'.\]'+'\n')
    (OUT/'tables/parametres_exemple.tex').write_text('\n'.join(params))
    fingerprints={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in
                  [SOURCE/'resultats.csv',SOURCE/'resume.csv',SOURCE/'comparaisons_confirmation.csv',DEEP/'decisions_detaillees.csv',DEEP/'groupes.csv',RESEARCH/'resume_transfert.csv',RESEARCH/'regle_figee.json']}
    manifest=dict(source='Rapport du jalon 3, résultats au 4 novembre 2026',sources_sha256=fingerprints,
                  figures=len(list((OUT/'figures').glob('*.pdf'))),conditions=len(conditions),
                  desaccord_classe_haute='Complément après expérience : moyenne de 1{y_diagnostic_A != 2}',
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/'donnees_rapport.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
