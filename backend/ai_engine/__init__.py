"""
AI Engine Module
Handles investment recommendation logic with real ML models and market data.
"""
import logging
import os

logger = logging.getLogger(__name__)

# Initialize models on module import
try:
    from .train_models import load_models
    logger.info("🚀 Loading pre-trained ML models...")
    scaler, risk_clf, return_reg, risk_logistic, kmeans = load_models()
    logger.info("✅ ML models loaded successfully!")
except Exception as e:
    logger.warning(f"⚠️ Could not load models on startup: {str(e)}")
    logger.info("Models will be trained on first recommendation request.")

__all__ = ["recommender", "market_data", "train_models"]
