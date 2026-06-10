"""
Phase 1: Train XGBoost model to predict donor response probability
Based on historical donation patterns from Dataset.csv
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import pickle
from datetime import datetime
import joblib

def load_and_preprocess_data():
    """Load Dataset.csv and engineer features for response prediction"""
    print("Loading donor dataset...")
    df = pd.read_csv('../Dataset.csv')
    print(f"Loaded {len(df)} donor records")

    # Parse dates
    df['registration_date'] = pd.to_datetime(df['registration_date'], errors='coerce')
    df['last_donation_date'] = pd.to_datetime(df['last_donation_date'], errors='coerce')
    df['last_contacted_date'] = pd.to_datetime(df['last_contacted_date'], errors='coerce')

    # Calculate days since last donation
    df['days_since_last_donation'] = (datetime.now() - df['last_donation_date']).dt.days
    df['days_since_last_contact'] = (datetime.now() - df['last_contacted_date']).dt.days

    # Fill NaN with reasonable defaults
    df['days_since_last_donation'] = df['days_since_last_donation'].fillna(999)
    df['days_since_last_contact'] = df['days_since_last_contact'].fillna(999)
    df['calls_to_donations_ratio'] = df['calls_to_donations_ratio'].fillna(99)
    df['donations_till_date'] = df['donations_till_date'].fillna(0)
    df['total_calls'] = df['total_calls'].fillna(0)

    # Encode categorical variables
    label_encoders = {}

    # Blood group encoding
    le_blood = LabelEncoder()
    df['blood_group_encoded'] = le_blood.fit_transform(df['blood_group'].fillna('Unknown'))
    label_encoders['blood_group'] = le_blood

    # Role encoding (Bridge Donor = 1, Emergency Donor = 0, Volunteer = 0)
    df['is_bridge_donor'] = (df['role'] == 'Bridge Donor').astype(int)

    # Donor type encoding (Regular Donor = 1, One-Time Donor = 0, Other = 0)
    df['is_regular_donor'] = (df['donor_type'] == 'Regular Donor').astype(int)

    # Active status encoding
    df['is_active'] = (df['user_donation_active_status'] == 'Active').astype(int)

    # Eligibility encoding
    df['is_eligible'] = (df['eligibility_status'] == 'eligible').astype(int)

    # Inactive trigger encoding (simplified)
    df['has_inactive_trigger'] = (~df['inactive_trigger_comment'].isna()).astype(int)

    # Create target variable: Will donate if contacted?
    # Better logic: Score-based probability using donor behavior patterns

    # Calculate donation likelihood score
    df['donation_score'] = 0

    # Active donors get points
    df.loc[df['is_active'] == 1, 'donation_score'] += 30

    # Eligible donors get points
    df.loc[df['is_eligible'] == 1, 'donation_score'] += 25

    # Recent donation (within 180 days)
    df.loc[df['days_since_last_donation'] < 180, 'donation_score'] += 20

    # Good call-to-donation ratio (responsive donors)
    df.loc[df['calls_to_donations_ratio'] < 3, 'donation_score'] += 15
    df.loc[(df['calls_to_donations_ratio'] >= 3) & (df['calls_to_donations_ratio'] < 5), 'donation_score'] += 10

    # Bridge donors are more committed
    df.loc[df['is_bridge_donor'] == 1, 'donation_score'] += 10

    # Regular donors more likely than one-time
    df.loc[df['is_regular_donor'] == 1, 'donation_score'] += 10

    # Binary target: score >= 60 = likely to donate
    df['will_donate'] = (df['donation_score'] >= 60).astype(int)

    # Select features for model
    feature_columns = [
        'donations_till_date',
        'calls_to_donations_ratio',
        'total_calls',
        'is_eligible',
        'is_active',
        'is_bridge_donor',
        'is_regular_donor',
        'days_since_last_donation',
        'days_since_last_contact',
        'has_inactive_trigger',
        'blood_group_encoded'
    ]

    X = df[feature_columns]
    y = df['will_donate']

    print(f"\nTarget distribution:")
    print(y.value_counts())
    print(f"\nPositive rate: {y.mean():.2%}")

    return X, y, feature_columns, label_encoders

def train_model(X, y, feature_columns):
    """Train XGBoost classifier"""
    print("\nSplitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")

    # Train XGBoost
    print("\nTraining XGBoost model...")
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )

    model.fit(X_train, y_train)

    # Evaluate
    print("\nEvaluating model...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")

    # Only calculate ROC-AUC if we have both classes in test set
    if len(set(y_test)) > 1:
        print(f"ROC-AUC: {roc_auc_score(y_test, y_pred_proba):.4f}")
    else:
        print("ROC-AUC: N/A (only one class in test set)")

    print(f"\nClassification Report:")
    if len(set(y_test)) > 1:
        print(classification_report(y_test, y_pred, target_names=['Will Not Donate', 'Will Donate']))
    else:
        print(classification_report(y_test, y_pred))

    # Feature importance
    print("\nFeature Importance:")
    importance_df = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(importance_df)

    return model

def save_model(model, feature_columns, label_encoders):
    """Save trained model and metadata"""
    print("\nSaving model...")

    model_data = {
        'model': model,
        'feature_columns': feature_columns,
        'label_encoders': label_encoders,
        'trained_at': datetime.now().isoformat()
    }

    # Save with joblib (better for sklearn/xgboost)
    joblib.dump(model_data, 'donor_response_model.pkl')
    print("Model saved to donor_response_model.pkl")

    # Also save with pickle for compatibility
    with open('donor_response_model.pickle', 'wb') as f:
        pickle.dump(model_data, f)
    print("Model also saved to donor_response_model.pickle")

def main():
    """Main training pipeline"""
    print("=" * 60)
    print("PHASE 1: Donor Response Prediction Model Training")
    print("=" * 60)

    # Load and preprocess
    X, y, feature_columns, label_encoders = load_and_preprocess_data()

    # Train
    model = train_model(X, y, feature_columns)

    # Save
    save_model(model, feature_columns, label_encoders)

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: uvicorn main:app --reload")
    print("2. Test endpoint: POST /api/workflow/start")
    print("3. Check donor ranking in response")

if __name__ == "__main__":
    main()
