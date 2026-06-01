#!/usr/bin/env python
"""
Script to run the M3_Predictive_Maintenance.ipynb notebook from the command line.
This script sets up the proper Python path and executes the notebook.
"""
from pathlib import Path
import sys

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# Set the notebooks directory as current working directory
import os
os.chdir(Path(__file__).parent)

print(f"Project root: {ROOT}")
print(f"Current directory: {Path.cwd()}")

# Now import and run the notebook cells
from pathlib import Path as P
import json
import sys as _sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Setup path like the notebook does
ROOT = P.cwd().parent if P.cwd().name == "notebooks" else P.cwd()
_sys.path.append(str(ROOT))

print("Importing backend modules...")
from backend.app.config.settings import get_settings
from backend.app.ml.preprocessing import load_raw_datasets, clean_dataframe, split_features_target
from backend.app.ml.feature_engineering import add_time_features, add_temporal_features, calculate_rul
from backend.app.ml.classification import train_classifiers
from backend.app.ml.rul_model import train_rul_models
from backend.app.ml.explainability import shap_summary_payload, top_feature_factors
from backend.app.services.training_service import train_all, load_metrics, select_training_rows
from backend.app.ml.inference import predict_failure, predict_rul, alerts_for_reading

print("All imports successful!")

# Initialize settings
settings = get_settings()
settings.data_raw_dir = ROOT / "data" / "raw"
settings.data_processed_dir = ROOT / "data" / "processed"
settings.model_dir = ROOT / "backend" / "saved_models"
settings.training_max_rows = 30000

RAW_DIR = settings.data_raw_dir
PROCESSED_PATH = settings.data_processed_dir / "maintenance_features.csv"
METRICS_PATH = settings.model_dir / "metrics.json"
print(f"ROOT: {ROOT}")

# Test loading data
print("\nLoading datasets...")
bundle = load_raw_datasets(RAW_DIR)
print(f"Sources: {bundle.source_files}")
print(f"Shape brute unifiée: {bundle.frame.shape}")
print(f"Cible: {bundle.target_column}")
print(f"Temps: {bundle.time_column}")
print(f"Équipement: {bundle.equipment_column}")
print(bundle.frame.head())

print("\n[OK] Notebook setup successful! All imports and data loading work correctly.")
print("\nTo run the full notebook interactively:")
print("  jupyter notebook notebooks/M3_Predictive_Maintenance.ipynb")
print("  or")
print("  jupyter lab notebooks/M3_Predictive_Maintenance.ipynb")