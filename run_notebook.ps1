#!/usr/bin/env pwsh
# Script PowerShell pour lancer le notebook avec le bon environnement

$PROJECT_ROOT = $PSScriptRoot
$NOTEBOOK_PATH = Join-Path $PROJECT_ROOT "notebooks" "M3_Predictive_Maintenance.ipynb"

Write-Host "Projet root: $PROJECT_ROOT" -ForegroundColor Green
Write-Host "Notebook: $NOTEBOOK_PATH" -ForegroundColor Green

# Vérifier que le notebook existe
if (-not (Test-Path $NOTEBOOK_PATH)) {
    Write-Host "Erreur: Notebook non trouvé à $NOTEBOOK_PATH" -ForegroundColor Red
    exit 1
}

# Vérifier que les packages sont installés
Write-Host "Vérification des dépendances..." -ForegroundColor Yellow
try {
    python -c "import matplotlib, pandas, seaborn, sklearn, xgboost, lightgbm, shap, fastapi, pydantic" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Certaines dépendances manquent. Installation..." -ForegroundColor Yellow
        pip install -r (Join-Path $PROJECT_ROOT "requirements-notebook.txt")
    }
} catch {
    Write-Host "Erreur lors de la vérification des dépendances" -ForegroundColor Red
    exit 1
}

# Vérifier que le kernel est installé
Write-Host "Vérification du kernel Jupyter..." -ForegroundColor Yellow
$kernelCheck = jupyter kernelspec list 2>&1 | Select-String "minepredict"
if (-not $kernelCheck) {
    Write-Host "Installation du kernel MinePredict..." -ForegroundColor Yellow
    python -m ipykernel install --user --name=minepredict --display-name "MinePredict ML"
}

# Lancer Jupyter
Write-Host "Lancement de Jupyter Notebook..." -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Le notebook va s'ouvrir dans votre navigateur." -ForegroundColor Cyan
Write-Host "Sélectionnez le kernel 'MinePredict ML' si demandé." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PROJECT_ROOT
jupyter notebook notebooks/M3_Predictive_Maintenance.ipynb