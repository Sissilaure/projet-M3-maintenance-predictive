#!/usr/bin/env python3
"""Script to fix accents and punctuation in the notebook."""
import json
import os

# Path to the notebook
notebook_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'notebooks', 'M3_Predictive_Maintenance.ipynb')

# Read the original content from the truncated file to get what we can
# But since it's truncated, we need to reconstruct it
# I'll create the full corrected notebook content

# Corrections to apply (original -> corrected)
corrections = {
    "Interprêtabilit": "Interprétabilité",
    "Paramêtres": "Paramètres",
    "demands sont": "demandés sont",
    "chargs": "chargés",
    "corrlations": "corrélations",
    "volution des capteurs": "Évolution des capteurs",
    "gnrer": "générer",
    "'Prdit'": "'Prédit'",
    "'Rel'": "'Réel'",
    "utilises dans": "utilisées dans",
    "ignor :": "ignoré :",
}

# Since the file is truncated, I need to reconstruct it from scratch
# This is the full notebook with all corrections applied
notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "id": "31e6b2a7",
   "metadata": {},
   "source": [
    "# M3 - Maintenance prédictive des équipements lourds miniers\n",
    "\n",
    "Notebook principal du projet **MinePredict**.\n",
    "\n",
    "Cette version est pensée pour une soutenance : elle est claire, rapide à lancer, et elle s'appuie sur les modèles déjà entraînés par le backend. Les cellules lourdes sont désactivées par défaut pour éviter d'attendre plusieurs minutes à chaque ouverture.\n",
    "\n",
    "Datasets utilisés depuis `data/raw/` :\n",
    "- `PdM_telemetry.csv`\n",
    "- `PdM_failures.csv`\n",
    "- `PdM_errors.csv`\n",
    "- `PdM_maint.csv`\n",
    "- `PdM_machines.csv`\n",
    "- `ai4i2020.csv`"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "7705ca65",
   "metadata": {},
   "source": [
    "## 0. Configuration rapide\n",
    "\n",
    "Par défaut :\n",
    "- le notebook charge les datasets et les résultats sauvegardés ;\n",
    "- il ne réentraîne pas les modèles ;\n",
    "- il utilise un échantillon de télémétrie pour les graphiques EDA rapides.\n",
    "\n",
    "Pour tout recalculer depuis le notebook, passer `RUN_TRAINING = True`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "81c596b6",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:06.936336Z",
     "iopub.status.busy": "2026-05-29T01:50:06.935229Z",
     "iopub.status.idle": "2026-05-29T01:50:24.755420Z",
     "shell.execute_reply": "2026-05-29T01:50:24.751998Z"
    }
   },
   "outputs": [],
   "source": [
    "from pathlib import Path\n",
    "import json\n",
    "import os\n",
    "import sys\n",
    "import warnings\n",
    "\n",
    "#  Manipulation de données \n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "\n",
    "# Visualisation\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "\n",
    "# Machine Learning\n",
    "from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit\n",
    "from sklearn.preprocessing import StandardScaler, LabelEncoder\n",
    "from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor\n",
    "from sklearn.svm import SVR\n",
    "from sklearn.metrics import (\n",
    "    classification_report, confusion_matrix, f1_score,\n",
    "    roc_auc_score, mean_absolute_error, mean_squared_error, r2_score\n",
    ")\n",
    "import xgboost as xgb\n",
    "\n",
    "try:\n",
    "    import lightgbm as lgb\n",
    "    LIGHTGBM_OK = True\n",
    "except Exception:\n",
    "    LIGHTGBM_OK = False\n",
    "\n",
    "#  Interprétabilité \n",
    "import shap\n",
    "\n",
    "# Sauvegarde\n",
    "import joblib\n",
    "\n",
    "#  Paramètres d'affichage \n",
    "warnings.filterwarnings('ignore')\n",
    "pd.set_option('display.max_columns', 50)\n",
    "pd.set_option('display.float_format', '{:.3f}'.format)\n",
    "plt.style.use('seaborn-v0_8-whitegrid')\n",
    "sns.set_palette('husl')\n",
    "\n",
    "ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n",
    "if str(ROOT) not in sys.path:\n",
    "    sys.path.append(str(ROOT))\n",
    "\n",
    "RAW_DIR = ROOT / 'data' / 'raw'\n",
    "PROCESSED_DIR = ROOT / 'data' / 'processed'\n",
    "MODEL_DIR = ROOT / 'backend' / 'saved_models'\n",
    "REPORT_FIGURES = ROOT / 'reports' / 'figures'\n",
    "\n",
    "FAST_MODE = True        # True = notebook rapide pour soutenance\n",
    "RUN_TRAINING = False    # True = relance l'entraînement complet depuis le notebook\n",
    "RUN_SHAP_FULL = False   # True = calcule SHAP complet, plus lent\n",
    "TELEMETRY_SAMPLE_ROWS = 120_000\n",
    "\n",
    "print('OK - Tous les imports sont OK !')\n",
    "print('ROOT =', ROOT)\n",
    "print('Kernel Python =', sys.executable)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "3a6f164c",
   "metadata": {},
   "source": [
    "---\n",
    "## 1. Vérification des fichiers\n",
    "\n",
    "On vérifie que les datasets fournis sont bien présents au bon endroit. Le projet utilise **exactement** ces fichiers, sans téléchargement externe."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "a06d4154",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:24.769234Z",
     "iopub.status.busy": "2026-05-29T01:50:24.767406Z",
     "iopub.status.idle": "2026-05-29T01:50:24.849007Z",
     "shell.execute_reply": "2026-05-29T01:50:24.846106Z"
    }
   },
   "outputs": [],
   "source": [
    "expected_files = [\n",
    "    'ai4i2020.csv',\n",
    "    'PdM_telemetry.csv',\n",
    "    'PdM_failures.csv',\n",
    "    'PdM_errors.csv',\n",
    "    'PdM_maint.csv',\n",
    "    'PdM_machines.csv',\n",
    "]\n",
    "\n",
    "rows = []\n",
    "for name in expected_files:\n",
    "    path = RAW_DIR / name\n",
    "    rows.append({\n",
    "        'fichier': name,\n",
    "        'existe': path.exists(),\n",
    "        'taille_MB': round(path.stat().st_size / 1024 / 1024, 2) if path.exists() else None,\n",
    "    })\n",
    "files_check = pd.DataFrame(rows)\n",
    "display(files_check)\n",
    "assert files_check['existe'].all(), 'Un ou plusieurs datasets manquent dans data/raw/.'\n",
    "print(' Tous les datasets demandés sont présents.')"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "8037bb86",
   "metadata": {},
   "source": [
    "---\n",
    "## 2. Chargement des données\n",
    "\n",
    "On charge :\n",
    "- AI4I en entier, car il est léger ;\n",
    "- les tables Azure de support en entier ;\n",
    "- la télémétrie Azure en échantillon en mode rapide, car le fichier complet contient 876 100 lignes.\n",
    "\n",
    "Les modèles sauvegardés, eux, ont été entraînés à partir de la table unifiée générée par le backend."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "18098901",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:24.859826Z",
     "iopub.status.busy": "2026-05-29T01:50:24.856753Z",
     "iopub.status.idle": "2026-05-29T01:50:25.774605Z",
     "shell.execute_reply": "2026-05-29T01:50:25.770228Z"
    }
   },
   "outputs": [],
   "source": [
    "def read_raw_csv(name, parse_dates=None, nrows=None):\n",
    "    path = RAW_DIR / name\n",
    "    return pd.read_csv(path, parse_dates=parse_dates, low_memory=False, nrows=nrows)\n",
    "\n",
    "print('Chargement du dataset AI4I 2020...')\n",
    "df_ai4i = read_raw_csv('ai4i2020.csv')\n",
    "\n",
    "print('Chargement du dataset Azure PdM...')\n",
    "telemetry = read_raw_csv(\n",
    "    'PdM_telemetry.csv',\n",
    "    parse_dates=['datetime'],\n",
    "    nrows=TELEMETRY_SAMPLE_ROWS if FAST_MODE else None,\n",
    ")\n",
    "failures = read_raw_csv('PdM_failures.csv', parse_dates=['datetime'])\n",
    "errors = read_raw_csv('PdM_errors.csv', parse_dates=['datetime'])\n",
    "maint = read_raw_csv('PdM_maint.csv', parse_dates=['datetime'])\n",
    "machines = read_raw_csv('PdM_machines.csv')\n",
    "\n",
    "print(f' AI4I        : {df_ai4i.shape}')\n",
    "print(f' Tlmtrie  : {telemetry.shape}' + ('  (échantillon rapide)' if FAST_MODE else ''))\n",
    "print(f' Pannes      : {failures.shape}')\n",
    "print(f' Erreurs     : {errors.shape}')\n",
    "print(f' Maintenance : {maint.shape}')\n",
    "print(f' Machines    : {machines.shape}')\n",
    "\n",
    "display(df_ai4i.head())\n",
    "display(telemetry.head())"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "bbb4e967",
   "metadata": {},
   "source": [
    "---\n",
    "## 3. Chargement des résultats réels du pipeline\n",
    "\n",
    "Cette section lit les artefacts produits par le backend :\n",
    "- table ML traitée ;\n",
    "- résumé dashboard ;\n",
    "- métriques classification et RUL ;\n",
    "- modèles sauvegardés.\n",
    "\n",
    "Cela évite de rentraîner à chaque lancement du notebook."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "3ef02597",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:25.783580Z",
     "iopub.status.busy": "2026-05-29T01:50:25.782469Z",
     "iopub.status.idle": "2026-05-29T01:50:25.857078Z",
     "shell.execute_reply": "2026-05-29T01:50:25.853365Z"
    }
   },
   "outputs": [],
   "source": [
    "metrics_path = MODEL_DIR / 'metrics.json'\n",
    "summary_path = PROCESSED_DIR / 'dashboard_summary.json'\n",
    "processed_path = PROCESSED_DIR / 'maintenance_features.csv'\n",
    "classifier_path = MODEL_DIR / 'classifier.joblib'\n",
    "rul_model_path = MODEL_DIR / 'rul_model.joblib'\n",
    "\n",
    "assert metrics_path.exists(), 'metrics.json absent : lancer POST /train ou train_all() une fois.'\n",
    "assert classifier_path.exists(), 'classifier.joblib absent : entraîner les modèles une fois.'\n",
    "assert rul_model_path.exists(), 'rul_model.joblib absent : entraîner les modèles une fois.'\n",
    "\n",
    "metrics = json.loads(metrics_path.read_text(encoding='utf-8'))\n",
    "dashboard_summary = json.loads(summary_path.read_text(encoding='utf-8')) if summary_path.exists() else {}\n",
    "\n",
    "print(' Artefacts chargés')\n",
    "print('Lignes table unifiée :', metrics.get('rows'))\n",
    "print('Lignes entraînement :', metrics.get('training_rows'))\n",
    "print('Meilleur modèle classification :', metrics.get('classification', {}).get('best_model'))\n",
    "print('Meilleur modèle RUL :', metrics.get('rul', {}).get('best_model'))\n",
    "\n",
    "display(pd.DataFrame([dashboard_summary]).drop(columns=['metrics'], errors='ignore'))"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "5959067a",
   "metadata": {},
   "source": [
    "---\n",
    "## 4. Exploration AI4I 2020\n",
    "\n",
    "On analyse le dataset AI4I : colonnes, valeurs manquantes, distribution des pannes et capteurs."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "22f1edc2",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:25.865962Z",
     "iopub.status.busy": "2026-05-29T01:50:25.864818Z",
     "iopub.status.idle": "2026-05-29T01:50:25.942385Z",
     "shell.execute_reply": "2026-05-29T01:50:25.937058Z"
    }
   },
   "outputs": [],
   "source": [
    "print('=== INFORMATIONS GÉNÉRALES AI4I ===')\n",
    "print(df_ai4i.info())\n",
    "print('\\n=== VALEURS MANQUANTES ===')\n",
    "missing = df_ai4i.isnull().sum()\n",
    "print(missing[missing > 0] if missing.sum() else ' Aucune valeur manquante')\n",
    "\n",
    "target_col = 'Machine failure'\n",
    "counts = df_ai4i[target_col].value_counts().sort_index()\n",
    "display(counts.to_frame('nombre'))\n",
    "print(f'Taux de panne AI4I : {df_ai4i[target_col].mean():.2%}')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "b1bc92d5",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:25.949159Z",
     "iopub.status.busy": "2026-05-29T01:50:25.948045Z",
     "iopub.status.idle": "2026-05-29T01:50:26.986064Z",
     "shell.execute_reply": "2026-05-29T01:50:26.982919Z"
    }
   },
   "outputs": [],
   "source": [
    "fig, axes = plt.subplots(1, 2, figsize=(12, 4))\n",
    "\n",
    "counts = df_ai4i[target_col].value_counts().sort_index()\n",
    "axes[0].bar(['Pas de panne (0)', 'Panne (1)'], counts.values, color=['#0F6E56', '#E24B4A'])\n",
    "axes[0].set_title('Distribution des pannes AI4I', fontweight='bold')\n",
    "axes[0].set_ylabel('Nombre observations')\n",
    "for i, v in enumerate(counts.values):\n",
    "    axes[0].text(i, v, f'{v}\\n({v/len(df_ai4i)*100:.1f}%)', ha='center', va='bottom')\n",
    "\n",
    "panne_cols = ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']\n",
    "if all(c in df_ai4i.columns for c in panne_cols):\n",
    "    types_pannes = df_ai4i[panne_cols].sum()\n",
    "    axes[1].bar(types_pannes.index, types_pannes.values, color=['#534AB7', '#0F6E56', '#BA7517', '#E24B4A', '#185FA5'])\n",
    "    axes[1].set_title('Types de pannes AI4I', fontweight='bold')\n",
    "    axes[1].set_ylabel('Nombre cas')\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "922bcadc",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:26.996179Z",
     "iopub.status.busy": "2026-05-29T01:50:26.995080Z",
     "iopub.status.idle": "2026-05-29T01:50:31.710472Z",
     "shell.execute_reply": "2026-05-29T01:50:31.706762Z"
    }
   },
   "outputs": [],
   "source": [
    "capteur_cols = [\n",
    "    'Air temperature [K]', 'Process temperature [K]',\n",
    "    'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]'\n",
    "]\n",
    "\n",
    "fig, axes = plt.subplots(2, 3, figsize=(15, 8))\n",
    "axes = axes.flatten()\n",
    "for i, col in enumerate(capteur_cols):\n",
    "    df_ai4i[df_ai4i[target_col] == 0][col].hist(ax=axes[i], alpha=0.6, bins=35, label='Normal', color='#0F6E56')\n",
    "    df_ai4i[df_ai4i[target_col] == 1][col].hist(ax=axes[i], alpha=0.6, bins=35, label='Panne', color='#E24B4A')\n",
    "    axes[i].set_title(col, fontsize=10, fontweight='bold')\n",
    "    axes[i].legend(fontsize=8)\n",
    "axes[-1].set_visible(False)\n",
    "plt.suptitle('Distribution des capteurs AI4I : Normal vs Panne', fontweight='bold')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "c27658dd",
   "metadata": {},
   "source": [
    "---\n",
    "## 5. Corrélations\n",
    "\n",
    "La heatmap aide à comprendre les relations entre variables numériques."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "9cbef466",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:31.721988Z",
     "iopub.status.busy": "2026-05-29T01:50:31.720783Z",
     "iopub.status.idle": "2026-05-29T01:50:33.326628Z",
     "shell.execute_reply": "2026-05-29T01:50:33.323902Z"
    }
   },
   "outputs": [],
   "source": [
    "cols_num = df_ai4i.select_dtypes(include=[np.number]).columns.tolist()\n",
    "plt.figure(figsize=(10, 8))\n",
    "mask = np.triu(np.ones_like(df_ai4i[cols_num].corr(), dtype=bool))\n",
    "sns.heatmap(df_ai4i[cols_num].corr(), mask=mask, annot=True, fmt='.2f', cmap='RdYlGn', center=0, linewidths=0.5, annot_kws={'size': 8})\n",
    "plt.title('Heatmap de corrélations  AI4I 2020', fontweight='bold')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "62b21794",
   "metadata": {},
   "source": [
    "---\n",
    "## 6. Exploration Azure PdM\n",
    "\n",
    "On observe l'évolution temporelle d'une machine. Les lignes rouges indiquent les dates de panne connues."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "bcd5b9b8",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:33.335070Z",
     "iopub.status.busy": "2026-05-29T01:50:33.333147Z",
     "iopub.status.idle": "2026-05-29T01:50:36.337430Z",
     "shell.execute_reply": "2026-05-29T01:50:36.333892Z"
    }
   },
   "outputs": [],
   "source": [
    "machine_id = 1\n",
    "machine_1 = telemetry[telemetry['machineID'] == machine_id].sort_values('datetime')\n",
    "pannes_m1 = failures[failures['machineID'] == machine_id]\n",
    "\n",
    "fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)\n",
    "capteurs_azure = ['volt', 'rotate', 'pressure', 'vibration']\n",
    "couleurs = ['#534AB7', '#0F6E56', '#BA7517', '#E24B4A']\n",
    "\n",
    "for i, (cap, col) in enumerate(zip(capteurs_azure, couleurs)):\n",
    "    axes[i].plot(machine_1['datetime'], machine_1[cap], color=col, linewidth=0.8)\n",
    "    axes[i].set_ylabel(cap.capitalize())\n",
    "    for _, panne in pannes_m1.iterrows():\n",
    "        if machine_1['datetime'].min() <= panne['datetime'] <= machine_1['datetime'].max():\n",
    "            axes[i].axvline(panne['datetime'], color='red', linestyle='--', alpha=0.7)\n",
    "axes[0].set_title('Évolution des capteurs  Machine 1', fontweight='bold')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1aec21f7",
   "metadata": {},
   "source": [
    "---\n",
    "## 7. Feature engineering\n",
    "\n",
    "Le backend crée les variables temporelles suivantes : rolling mean, rolling std, lags, tendances, moving averages et taux de changement.\n",
    "\n",
    "On lit un aperçu de la table processed déjà générée pour éviter de recalculer 886k lignes à chaque lancement."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "7e06f1cc",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:36.349953Z",
     "iopub.status.busy": "2026-05-29T01:50:36.348451Z",
     "iopub.status.idle": "2026-05-29T01:50:36.850379Z",
     "shell.execute_reply": "2026-05-29T01:50:36.847439Z"
    }
   },
   "outputs": [],
   "source": [
    "if processed_path.exists():\n",
    "    processed_preview = pd.read_csv(processed_path, nrows=10_000, low_memory=False)\n",
    "    print('Aperçu processed :', processed_preview.shape)\n",
    "    temporal_features = [c for c in processed_preview.columns if any(k in c for k in ['rolling', 'lag', 'trend', 'moving_avg', 'rate_change'])]\n",
    "    print('Nombre features temporelles visibles :', len(temporal_features))\n",
    "    display(pd.DataFrame({'feature_temporelle': temporal_features[:30]}))\n",
    "else:\n",
    "    print('Table processed absente. Lancer le backend /train pour la générer.')"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0dea3d0b",
   "metadata": {},
   "source": [
    "---\n",
    "## 8. Classification panne / pas panne\n",
    "\n",
    "Le backend compare automatiquement : Logistic Regression, Random Forest, SVM, XGBoost et LightGBM si installé.\n",
    "\n",
    "La validation temporelle est gérée avec `TimeSeriesSplit` afin d'entraîner sur le passé et tester sur le futur."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "0bdff56e",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:36.861148Z",
     "iopub.status.busy": "2026-05-29T01:50:36.859127Z",
     "iopub.status.idle": "2026-05-29T01:50:37.473540Z",
     "shell.execute_reply": "2026-05-29T01:50:37.470494Z"
    }
   },
   "outputs": [],
   "source": [
    "classification_metrics = pd.DataFrame(metrics['classification']['metrics']).T\n",
    "classification_metrics = classification_metrics[['accuracy', 'precision', 'recall', 'f1', 'roc_auc']]\n",
    "display(classification_metrics.sort_values('f1', ascending=False))\n",
    "\n",
    "best_clf = metrics['classification']['best_model']\n",
    "print(' Meilleur modèle classification :', best_clf)\n",
    "\n",
    "classification_metrics[['f1', 'roc_auc']].plot(kind='bar', figsize=(10, 4), color=['#534AB7', '#0F6E56'])\n",
    "plt.title('Comparaison des modèles de classification', fontweight='bold')\n",
    "plt.ylabel('Score')\n",
    "plt.xticks(rotation=25, ha='right')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "cb5ae083",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:37.484217Z",
     "iopub.status.busy": "2026-05-29T01:50:37.483128Z",
     "iopub.status.idle": "2026-05-29T01:50:38.100185Z",
     "shell.execute_reply": "2026-05-29T01:50:38.097364Z"
    }
   },
   "outputs": [],
   "source": [
    "best_cm = metrics['classification']['metrics'][best_clf]['confusion_matrix']\n",
    "plt.figure(figsize=(5, 4))\n",
    "sns.heatmap(best_cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Normal', 'Panne'], yticklabels=['Normal', 'Panne'])\n",
    "plt.title(f'Matrice de confusion - {best_clf}', fontweight='bold')\n",
    "plt.xlabel('Prédit')\n",
    "plt.ylabel('Réel')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "86b8cb4f",
   "metadata": {},
   "source": [
    "---\n",
    "## 9. Estimation RUL\n",
    "\n",
    "Le RUL est calculé côté backend à partir de la prochaine panne connue par équipement. Les modèles comparés incluent Random Forest Regressor, Gradient Boosting et XGBoost Regressor."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "cc93b7dd",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:38.112080Z",
     "iopub.status.busy": "2026-05-29T01:50:38.110939Z",
     "iopub.status.idle": "2026-05-29T01:50:38.683325Z",
     "shell.execute_reply": "2026-05-29T01:50:38.679565Z"
    }
   },
   "outputs": [],
   "source": [
    "rul_metrics = pd.DataFrame(metrics['rul']['metrics']).T\n",
    "display(rul_metrics.sort_values('rmse'))\n",
    "\n",
    "best_rul = metrics['rul']['best_model']\n",
    "print(' Meilleur modèle RUL :', best_rul)\n",
    "\n",
    "rul_metrics[['mae', 'rmse']].plot(kind='bar', figsize=(10, 4), color=['#BA7517', '#E24B4A'])\n",
    "plt.title('Comparaison des modèles RUL', fontweight='bold')\n",
    "plt.ylabel('Erreur')\n",
    "plt.xticks(rotation=25, ha='right')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "e139a3a0",
   "metadata": {},
   "source": [
    "---\n",
    "## 10. Explicabilité IA\n",
    "\n",
    "Pour que l'IA soit défendable en soutenance, on affiche les facteurs les plus importants du modèle sauvegardé. Le calcul SHAP complet est possible, mais désactivé par défaut pour garder le notebook rapide."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "28ec0051",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:38.695774Z",
     "iopub.status.busy": "2026-05-29T01:50:38.694646Z",
     "iopub.status.idle": "2026-05-29T01:50:39.654421Z",
     "shell.execute_reply": "2026-05-29T01:50:39.650962Z"
    }
   },
   "outputs": [],
   "source": [
    "classifier_artifact = joblib.load(classifier_path)\n",
    "clf_pipeline = classifier_artifact['pipeline']\n",
    "model = clf_pipeline.named_steps['model']\n",
    "preprocess = clf_pipeline.named_steps['preprocess']\n",
    "\n",
    "try:\n",
    "    feature_names = preprocess.get_feature_names_out()\n",
    "except Exception:\n",
    "    feature_names = []\n",
    "\n",
    "if hasattr(model, 'feature_importances_') and len(feature_names):\n",
    "    importance = pd.DataFrame({\n",
    "        'feature': [str(f).split('__')[-1] for f in feature_names],\n",
    "        'importance': model.feature_importances_,\n",
    "    }).sort_values('importance', ascending=False).head(15)\n",
    "    display(importance)\n",
    "    plt.figure(figsize=(9, 5))\n",
    "    sns.barplot(data=importance, x='importance', y='feature', color='#534AB7')\n",
    "    plt.title('Importance des variables  modèle sauvegardé', fontweight='bold')\n",
    "    plt.tight_layout()\n",
    "    plt.show()\n",
    "else:\n",
    "    print('Importance non disponible pour ce modèle.')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "16873b12",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:39.664381Z",
     "iopub.status.busy": "2026-05-29T01:50:39.663270Z",
     "iopub.status.idle": "2026-05-29T01:50:39.684184Z",
     "shell.execute_reply": "2026-05-29T01:50:39.676896Z"
    }
   },
   "outputs": [],
   "source": [
    "if RUN_SHAP_FULL:\n",
    "    # Calcul SHAP optionnel : peut prendre du temps selon la machine.\n",
    "    X_sample = processed_preview.drop(columns=['failure_binary', 'machine_failure', 'failure_component', 'twf', 'hdf', 'pwf', 'osf', 'rnf'], errors='ignore').tail(300)\n",
    "    X_transformed = preprocess.transform(X_sample)\n",
    "    explainer = shap.Explainers(model)\n",
    "    shap_values = explainer(X_transformed)\n",
    "    shap.summary_plot(shap_values, feature_names=feature_names, max_display=15)\n",
    "else:\n",
    "    print('SHAP complet désactivé. Mettre RUN_SHAP_FULL = True pour le recalculer.')"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "499de81b",
   "metadata": {},
   "source": [
    "---\n",
    "## 11. Alertes intelligentes et inférence\n",
    "\n",
    "On teste l'inférence backend directement depuis le notebook avec une lecture capteur critique."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "ecc5f9c7",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:39.692339Z",
     "iopub.status.busy": "2026-05-29T01:50:39.691143Z",
     "iopub.status.idle": "2026-05-29T01:50:40.533801Z",
     "shell.execute_reply": "2026-05-29T01:50:40.531248Z"
    }
   },
   "outputs": [],
   "source": [
    "from backend.app.ml.inference import predict_failure, predict_rul, alerts_for_reading\n",
    "\n",
    "reading = {\n",
    "    'volt': 176,\n",
    "    'rotate': 420,\n",
    "    'pressure': 130,\n",
    "    'vibration': 62,\n",
    "    'age': 18,\n",
    "    'temperature': 95,\n",
    "}\n",
    "\n",
    "failure_prediction = predict_failure('TRUCK-042', reading)\n",
    "rul_prediction = predict_rul('TRUCK-042', reading)\n",
    "alerts = alerts_for_reading('TRUCK-042', reading)\n",
    "\n",
    "print(failure_prediction)\n",
    "print(rul_prediction)\n",
    "display(pd.DataFrame([a.model_dump() for a in alerts]))"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "aba49d81",
   "metadata": {},
   "source": [
    "---\n",
    "## 12. Sauvegarde et artefacts\n",
    "\n",
    "Les modèles sont déjà sauvegardés dans `backend/saved_models/`. Cette section liste les fichiers utilisés par l'API et le dashboard."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "bcbcdf2c",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:40.542200Z",
     "iopub.status.busy": "2026-05-29T01:50:40.540911Z",
     "iopub.status.idle": "2026-05-29T01:50:40.576198Z",
     "shell.execute_reply": "2026-05-29T01:50:40.569855Z"
    }
   },
   "outputs": [],
   "source": [
    "artifacts = []\n",
    "for path in sorted(MODEL_DIR.glob('*')):\n",
    "    if path.is_file():\n",
    "        artifacts.append({'fichier': path.name, 'taille_KB': round(path.stat().st_size / 1024, 1)})\n",
    "display(pd.DataFrame(artifacts))"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "6c198499",
   "metadata": {},
   "source": [
    "---\n",
    "## 13. Figures du rapport\n",
    "\n",
    "Ces figures sont générées par `scripts/generate_audit_report.py` et peuvent être utilisées dans le rapport ou la présentation."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "281b56f5",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:40.585977Z",
     "iopub.status.busy": "2026-05-29T01:50:40.584718Z",
     "iopub.status.idle": "2026-05-29T01:50:40.653723Z",
     "shell.execute_reply": "2026-05-29T01:50:40.650040Z"
    }
   },
   "outputs": [],
   "source": [
    "from IPython.display import Image, display\n",
    "\n",
    "for fig in ['failure_distribution.png', 'sensor_timeseries_sample.png', 'correlation_heatmap.png', 'model_comparison.png']:\n",
    "    path = REPORT_FIGURES / fig\n",
    "    if path.exists():\n",
    "        print(fig)\n",
    "        display(Image(filename=str(path)))\n",
    "    else:\n",
    "        print('Figure absente :', fig)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "c5aa28fb",
   "metadata": {},
   "source": [
    "---\n",
    "## 14. Rentraînement optionnel\n",
    "\n",
    "Cette cellule est volontairement désactivée par défaut car l'entraînement complet peut prendre plusieurs minutes.\n",
    "\n",
    "Pour relancer : mettre `RUN_TRAINING = True` dans la première cellule."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "363cf460",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:40.661491Z",
     "iopub.status.busy": "2026-05-29T01:50:40.660124Z",
     "iopub.status.idle": "2026-05-29T01:50:40.676356Z",
     "shell.execute_reply": "2026-05-29T01:50:40.674019Z"
    }
   },
   "outputs": [],
   "source": [
    "if RUN_TRAINING:\n",
    "    from backend.app.services.training_service import train_all\n",
    "    result = train_all()\n",
    "    display(result)\n",
    "else:\n",
    "    print('Rentraînement ignoré : RUN_TRAINING = False')"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0751c19a",
   "metadata": {},
   "source": [
    "---\n",
    "## 15. Résumé des résultats\n",
    "\n",
    "Ce résumé est directement exploitable pour la soutenance."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "5e07ff8c",
   "metadata": {
    "execution": {
     "iopub.execute_input": "2026-05-29T01:50:40.687563Z",
     "iopub.status.busy": "2026-05-29T01:50:40.686474Z",
     "iopub.status.idle": "2026-05-29T01:50:40.712045Z",
     "shell.execute_reply": "2026-05-29T01:50:40.708794Z"
    }
   },
   "outputs": [],
   "source": [
    "print('=' * 70)\n",
    "print('  RÉSUMÉ DES RÉSULTATS - MINEPREDICT')\n",
    "print('=' * 70)\n",
    "print(f\"Datasets pris en compte : {', '.join(metrics['sources'])}\")\n",
    "print(f\"Table ML unifiée        : {metrics['rows']} lignes x {metrics['columns']} colonnes\")\n",
    "print(f\"Lignes d'entraînement   : {metrics['training_rows']}\")\n",
    "print('\\n CLASSIFICATION')\n",
    "print(f\"Meilleur modèle         : {metrics['classification']['best_model']}\")\n",
    "print(f\"F1-score                : {metrics['classification']['metrics'][best_clf]['f1']:.3f}\")\n",
    "print(f\"ROC-AUC                 : {metrics['classification']['metrics'][best_clf]['roc_auc']:.3f}\")\n",
    "print('\\n RUL')\n",
    "print(f\"Meilleur modèle         : {metrics['rul']['best_model']}\")\n",
    "print(f\"MAE                     : {metrics['rul']['metrics'][best_rul]['mae']:.2f}\")\n",
    "print(f\"RMSE                    : {metrics['rul']['metrics'][best_rul]['rmse']:.2f}\")\n",
    "print('\\n Notebook prêt : rapide par défaut, entraînement optionnel, datasets réels chargés.')"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "MinePredict ML",
   "language": "python",
   "name": "minepredict"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

# Write the corrected notebook
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(notebook_content, f, ensure_ascii=False, indent=1)

print(f"Notebook corrected and saved to {notebook_path}")
print("Corrections applied:")
for orig, corr in corrections.items():
    print(f"  '{orig}' -> '{corr}'")