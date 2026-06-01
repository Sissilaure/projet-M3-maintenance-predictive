$ErrorActionPreference = "Stop"
if (!(Test-Path ".venv")) {
  python -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
