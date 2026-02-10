# AURORA

AURORA ist ein AI-gestützter PC-Guardian für Windows-first Desktop Monitoring, Diagnose und sichere Optimierungs-Workflows.

## Kernprinzipien

- **Opt-in Actions**: Jede Änderung hat `preview`, `risk`, `rollback`.
- **Keine stillen Änderungen durch AI**: Copilot schlägt vor, UI bestätigt.
- **Modular**: Scanner, Actions, Advisor, AI, GUI und CLI sind getrennt.
- **Release-orientiert**: Logging, SQLite Audit, Tests und klare Struktur.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

## Quick Start

```bash
aurora --help
aurora scan
aurora fix-preview
aurora report
```

## GUI

```bash
python -m pip install -e ".[gui]"
python -m aurora
```

## Sicherheitsmodell

- Actions sind plugin-artig und implementieren `preview/apply/rollback`.
- `apply()` verlangt explizite Bestätigung.
- Audit Events werden in SQLite gespeichert.

## Entwicklung

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check src/aurora tests
```
