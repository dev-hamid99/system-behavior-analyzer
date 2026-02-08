# Windows quick start (PowerShell)

```powershell
cd system-behavior-analyzer
py -m venv .venv --symlinks
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

Now run:

```powershell
sba --help
sba collect --samples 10
sba train
sba detect --limit 20
```
