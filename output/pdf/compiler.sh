#!/bin/sh
set -eu
cd "$(dirname "$0")"
if command -v latexmk >/dev/null 2>&1; then
    latexmk -pdf -interaction=nonstopmode -halt-on-error rapport_jalon3.tex
elif command -v pdflatex >/dev/null 2>&1; then
    pdflatex -interaction=nonstopmode -halt-on-error rapport_jalon3.tex
    pdflatex -interaction=nonstopmode -halt-on-error rapport_jalon3.tex
    pdflatex -interaction=nonstopmode -halt-on-error rapport_jalon3.tex
elif command -v tectonic >/dev/null 2>&1; then
    tectonic --keep-logs rapport_jalon3.tex
else
    printf '%s\n' 'Installer LaTeX (latexmk ou pdflatex) ou Tectonic pour compiler.' >&2
    exit 1
fi
