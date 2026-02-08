# system-behavior-analyzer

Collect system metrics and detect anomalies.

## Setup (local dev)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"
```

## Optional GUI

```bash
pip install -e ".[gui]"
```

## Project layout

- `src/sba/` — package (CLI, collectors, storage, ML, GUI)
- `tests/` — unit/integration tests
- `.github/workflows/` — CI pipeline
- `docs/` — documentation notes

> Note: runtime data/artifacts should go into `data/` (ignored by git).
