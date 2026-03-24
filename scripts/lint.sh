#!/usr/bin/env bash
set -euo pipefail

# Run flake8 using the repository .flake8 config (two passes like CI previously did)
flake8 . --config .flake8 --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --config .flake8 --count --exit-zero --statistics

