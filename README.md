# Habit Tracker (Don't Miss Two Days)

A small CLI app to log daily habit completions from Todoist and produce a morning report. Supports MOCK and LIVE modes.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill values
export PYTHONPATH=$PWD
python simulate.py
python nightly.py
python report.py
