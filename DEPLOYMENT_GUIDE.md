# 🚀 Guide de Déploiement Complet - MinePredict

Ce guide explique comment déployer le dashboard sur **Vercel** (frontend) et **Render** (backend).

---

## 📋 Prérequis

✅ Compte GitHub (pour héberger le code)  
✅ Compte Vercel (https://vercel.com - gratuit)  
✅ Compte Render (https://render.com - gratuit)  
✅ Compte Firebase (pour les capteurs temps réel)  
✅ Git installé localement  

---

## **PARTIE 1 : Préparation du Code**

### 1.1 Vérifier la structure du projet

```
projet-machine-learning/
├── frontend/          # React + Vite
│   ├── package.json
│   ├── vite.config.js
│   └── src/
├── backend/           # FastAPI
│   ├── requirements.txt
│   ├── app/
│   └── Dockerfile
└── README.md
```

### 1.2 Créer un `.gitignore` robuste (à la racine)

```
# Python
__pycache__/
*.py[cod]
*.egg-info/
.env
.venv/
venv/
env/

# Node
node_modules/
dist/
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

### 1.3 Créer un fichier `.env.example` (pour documenter les variables)

**À la racine:**
```env
# Backend (Render)
DATABASE_URL=postgresql://user:password@localhost/dbname
FIREBASE_API_KEY=xxx
FIREBASE_DATABASE_URL=https://xxx.firebaseio.com

# Frontend (Vercel)
VITE_API_BASE_URL=https://api.votreapp.com
VITE_FIREBASE_API_KEY=xxx
VITE_FIREBASE_DATABASE_URL=https://xxx.firebaseio.com
```

### 1.4 Pousser le code sur GitHub

```bash
# Si pas encore fait
git init
git add .
git commit -m "Initial commit - ready for deployment"
git remote add origin https://github.com/votre-username/projet-machine-learning.git
git branch -M main
git push -u origin main
```

---

## **PARTIE 2 : Déployer le Backend sur Render**

### 2.1 Préparer le backend pour Render

**Étape A: Créer `backend/runtime.txt`** (spécifier la version Python)
```
3.11
```

**Étape B: Créer `backend/.env.example`**
```env
DATABASE_URL=postgresql://...
FIREBASE_API_KEY=xxx
MODELS_PATH=/models
```

**Étape C: Vérifier/Mettre à jour `backend/requirements.txt`**
```bash
# À jour pour production
python -m pip freeze > backend/requirements.txt
```

### 2.2 Créer le service Render

1. **Aller sur** https://render.com et **s'authentifier avec GitHub**

2. **Créer un nouveau service:**
   - Cliquer sur **"New +"** → **"Web Service"**
   - Sélectionner le repository GitHub
   - Configurer:
     - **Name:** `minepredict-api` (ou votre choix)
     - **Environment:** `Python 3`
     - **Build Command:** 
       ```
       pip install -r backend/requirements.txt
       ```
     - **Start Command:** 
       ```
       cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
       ```

3. **Variables d'environnement** (dans Render dashboard):
   - Cliquer sur **"Environment"** et ajouter:
     ```
     DATABASE_URL = postgresql://... (si utilisé)
     FIREBASE_API_KEY = votre_clé_firebase
     FIREBASE_DATABASE_URL = https://votre-project.firebaseio.com
     MODELS_PATH = /models
     ```

4. **Déployer:**
   - Cliquer sur **"Create Web Service"**
   - Attendre le déploiement (~2-3 min)
   - Récupérer l'URL: `https://minepredict-api.onrender.com`

⚠️ **Important:** Render gratuit met en veille après 15 min d'inactivité. Pour éviter, passer à un plan payant ($7/mois) ou utiliser un "ping" toutes les 10 min.

---

## **PARTIE 3 : Déployer le Frontend sur Vercel**

### 3.1 Préparer le frontend

**Vérifier `frontend/vite.config.js`:**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
```

### 3.2 Déployer sur Vercel

1. **Aller sur** https://vercel.com et **s'authentifier avec GitHub**

2. **Importer le projet:**
   - Cliquer sur **"Add New..."** → **"Project"**
   - Sélectionner le repository
   - Vercel détecte automatiquement Vite

3. **Configurer le déploiement:**
   - **Framework Preset:** `Vite`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm ci` (recommandé)
   - **Root Directory:** `./frontend` (important!)

4. **Variables d'environnement** (avant de cliquer "Deploy"):
   - Cliquer sur **"Environment Variables"** et ajouter:
     ```
     VITE_API_BASE_URL = https://minepredict-api.onrender.com
     VITE_FIREBASE_API_KEY = votre_clé_firebase
     VITE_FIREBASE_AUTH_DOMAIN = votre-project.firebaseapp.com
     VITE_FIREBASE_DATABASE_URL = https://votre-project.firebaseio.com
     VITE_FIREBASE_PROJECT_ID = votre-project-id
     VITE_FIREBASE_STORAGE_BUCKET = votre-project.appspot.com
     VITE_FIREBASE_MESSAGING_SENDER_ID = xxx
     VITE_FIREBASE_APP_ID = xxx
     VITE_FIREBASE_SENSORS_PATH = /sensors/latest
     ```

5. **Déployer:**
   - Cliquer sur **"Deploy"**
   - Attendre la compilation (~1-2 min)
   - URL finale: `https://votre-app.vercel.app`

---

## **PARTIE 4 : Configuration Cross-Domain (CORS)**

### Backend (Render) - Ajouter les CORS

**Fichier: `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Permettre les requêtes du frontend Vercel
allowed_origins = [
    "http://localhost:3000",           # Développement local
    "https://votre-app.vercel.app",     # Production Vercel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... reste du code
```

---

## **PARTIE 5 : Mise à Jour Continue**

### 5.1 Déploiements automatiques

**Les deux plateformes (Vercel + Render) redéploient automatiquement quand vous pushez sur `main`:**

```bash
# Après une modification locale
git add .
git commit -m "feat: add humidity sensor"
git push origin main

# ✅ Vercel et Render redéploient automatiquement
```

### 5.2 Revert rapide (en cas de bug)

**Sur Vercel Dashboard:**
- Aller dans **"Deployments"**
- Trouver le déploiement stable
- Cliquer sur **"..."** → **"Promote to Production"**

**Sur Render Dashboard:**
- Aller dans **"Deploys"**
- Cliquer sur le déploiement précédent → **"Rollback"**

---

## **PARTIE 6 : Monitoring & Dépannage**

### 6.1 Vérifier les logs

**Backend (Render):**
- Dashboard Render → Sélectionner le service
- Cliquer sur **"Logs"** en temps réel

**Frontend (Vercel):**
- Dashboard Vercel → Projet
- Cliquer sur **"Deployments"**
- Voir les logs de build

### 6.2 Problèmes courants

| Problème | Solution |
|----------|----------|
| **Frontend cherche le mauvais API** | Vérifier `VITE_API_BASE_URL` dans Vercel env vars |
| **CORS error** | Ajouter l'URL Vercel à `allowed_origins` du backend |
| **Firebase ne charge pas** | Vérifier les clés Firebase dans `.env` |
| **Build échoue sur Render** | Voir les logs → souvent un `import` manquant |
| **Backend en veille (gratuit Render)** | Upgrader à plan payant ou ajouter un cron ping |

### 6.3 Test post-déploiement

```bash
# Tester l'API
curl https://minepredict-api.onrender.com/health

# Ouvrir le frontend
# https://votre-app.vercel.app

# Vérifier la console (F12) pour les erreurs CORS/Firebase
```

---

## **PARTIE 7 : Optimisations Production**

### 7.1 Frontend - Optimiser les performances

**`frontend/vite.config.js`:**
```javascript
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,        // Pas de sourcemaps en prod
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'charts': ['recharts']
        }
      }
    }
  }
})
```

### 7.2 Backend - Ajouter un health check

**`backend/app/routes/health.py`:**
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "minepredict-api"}
```

### 7.3 Ajouter un `vercel.json` (optionnel)

**`frontend/vercel.json`:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "VITE_API_BASE_URL": "@vite_api_base_url"
  }
}
```

---

## **Résumé des URLs Finales**

| Composant | URL | Plateforme |
|-----------|-----|-----------|
| **Frontend Dashboard** | https://votre-app.vercel.app | Vercel |
| **Backend API** | https://minepredict-api.onrender.com | Render |
| **Documentation API** | https://minepredict-api.onrender.com/docs | Swagger UI |

---

## **Checklist Finale**

- [ ] Code poussé sur GitHub
- [ ] Backend déployé sur Render (API accessible)
- [ ] Frontend déployé sur Vercel (dashboard accessible)
- [ ] Variables d'environnement configurées (API, Firebase)
- [ ] CORS configuré correctement
- [ ] Health check fonctionne
- [ ] Dashboard se charge et reçoit les données
- [ ] Logs consultables (Render + Vercel)

---

**Questions?** Consultez:
- 📖 Vercel Docs: https://vercel.com/docs
- 📖 Render Docs: https://render.com/docs
- 📖 FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
