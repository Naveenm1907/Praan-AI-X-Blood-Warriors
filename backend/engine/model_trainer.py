"""
ML Model Trainer for Blood Parameter Prediction
Trains actual ML models (Random Forest, Gradient Boosting) on the dataset
"""
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import logging

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)


class BloodParameterPredictor:
    """ML-based predictor for blood parameters"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.severity_model = None
        self.severity_scaler = None
        self.loaded = False
        self.load_models()

    def load_models(self):
        """Load trained models from disk"""
        try:
            # Load parameter prediction models
            for param in ['hb_level', 'mcv_level', 'mch_level', 'mchc_level', 'rbc_count', 'ferritin_level']:
                model_path = MODEL_DIR / f"{param}_model.pkl"
                scaler_path = MODEL_DIR / f"{param}_scaler.pkl"

                if model_path.exists() and scaler_path.exists():
                    with open(model_path, 'rb') as f:
                        self.models[param] = pickle.load(f)
                    with open(scaler_path, 'rb') as f:
                        self.scalers[param] = pickle.load(f)

            # Load severity prediction model
            severity_model_path = MODEL_DIR / "severity_model.pkl"
            severity_scaler_path = MODEL_DIR / "severity_scaler.pkl"

            if severity_model_path.exists() and severity_scaler_path.exists():
                with open(severity_model_path, 'rb') as f:
                    self.severity_model = pickle.load(f)
                with open(severity_scaler_path, 'rb') as f:
                    self.severity_scaler = pickle.load(f)

            if self.models and self.severity_model:
                self.loaded = True
                logger.info(f"Loaded {len(self.models)} parameter models and severity model")
            else:
                logger.warning("Models not found, training required")
                self.train_models()

        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self.train_models()

    def train_models(self):
        """Train ML models on the dataset"""
        logger.info("Training ML models...")

        # Load dataset
        dataset_path = Path(__file__).parent.parent / "thalassemia_transfusion_10k.csv"
        df = pd.read_csv(dataset_path)

        # Map column names
        column_mapping = {
            'hb_current_g_dl': 'hb_level',
            'mcv_fL': 'mcv_level',
            'mch_pg': 'mch_level',
            'mchc_g_dl': 'mchc_level',
            'rbc_M_ul': 'rbc_count',
            'ferritin_ng_ml': 'ferritin_level'
        }

        # Train parameter prediction models
        params = ['hb_level', 'mcv_level', 'mch_level', 'mchc_level', 'rbc_count', 'ferritin_level']

        for param in params:
            original_col = [k for k, v in column_mapping.items() if v == param][0]

            if original_col not in df.columns:
                continue

            logger.info(f"Training model for {param}...")

            # Features: use other blood parameters to predict this one
            other_params = [p for p in params if p != param]
            feature_cols = []
            for p in other_params:
                orig = [k for k, v in column_mapping.items() if v == p][0]
                if orig in df.columns:
                    feature_cols.append(orig)

            # Also use age, sex, severity as features
            if 'age' in df.columns:
                feature_cols.append('age')
            if 'sex' in df.columns:
                df['sex_encoded'] = df['sex'].map({'M': 0, 'F': 1})
                feature_cols.append('sex_encoded')

            # Prepare data
            feature_data = df[feature_cols].copy()
            target_data = df[original_col].copy()

            # Remove rows with missing values
            mask = feature_data.notna().all(axis=1) & target_data.notna()
            feature_data = feature_data[mask]
            target_data = target_data[mask]

            if len(feature_data) < 100:
                logger.warning(f"Not enough data for {param}, skipping")
                continue

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                feature_data, target_data, test_size=0.2, random_state=42
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train Random Forest
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_train_scaled, y_train)

            # Evaluate
            y_pred = model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            logger.info(f"{param}: MAE={mae:.3f}, R2={r2:.3f}")

            # Save model and scaler
            with open(MODEL_DIR / f"{param}_model.pkl", 'wb') as f:
                pickle.dump(model, f)
            with open(MODEL_DIR / f"{param}_scaler.pkl", 'wb') as f:
                pickle.dump(scaler, f)

            self.models[param] = model
            self.scalers[param] = scaler

        # Train severity classification model
        logger.info("Training severity prediction model...")
        self._train_severity_model(df, column_mapping)

        self.loaded = True
        logger.info("Training complete")

    def _train_severity_model(self, df: pd.DataFrame, column_mapping: Dict):
        """Train severity classification model"""
        # Features: blood parameters
        feature_cols = []
        for param in ['hb_level', 'mcv_level', 'mch_level', 'mchc_level', 'rbc_count', 'ferritin_level']:
            orig = [k for k, v in column_mapping.items() if v == param][0]
            if orig in df.columns:
                feature_cols.append(orig)

        if 'age' in df.columns:
            feature_cols.append('age')

        # Target: severity
        if 'severity' not in df.columns:
            logger.error("Severity column not found")
            return

        # Map severity to numeric
        severity_map = {
            'No Thalassemia': 0,
            'Mild': 1,
            'Moderate': 2,
            'Moderate-Severe': 3,
            'Severe': 4
        }

        df['severity_encoded'] = df['severity'].map(severity_map)

        # Prepare data
        feature_data = df[feature_cols].copy()
        target_data = df['severity_encoded'].copy()

        # Remove rows with missing values
        mask = feature_data.notna().all(axis=1) & target_data.notna()
        feature_data = feature_data[mask]
        target_data = target_data[mask]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            feature_data, target_data, test_size=0.2, random_state=42
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train Gradient Boosting
        from sklearn.ensemble import GradientBoostingClassifier
        model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)

        # Evaluate
        from sklearn.metrics import accuracy_score, classification_report
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Severity model accuracy: {accuracy:.3f}")
        logger.info(f"Classification report:\n{classification_report(y_test, y_pred)}")

        # Save model and scaler
        with open(MODEL_DIR / "severity_model.pkl", 'wb') as f:
            pickle.dump(model, f)
        with open(MODEL_DIR / "severity_scaler.pkl", 'wb') as f:
            pickle.dump(scaler, f)

        self.severity_model = model
        self.severity_scaler = scaler

    def predict_parameters(self, partial_params: Dict) -> Dict:
        """
        Predict missing blood parameters using ML models

        Args:
            partial_params: Dict with some known parameters

        Returns:
            Dict with all parameters filled in
        """
        if not self.loaded:
            logger.warning("Models not loaded")
            return partial_params

        result = partial_params.copy()

        # Column mapping (reverse)
        reverse_mapping = {
            'hb_level': 'hb_current_g_dl',
            'mcv_level': 'mcv_fL',
            'mch_level': 'mch_pg',
            'mchc_level': 'mchc_g_dl',
            'rbc_count': 'rbc_M_ul',
            'ferritin_level': 'ferritin_ng_ml'
        }

        # Predict missing parameters
        for param in ['hb_level', 'mcv_level', 'mch_level', 'mchc_level', 'rbc_count', 'ferritin_level']:
            if result.get(param) is None and param in self.models:
                # Prepare features
                features = {}
                for other_param in ['hb_level', 'mcv_level', 'mch_level', 'mchc_level', 'rbc_count', 'ferritin_level']:
                    if other_param != param and result.get(other_param) is not None:
                        orig = reverse_mapping.get(other_param, other_param)
                        features[orig] = result[other_param]

                if len(features) > 0:
                    # Create feature vector
                    feature_vector = list(features.values())
                    feature_array = np.array([feature_vector])

                    # Scale
                    if param in self.scalers:
                        feature_array_scaled = self.scalers[param].transform(feature_array)
                    else:
                        feature_array_scaled = feature_array

                    # Predict
                    predicted_value = self.models[param].predict(feature_array_scaled)[0]
                    result[param] = float(predicted_value)
                    result[f"{param}_predicted"] = True
                    logger.debug(f"Predicted {param}: {predicted_value:.2f}")

        return result

    def predict_severity(self, params: Dict) -> Dict:
        """
        Predict severity level from blood parameters

        Args:
            params: Dict with blood parameters

        Returns:
            Dict with predicted severity and confidence
        """
        if not self.loaded or self.severity_model is None:
            return {'severity': 'Unknown', 'confidence': 0.0}

        # Prepare features
        feature_cols = ['hb_level', 'mcv_level', 'mch_level', 'mchc_level', 'rbc_count', 'ferritin_level']
        feature_values = []

        for col in feature_cols:
            value = params.get(col)
            if value is None:
                # Use median from training data as fallback
                value = 8.5 if col == 'hb_level' else 70.0
            feature_values.append(value)

        # Scale
        feature_array = np.array([feature_values])
        if self.severity_scaler:
            feature_array_scaled = self.severity_scaler.transform(feature_array)
        else:
            feature_array_scaled = feature_array

        # Predict
        severity_encoded = self.severity_model.predict(feature_array_scaled)[0]
        probabilities = self.severity_model.predict_proba(feature_array_scaled)[0]

        # Map back to severity names
        severity_map = {
            0: 'No Thalassemia',
            1: 'Mild',
            2: 'Moderate',
            3: 'Moderate-Severe',
            4: 'Severe'
        }

        severity = severity_map.get(int(severity_encoded), 'Unknown')
        confidence = float(np.max(probabilities))

        return {
            'severity': severity,
            'confidence': confidence,
            'probabilities': {
                severity_map[i]: float(prob)
                for i, prob in enumerate(probabilities)
            }
        }


# Global predictor instance
_predictor = None

def get_predictor() -> BloodParameterPredictor:
    """Get or create the global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = BloodParameterPredictor()
    return _predictor
