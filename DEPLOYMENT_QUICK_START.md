# 🚀 Checklist Déploiement Rapide - 10 min

## ✅ Avant de commencer

```bash
# 1. Vérifier que le code est sur GitHub
git status
git push origin main

# 2. Installer Firebase pour le dev (si pas fait)
cd frontend
npm install firebase
```

---

## 🔧 BACKEND - Render (5 min)

### Étape 1: Créer le service
- https://render.com → Sign in with GitHub
- **"New Web Service"**
- Sélectionner votre repo
- **Root Directory:** `/backend` (important!)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Étape 2: Variables d'environnement (dans Render)
```
FRONTEND_URL=https://votre-app.vercel.app
ALLOWED_ORIGINS=https://votre-app.vercel.app,http://localhost:3000
FIREBASE_API_KEY=xxx
FIREBASE_DATABASE_URL=https://xxx.firebaseio.com
APP_ENV=production
```

### Étape 3: Déployer
- Cliquer **"Create Web Service"** et attendre (~3 min)
- **Copier l'URL:** `https://minepredict-api.onrender.com`

---

## 🎨 FRONTEND - Vercel (5 min)

### Étape 1: Importer le projet
- https://vercel.com → Import Project
- Sélectionner votre repo GitHub
- **Root Directory:** `./frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`

### Étape 2: Variables d'environnement (avant de déployer!)
```
VITE_API_BASE_URL=https://minepredict-api.onrender.com
VITE_FIREBASE_API_KEY=xxx
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=https://xxx.firebaseio.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=xxx
VITE_FIREBASE_APP_ID=xxx
VITE_FIREBASE_SENSORS_PATH=/sensors/latest
```

### Étape 3: Déployer
- Cliquer **"Deploy"** et attendre (~2 min)
- **Vous avez une URL:** `https://votre-app.vercel.app`

---

## 🧪 Test Final

```bash
# Vérifier l'API backend
curl https://minepredict-api.onrender.com/health

# Ouvrir le dashboard
# https://votre-app.vercel.app

# Vérifier la console (F12)
# ✅ Pas d'erreurs CORS
# ✅ Données Firebase reçues
```

---

## 📚 Voir aussi

- 📖 Guide complet: **DEPLOYMENT_GUIDE.md**
- 🔗 Settings: **backend/app/config/settings.py**
- 🔗 Main: **backend/app/main.py** (CORS configuré)

---

## ⚡ Conseils Pro

1. **Render gratuit se met en veille** → Upgrader ($7/mois) ou ajouter un ping toutes les 10 min
2. **Mise à jour auto:** Git push → Redéploiement auto Vercel + Render
3. **Rollback rapide:** Vercel/Render Dashboard → Deployments → Choisir ancienne version
4. **Logs:** Render/Vercel Dashboard → Voir les erreurs en temps réel

---

Besoin d'aide? Voir **DEPLOYMENT_GUIDE.md** pour le guide complet! 🎯
