# System Behavior Analyzer (SBA)

Collect system metrics (CPU/RAM/Disk/Network) with `psutil`, persist them to **SQLite** + **Parquet**, and detect anomalies using **IsolationForest**.

## Quick start

### 1) Install (recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

Check:

```bash
sba --help
```

### 2) Collect data

Collect 60 samples (about 5 minutes at the default 5s interval):

```bash
sba collect --samples 60
```

Outputs:
- `data/metrics.sqlite`
- `data/metrics.parquet`

### 3) Train

```bash
sba train
```

Model output:
- `models/isoforest.joblib`

### 4) Detect anomalies

```bash
sba detect --limit 20
```

## Run as a module

This also works:

```bash
python -m sba --help
```

## Optional: GUI (Guardian)

GUI is optional and not installed by default.

```bash
python -m pip install -e ".[gui]"
```

Launch GUI directly as a module:

```bash
python -m sba.guardian_gui
```

Or launch via CLI command:

```bash
sba gui
```

## Development

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check .
mypy src
```
