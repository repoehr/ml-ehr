"""Helpers for loading original notebook functions and preparing tutorial inputs."""
import ast
import gc
import json
from functools import reduce
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, roc_curve, precision_score
from sklearn.metrics import roc_auc_score, average_precision_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def notebook_functions(filename, names):
    """Load only named functions; do not run notebook paths, imports or cells."""
    notebook = json.loads((ROOT / filename).read_text())
    namespace = dict(np=np, pd=pd, gc=gc, reduce=reduce, tqdm=tqdm,
                     roc_auc_score=roc_auc_score, average_precision_score=average_precision_score)
    found = set()
    for cell in notebook['cells']:
        if cell['cell_type'] != 'code':
            continue
        source = ''.join(line for line in ''.join(cell['source']).splitlines(keepends=True)
                         if not line.lstrip().startswith(('%', '!')))
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
        if nodes:
            exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec'), namespace)
            found.update(n.name for n in nodes)
    if found != set(names):
        raise RuntimeError(f'Missing notebook functions: {set(names)-found}')
    return namespace


def prepare_features(X, demo):
    """Convert cutoff dates to age and append explicitly coded demographics."""
    X = X.copy()
    X['age_at_prediction_window'] = (
        X['age_at_prediction_window'] - X.patid.map(demo.birth_date)).dt.days / 365.25
    # Categories are predefined for this synthetic example, not learned from test subjects.
    categories = {
        'sex': ['Female', 'Male'],
        'race': ['White', 'Black or African American', 'Asian', 'Other'],
        'ethnicity': ['Not Hispanic or Latino', 'Hispanic or Latino'],
    }
    for field, levels in categories.items():
        values = X.patid.map(demo[field])
        for level in levels[1:]:
            X[f'{field}_{level}_demographic'] = (values == level).astype(int)
    return X


def feature_dictionary(columns):
    definitions = {
        '401.1_dx': 'Essential hypertension (Phecode 401.1)',
        '250.2_dx': 'Type 2 diabetes (Phecode 250.2)',
        '6809_rx': 'Metformin ingredient (RxNorm 6809)',
        '29046_rx': 'Lisinopril ingredient (RxNorm 29046)',
        '83367_rx': 'Atorvastatin ingredient (RxNorm 83367)',
        'age_at_prediction_window': 'Age in years at the prediction cutoff',
    }
    rows = []
    for c in columns:
        description = definitions.get(c, c.replace('_', ' '))
        rows.append([c, 'age_years' if c == 'age_at_prediction_window' else 'binary_indicator', description])
    return pd.DataFrame(rows, columns=['feature', 'type', 'description'])


def retrain_functions():
    functions = notebook_functions('evaluation_retrain_parad.ipynb', [
        'preprocess', 'build_RF_model', 'evaluate_params', 'calculate_metrics',
        'ppv_sensitivity', 'evaluate_ensemble_model'])
    functions.update(RandomForestClassifier=RandomForestClassifier,
                     StandardScaler=StandardScaler, f1_score=f1_score,
                     roc_curve=roc_curve, precision_score=precision_score)
    # Original RF functions predict with arrays after fitting with named columns.
    # Suppress only this known feature-name warning; preserve other warnings.
    warnings.filterwarnings(
        "ignore", message="X does not have valid feature names, but RandomForestClassifier was fitted with feature names",
        category=UserWarning)
    return functions


def toy_rf_candidates():
    return [dict(n_estimators=50, max_depth=3, min_samples_split=5, max_features='sqrt'),
            dict(n_estimators=100, max_depth=6, min_samples_split=5, max_features='sqrt')]

