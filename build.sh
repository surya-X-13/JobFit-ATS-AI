#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
