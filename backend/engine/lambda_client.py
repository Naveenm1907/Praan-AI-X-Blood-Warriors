"""
Lambda client for PRAAN AI severity classification
Calls deployed Lambda function via API Gateway
"""
import json
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# API Gateway endpoint
LAMBDA_API_URL = 'https://ebylzvfohb.execute-api.eu-north-1.amazonaws.com/default/praan-severity-classifier'


def classify_severity_lambda(params: Dict) -> Dict:
    """
    Call deployed Lambda function for severity classification via API Gateway

    Args:
        params: Dict with blood parameters (hb_level, mcv_level, etc.)

    Returns:
        Dict with severity, confidence, probabilities, days_until_transfusion
    """
    try:
        # Call API Gateway endpoint
        response = requests.post(
            LAMBDA_API_URL,
            json=params,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        if response.status_code != 200:
            logger.error(f"Lambda API error: {response.status_code} - {response.text}")
            return {'severity': 'Unknown', 'confidence': 0.0}

        result = response.json()

        # Parse Lambda response format
        if isinstance(result, str):
            result = json.loads(result)

        # Extract from body if wrapped
        if 'body' in result:
            body = result['body']
            if isinstance(body, str):
                result = json.loads(body)

        return result

    except Exception as e:
        logger.error(f"Lambda API call failed: {e}")
        # Fall back to local models
        from engine.severity import classify_severity
        return classify_severity(params, use_ml=True)


def ml_severity(params: Dict) -> Dict:
    """Wrapper for Lambda-based ML severity"""
    result = classify_severity_lambda(params)
    return {
        'severity': result.get('severity', 'Unknown'),
        'confidence': result.get('confidence', 0.0),
        'probabilities': result.get('probabilities', {}),
    }


def predict_transfusion_date_lambda(params: Dict) -> Optional[int]:
    """Get transfusion prediction from Lambda"""
    result = classify_severity_lambda(params)
    return result.get('days_until_transfusion')


# Alias for backward compatibility
predict_transfusion_date = predict_transfusion_date_lambda
