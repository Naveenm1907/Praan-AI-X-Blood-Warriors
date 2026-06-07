"""
Thalassemia Severity Classification Engine
Ported from Colab notebook: thalassemia_no_llm_v3.ipynb

Trains Random Forest classifier + transfusion date regressor on dataset.
Also provides rule-based fallback.
"""
import os
import pickle
import logging
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent / "models"
DATASET_PATH = Path(__file__).parent.parent / "thalassemia_transfusion_10k.csv"
DATASET_CACHE = '/tmp/thalassemia_transfusion_10k.csv'

# S3 config for Lambda deployment
S3_BUCKET = os.getenv('S3_BUCKET', 'praanai')
S3_DATASET_KEY = os.getenv('S3_DATASET_KEY', 'thalassemia_transfusion_10k.csv')

SEVERITY_ORDER = ['No Thalassemia', 'Mild', 'Moderate', 'Moderate-Severe', 'Severe']
SEV_MAP = {s: i for i, s in enumerate(SEVERITY_ORDER)}

# Global state
_models: Optional[Dict] = None


def _get_dataset_path() -> str:
    """Get dataset path - local file or download from S3"""
    if DATASET_PATH.exists():
        return str(DATASET_PATH)

    # Lambda environment: download from S3
    try:
        import boto3
        cache = Path(DATASET_CACHE)
        if not cache.exists():
            logger.info(f"Downloading dataset from s3://{S3_BUCKET}/{S3_DATASET_KEY}")
            s3 = boto3.client('s3')
            s3.download_file(S3_BUCKET, S3_DATASET_KEY, str(cache))
        return str(cache)
    except Exception as e:
        logger.error(f"Failed to download dataset from S3: {e}")
        raise


def _load_dataset() -> pd.DataFrame:
    """Load and preprocess the dataset"""
    dataset_path = _get_dataset_path()
    df = pd.read_csv(dataset_path)
    df['severity_code'] = df['severity'].map(SEV_MAP)

    # Encode categorical columns
    col_sex = None
    for c in ['sex', 'Sex', 'gender', 'Gender']:
        if c in df.columns:
            col_sex = c
            break

    le_sex = None
    if col_sex:
        le_sex = LabelEncoder().fit(df[col_sex].fillna('M'))
        df['sexenc'] = le_sex.transform(df[col_sex].fillna('M'))
    else:
        df['sexenc'] = 0.0

    col_blood = None
    for c in ['bloodgroup', 'blood_group', 'BloodGroup']:
        if c in df.columns:
            col_blood = c
            break

    le_blood = None
    if col_blood:
        le_blood = LabelEncoder().fit(df[col_blood].fillna('O'))
        df['bloodenc'] = le_blood.transform(df[col_blood].fillna('O'))
    else:
        df['bloodenc'] = 0.0

    col_spleen = None
    for c in ['spleenenlargement', 'spleen_enlargement', 'SpleenEnlargement']:
        if c in df.columns:
            col_spleen = c
            break

    le_spleen = None
    if col_spleen:
        le_spleen = LabelEncoder().fit(df[col_spleen].fillna('Normal'))
        df['spleenenc'] = le_spleen.transform(df[col_spleen].fillna('Normal'))
    else:
        df['spleenenc'] = 0.0

    return df, le_sex, le_blood, le_spleen


def _resolve_features(df: pd.DataFrame):
    """Resolve feature column names from dataset"""
    candidate_base = [
        'age', 'weightkg',
        'hbcurrentgdl', 'rbcMul', 'mcvfL', 'mchpg', 'mchcgdl',
        'rdwpct', 'ferritinngml',
        'hbApct', 'hbA2pct', 'hbFpct',
        'mentzerindex',
    ]
    base_features = [c for c in candidate_base if c in df.columns]
    all_features = base_features + ['sexenc', 'bloodenc', 'spleenenc']

    candidate_tf = base_features + [
        'hbposttransfusiongdl', 'hbdroprateperday',
        'hbtransfusionthresholdgdl', 'dayssincelasttransfusion',
        'unitspersession', 'avgtransfusionintervaldays',
    ]
    tf_features = [c for c in candidate_tf if c in df.columns]
    all_tf_features = tf_features + ['sexenc', 'bloodenc', 'spleenenc']

    return all_features, all_tf_features


def train_models():
    """Train severity classifier + transfusion regressor"""
    logger.info("Training ML models from dataset...")

    df, le_sex, le_blood, le_spleen = _load_dataset()
    all_features, all_tf_features = _resolve_features(df)

    logger.info(f"Dataset: {len(df)} rows")
    logger.info(f"Severity distribution: {df['severity'].value_counts().to_dict()}")
    logger.info(f"Features: {all_features}")

    # ── Severity Classifier ──
    X_cls = df[all_features].copy()
    y_cls = df['severity_code'].copy()

    imputer_cls = SimpleImputer(strategy='median')
    X_cls_imp = imputer_cls.fit_transform(X_cls)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X_cls_imp, y_cls, test_size=0.2, random_state=42, stratify=y_cls
    )

    clf = RandomForestClassifier(n_estimators=200, max_depth=12, n_jobs=-1, random_state=42)
    clf.fit(X_tr, y_tr)

    from sklearn.metrics import classification_report
    y_pred_cls = clf.predict(X_te)
    present_codes = sorted(y_cls.unique())
    present_names = [SEVERITY_ORDER[c] for c in present_codes]
    report = classification_report(y_te, y_pred_cls, labels=present_codes, target_names=present_names, zero_division=0)
    logger.info(f"Severity Classifier Report:\n{report}")

    # ── Transfusion Date Regressor ──
    tf_target = None
    for c in ['daysuntilnexttransfusion', 'days_until_next_transfusion', 'nexttransfusiondays']:
        if c in df.columns:
            tf_target = c
            break

    reg = None
    imputer_reg = None
    if tf_target:
        df_tf = df.dropna(subset=[tf_target]).copy()
        X_reg = df_tf[all_tf_features]
        y_reg = df_tf[tf_target]

        imputer_reg = SimpleImputer(strategy='median')
        X_reg_imp = imputer_reg.fit_transform(X_reg)

        X_tr2, X_te2, y_tr2, y_te2 = train_test_split(X_reg_imp, y_reg, test_size=0.2, random_state=42)

        reg = RandomForestRegressor(n_estimators=200, max_depth=14, n_jobs=-1, random_state=42)
        reg.fit(X_tr2, y_tr2)

        from sklearn.metrics import mean_absolute_error, r2_score
        y_pred_reg = reg.predict(X_te2)
        mae = mean_absolute_error(y_te2, y_pred_reg)
        r2 = r2_score(y_te2, y_pred_reg)
        logger.info(f"Transfusion Regressor: MAE={mae:.1f} days, R²={r2:.3f}")

    # ── Save all models ──
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    models_data = {
        'clf': clf,
        'imputer_cls': imputer_cls,
        'all_features': all_features,
        'all_tf_features': all_tf_features,
        'le_sex': le_sex,
        'le_blood': le_blood,
        'le_spleen': le_spleen,
    }

    if reg:
        models_data['reg'] = reg
        models_data['imputer_reg'] = imputer_reg

    with open(MODEL_DIR / "trained_models.pkl", 'wb') as f:
        pickle.dump(models_data, f)

    logger.info(f"Models saved to {MODEL_DIR / 'trained_models.pkl'}")
    return models_data


def load_models() -> Dict:
    """Load trained models, train if not found"""
    global _models
    if _models is not None:
        return _models

    model_path = MODEL_DIR / "trained_models.pkl"

    # Try local file first
    if model_path.exists():
        with open(model_path, 'rb') as f:
            _models = pickle.load(f)
        logger.info("Loaded trained models from disk")
        return _models

    # Lambda environment: try downloading from S3
    try:
        import boto3
        cache_path = Path('/tmp/trained_models.pkl')
        if not cache_path.exists():
            logger.info(f"Downloading model from s3://{S3_BUCKET}/trained_models.pkl")
            s3 = boto3.client('s3')
            s3.download_file(S3_BUCKET, 'trained_models.pkl', str(cache_path))
        with open(cache_path, 'rb') as f:
            _models = pickle.load(f)
        logger.info("Loaded trained models from S3 cache")
        return _models
    except Exception as e:
        logger.warning(f"Failed to download from S3: {e}")

    # Fall back to training
    logger.info("No saved models found, training...")
    _models = train_models()
    return _models


def rule_severity(params: Dict) -> str:
    """
    Rule-based severity classification (clinical scoring).
    Accepts both short names and dataset column names.
    """
    score = 0
    hb = params.get('hb') or params.get('hbcurrentgdl') or params.get('hb_level')
    hbA2 = params.get('hbA2') or params.get('hbA2pct') or params.get('hb_a2')
    hbF = params.get('hbF') or params.get('hbFpct') or params.get('hb_f')
    mcv = params.get('mcv') or params.get('mcvfL') or params.get('mcv_level')
    mch = params.get('mch') or params.get('mchpg') or params.get('mch_level')
    ferritin = params.get('ferritin') or params.get('ferritinngml') or params.get('ferritin_level')
    result = (params.get('resulttext') or params.get('ocr_text') or '').upper()

    # Lab text shortcut
    if 'NEGATIVE' in result and ('BETA THALASSEMIA' in result or 'THALASSAEMIA' in result):
        return 'No Thalassemia'

    if hb is not None:
        if hb < 5:
            score += 4
        elif hb < 7:
            score += 2
        elif hb < 9:
            score += 1
    if hbF is not None:
        if hbF > 70:
            score += 4
        elif hbF > 40:
            score += 2
        elif hbF > 10:
            score += 1
    if hbA2 is not None:
        if hbA2 > 7:
            score += 2
        elif hbA2 > 3.9:
            score += 1
    if mcv is not None and mcv < 70:
        score += 1
    if mch is not None and mch < 22:
        score += 1
    if ferritin is not None and ferritin > 1000:
        score += 1

    if score >= 8:
        return 'Severe'
    elif score >= 5:
        return 'Moderate-Severe'
    elif score >= 3:
        return 'Moderate'
    elif score >= 1:
        return 'Mild'
    else:
        return 'No Thalassemia'


def ml_severity(params: Dict) -> Dict:
    """
    ML-based severity classification using trained Random Forest.
    """
    models = load_models()
    clf = models['clf']
    imputer = models['imputer_cls']
    features = models['all_features']
    le_sex = models.get('le_sex')

    # Build feature row
    row = {f: np.nan for f in features}

    feature_mapping = {
        'hbcurrentgdl': params.get('hb') or params.get('hb_level'),
        'rbcMul': params.get('rbc') or params.get('rbc_count'),
        'mcvfL': params.get('mcv') or params.get('mcv_level'),
        'mchpg': params.get('mch') or params.get('mch_level'),
        'mchcgdl': params.get('mchc') or params.get('mchc_level'),
        'rdwpct': params.get('rdw') or params.get('rdw_pct'),
        'ferritinngml': params.get('ferritin') or params.get('ferritin_level'),
        'hbApct': params.get('hbA') or params.get('hb_a'),
        'hbA2pct': params.get('hbA2') or params.get('hb_a2'),
        'hbFpct': params.get('hbF') or params.get('hb_f'),
        'age': params.get('age') or params.get('patientage'),
    }

    for col_name, val in feature_mapping.items():
        if col_name in row and val is not None:
            row[col_name] = float(val)

    # Encode sex
    sv = params.get('patientsex') or params.get('sex')
    if le_sex and sv and sv in list(le_sex.classes_):
        row['sexenc'] = float(le_sex.transform([sv])[0])
    else:
        row['sexenc'] = 0.0

    row['bloodenc'] = 0.0
    row['spleenenc'] = 0.0

    # Mentzer index
    mcv_val = row.get('mcvfL')
    rbc_val = row.get('rbcMul', 0)
    if 'mentzerindex' in row and mcv_val == mcv_val and rbc_val and rbc_val != 0:
        row['mentzerindex'] = mcv_val / rbc_val

    X_single = pd.DataFrame([row], columns=features)
    X_single_imp = imputer.transform(X_single)

    ml_sev_code = clf.predict(X_single_imp)[0]
    severity = SEVERITY_ORDER[ml_sev_code]

    result = {'severity': severity, 'confidence': 0.0, 'probabilities': {}}

    try:
        proba = clf.predict_proba(X_single_imp)[0]
        labels = [SEVERITY_ORDER[c] for c in clf.classes_]
        result['confidence'] = float(max(proba))
        result['probabilities'] = {lab: round(float(pr), 3) for lab, pr in zip(labels, proba)}
    except Exception:
        pass

    return result


def classify_severity(params: Dict, use_ml: bool = True) -> Dict:
    """
    Classify severity using both rule-based and ML methods.
    """
    rule_sev = rule_severity(params)

    result = {
        'rule_severity': rule_sev,
        'ml_severity': None,
        'confidence': None,
        'method': 'rule',
    }

    if use_ml:
        try:
            ml_result = ml_severity(params)
            result['ml_severity'] = ml_result['severity']
            result['confidence'] = ml_result['confidence']
            result['probabilities'] = ml_result.get('probabilities', {})
            result['method'] = 'both'
        except Exception as e:
            logger.warning(f"ML classification failed: {e}")

    return result


def predict_transfusion_date(params: Dict) -> Optional[int]:
    """Predict days until next transfusion using trained regressor"""
    models = load_models()
    reg = models.get('reg')
    if reg is None:
        return None

    imputer = models['imputer_reg']
    features = models['all_tf_features']
    le_sex = models.get('le_sex')

    row = {f: np.nan for f in features}

    feature_mapping = {
        'hbcurrentgdl': params.get('hb') or params.get('hb_level'),
        'rbcMul': params.get('rbc') or params.get('rbc_count'),
        'mcvfL': params.get('mcv') or params.get('mcv_level'),
        'mchpg': params.get('mch') or params.get('mch_level'),
        'mchcgdl': params.get('mchc') or params.get('mchc_level'),
        'rdwpct': params.get('rdw') or params.get('rdw_pct'),
        'ferritinngml': params.get('ferritin') or params.get('ferritin_level'),
        'hbApct': params.get('hbA') or params.get('hb_a'),
        'hbA2pct': params.get('hbA2') or params.get('hb_a2'),
        'hbFpct': params.get('hbF') or params.get('hb_f'),
        'age': params.get('age') or params.get('patientage'),
    }

    for col_name, val in feature_mapping.items():
        if col_name in row and val is not None:
            row[col_name] = float(val)

    sv = params.get('patientsex') or params.get('sex')
    if le_sex and sv and sv in list(le_sex.classes_):
        row['sexenc'] = float(le_sex.transform([sv])[0])
    else:
        row['sexenc'] = 0.0

    row['bloodenc'] = 0.0
    row['spleenenc'] = 0.0

    mcv_val = row.get('mcvfL')
    rbc_val = row.get('rbcMul', 0)
    if 'mentzerindex' in row and mcv_val == mcv_val and rbc_val and rbc_val != 0:
        row['mentzerindex'] = mcv_val / rbc_val

    X_single = pd.DataFrame([row], columns=features)
    X_single_imp = imputer.transform(X_single)

    days = reg.predict(X_single_imp)[0]
    return max(0, round(days))


# Train on import if no saved model
load_models()
