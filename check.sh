#!/bin/sh
# test.sh ver. 20240920114214 Copyright 2024 alexx, MIT License
# RDFa:deps="[ruff black pylint]"
usage(){ printf "Usage: %s [-h]\n\t -h This help message\n" "$(basename $0)";
exit 0;}
[ "$1" ]&& echo "$1"|grep -q '\-h' && usage
set -e

.venv/bin/ruff check p3sw.py
.venv/bin/black p3sw.py && \
.venv/bin/pylint p3sw.py
