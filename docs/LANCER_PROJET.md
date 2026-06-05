# 🚀 Guide Complet - Lancer le Projet MinePredict

## TABLE DES MATIÈRES
1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Lancer le projet](#lancer)
4. [Vérification](#vérification)
5. [Accès URL](#accès-urls)

---

## ✅ Prérequis

Avant de commencer, assure-toi que tu as :

- **Python 3.11+** installé
  ```bash
  python --version
  ```
  → Doit afficher Python 3.11.x ou plus

- **Node.js 18+** et **npm** installés
  ```bash
  node --version
  npm --version
  ```
  → Doit afficher v18.x ou plus

- **Git** installé (optionnel, déjà présent sur ton PC)

---

## 📥 Installation Complète

### Étape 1 : Ouvrir Terminal PowerShell

**Sur Windows** :
- Ouvre l'Explorateur de fichiers
- Navigue vers : `C:\Users\[tonnom]\Desktop\projet machine-learning`
- Clic droit dans le dossier → **"Ouvrir PowerShell ici"**

OU directement :
```powershell
cd C:\Users\[tonnom]\Desktop\projet\ machine-learning
```

### Étape 2 : Installer Dépendances Backend

```powershell
# Créer environnement virtuel Python
python -m venv .venv

# Activer environnement
.\.venv\Scripts\activate

# Installer dépendances
pip install -r backend/requirements.txt
```

**Expected Output** :
```
Successfully installed fastapi==0.104.1 uvicorn==0.24.0 ...
```

**⚠️ Si tu as une erreur** :
```
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Étape 3 : Installer Dépendances Frontend

```powershell
# Naviguer vers frontend
cd frontend

# Installer packages npm
npm install

# Revenir au root
cd ..
```

**Expected Output** :
```
added 450 packages in 42s
```

**⚠️ Si npm hang** (prend trop long) :
```bash
npm install --legacy-peer-deps
```

### Étape 4 : Vérifier Données

Avant de lancer, assure-toi que tu as les datasets :

```powershell
ls data/raw/
```

**Fichiers requis** :
- `PdM_machines.csv`
- `PdM_telemetry.csv`
- `PdM_failures.csv`
- `PdM_maint.csv`
- `PdM_errors.csv`

❌ Si absent : télécharge les datasets et mets-les dans `data/raw/`

---

## 🎬 Lancer le Projet

### Option 1 : Lancer Backend et Frontend Séparément (RECOMMANDÉ)

#### Terminal 1 : Lancer Backend FastAPI

```powershell
# Dans le dossier root du projet
# Assure-toi que .venv est activé
.\.venv\Scripts\activate

# Lancer backend sur port 8000
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output** :
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

✅ Le backend est lancé. **NE FERME PAS ce terminal.**

#### Terminal 2 : Lancer Frontend Vite

Ouvre un **NOUVEAU terminal PowerShell** dans le même dossier :

```powershell
# Naviguer vers frontend
cd frontend

# Lancer serveur de développement
npm run dev
```

**Expected Output** :
```
Local:        http://localhost:5173/
Press q to quit
```

✅ Le frontend est lancé.

---

### Option 2 : Lancer avec Docker (Pour prod)

Si tu as Docker installé :

```powershell
# Lancer backend et frontend en conteneurs
docker-compose up --build

# Attend ~2 minutes
```

Puis dans browser : `http://localhost:3000`

---

## 🔍 Vérification que Tout Fonctionne

### Vérifier Backend

Ouvre dans le browser :
```
http://localhost:8000/docs
```

Tu dois voir :
- Swagger interface
- 8 endpoints listés : `/train`, `/predict/failure`, `/dashboard/stats`, etc.

### Vérifier Frontend

Ouvre dans le browser :
```
http://localhost:5173/
```

Tu dois voir :
- Page Dashboard avec 8 cartes KPI (Équipements, Critiques, Risque, etc.)
- Graphiques temps réel
- Menu latéral avec pages

---

## 🌐 Accès URLs Complètes

### Frontend (React)

| Page | URL | Fonction |
|------|-----|----------|
| **Dashboard** | `http://localhost:5173/` | KPIs, overview, santé globale |
| **Monitoring** | `http://localhost:5173/#/monitoring` | Table équipements, flux capteurs |
| **Paramètres** | `http://localhost:5173/#/settings` | Bouton "Entraîner modèles" |
| **Alertes** | `http://localhost:5173/#/alerts` | Table alertes intelligentes |
| **Analytics** | `http://localhost:5173/#/analytics` | Feature importance, matrice confusion |
| **Explainability** | `http://localhost:5173/#/explainability` | Explications IA |
| **Historique** | `http://localhost:5173/#/history` | Timeline événements |
| **RUL** | `http://localhost:5173/#/rul` | Estimée durée vie résiduelle |

### Backend (FastAPI)

| Endpoint | URL | Méthode | Fonction |
|----------|-----|---------|----------|
| **API Docs** | `http://localhost:8000/docs` | GET | Swagger interface |
| **OpenAPI** | `http://localhost:8000/openapi.json` | GET | Spec JSON |
| **Health Check** | `http://localhost:8000/health` | GET | Vérifier backend alive |
| **Dashboard Stats** | `http://localhost:8000/dashboard/stats` | GET | KPIs JSON |
| **Train** | `http://localhost:8000/train` | POST | Lancer entraînement |
| **Train Status** | `http://localhost:8000/train/status` | GET | Statut progression |
| **Prédire Panne** | `http://localhost:8000/predict/failure` | POST | Prédiction binaire |
| **Prédire RUL** | `http://localhost:8000/predict/rul` | POST | Estimation cycles |

---

## 📝 Checklist Lancement

- [ ] Python 3.11+ installé
- [ ] Node.js 18+ installé
- [ ] `.venv` créé et activé
- [ ] `pip install -r backend/requirements.txt` réussi
- [ ] `npm install` réussi dans frontend/
- [ ] Données dans `data/raw/` présentes
- [ ] Backend lancé sur `http://localhost:8000`
- [ ] Frontend lancé sur `http://localhost:5173`
- [ ] Dashboard accessible sur `http://localhost:5173`
- [ ] API Docs accessible sur `http://localhost:8000/docs`

---

## 🆘 Troubleshooting

### Erreur : "Port 8000 already in use"

```powershell
# Trouver processus sur port 8000
Get-NetTCPConnection -LocalPort 8000

# Tuer le processus
Stop-Process -Id [PID] -Force

# Relancer
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Erreur : "Port 5173 already in use"

```bash
cd frontend
npm run dev -- --port 5174
```

Puis accède à `http://localhost:5174`

### Erreur : "Module not found"

```powershell
# Vérifier que .venv est activé
.\.venv\Scripts\activate

# Réinstaller
pip install -r backend/requirements.txt
```

### Erreur : "npm ERR! ERESOLVE"

```bash
npm install --legacy-peer-deps
```

### Frontend affiche "Cannot GET /"

Le Vite server doit être lancé. Vérifies que tu vois :
```
Local: http://localhost:5173/
```

Sinon relance `npm run dev`

---

## 🎯 Prochaines Étapes après Lancement

### 1. Charger les Données (première fois)

Vérifier que les CSVs sont dans `data/raw/` :
```powershell
ls data/raw/
```

### 2. Entraîner les Modèles (première fois)

1. Ouvre `http://localhost:5173/#/settings`
2. Clique "Entraîner les modèles"
3. Observe barre progression 0→100%
4. Attend 2-5 minutes
5. Voir résultats JSON

### 3. Voir Prédictions

1. Ouvre `http://localhost:5173/` (Dashboard)
2. Voir KPIs chargés
3. Consulter graphiques

### 4. Tester API

Ouvre `http://localhost:8000/docs` et teste :
- GET `/dashboard/stats`
- POST `/predict/failure` avec JSON

---

## 📚 Documentation Complète

Une fois lancé, consulte :
- **Soutenance** : `docs/GUIDE_SOUTENANCE_COMPLET.md`
- **Arduino** : `docs/ARDUINO_INTEGRATION.md`
- **Installation** : `README_local.md`

---

## ✅ Succès !

Si tu vois :
- ✅ Frontend Dashboard avec données
- ✅ Backend API Docs
- ✅ Pas erreurs rouges

→ **Le projet est lancé correctement !**

🚀 Tu peux maintenant préparer ta soutenance en ayant un système fonctionnel.
