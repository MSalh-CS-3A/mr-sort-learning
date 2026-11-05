"""Stratégies de l'agent malveillant H : un fichier par personne ou par idée.

Chaque fichier de ce dossier est importé automatiquement ; ses fonctions
décorées par @hacker deviennent disponibles. Préfixer par _ pour l'ignorer.
"""

import importlib
import pkgutil

for _module in pkgutil.iter_modules(__path__):
    if not _module.name.startswith("_"):
        importlib.import_module(f"{__name__}.{_module.name}")
