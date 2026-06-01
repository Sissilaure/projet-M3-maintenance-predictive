@echo off
REM Script batch pour lancer le notebook avec le bon environnement

set PROJECT_ROOT=%~dp0
set NOTEBOOK_PATH=%PROJECT_ROOT%notebooks\M3_Predictive_Maintenance.ipynb

echo Projet root: %PROJECT_ROOT%
echo Notebook: %NOTEBOOK_PATH%

REM Vérifier que le notebook existe
if not exist "%NOTEBOOK_PATH%" (
    echo Erreur: Notebook non trouve a %NOTEBOOK_PATH%
    exit /b 1
)

REM Vérifier que les packages sont installés
echo Verification des dependances...
python -c "import matplotlib, pandas, seaborn, sklearn, xgboost, lightgbm, shap, fastapi, pydantic" 2>nul
if errorlevel 1 (
    echo Certaines dependances manquent. Installation...
    pip install -r "%PROJECT_ROOT%requirements-notebook.txt"
)

REM Vérifier que le kernel est installé
echo Verification du kernel Jupyter...
jupyter kernelspec list | findstr minepredict >nul
if errorlevel 1 (
    echo Installation du kernel MinePredict...
    python -m ipykernel install --user --name=minepredict --display-name "MinePredict ML"
)

REM Lancer Jupyter
echo.
echo ============================================
echo Le notebook va s'ouvrir dans votre navigateur.
echo Selectionnez le kernel 'MinePredict ML' si demande.
echo ============================================
echo.

cd /d "%PROJECT_ROOT%"
jupyter notebook notebooks\M3_Predictive_Maintenance.ipynb