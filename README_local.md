# MinePredict - Maintenance prédictive des équipements lourds miniers

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![React](https://img.shields.io/badge/React-Vite-61dafb)
![ML](https://img.shields.io/badge/ML-Predictive%20Maintenance-orange)
![Status](https://img.shields.io/badge/status-academic%20ready-success)

MinePredict est un projet full stack de Machine Learning pour prédire les pannes, estimer la durée de vie résiduelle (RUL), générer des alertes intelligentes et expliquer les décisions de l'IA sur des équipements lourds miniers.

## Objectifs

- Prédire panne / pas panne avec plusieurs modèles supervisés.
- Estimer le RUL à partir de signaux capteurs et d'une validation temporelle.
- Surveiller camions-benne, foreuses, concasseurs et machines industrielles.
- Fournir une API FastAPI et un dashboard React moderne.
- Expliquer les prédictions avec importance de variables et SHAP.

## Architecture

```text
backend/                 API FastAPI, services et pipeline ML
frontend/                Interface React + Vite + Tailwind
notebooks/               Notebook académique principal
data/raw/                Datasets fournis uniquement
data/processed/          Données transformées
models/                  Artefacts ML exportables
reports/                 Rapport IMRAD et figures
docs/                    Présentation et plan oral
tests/                   Tests unitaires, API et ML
screenshots/             Captures pour GitHub/soutenance
```

## Datasets

Le projet utilise uniquement les fichiers placés dans `data/raw/` :

- Microsoft Azure Predictive Maintenance
- AI4I 2020 Predictive Maintenance Dataset

Le pipeline détecte automatiquement les colonnes de panne, temps, équipement et capteurs. Aucun téléchargement externe n'est effectué.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend\requirements.txt
pip install -r requirements-notebook.txt
```

```powershell
cd frontend
npm install
```

## Lancement

Backend :

```powershell
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend :

```powershell
cd frontend
npm run dev
```

Le frontend est disponible sur `http://localhost:3000`.

Docker :

```powershell
docker compose up --build
```

## API

- `GET /health`
- `POST /predict/failure`
- `POST /predict/rul`
- `GET /alerts`
- `POST /alerts`
- `GET /metrics`
- `GET /dashboard/stats`
- `GET /equipment/{id}`
- `POST /train`

Documentation interactive : `http://localhost:8000/docs`

## Modèles ML

Classification :

- Logistic Regression
- Random Forest
- XGBoost
- LightGBM
- SVM

Régression RUL :

- Random Forest Regressor
- XGBoost Regressor
- Gradient Boosting
- Extension pédagogique prévue pour LSTM léger quand les séquences par équipement sont longues.

## Validation

La validation utilise `TimeSeriesSplit` afin que l'entraînement apprenne sur le passé et que le test évalue le futur. Cette approche limite les fuites de données, point critique en maintenance prédictive.

## Dashboard

Le frontend contient :

- Dashboard principal
- Monitoring équipements
- Alertes intelligentes
- Estimation RUL
- Analytics
- Explicabilité IA
- Historique
- Paramètres

## Workflow Git conseillé

```powershell
git checkout -b feature/minepredict
git add .
git commit -m "Initial full stack predictive maintenance project"
git push origin feature/minepredict
```

## Roadmap

- Ajouter authentification et rôles maintenance / data science.
- Stocker les mesures temps réel dans PostgreSQL ou TimescaleDB.
- Ajouter ingestion Kafka/MQTT pour capteurs industriels.
- Déployer backend et frontend sur cloud.
- Ajouter suivi MLflow et monitoring de drift.

## Auteurs

Projet académique M3 - Maintenance prédictive des équipements lourds miniers.
