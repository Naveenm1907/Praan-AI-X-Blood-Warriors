"""
Transfusion Urgency Estimator
Predicts when next transfusion is needed
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TransfusionEstimator:
    """Estimates transfusion urgency and next date"""

    def estimate_urgency(
        self,
        last_transfusion_date: Optional[str],
        transfusion_interval_days: int,
        severity: str
    ) -> Dict:
        """
        Estimate urgency for a patient

        Args:
            last_transfusion_date: ISO date string or None
            transfusion_interval_days: Expected interval between transfusions
            severity: Severity classification

        Returns:
            Dict with urgency info
        """
        # Parse last transfusion date
        if last_transfusion_date:
            try:
                last_date = datetime.fromisoformat(last_transfusion_date)
            except ValueError:
                last_date = None
        else:
            last_date = None

        # Calculate days until next transfusion
        if last_date:
            next_date = last_date + timedelta(days=transfusion_interval_days)
            days_until = (next_date - datetime.now()).days
        else:
            # No history, use severity to estimate
            if severity == "Severe":
                days_until = 7
            elif severity == "Moderate":
                days_until = 21
            elif severity == "Mild":
                days_until = 42
            else:
                days_until = 90

            next_date = datetime.now() + timedelta(days=days_until)

        # Determine urgency level
        if days_until <= 3:
            urgency_level = "CRITICAL"
        elif days_until <= 7:
            urgency_level = "URGENT"
        elif days_until <= 14:
            urgency_level = "SOON"
        else:
            urgency_level = "SCHEDULED"

        return {
            "urgency_level": urgency_level,
            "days_until_transfusion": days_until,
            "next_transfusion_date": next_date.isoformat(),
            "last_transfusion_date": last_date.isoformat() if last_date else None,
            "transfusion_interval_days": transfusion_interval_days,
        }

    def get_transfusion_info(self, patient) -> Dict:
        """Get detailed transfusion info for a patient"""
        if hasattr(patient, '__dict__'):
            # SQLAlchemy model
            return self.estimate_urgency(
                patient.last_transfusion_date,
                patient.transfusion_interval_days or 28,
                patient.severity or "Unknown"
            )
        else:
            # Dict
            return self.estimate_urgency(
                patient.get('last_transfusion_date'),
                patient.get('transfusion_interval_days', 28),
                patient.get('severity', 'Unknown')
            )
