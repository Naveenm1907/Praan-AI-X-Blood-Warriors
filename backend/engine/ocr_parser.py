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
import os

pytesseract.pytesseract.tesseract_cmd = os.environ.get(
    "TESSERACT_CMD",
    os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"), "Tesseract-OCR", "tesseract.exe"),
)

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
                'hb_level':      float(subset['hb_current_g_dl'].median()) if 'hb_current_g_dl' in subset.columns else 8.5,
                'mcv_level':     float(subset['mcv_fL'].median())          if 'mcv_fL' in subset.columns else 70.0,
                'mch_level':     float(subset['mch_pg'].median())          if 'mch_pg' in subset.columns else 22.0,
                'mchc_level':    float(subset['mchc_g_dl'].median())       if 'mchc_g_dl' in subset.columns else 32.0,
                'rbc_count':     float(subset['rbc_M_ul'].median())        if 'rbc_M_ul' in subset.columns else 4.2,
                'ferritin_level': float(subset['ferritin_ng_ml'].median()) if 'ferritin_ng_ml' in subset.columns else 450.0,
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
        """Extract text from image using Tesseract (replicated from notebook)"""
        try:
            # Preprocess for better OCR
            img = image.convert('L')
            w, h = img.size
            up2 = img.resize((w * 2, h * 2), Image.LANCZOS)
            from PIL import ImageOps, ImageFilter
            ac = ImageOps.autocontrast(up2)
            
            # Simple single pass to avoid heavy processing
            text = pytesseract.image_to_string(ac, config='--oem 3 --psm 6')
            if not text.strip():
                text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""

    def _normalize_text(self, text: str) -> str:
        NORM_FIXES = {
            'HBA2':'HbA2','HBAZ':'HbA2','HBF':'HbF','HBA ':'HbA ',
            'M.C.V':'MCV','M.C.H.C':'MCHC','M.C.H':'MCH',
            'R.B.C':'RBC','W.B.C':'WBC','P.L.T':'PLT',
            'RDW-CV':'RDW','RDW CV':'RDW',
            'HAEMOGLOBIN':'Hemoglobin','HGB':'Hemoglobin',
            'RBC.':'RBC','MCH.C':'MCHC','MCH.':'MCH',
            'PLT Count':'PLT','PLT COUNT':'PLT',
            'x 10e6/uL':'x10e6uL','x10e6/uL':'x10e6uL',
            'x 10e3/uL':'x10e3uL','x10e3/uL':'x10e3uL',
            'x10^6/uL':'x10e6uL','x10^3/uL':'x10e3uL',
            'SEX :':'Sex:','AGE :':'Age:','NAME :':'Name:',
        }
        for k,v in NORM_FIXES.items(): text = text.replace(k,v)
        text = re.sub(r'[ \t]+',' ',text)
        text = re.sub(r'\n+','\n',text)
        return text.strip()

    def _to_float(self, x):
        if x is None: return None
        x = re.sub(r'[^0-9.\-]','',str(x).replace(',','.'))
        if x in ('','.','-','-.','.-'): return None
        try:    return float(x)
        except: return None

    def _find_first(self, patterns, text, flags=re.I):
        for p in patterns:
            m = re.search(p, text, flags)
            if m: return m.group(1).strip()
        return None

    def _extract_numeric(self, text, labels, units=None):
        ug  = ('(?:'+('|'.join(units))+r')?') if units else r'(?:[%A-Za-z/µ^0-9]*)?'
        lg  = '(?:'+('|'.join(labels))+')'
        for pat in [
            rf'{lg}\s*[:\-=]?\s*([0-9]+(?:[\.,][0-9]+)?)\s*{ug}',
            rf'{lg}[^\n]{{0,40}}?([0-9]+(?:[\.,][0-9]+)?)\s*{ug}',
        ]:
            v = self._to_float(self._find_first([pat], text, flags=re.I))
            if v is not None: return v
        return None

    def _extract_values(self, text: str) -> Dict:
        """Extract blood parameter values from OCR text"""
        t = self._normalize_text(text)

        extracted = {}

        extracted['hb_level']    = self._extract_numeric(t,[r'Hemoglobin\b',r'\bHb\b',r'\bHGB\b'],[r'g/?dL',r'g%'])
        extracted['rbc_count']   = self._extract_numeric(t,[r'\bRBC\b'],[r'x10e6uL',r'million/?cmm'])
        if extracted['rbc_count'] is None or extracted['rbc_count'] >= 10.0:  # If it mistakenly caught '10' from the unit
            extracted['rbc_count']  = self._extract_numeric(t,[r'\bRBC\b'])
        extracted['mcv_level']   = self._extract_numeric(t,[r'\bMCV\b'],[r'fL'])
        extracted['mch_level']   = self._extract_numeric(t,[r'\bMCH\b(?!C)'],[r'p[sg]'])
        extracted['mchc_level']  = self._extract_numeric(t,[r'\bMCHC\b'],[r'g/?dL'])
        extracted['rdw_pct']     = self._extract_numeric(t,[r'\bRDW\b'],[r'%'])
        extracted['platelet_count'] = self._extract_numeric(t,[r'\bPLT\b',r'Platelet(?:\s+Count)?'],[r'x10e3uL',r'lakh'])
        if extracted['platelet_count'] is None:   
            extracted['platelet_count'] = self._extract_numeric(t,[r'\bPLT\b',r'Platelet(?:\s+Count)?'])
        extracted['wbc_count']   = self._extract_numeric(t,[r'\bWBC\b',r'\bTLC\b'],[r'x10e3uL'])
        if extracted['wbc_count'] is None:   
            extracted['wbc_count'] = self._extract_numeric(t,[r'\bWBC\b',r'\bTLC\b'])
        extracted['ferritin_level'] = self._extract_numeric(t,[r'Ferritin\b'],[r'ng/?mL'])
        extracted['hb_a2']  = self._extract_numeric(t,[r'\bA2\s*[:\-]?\s*(?=[0-9])',r'HbA2\b',r'Hb A2\b'],[r'%'])
        extracted['hb_f']   = self._extract_numeric(t,[r'\bF\s*[:\-]?\s*(?=[0-9])',r'HbF\b',r'Hb F\b'],[r'%'])
        extracted['hb_a_pct'] = self._extract_numeric(t,[r'HbA\b(?!2)',r'Hb A\b(?!2)'],[r'%'])

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
