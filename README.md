# AURORA (formerly System Behavior Analyzer)

AURORA is an AI-powered PC Guardian desktop app with safe diagnostics and optimization workflows.

## Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

Install GUI dependencies:

```bash
python -m pip install -e ".[gui]"
```

## Launch

### AURORA GUI (default module launch)

```bash
python -m aurora
```

### AURORA CLI

```bash
aurora --help
aurora scan
aurora fix-preview
aurora report
aurora gui
```

`python -m aurora --help` also shows CLI help.

## Legacy SBA compatibility

SBA command is still available:

```bash
sba --help
```

## Development

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check src tests
```
