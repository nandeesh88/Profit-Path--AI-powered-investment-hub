"""
Model Training and Initialization Script
Run this to train ML models with real financial data before starting the API.
This script should be run once during initial setup and can be re-run to retrain models.

Usage:
    python train_models_setup.py
"""
import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main training pipeline."""
    try:
        logger.info("=" * 80)
        logger.info("🚀 PROFIT-PATH AI INVESTMENT MODEL TRAINING")
        logger.info("=" * 80)
        
        # Import training module
        from ai_engine.train_models import train_and_save_models
        
        logger.info("\n📊 Phase 1: Training ML Models with Real Financial Data")
        logger.info("-" * 80)
        
        # Train models
        scaler, risk_clf, return_reg, risk_logistic, kmeans = train_and_save_models()
        
        logger.info("\n✅ Model training complete!")
        logger.info(f"   - Feature Scaler: StandardScaler")
        logger.info(f"   - Risk Classifier: RandomForestClassifier (n=200 trees)")
        logger.info(f"   - Return Regressor: GradientBoostingRegressor")
        logger.info(f"   - Risk Logistic: LogisticRegression")
        logger.info(f"   - User Segmentation: KMeans (k=5 clusters)")
        
        logger.info("\n📈 Phase 2: Testing Recommendation Engine")
        logger.info("-" * 80)
        
        # Test the recommendation system
        from ai_engine.recommender import generate_recommendation
        
        test_cases = [
            {
                "name": "Conservative Investor",
                "monthly_income": 75000,
                "monthly_expenses": 55000,
                "risk_tolerance": "low",
                "financial_goal": "Safety and steady growth",
                "age": 45,
                "investment_horizon_years": 8,
            },
            {
                "name": "Balanced Investor",
                "monthly_income": 100000,
                "monthly_expenses": 70000,
                "risk_tolerance": "medium",
                "financial_goal": "Wealth creation and retirement",
                "age": 35,
                "investment_horizon_years": 15,
            },
            {
                "name": "Aggressive Investor",
                "monthly_income": 150000,
                "monthly_expenses": 60000,
                "risk_tolerance": "high",
                "financial_goal": "Maximum growth and wealth accumulation",
                "age": 28,
                "investment_horizon_years": 25,
            },
        ]
        
        for test in test_cases:
            logger.info(f"\nTesting: {test['name']}")
            logger.info(f"  Income: ₹{test['monthly_income']:,.0f}/month")
            logger.info(f"  Expenses: ₹{test['monthly_expenses']:,.0f}/month")
            logger.info(f"  Savings: ₹{test['monthly_income'] - test['monthly_expenses']:,.0f}/month")
            logger.info(f"  Risk: {test['risk_tolerance'].upper()}")
            
            try:
                rec = generate_recommendation(
                    monthly_income=test["monthly_income"],
                    monthly_expenses=test["monthly_expenses"],
                    risk_tolerance=test["risk_tolerance"],
                    financial_goal=test["financial_goal"],
                    age=test["age"],
                    investment_horizon_years=test["investment_horizon_years"],
                )
                
                logger.info(f"  ✅ Segment: {rec['user_segment']}")
                logger.info(f"  ✅ Expected Return: {rec['expected_return_percent']:.2f}%")
                logger.info(f"  ✅ Monthly SIP: ₹{rec['sip_recommendation']['monthly_sip_amount']:,.0f}")
                logger.info(f"  ✅ Portfolio - Stocks: {rec['portfolio_allocation']['stocks_percent']}%, "
                           f"MF: {rec['portfolio_allocation']['mutual_funds_percent']}%, "
                           f"SIP: {rec['portfolio_allocation']['sip_percent']}%, "
                           f"Emergency: {rec['portfolio_allocation']['emergency_fund_percent']}%")
            except Exception as e:
                logger.error(f"  ❌ Error: {str(e)}", exc_info=True)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ TRAINING AND TESTING COMPLETE!")
        logger.info("=" * 80)
        logger.info("\n📝 Next Steps:")
        logger.info("  1. Start the FastAPI backend: python main.py")
        logger.info("  2. Test investment endpoints:")
        logger.info("     POST /api/v1/investments/recommend")
        logger.info("  3. Monitor logs for real-time model inference")
        logger.info("\n" + "=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Training failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
