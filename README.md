\# System Behavior Analyzer (SBA)



A small toolkit to collect system metrics, store them (Parquet + SQLite), and run anomaly detection (IsolationForest).

Includes a CLI (`sba`) and a desktop GUI (`sba gui`).



\## Features



\- Collect system metrics (CPU, memory, disk, network)

\- Store metrics to Parquet + SQLite

\- Train IsolationForest model

\- Detect anomalies

\- Desktop GUI (PySide6)



\## Requirements



\- Python 3.10+ recommended

\- Windows / Linux / macOS



\## Installation (Windows / PowerShell)



```powershell

git clone https://github.com/dev-hamid99/system-behavior-analyzer.git

cd system-behavior-analyzer



python -m venv .venv

\& .\\.venv\\Scripts\\Activate.ps1



pip install -r requirements.txt

pip install -e .



