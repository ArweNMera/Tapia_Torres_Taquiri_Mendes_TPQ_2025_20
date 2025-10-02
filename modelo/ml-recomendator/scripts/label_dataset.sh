#!/usr/bin/env bash
set -euo pipefail
python -m src.pipeline.label_dataset --in data/raw/surveys --who data/raw/who --out data/interim/children_labeled.csv
