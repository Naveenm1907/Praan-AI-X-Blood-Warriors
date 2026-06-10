"""
run_local.py — Local runner for Thalassemia Severity & Transfusion Predictor
============================================================================
This script mirrors the Colab notebook (thalassemia_no_llm_v3.ipynb) but runs
completely locally without any Google Colab dependencies.

What it does:
  1. Loads the CSV dataset (thalassemia_transfusion_10k.csv)
  2. Trains (or reloads) the severity classifier + transfusion regressor
  3. Runs batch predictions on all rows
  4. (Optional) Writes patients to the RDS database via the backend API or directly

Usage:
  python run_local.py                   # train + predict (dry-run, no DB write)
  python run_local.py --write-db        # also upsert predictions into RDS
  python run_local.py --csv path/to.csv # use a specific CSV file
  python run_local.py --retrain         # force retrain even if models exist

Requirements (install in your venv):
  pip install scikit-learn pandas numpy requests python-dotenv sqlalchemy psycopg2-binary
"""

import argparse
import logging
import sys
from pathlib import Path

# ── Make sure we can import the backend package ────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("run_local")

# Default CSV locations (tries backend-local first, then root dev folder)
DEFAULT_CSV_PATHS = [
    BACKEND_DIR / "thalassemia_transfusion_10k.csv",
    Path("c:/dev/thalassemia_transfusion_10k.csv"),
]


def find_csv(override: str = None) -> Path:
    if override:
        p = Path(override)
        if not p.exists():
            raise FileNotFoundError(f"CSV not found: {p}")
        return p
    for p in DEFAULT_CSV_PATHS:
        if p.exists():
            return p
    raise FileNotFoundError(
        "thalassemia_transfusion_10k.csv not found. "
        "Pass --csv <path> or place it in the backend folder."
    )


def train_and_load_models(retrain: bool = False):
    """Force-retrain (delete pkl) or just load models."""
    from engine.severity import MODEL_DIR, load_models, train_models

    if retrain:
        pkl = MODEL_DIR / "trained_models.pkl"
        if pkl.exists():
            pkl.unlink()
            logger.info(f"Deleted existing model: {pkl}")

    logger.info("Loading/training models…")
    models = load_models()
    logger.info(f"Models ready. Keys: {list(models.keys())}")
    return models


def run_batch_prediction(csv_path: Path) -> pd.DataFrame:
    """
    Load the CSV, run severity + transfusion predictions on every row,
    and return an enriched DataFrame.
    """
    from engine.severity import classify_severity, predict_transfusion_date, SEVERITY_ORDER

    logger.info(f"Loading dataset: {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} rows, {df.shape[1]} columns")
    logger.info(f"Columns: {list(df.columns)}")
    logger.info(f"\nSeverity distribution:\n{df['severity'].value_counts().to_string()}")

    ml_severities = []
    ml_confidences = []
    rule_severities = []
    pred_days = []

    for i, row in df.iterrows():
        # Build params dict from CSV row — match actual column names
        params = {
            'hb_level':      row.get('hb_current_g_dl'),
            'mcv_level':     row.get('mcv_fL'),
            'mch_level':     row.get('mch_pg'),
            'mchc_level':    row.get('mchc_g_dl'),
            'rbc_count':     row.get('rbc_M_ul'),
            'ferritin_level': row.get('ferritin_ng_ml'),
            'rdw_pct':       row.get('rdw_pct'),
            'weight_kg':     row.get('weight_kg'),
            'hb_a_pct':      row.get('hb_A_pct'),
            'hb_a2':         row.get('hb_A2_pct'),
            'hb_f':          row.get('hb_F_pct'),
            'age':           row.get('age'),
            'sex':           row.get('sex'),
            # Transfusion
            'hb_post_transfusion':           row.get('hb_post_transfusion_g_dl'),
            'hb_drop_rate_per_day':          row.get('hb_drop_rate_per_day'),
            'hb_transfusion_threshold':      row.get('hb_transfusion_threshold_g_dl'),
            'days_since_last_transfusion':   row.get('days_since_last_transfusion'),
            'units_per_session':             row.get('units_per_session'),
            'avg_transfusion_interval_days': row.get('avg_transfusion_interval_days'),
        }

        # Severity classification
        result = classify_severity(params, use_ml=True)
        ml_severities.append(result.get('ml_severity') or result['rule_severity'])
        ml_confidences.append(result.get('confidence', 0.0))
        rule_severities.append(result['rule_severity'])

        # Transfusion date prediction
        days = predict_transfusion_date(params)
        pred_days.append(days)

        if (i + 1) % 1000 == 0:
            logger.info(f"  Processed {i + 1}/{len(df)} rows…")

    df['ml_severity_pred']     = ml_severities
    df['rule_severity_pred']   = rule_severities
    df['ml_confidence']        = ml_confidences
    df['pred_days_to_transfusion'] = pred_days

    # Quick accuracy check
    if 'severity' in df.columns:
        correct = (df['ml_severity_pred'] == df['severity']).sum()
        total   = len(df)
        logger.info(f"\n== ML Severity Accuracy: {correct}/{total} = {correct/total:.2%} ==")

    return df


def show_sample(df: pd.DataFrame, n: int = 5):
    """Print a compact sample of predictions."""
    cols = [
        'patient_id', 'age', 'severity',
        'ml_severity_pred', 'ml_confidence',
        'rule_severity_pred', 'pred_days_to_transfusion',
    ]
    cols = [c for c in cols if c in df.columns]
    logger.info(f"\nSample predictions (first {n} rows):\n{df[cols].head(n).to_string(index=False)}")


def write_to_database(df: pd.DataFrame):
    """
    Upsert rows from the predictions DataFrame into the RDS Postgres patients table.
    Only writes rows that have a patient_id and sufficient blood parameters.
    """
    logger.info("Connecting to database…")
    try:
        from database import SessionLocal, init_db
        from models.patient import Patient

        init_db()
        db = SessionLocal()

        created = 0
        updated = 0

        for _, row in df.iterrows():
            pid_str = str(row.get('patient_id', ''))
            if not pid_str:
                continue

            # Check if patient with this patient_id already exists (stored in ocr_text as a tag)
            existing = db.query(Patient).filter(
                Patient.ocr_text.like(f"%patient_id:{pid_str}%")
            ).first()

            severity   = row.get('ml_severity_pred') or row.get('severity')
            pred_days  = row.get('pred_days_to_transfusion')
            pred_days  = int(pred_days) if pd.notna(pred_days) else None

            from datetime import datetime, timedelta
            next_date = None
            urgency   = 'SCHEDULED'
            if pred_days is not None:
                next_date = (datetime.now() + timedelta(days=pred_days)).strftime('%Y-%m-%d')
                if pred_days <= 3:   urgency = 'CRITICAL'
                elif pred_days <= 7: urgency = 'URGENT'
                elif pred_days <= 14: urgency = 'SOON'

            def _f(col, default=None):
                v = row.get(col)
                return float(v) if pd.notna(v) else default

            def _i(col, default=None):
                v = row.get(col)
                return int(v) if pd.notna(v) else default

            if existing:
                existing.hb_level        = _f('hb_current_g_dl')
                existing.mcv_level       = _f('mcv_fL')
                existing.mch_level       = _f('mch_pg')
                existing.mchc_level      = _f('mchc_g_dl')
                existing.rbc_count       = _f('rbc_M_ul')
                existing.ferritin_level  = _f('ferritin_ng_ml')
                existing.rdw_pct         = _f('rdw_pct')
                existing.weight_kg       = _f('weight_kg')
                existing.hb_a_pct        = _f('hb_A_pct')
                existing.hb_a2           = _f('hb_A2_pct')
                existing.hb_f            = _f('hb_F_pct')
                existing.hb_post_transfusion         = _f('hb_post_transfusion_g_dl')
                existing.hb_drop_rate_per_day        = _f('hb_drop_rate_per_day')
                existing.hb_transfusion_threshold    = _f('hb_transfusion_threshold_g_dl')
                existing.days_since_last_transfusion = _i('days_since_last_transfusion')
                existing.units_per_session           = _f('units_per_session')
                existing.avg_transfusion_interval_days = _f('avg_transfusion_interval_days')
                existing.severity              = severity
                existing.severity_score        = _f('ml_confidence', 0.5)
                existing.urgency_level         = urgency
                existing.days_until_transfusion = pred_days
                existing.next_transfusion_date = next_date
                updated += 1
            else:
                blood_group = str(row.get('blood_group', 'O+')).strip()
                sex_val     = str(row.get('sex', 'M')).strip()
                gender      = 'Male' if sex_val == 'M' else 'Female'

                p = Patient(
                    name       = pid_str,
                    age        = _i('age', 0),
                    gender     = gender,
                    blood_group = blood_group if blood_group in [
                        'A+','A-','B+','B-','AB+','AB-','O+','O-'
                    ] else 'O+',
                    phone    = '0000000000',
                    location = 'Unknown',

                    hb_level       = _f('hb_current_g_dl'),
                    mcv_level      = _f('mcv_fL'),
                    mch_level      = _f('mch_pg'),
                    mchc_level     = _f('mchc_g_dl'),
                    rbc_count      = _f('rbc_M_ul'),
                    ferritin_level = _f('ferritin_ng_ml'),
                    rdw_pct        = _f('rdw_pct'),
                    weight_kg      = _f('weight_kg'),
                    hb_a_pct       = _f('hb_A_pct'),
                    hb_a2          = _f('hb_A2_pct'),
                    hb_f           = _f('hb_F_pct'),

                    hb_post_transfusion         = _f('hb_post_transfusion_g_dl'),
                    hb_drop_rate_per_day        = _f('hb_drop_rate_per_day'),
                    hb_transfusion_threshold    = _f('hb_transfusion_threshold_g_dl'),
                    days_since_last_transfusion = _i('days_since_last_transfusion'),
                    units_per_session           = _f('units_per_session'),
                    avg_transfusion_interval_days = _f('avg_transfusion_interval_days'),

                    severity               = severity,
                    severity_score         = _f('ml_confidence', 0.5),
                    urgency_level          = urgency,
                    days_until_transfusion = pred_days,
                    next_transfusion_date  = next_date,

                    ocr_text = f"patient_id:{pid_str}",
                )
                db.add(p)
                created += 1

            if (created + updated) % 500 == 0:
                db.commit()
                logger.info(f"  DB commit — created: {created}, updated: {updated}")

        db.commit()
        logger.info(f"\nDatabase write complete — created: {created}, updated: {updated}")
        db.close()

    except Exception as e:
        logger.error(f"Database write failed: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Thalassemia local predictor")
    parser.add_argument('--csv',      type=str, default=None,  help="Path to thalassemia CSV")
    parser.add_argument('--retrain',  action='store_true',     help="Force retrain models")
    parser.add_argument('--write-db', action='store_true',     help="Write predictions to RDS")
    parser.add_argument('--sample',   type=int, default=5,     help="Number of sample rows to print")
    args = parser.parse_args()

    csv_path = find_csv(args.csv)
    logger.info(f"Using CSV: {csv_path}")

    # Step 1: Train / load models
    train_and_load_models(retrain=args.retrain)

    # Step 2: Batch predict
    df = run_batch_prediction(csv_path)

    # Step 3: Show sample
    show_sample(df, n=args.sample)

    # Step 4 (optional): Write to database
    if args.write_db:
        write_to_database(df)
    else:
        logger.info("\nDry-run complete (no DB write). Use --write-db to persist to RDS.")

    logger.info("Done.")


if __name__ == '__main__':
    main()
