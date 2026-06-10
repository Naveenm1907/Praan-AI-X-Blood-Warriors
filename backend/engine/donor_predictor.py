"""
Donor Response Prediction Engine
Uses trained XGBoost model to predict donation probability
"""
import joblib
import pickle
from pathlib import Path
import numpy as np
from datetime import datetime

class DonorResponsePredictor:
    def __init__(self):
        """Load trained model"""
        self.model = None
        self.feature_columns = None
        self.label_encoders = None
        self.load_model()

    def load_model(self):
        """Load model from disk"""
        model_path = Path('donor_response_model.pkl')

        if not model_path.exists():
            print(f"Warning: Model file not found at {model_path}")
            print("Please run: python train_donor_model.py")
            return

        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.feature_columns = model_data['feature_columns']
            self.label_encoders = model_data['label_encoders']
            print(f"Donor response model loaded (trained: {model_data['trained_at']})")
        except Exception as e:
            print(f"Error loading model: {e}")

    def predict_response_probability(self, donor_data: dict) -> float:
        """
        Predict probability that donor will respond positively to contact

        Args:
            donor_data: Dictionary with donor features

        Returns:
            float: Probability between 0 and 1
        """
        if self.model is None:
            # Fallback to rule-based scoring
            return self._rule_based_score(donor_data)

        try:
            # Extract features in correct order
            features = []
            for col in self.feature_columns:
                if col in ['blood_group_encoded']:
                    # Encode blood group
                    le = self.label_encoders['blood_group']
                    blood_group = donor_data.get('blood_group', 'O+')
                    try:
                        encoded = le.transform([blood_group])[0]
                    except:
                        encoded = 0
                    features.append(encoded)
                elif col == 'is_bridge_donor':
                    features.append(1 if donor_data.get('role') == 'Bridge Donor' else 0)
                elif col == 'is_regular_donor':
                    features.append(1 if donor_data.get('donor_type') == 'Regular Donor' else 0)
                elif col == 'is_active':
                    features.append(1 if donor_data.get('user_donation_active_status') == 'Active' else 0)
                elif col == 'is_eligible':
                    features.append(1 if donor_data.get('eligibility_status') == 'eligible' else 0)
                elif col == 'has_inactive_trigger':
                    features.append(1 if donor_data.get('inactive_trigger_comment') else 0)
                elif col == 'days_since_last_donation':
                    last_date = donor_data.get('last_donation_date')
                    if last_date:
                        days = (datetime.now() - datetime.fromisoformat(last_date)).days
                    else:
                        days = 999
                    features.append(days)
                elif col == 'days_since_last_contact':
                    last_date = donor_data.get('last_contacted_date')
                    if last_date:
                        days = (datetime.now() - datetime.fromisoformat(last_date)).days
                    else:
                        days = 999
                    features.append(days)
                else:
                    # Direct feature
                    features.append(donor_data.get(col, 0))

            # Reshape for prediction
            X = np.array(features).reshape(1, -1)

            # Predict probability
            proba = self.model.predict_proba(X)[0][1]  # Probability of class 1 (will donate)

            return float(proba)

        except Exception as e:
            print(f"Prediction error: {e}")
            return self._rule_based_score(donor_data)

    def _rule_based_score(self, donor_data: dict) -> float:
        """Fallback rule-based scoring"""
        score = 0.0

        # Active status (40% weight)
        if donor_data.get('user_donation_active_status') == 'Active':
            score += 0.4

        # Eligibility (30% weight)
        if donor_data.get('eligibility_status') == 'eligible':
            score += 0.3

        # Call-to-donation ratio (20% weight)
        ratio = donor_data.get('calls_to_donations_ratio', 99)
        if ratio < 5:
            score += 0.2
        elif ratio < 10:
            score += 0.1

        # Recent donation (10% weight)
        last_date = donor_data.get('last_donation_date')
        if last_date:
            days = (datetime.now() - datetime.fromisoformat(last_date)).days
            if days < 180:
                score += 0.1

        return min(score, 1.0)

# Global instance
predictor = DonorResponsePredictor()

def predict_donor_response(donor_data: dict) -> float:
    """Convenience function for prediction"""
    return predictor.predict_response_probability(donor_data)
