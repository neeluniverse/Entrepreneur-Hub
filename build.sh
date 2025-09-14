#!/usr/bin/env bash
# build.sh
set -o errexit

# Install Python 3.10
pyenv install 3.10.12 --skip-existing
pyenv global 3.10.12

# Install dependencies
pip install -r requirements.txt
