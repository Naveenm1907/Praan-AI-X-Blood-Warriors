"""
OCR Parser for Medical Reports
Uses trained ML models for severity classification and transfusion prediction.
Falls back to deterministic values from dataset statistics when OCR unavailable.
"""
import io
import re
import logging
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
from PIL import Image
import pytesseract

from engine.severity import rule_severity, ml_severity, predict_transfusion_date, load_models

logger = logging.getLogger(__name__)


class OCRParser:
    """Parse medical reports using OCR + trained ML models"""

    def __init__(self):
        # Load dataset statistics for deterministic fallback
        self.stats = self._load_dataset_stats()

    def _load_dataset_stats(self) -> Dict:
        """Load median values from dataset for deterministic fallback"""
        dataset_path = Path(__file__).parent.parent / "thalassemia_transfusion_10k.csv"
        df = pd.read_csv(dataset_path)

        # Get medians for each severity level
        stats = {}
        for severity in ['Mild', 'Moderate', 'Moderate-Severe', 'Severe']:
            subset = df[df['severity'] == severity]
            stats[severity] = {
                'hb_level': float(subset['hb_current_g_dl'].median()) if 'hb_current_g_dl' in subset else 8.5,
                'mcv_level': float(subset['mcvfL'].median()) if 'mcvfL' in subset else 70.0,
                'mch_level': float(subset['mchpg'].median()) if 'mchpg' in subset else 22.0,
                'mchc_level': float(subset['mchcgdl'].median()) if 'mchcgdl' in subset else 32.0,
                'rbc_count': float(subset['rbcMul'].median()) if 'rbcMul' in subset else 4.2,
                'ferritin_level': float(subset['ferritinngml'].median()) if 'ferritinngml' in subset else 450.0,
            }

        return stats

    async def parse_report(self, image_file) -> Dict:
        """
        Parse medical report image and predict severity.

        Args:
            image_file: Uploaded image file (UploadFile)

        Returns:
            Dict with extracted values, severity, and transfusion prediction
        """
        try:
            # Read image
            contents = await image_file.read()
            image = Image.open(io.BytesIO(contents))

            # Extract text using Tesseract
            text = self._extract_text(image)
            logger.info(f"Extracted text: {text[:200]}...")

            # Parse values from text
            extracted = self._extract_values(text)
            logger.info(f"Extracted values: {extracted}")

            # Classify severity using both rule-based and ML
            severity_result = self._classify_severity(extracted)

            # Predict transfusion date if severe enough
            transfusion_days = self._predict_transfusion(extracted, severity_result)

            return {
                **extracted,
                **severity_result,
                'transfusion_days': transfusion_days,
                'raw_text': text,
            }

        except Exception as e:
            logger.error(f"OCR parsing failed: {e}")
            return self._fallback_prediction()

    def _extract_text(self, image: Image.Image) -> str:
        """Extract text from image using Tesseract"""
        try:
            # Preprocess for better OCR
            image = image.convert('L')  # Grayscale
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""

    def _extract_values(self, text: str) -> Dict:
        """Extract blood parameter values from OCR text"""
        text_lower = text.lower()

        extracted = {}

        # Patterns for each parameter
        patterns = {
            'hb_level': [
                r'hemoglobin[:\s]+([\d.]+)',
                r'hb[:\s]+([\d.]+)',
                r'haemoglobin[:\s]+([\d.]+)',
            ],
            'mcv_level': [
                r'mcv[:\s]+([\d.]+)',
                r'mean\s+corpuscular\s+volume[:\s]+([\d.]+)',
            ],
            'mch_level': [
                r'mch[:\s]+([\d.]+)',
                r'mean\s+corpuscular\s+hemoglobin[:\s]+([\d.]+)',
            ],
            'mchc_level': [
                r'mchc[:\s]+([\d.]+)',
                r'mean\s+corpuscular\s+hemoglobin\s+concentration[:\s]+([\d.]+)',
            ],
            'rbc_count': [
                r'rbc[:\s]+([\d.]+)',
                r'red\s+blood\s+cell[:\s]+([\d.]+)',
            ],
            'ferritin_level': [
                r'ferritin[:\s]+([\d.]+)',
                r'serum\s+ferritin[:\s]+([\d.]+)',
            ],
        }

        for param, param_patterns in patterns.items():
            for pattern in param_patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1))
                        extracted[param] = value
                        break
                    except (ValueError, IndexError):
                        continue

        return extracted

    def _classify_severity(self, extracted: Dict) -> Dict:
        """Classify severity using rule-based + ML models"""
        # Rule-based classification
        rule_sev = rule_severity(extracted)

        # ML-based classification
        try:
            ml_result = ml_severity(extracted)
            ml_sev = ml_result['severity']
            ml_conf = ml_result['confidence']
            ml_probs = ml_result.get('probabilities', {})
        except Exception as e:
            logger.warning(f"ML classification failed: {e}")
            ml_sev = None
            ml_conf = 0.0
            ml_probs = {}

        # Use ML if available, otherwise rule-based
        if ml_sev:
            severity = ml_sev
            severity_score = ml_conf
            method = 'ml'
        else:
            severity = rule_sev
            severity_score = 0.5  # Default confidence for rule-based
            method = 'rule'

        return {
            'severity': severity,
            'severity_score': severity_score,
            'severity_method': method,
            'rule_severity': rule_sev,
            'ml_severity': ml_sev,
            'ml_probabilities': ml_probs,
        }

    def _predict_transfusion(self, extracted: Dict, severity_result: Dict) -> Optional[int]:
        """Predict days until next transfusion"""
        severity = severity_result['severity']

        # Only predict for moderate and above
        if severity in ['Mild', 'No Thalassemia']:
            return None

        try:
            days = predict_transfusion_date(extracted)
            return days if days is not None else self._rule_based_transfusion(severity, extracted)
        except Exception as e:
            logger.warning(f"ML transfusion prediction failed: {e}")
            return self._rule_based_transfusion(severity, extracted)

    def _rule_based_transfusion(self, severity: str, extracted: Dict) -> int:
        """Rule-based transfusion prediction"""
        hb = extracted.get('hb_level', 8.5)

        # Rule from Colab notebook
        if severity == 'Severe':
            drop_rate = 0.17
        elif severity == 'Moderate-Severe':
            drop_rate = 0.11
        elif severity == 'Moderate':
            drop_rate = 0.055
        else:
            return None

        days = max(0, round((hb - 9.0) / drop_rate))
        return days

    def _fallback_prediction(self) -> Dict:
        """
        Deterministic fallback when OCR fails.
        Uses median values from Moderate severity in dataset.
        """
        # Use Moderate as default (most common)
        fallback_values = self.stats['Moderate']

        # Classify using these values
        severity_result = self._classify_severity(fallback_values)

        # Predict transfusion
        transfusion_days = self._predict_transfusion(fallback_values, severity_result)

        return {
            **fallback_values,
            **severity_result,
            'transfusion_days': transfusion_days,
            'raw_text': 'OCR failed - using deterministic fallback from dataset',
            'fallback_used': True,
        }

    def predict_from_manual_input(self, manual_values: Dict) -> Dict:
        """
        Predict severity and transfusion from manually entered values.
        Uses the same trained ML models.
        """
        # Classify severity
        severity_result = self._classify_severity(manual_values)

        # Predict transfusion
        transfusion_days = self._predict_transfusion(manual_values, severity_result)

        return {
            **manual_values,
            **severity_result,
            'transfusion_days': transfusion_days,
        }


# Global instance
_parser = None

def get_parser() -> OCRParser:
    """Get or create the global parser instance"""
    global _parser
    if _parser is None:
        _parser = OCRParser()
    return _parser
