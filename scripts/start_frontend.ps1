$ErrorActionPreference = "Stop"
Set-Location frontend
npm install
npm run dev -- --host 127.0.0.1 --port 3000
