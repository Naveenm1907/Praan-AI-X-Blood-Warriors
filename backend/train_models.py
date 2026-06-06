"""
Train ML models for thalassemia severity classification and transfusion prediction.
Run this script to train models from the dataset.

Usage:
    python train_models.py
"""
import sys
import logging
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Train and save ML models"""
    logger.info("=" * 60)
    logger.info("Starting model training...")
    logger.info("=" * 60)

    try:
        # Import the training function
        from engine.severity import train_models

        # Train models
        models_data = train_models()

        # Verify training
        if models_data and 'clf' in models_data:
            logger.info("=" * 60)
            logger.info("✓ Models trained successfully!")
            logger.info("=" * 60)
            logger.info(f"Classifier: {type(models_data['clf']).__name__}")
            logger.info(f"Features: {len(models_data['all_features'])} features")

            if 'reg' in models_data:
                logger.info(f"Regressor: {type(models_data['reg']).__name__}")
                logger.info(f"Transfusion features: {len(models_data['all_tf_features'])} features")

            # Test the trained models
            logger.info("\nTesting with sample data...")
            from engine.severity import ml_severity, rule_severity

            test_params = {
                'hb_level': 7.5,
                'mcv_level': 65.0,
                'mch_level': 20.0,
                'ferritin_level': 800.0,
            }

            rule_result = rule_severity(test_params)
            logger.info(f"Rule-based severity: {rule_result}")

            ml_result = ml_severity(test_params)
            logger.info(f"ML severity: {ml_result['severity']} (confidence: {ml_result['confidence']:.3f})")
            logger.info(f"Probabilities: {ml_result['probabilities']}")

            logger.info("=" * 60)
            logger.info("✓ Training complete! Models saved to backend/engine/models/")
            logger.info("=" * 60)

        else:
            logger.error("Training failed - no models returned")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
