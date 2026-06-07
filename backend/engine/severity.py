"""
Thalassemia Severity Classification Engine
Ported from Colab notebook: thalassemia_no_llm_v3.ipynb

Trains Random Forest classifier + transfusion date regressor on dataset.
Also provides rule-based fallback.

Column names match the actual CSV:
  hb_current_g_dl, rbc_M_ul, mcv_fL, mch_pg, mchc_g_dl,
  rdw_pct, ferritin_ng_ml, hb_A_pct, hb_A2_pct, hb_F_pct,
  mentzer_index, weight_kg,
  hb_post_transfusion_g_dl, hb_drop_rate_per_day,
  hb_transfusion_threshold_g_dl, days_since_last_transfusion,
  units_per_session, avg_transfusion_interval_days,
  days_until_next_transfusion
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
    dataset_path = _get_dataset_path()
    df = pd.read_csv(dataset_path)
    df = pd.read_csv(DATASET_PATH)
    df['severity_code'] = df['severity'].map(SEV_MAP)

    # Compute mentzer_index if not present
    if 'mentzer_index' not in df.columns:
        if 'mcv_fL' in df.columns and 'rbc_M_ul' in df.columns:
            df['mentzer_index'] = df['mcv_fL'] / df['rbc_M_ul'].replace(0, np.nan)

    # ── Sex encoder ──────────────────────────────────────────────────────────
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

    # ── Blood group encoder ───────────────────────────────────────────────────
    col_blood = None
    for c in ['blood_group', 'bloodgroup', 'BloodGroup', 'blood group', 'ABO']:
        if c in df.columns:
            col_blood = c
            break

    le_blood = None
    if col_blood:
        le_blood = LabelEncoder().fit(df[col_blood].fillna('O'))
        df['bloodenc'] = le_blood.transform(df[col_blood].fillna('O'))
    else:
        df['bloodenc'] = 0.0

    # ── Spleen encoder ────────────────────────────────────────────────────────
    col_spleen = None
    for c in ['spleen_enlargement', 'spleenenlargement', 'SpleenEnlargement',
              'spleen', 'spleensize', 'spleenstatus']:
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
    """
    Resolve feature column names from dataset.
    Uses the ACTUAL CSV column names (snake_case).
    """
    # Base clinical features — same names as CSV
    candidate_base = [
        'age', 'weight_kg',
        'hb_current_g_dl', 'rbc_M_ul', 'mcv_fL', 'mch_pg', 'mchc_g_dl',
        'rdw_pct', 'ferritin_ng_ml',
        'hb_A_pct', 'hb_A2_pct', 'hb_F_pct',
        'mentzer_index',
    ]
    base_features = [c for c in candidate_base if c in df.columns]
    all_features = base_features + ['sexenc', 'bloodenc', 'spleenenc']

    # Extended features for transfusion date regression
    candidate_tf = base_features + [
        'hb_post_transfusion_g_dl',
        'hb_drop_rate_per_day',
        'hb_transfusion_threshold_g_dl',
        'days_since_last_transfusion',
        'units_per_session',
        'avg_transfusion_interval_days',
    ]
    tf_features = [c for c in candidate_tf if c in df.columns]
    all_tf_features = tf_features + ['sexenc', 'bloodenc', 'spleenenc']

    return all_features, all_tf_features


def train_models():
    """Train severity classifier + transfusion regressor using correct CSV columns."""
    logger.info("Training ML models from dataset...")

    df, le_sex, le_blood, le_spleen = _load_dataset()
    all_features, all_tf_features = _resolve_features(df)

    logger.info(f"Dataset: {len(df)} rows")
    logger.info(f"Severity distribution: {df['severity'].value_counts().to_dict()}")
    logger.info(f"Classification features ({len(all_features)}): {all_features}")
    logger.info(f"Regression features ({len(all_tf_features)}): {all_tf_features}")

    # ── Severity Classifier ──────────────────────────────────────────────────
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

    # ── Transfusion Date Regressor ───────────────────────────────────────────
    tf_target = None
    for c in ['days_until_next_transfusion', 'daysuntilnexttransfusion', 'nexttransfusiondays']:
        if c in df.columns:
            tf_target = c
            break

    reg = None
    imputer_reg = None
    if tf_target:
        df_tf = df.dropna(subset=[tf_target]).copy()
        logger.info(f"Transfusion regression training rows: {len(df_tf)}")
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
    else:
        logger.warning("No transfusion target column found — skipping regressor training")

    # ── Save all models ──────────────────────────────────────────────────────
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
    """Load trained models, train if not found."""
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
    Accepts short names, CSV column names, or API field names.
    """
    score = 0
    hb      = params.get('hb') or params.get('hb_current_g_dl') or params.get('hb_level')
    hbA2    = params.get('hbA2') or params.get('hb_A2_pct') or params.get('hb_a2')
    hbF     = params.get('hbF') or params.get('hb_F_pct') or params.get('hb_f')
    mcv     = params.get('mcv') or params.get('mcv_fL') or params.get('mcv_level')
    mch     = params.get('mch') or params.get('mch_pg') or params.get('mch_level')
    ferritin = params.get('ferritin') or params.get('ferritin_ng_ml') or params.get('ferritin_level')
    result  = (params.get('resulttext') or params.get('ocr_text') or '').upper()

    # Lab text shortcut
    if 'NEGATIVE' in result and ('BETA THALASSEMIA' in result or 'THALASSAEMIA' in result):
        return 'No Thalassemia'

    if hb is not None:
        if hb < 5:   score += 4
        elif hb < 7: score += 2
        elif hb < 9: score += 1
    if hbF is not None:
        if hbF > 70:   score += 4
        elif hbF > 40: score += 2
        elif hbF > 10: score += 1
    if hbA2 is not None:
        if hbA2 > 7:    score += 2
        elif hbA2 > 3.9: score += 1
    if mcv is not None and mcv < 70:       score += 1
    if mch is not None and mch < 22:       score += 1
    if ferritin is not None and ferritin > 1000: score += 1

    if score >= 8:   return 'Severe'
    elif score >= 5: return 'Moderate-Severe'
    elif score >= 3: return 'Moderate'
    elif score >= 1: return 'Mild'
    else:            return 'No Thalassemia'


def _build_feature_row(params: Dict, features: list, le_sex) -> Dict:
    """
    Build a feature row dict from params, mapping all alias names to CSV column names.
    """
    row = {f: np.nan for f in features}

    # Map from short/API names → actual CSV column names
    feature_mapping = {
        'hb_current_g_dl':              params.get('hb')         or params.get('hb_level'),
        'rbc_M_ul':                     params.get('rbc')        or params.get('rbc_count'),
        'mcv_fL':                       params.get('mcv')        or params.get('mcv_level'),
        'mch_pg':                       params.get('mch')        or params.get('mch_level'),
        'mchc_g_dl':                    params.get('mchc')       or params.get('mchc_level'),
        'rdw_pct':                      params.get('rdw')        or params.get('rdw_pct'),
        'ferritin_ng_ml':               params.get('ferritin')   or params.get('ferritin_level'),
        'hb_A_pct':                     params.get('hbA')        or params.get('hb_a_pct'),
        'hb_A2_pct':                    params.get('hbA2')       or params.get('hb_a2'),
        'hb_F_pct':                     params.get('hbF')        or params.get('hb_f'),
        'age':                          params.get('age')        or params.get('patientage'),
        'weight_kg':                    params.get('weight_kg'),
        # Transfusion-related
        'hb_post_transfusion_g_dl':     params.get('hb_post_transfusion'),
        'hb_drop_rate_per_day':         params.get('hb_drop_rate_per_day'),
        'hb_transfusion_threshold_g_dl': params.get('hb_transfusion_threshold'),
        'days_since_last_transfusion':  params.get('days_since_last_transfusion'),
        'units_per_session':            params.get('units_per_session'),
        'avg_transfusion_interval_days': params.get('avg_transfusion_interval_days'),
    }

    for col_name, val in feature_mapping.items():
        if col_name in row and val is not None:
            row[col_name] = float(val)

    # Encode sex
    sv = params.get('patientsex') or params.get('sex') or params.get('gender')
    if le_sex and sv and sv in list(le_sex.classes_):
        row['sexenc'] = float(le_sex.transform([sv])[0])
    else:
        row['sexenc'] = 0.0

    # Blood group / spleen (default 0)
    row['bloodenc'] = 0.0
    row['spleenenc'] = 0.0

    # Compute Mentzer index if possible
    mcv_val = row.get('mcv_fL')
    rbc_val = row.get('rbc_M_ul', 0) or 0
    if 'mentzer_index' in row and mcv_val == mcv_val and rbc_val and rbc_val != 0:
        row['mentzer_index'] = mcv_val / rbc_val

    return row


def ml_severity(params: Dict) -> Dict:
    """
    ML-based severity classification using trained Random Forest.
    """
    models = load_models()
    clf     = models['clf']
    imputer = models['imputer_cls']
    features = models['all_features']
    le_sex  = models.get('le_sex')

    row = _build_feature_row(params, features, le_sex)

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
    Classify severity using both rule-based and ML methods with smart consensus.
    """
    rule_sev = rule_severity(params)

    result = {
        'rule_severity': rule_sev,
        'ml_severity': None,
        'confidence': None,
        'consensus_severity': rule_sev,
        'method': 'rule',
    }

    if use_ml:
        try:
            ml_result = ml_severity(params)
            result['ml_severity'] = ml_result['severity']
            result['confidence'] = ml_result['confidence']
            result['probabilities'] = ml_result.get('probabilities', {})
            result['method'] = 'both'

            result['consensus_severity'] = _consensus_severity(params, rule_sev, ml_result)
        except Exception as e:
            logger.warning(f"ML classification failed: {e}")

    return result


def _consensus_severity(params: Dict, rule_sev: str, ml_result: Dict) -> str:
    """
    Pick the best severity estimate using smart consensus between rule-based and ML.
    Trusts rule-based for clear-cut clinical cases where ML may be unreliable.
    """
    ml_sev = ml_result['severity']
    ml_conf = ml_result.get('confidence', 0.0)

    if rule_sev == ml_sev:
        return rule_sev

    sev_idx = {s: i for i, s in enumerate(SEVERITY_ORDER)}
    rule_idx = sev_idx.get(rule_sev, 0)
    ml_idx = sev_idx.get(ml_sev, 0)
    gap = abs(rule_idx - ml_idx)

    hb = params.get('hb') or params.get('hb_current_g_dl') or params.get('hb_level')
    mcv = params.get('mcv') or params.get('mcv_fL') or params.get('mcv_level')
    rbc = params.get('rbc') or params.get('rbc_count')

    # Trust rule-based when HB is clearly normal — ML is unreliable here
    if hb is not None and hb >= 12.0 and rule_sev == 'No Thalassemia':
        logger.info(f"Consensus: trusting rule-based (HB={hb} is normal, rule={rule_sev}, ml={ml_sev})")
        return rule_sev

    # Trust rule-based when values are outside physiological range (likely OCR/unit mismatch)
    if rbc is not None and (rbc > 7.0 or rbc < 1.0):
        logger.info(f"Consensus: trusting rule-based (RBC={rbc} outside normal range, rule={rule_sev}, ml={ml_sev})")
        return rule_sev

    # Trust rule-based for large disagreements (2+ severity levels) with low ML confidence
    if gap >= 2 and ml_conf < 0.9:
        logger.info(f"Consensus: trusting rule-based (gap={gap}, conf={ml_conf:.2f}, rule={rule_sev}, ml={ml_sev})")
        return rule_sev

    # Default: trust ML if high confidence, otherwise rule-based
    if ml_conf >= 0.85:
        return ml_sev
    return rule_sev


def predict_transfusion_date(params: Dict) -> Optional[int]:
    """Predict days until next transfusion using trained regressor."""
    models = load_models()
    reg = models.get('reg')
    if reg is None:
        return None

    imputer  = models['imputer_reg']
    features = models['all_tf_features']
    le_sex   = models.get('le_sex')

    row = _build_feature_row(params, features, le_sex)

    X_single = pd.DataFrame([row], columns=features)
    X_single_imp = imputer.transform(X_single)

    days = reg.predict(X_single_imp)[0]
    return max(0, round(days))


# Train on import if no saved model
load_models()
