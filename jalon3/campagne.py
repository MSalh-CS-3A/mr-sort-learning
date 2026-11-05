"""Campagnes locales par lots audités, exécutés depuis une copie figée du code.

python -m jalon3.campagne --phase calibrage --sortie jalon3/results/calibrage_local_v2
python -m jalon3.campagne --sortie DOSSIER --etat
python -m jalon3.campagne --sortie DOSSIER --reprendre
"""

import argparse
from collections import deque
import csv
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import shutil
import signal
import statistics
import subprocess
import sys
import time

ATTAQUES = ["classe_basse", "classe_haute", "etiquettes_aleatoires", "mrsort_aleatoire", "mrsort_concentre"]
DEFENSES = ["filtrage_iteratif", "inv2_mieux_explique", "inv2_plus_grand", "naif", "naif_multi"]
PAQUETS = ("lincs", "numpy", "scikit-learn", "matplotlib", "threadpoolctl")
CLE = ("criteres", "categories", "graine", "taille", "ratio", "hacker", "defense")


def maintenant():
    return datetime.now(timezone.utc).isoformat()


def ecrire_json(chemin, valeur):
    chemin = Path(chemin)
    temporaire = chemin.with_name(chemin.name + ".tmp")
    temporaire.write_text(json.dumps(valeur, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporaire.replace(chemin)


def lire_json(chemin):
    return json.loads(Path(chemin).read_text(encoding="utf-8"))


def empreinte(chemin):
    with Path(chemin).open("rb") as fichier:
        return hashlib.file_digest(fichier, "sha256").hexdigest()


def verrou_actif(chemin):
    """Les verrous fichiers fonctionnent aussi entre espaces de PID distincts."""
    if not chemin.exists():
        return False
    with chemin.open("r") as fichier:
        try:
            fcntl.flock(fichier, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
    return False


def ressources():
    cpu = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count() or 1
    memoire = {}
    if Path("/proc/meminfo").exists():
        for ligne in Path("/proc/meminfo").read_text().splitlines():
            cle, valeur = ligne.split(":", 1)
            memoire[cle] = int(valeur.split()[0]) * 1024
    disponible = memoire.get("MemAvailable")
    # Un choix conservateur pour ce poste ; ce n'est pas une réservation mémoire.
    processus = min(2, max(1, cpu - 2))
    if disponible is not None:
        processus = min(processus, max(1, int(disponible / (1.5 * 1024**3))))
    return dict(cpu_logiques=cpu, memoire_totale=memoire.get("MemTotal"),
                memoire_disponible=disponible, processus_conseilles=processus,
                plateforme=platform.platform())


def plan(phase, dossier, temps=12):
    if phase not in ("calibrage", "principale", "complete", "confirmation"):
        raise ValueError("Phase inconnue")
    if phase == "confirmation":
        return dict(hackers=["classe_haute", "mrsort_aleatoire"],
                    defenses=["inv2_plus_grand", "naif"], ratios=[0., .25, .5, 1.], dimensions=[[6, 3]],
                    tailles=[300, 500, 1000], graines=list(range(1000, 1020)),
                    taille_test=10000, temps=temps, processus=1, sortie=str(Path(dossier).resolve()),
                    sans_figures=True, lister=False)
    return dict(hackers=ATTAQUES, defenses=DEFENSES, ratios=[0., .25, .5, 1.], dimensions=[[6, 3]],
                tailles=[100, 300, 500, 1000] if phase == "complete" else [300],
                graines=list(range(100, 105)) if phase == "calibrage" else list(range(1000, 1030)),
                taille_test=10000, temps=temps, processus=1, sortie=str(Path(dossier).resolve()),
                sans_figures=True, lister=False)


def lots(configuration):
    return [dict(id=f"{d}x{c}_n{n}_g{s:04d}", dimension=[d, c], taille=n, graine=s)
            for d, c in configuration["dimensions"] for n in configuration["tailles"]
            for s in configuration["graines"]]


def configuration_lot(configuration, lot, dossier):
    return dict(configuration, dimensions=[lot["dimension"]], tailles=[lot["taille"]],
                graines=[lot["graine"]], sortie=str(Path(dossier).resolve()))


def meme_configuration(a, b):
    # Le déplacement d'une archive ne change pas l'expérience scientifique.
    return {k: v for k, v in a.items() if k != "sortie"} == {k: v for k, v in b.items() if k != "sortie"}


def cles_attendues(configuration):
    return {(d, c, s, n, r, h, b) for d, c in configuration["dimensions"]
            for s in configuration["graines"] for n in configuration["tailles"]
            for r in configuration["ratios"]
            for h in (["aucun"] if r == 0 else configuration["hackers"])
            for b in configuration["defenses"]}


def verifier_couverture(lignes, configuration):
    cles = [tuple(float(l[k]) if k == "ratio" else int(l[k]) if k in CLE[:4] else l[k]
                  for k in CLE) for l in lignes]
    if len(cles) != len(set(cles)) or set(cles) != cles_attendues(configuration):
        raise ValueError("Plan incomplet, inattendu ou doublons")
    if any(l["statut"] != "ok" for l in lignes):
        raise ValueError("Au moins une évaluation est en erreur")


def verifier_archive(racine, manifeste):
    for relatif, attendu in manifeste["sources_sha256"].items():
        if empreinte(Path(racine) / "sources" / relatif) != attendu:
            raise ValueError(f"Source archivée modifiée : {relatif}")
    versions = {p: importlib.metadata.version(p) for p in PAQUETS}
    if manifeste["versions"] != versions or manifeste["python"] != sys.version:
        raise ValueError("L'environnement Python a changé ; restaurer les versions archivées avant reprise")


def terminer_lot(dossier, configuration, secondes):
    """À appeler seulement après l'audit scientifique du lot."""
    from .analyse import lire_resultats
    if not meme_configuration(lire_json(dossier / "configuration.json")["configuration"], configuration):
        raise ValueError("Configuration exécutée différente du lot demandé")
    verifier_couverture(lire_resultats(dossier / "resultats.csv"), configuration)
    audit = lire_json(dossier / "audit.json")
    if audit.get("statut") != "ok" or audit["decisions_verifiees"] != len(cles_attendues(configuration)):
        raise ValueError("Audit absent ou incomplet")
    fichiers = {p.relative_to(dossier).as_posix(): empreinte(p)
                for p in sorted(dossier.rglob("*")) if p.is_file() and p.name != "termine.json"
                and "__pycache__" not in p.parts}
    ecrire_json(dossier / "termine.json", dict(statut="ok", date=maintenant(), secondes=secondes,
                                             configuration=configuration, fichiers_sha256=fichiers))


def lot_valide(dossier, configuration):
    if not (dossier / "termine.json").exists():
        return False
    marqueur = lire_json(dossier / "termine.json")
    if not meme_configuration(marqueur["configuration"], configuration) or marqueur["statut"] != "ok":
        raise ValueError(f"Configuration du lot terminé incompatible : {dossier.name}")
    for relatif, attendu in marqueur["fichiers_sha256"].items():
        if empreinte(dossier / relatif) != attendu:
            raise ValueError(f"Artefact modifié dans le lot terminé {dossier.name} : {relatif}")
    return True


def importer_lots(racine, manifeste, origine):
    """Étendre une campagne sans recalculer ses lots ; conserver leurs archives intactes."""
    origine = origine.resolve()
    source = lire_json(origine / "configuration.json")
    verifier_archive(origine, source)
    if source["sources_sha256"] != manifeste["sources_sha256"]:
        raise ValueError("Les campagnes à réunir doivent utiliser exactement les mêmes sources archivées")
    provenance = lire_json(racine / "provenance_lots.json") if (racine / "provenance_lots.json").exists() else {}
    imports = 0
    for lot in lots(manifeste["configuration"]):
        cible = racine / "lots" / lot["id"]
        if cible.exists():
            continue
        original = origine / "lots" / lot["id"]
        config = configuration_lot(manifeste["configuration"], lot, cible)
        if lot_valide(original, config):
            cible.parent.mkdir(parents=True, exist_ok=True)
            # Copier dans une zone intermédiaire : une copie interrompue reste non validée.
            temporaire = cible.with_name(cible.name + f".import_{time.time_ns()}")
            shutil.copytree(original, temporaire)
            temporaire.rename(cible)
            provenance[lot["id"]] = str(original)
            imports += 1
    ecrire_json(racine / "provenance_lots.json", provenance)
    print(f"{imports} lots audités importés de {origine}.", flush=True)


def interrompre(*_):
    raise KeyboardInterrupt


def executer_lot(racine, nom):
    racine = racine.resolve()
    verrous = racine / "verrous_lots"
    verrous.mkdir(exist_ok=True)
    with (verrous / nom).open("a") as verrou:
        fcntl.flock(verrou, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _executer_lot(racine, nom)


def _executer_lot(racine, nom):
    """Sous-processus isolé : les stratégies ne reçoivent que leurs vues habituelles."""
    from .experiences import main as experience
    from .validation_comparaisons import verifier
    from threadpoolctl import threadpool_limits
    racine = racine.resolve()
    manifeste = lire_json(racine / "configuration.json")
    verifier_archive(racine, manifeste)
    lot = next(l for l in lots(manifeste["configuration"]) if l["id"] == nom)
    dossier = racine / "lots" / nom
    config = configuration_lot(manifeste["configuration"], lot, dossier)
    debut = time.monotonic()
    arguments = ["--hackers", *config["hackers"], "--defenses", *config["defenses"],
                 "--dimensions", "x".join(map(str, lot["dimension"])), "--tailles", str(lot["taille"]),
                 "--graines", str(lot["graine"]), "--ratios", *map(str, config["ratios"]),
                 "--taille-test", str(config["taille_test"]), "--temps", str(config["temps"]),
                 "--processus", "1", "--sortie", str(dossier), "--sans-figures"]
    if experience(arguments):
        return 1
    # Le code, les entrées, les modèles et les métriques sont contrôlés avant le marqueur.
    with threadpool_limits(limits=1):
        verifier(dossier)
    terminer_lot(dossier, config, time.monotonic() - debut)
    return 0


def agreger(racine, manifeste, termines, figures=False):
    """N'agréger que les lots complets ; les lignes partielles restent dans leurs journaux."""
    from .analyse import analyser, lire_resultats
    from .experiences import COLONNES
    configuration = manifeste["configuration"]
    lignes = []
    for lot in termines:
        dossier = racine / "lots" / lot["id"]
        config = configuration_lot(configuration, lot, dossier)
        lot_lignes = lire_resultats(dossier / "resultats.csv")
        verifier_couverture(lot_lignes, config)
        lignes.extend(lot_lignes)
    if lignes:
        temporaire = racine / "resultats.csv.tmp"
        with temporaire.open("w", newline="", encoding="utf-8") as fichier:
            sortie = csv.DictWriter(fichier, fieldnames=COLONNES)
            sortie.writeheader()
            sortie.writerows({c: l.get(c) for c in COLONNES} for l in lignes)
        temporaire.replace(racine / "resultats.csv")
        analyser(racine, figures=figures)
    complet = len(termines) == len(lots(configuration))
    if complet:
        verifier_couverture(lignes, configuration)
    rapport = dict(statut="ok" if complet else "incomplet", decisions_verifiees=len(lignes),
                   decisions_attendues=len(cles_attendues(configuration)), lots_valides=[l["id"] for l in termines],
                   lots_attendus=len(lots(configuration)),
                   audits=[f"lots/{l['id']}/audit.json" for l in termines], date=maintenant())
    if complet and (racine / "campagne.json").exists() and lire_json(racine / "campagne.json")["phase"] == "confirmation":
        from .confirmation import analyser_confirmation
        rapport["appariement_tailles"] = analyser_confirmation(racine, configuration)
    ecrire_json(racine / "audit_campagne.json", rapport)
    if lignes:
        texte = (racine / "bilan.md").read_text(encoding="utf-8")
        avertissement = (f"> Campagne {'complète' if complet else 'INCOMPLÈTE'} : {len(termines)}/"
                         f"{rapport['lots_attendus']} lots audités, {len(lignes)}/"
                         f"{rapport['decisions_attendues']} évaluations. Les artefacts sont dans `lots/`.\n\n")
        (racine / "bilan.md").write_text(avertissement + texte, encoding="utf-8")
    return rapport


def estimation(racine, termines, processus):
    durees = [lire_json(racine / "lots" / l["id"] / "termine.json")["secondes"] for l in termines]
    if not durees:
        return {}
    campagne = racine / "campagne.json"
    if campagne.exists() and lire_json(campagne)["phase"] == "confirmation":
        configuration = lire_json(racine / "configuration.json")["configuration"]
        nombre_lots = len(lots(configuration))
        moyennes = {n: statistics.mean([d for l, d in zip(termines, durees) if l["taille"] == n])
                    for n in configuration["tailles"] if any(l["taille"] == n for l in termines)}
        restants = [l for l in lots(configuration) if l["id"] not in {t["id"] for t in termines}]
        restant = sum(moyennes.get(l["taille"], statistics.mean(durees)) for l in restants)
        resultat = dict(lots_mesures=len(durees), lots_attendus=nombre_lots,
                        secondes_lots_cumulees=sum(durees), secondes_restantes_cumulees_estimees=restant,
                        heures_restantes_ideales=restant / processus / 3600,
                        moyennes_secondes_par_taille=moyennes, processus=processus)
        texte = (f"# Estimation de la confirmation\n\n{len(durees)}/{nombre_lots} lots audités ; "
                 f"{sum(durees) / 3600:.2f} h cumulées mesurées.\n\n"
                 f"Durée restante idéale estimée avec {processus} processus : {restant / processus / 3600:.2f} h.\n\n"
                 "Estimation indicative fondée sur les durées par taille déjà observées. "
                 "Une taille non encore mesurée est provisoirement extrapolée depuis les autres ; "
                 "son coût peut être différent. Les lots actifs sont comptés comme restant entièrement à faire. "
                 "Les durées de sous-processus ne sont pas du temps CPU mesuré.\n")
        (racine / "estimation.md").write_text(texte, encoding="utf-8")
        ecrire_json(racine / "estimation.json", resultat)
        return resultat
    moyenne = statistics.mean(durees)
    resultat = dict(lots_mesures=len(durees), secondes_lots_cumulees=sum(durees),
                    secondes_moyennes_par_lot=moyenne,
                    principale_heures_cumulees=moyenne * 30 / 3600,
                    complete_heures_cumulees=moyenne * 120 / 3600,
                    processus=processus)
    texte = ["# Estimation locale", "",
             f"Mesure sur {len(durees)} lot(s) terminé(s) et audité(s) : {moyenne / 60:.1f} minutes par lot en moyenne.", "",
             "| Cible | Évaluations | Heures cumulées estimées | Durée idéale avec le parallélisme actuel |",
             "|---|---:|---:|---:|",
             f"| Principale (30 graines, N_A=300) | 2 400 | {resultat['principale_heures_cumulees']:.1f} | {resultat['principale_heures_cumulees'] / processus:.1f} h |",
             f"| Quatre tailles (30 graines) | 9 600 | {resultat['complete_heures_cumulees']:.1f} | {resultat['complete_heures_cumulees'] / processus:.1f} h |", "",
             "Extrapolation indicative, pas une garantie : la difficulté varie avec le modèle, l'attaque et la taille. "
             "Le calibrage à N_A=300 ne mesure pas les autres tailles. Les durées incluent les audits des lots ; "
             "les installations, l'agrégation finale, les figures et les interruptions s'ajoutent. "
             "Les heures cumulées sont des durées de sous-processus, pas une mesure de temps CPU."]
    (racine / "estimation.md").write_text("\n".join(texte) + "\n", encoding="utf-8")
    ecrire_json(racine / "estimation.json", resultat)
    return resultat


def etat(racine):
    manifeste = lire_json(racine / "configuration.json")
    total = 0
    termines = []
    partielles = 0
    for lot in lots(manifeste["configuration"]):
        dossier = racine / "lots" / lot["id"]
        fichiers = list(dossier.glob("instances/*/graine_*/parties.csv"))
        for fichier in fichiers:
            with fichier.open(newline="", encoding="utf-8") as entree:
                nombre = sum(1 for l in csv.DictReader(entree) if l.get("statut") in ("ok", "erreur"))
            if (dossier / "termine.json").exists():
                total += nombre
            else:
                partielles += nombre
        if (dossier / "termine.json").exists():
            termines.append(lot["id"])
    rapport = dict(lots_termines=len(termines), lots_attendus=len(lots(manifeste["configuration"])),
                   evaluations_lots_termines=total, evaluations_dans_lots_non_audites=partielles,
                   evaluations_attendues=len(cles_attendues(manifeste["configuration"])))
    if (racine / "progression.json").exists():
        rapport["lanceur"] = lire_json(racine / "progression.json")
        rapport["lanceur"]["verrou_actif"] = verrou_actif(racine / ".verrou")
    print(json.dumps(rapport, ensure_ascii=False, indent=2))
    return rapport


def lancer(racine, manifeste, processus, termines):
    configuration = manifeste["configuration"]
    finis = {l["id"] for l in termines}
    attente = deque(l for l in lots(configuration) if l["id"] not in finis)
    actifs, echecs = {}, []
    arret = racine / "ARRETER"
    journal = racine / "journaux"
    journal.mkdir(exist_ok=True)

    def progression(statut):
        ecrire_json(racine / "progression.json", dict(statut=statut, pid=os.getpid(), date=maintenant(),
                    processus=processus, lots_termines=len(termines), lots_attendus=len(lots(configuration)),
                    actifs={nom: p.pid for nom, (p, _, _) in actifs.items()}, echecs=echecs,
                    lots_en_attente=len(attente)))

    try:
        while attente or actifs:
            while attente and len(actifs) < processus and not arret.exists():
                lot = attente.popleft()
                nom = lot["id"]
                dossier = racine / "lots" / nom
                if dossier.exists():
                    ancien = racine / "tentatives_interrompues"
                    ancien.mkdir(exist_ok=True)
                    dossier.rename(ancien / f"{nom}_{time.time_ns()}")
                fichier = (journal / f"{nom}_{time.time_ns()}.log").open("w", encoding="utf-8")
                environnement = dict(os.environ, PYTHONPATH=str(racine / "sources"), PYTHONDONTWRITEBYTECODE="1",
                                      OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
                                      MPLCONFIGDIR="/tmp/projet-jalon3-matplotlib")
                commande = [os.path.abspath(sys.executable), "-u", "-m", "jalon3.campagne", "--sortie", str(racine),
                            "--executer-lot", nom]
                p = subprocess.Popen(commande, cwd=racine / "sources", env=environnement,
                                     stdin=subprocess.DEVNULL, stdout=fichier, stderr=subprocess.STDOUT,
                                     start_new_session=True)
                actifs[nom] = p, fichier, lot
                print(f"Lot démarré : {nom} (PID {p.pid}).", flush=True)
                progression("en_cours")
            for nom, (p, fichier, lot) in list(actifs.items()):
                code = p.poll()
                if code is None:
                    continue
                fichier.close()
                del actifs[nom]
                dossier = racine / "lots" / nom
                config = configuration_lot(configuration, lot, dossier)
                if code == 0 and lot_valide(dossier, config):
                    termines.append(lot)
                    print(f"Lot audité : {nom} ; {len(termines)}/{len(lots(configuration))}.", flush=True)
                    agreger(racine, manifeste, termines)
                    estimation(racine, termines, processus)
                else:
                    echecs.append(dict(lot=nom, code=code, journal=str(fichier.name)))
                    print(f"ÉCHEC : {nom} ; consulter {fichier.name}.", flush=True)
                progression("en_cours")
            if arret.exists() and not actifs:
                break
            if actifs:
                time.sleep(1)
    except BaseException:
        # Les enfants ont leur session : un Ctrl-C ne doit pas les laisser orphelins.
        for p, _, _ in actifs.values():
            if p.poll() is None:
                os.killpg(p.pid, signal.SIGTERM)
        for p, fichier, _ in actifs.values():
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()
            fichier.close()
        actifs.clear()
        progression("interrompu")
        raise
    complet = len(termines) == len(lots(configuration))
    progression("analyse" if complet else "echec" if echecs else "arrete")
    agreger(racine, manifeste, termines, figures=bool(termines))
    estimation(racine, termines, processus)
    progression("termine" if complet else "echec" if echecs else "arrete")
    print(f"Campagne : {len(termines)}/{len(lots(configuration))} lots audités. Résultats : {racine}", flush=True)
    return 0 if complet else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("calibrage", "principale", "complete", "confirmation"))
    parser.add_argument("--sortie", type=Path, required=True)
    parser.add_argument("--processus", type=int)
    parser.add_argument("--temps", type=float)
    parser.add_argument("--reprendre", action="store_true")
    parser.add_argument("--etat", action="store_true")
    parser.add_argument("--analyser", action="store_true", help="Vérifier et agréger les lots terminés, sans apprendre.")
    parser.add_argument("--plan", action="store_true", help="Afficher le plan sans créer ni lancer de campagne.")
    parser.add_argument("--depuis", type=Path, help="Importer les lots audités compatibles d'une campagne précédente.")
    parser.add_argument("--executer-lot", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    racine = args.sortie.resolve()
    if args.executer_lot:
        return executer_lot(racine, args.executer_lot)
    if args.etat:
        etat(racine)
        return 0
    machine = ressources()
    processus = args.processus if args.processus is not None else machine["processus_conseilles"]
    if processus < 1 or (args.temps is not None and (not math.isfinite(args.temps) or args.temps <= 0)):
        parser.error("Processus et budget strictement positifs requis")
    phase = args.phase or "calibrage"
    configuration = plan(phase, racine, args.temps if args.temps is not None else 12)
    if args.plan:
        print(json.dumps(dict(phase=phase, configuration=configuration, ressources=machine, processus=processus,
                              lots=len(lots(configuration)), evaluations=len(cles_attendues(configuration))),
                         ensure_ascii=False, indent=2))
        return 0
    if racine.exists() and not (args.reprendre or args.analyser):
        parser.error("Le dossier existe déjà : utiliser --reprendre ou une nouvelle --sortie")
    if not racine.exists() and (args.reprendre or args.analyser):
        parser.error("Campagne inexistante")
    creation = not racine.exists()
    racine.mkdir(parents=True, exist_ok=True)
    # Verrou système libéré automatiquement même après interruption brutale.
    with (racine / ".verrou").open("a") as verrou:
        try:
            fcntl.flock(verrou, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error("Un autre lanceur utilise déjà cette campagne")
        if creation:
            from .experiences import archiver_configuration
            archiver_configuration(configuration)
            ecrire_json(racine / "campagne.json", dict(phase=phase, date=maintenant(), ressources=machine,
                                                      note="Budget souple ; naif et Inv2 gardent leurs arrêts propres."))
        manifeste = lire_json(racine / "configuration.json")
        verifier_archive(racine, manifeste)
        # Après un SIGKILL du parent, un enfant pourrait être encore actif.
        for verrou_lot in (racine / "verrous_lots").glob("*"):
            if verrou_actif(verrou_lot):
                parser.error(f"Un sous-processus précédent utilise encore {verrou_lot.name} ; attendre sa fin avant reprise")
        enregistre = lire_json(racine / "campagne.json")
        if args.phase is not None and args.phase != enregistre["phase"]:
            parser.error("La phase ne peut pas changer dans une campagne existante")
        if args.temps is not None and args.temps != manifeste["configuration"]["temps"]:
            parser.error("Le budget ne peut pas changer lors d'une reprise")
        if args.depuis:
            importer_lots(racine, manifeste, args.depuis)
        termines = []
        for lot in lots(manifeste["configuration"]):
            dossier = racine / "lots" / lot["id"]
            if lot_valide(dossier, configuration_lot(manifeste["configuration"], lot, dossier)):
                termines.append(lot)
        if args.analyser:
            agreger(racine, manifeste, termines, figures=bool(termines))
            estimation(racine, termines, processus)
            return 0
        print(f"{len(lots(manifeste['configuration']))} lots ; "
              f"{len(cles_attendues(manifeste['configuration']))} évaluations ; {processus} processus ; "
              f"{len(termines)} lots déjà audités.", flush=True)
        signal.signal(signal.SIGTERM, interrompre)
        return lancer(racine, manifeste, processus, termines)


if __name__ == "__main__":
    raise SystemExit(main())
