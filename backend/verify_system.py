#!/usr/bin/env python
"""
System Verification & Health Check Script
Run this to verify that the AI Investment Recommendation Engine is working correctly.
"""
import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_check(status, message):
    """Print check result."""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {message}")

def verify_imports():
    """Verify all required packages are installed."""
    print_header("1. DEPENDENCY CHECK")
    
    dependencies = {
        "numpy": "Data processing",
        "pandas": "Data manipulation",
        "scikit-learn": "Machine learning",
        "yfinance": "Financial data",
        "fastapi": "Web framework",
        "pydantic": "Data validation",
        "motor": "Async MongoDB",
    }
    
    all_ok = True
    for package, description in dependencies.items():
        try:
            __import__(package)
            print_check(True, f"{package:<15} - {description}")
        except ImportError:
            print_check(False, f"{package:<15} - {description} [MISSING]")
            all_ok = False
    
    return all_ok

def verify_ai_modules():
    """Verify AI engine modules exist and can be imported."""
    print_header("2. AI ENGINE MODULES")
    
    all_ok = True
    
    # Check market_data module
    try:
        from ai_engine.market_data import MarketDataFetcher, fetch_real_stock_recommendations
        print_check(True, "market_data.py - Real financial data module")
    except Exception as e:
        print_check(False, f"market_data.py - {str(e)}")
        all_ok = False
    
    # Check train_models module
    try:
        from ai_engine.train_models import RealFinancialDataTrainer, load_models
        print_check(True, "train_models.py - ML model training module")
    except Exception as e:
        print_check(False, f"train_models.py - {str(e)}")
        all_ok = False
    
    # Check recommender module
    try:
        from ai_engine.recommender import generate_recommendation
        print_check(True, "recommender.py - Recommendation engine")
    except Exception as e:
        print_check(False, f"recommender.py - {str(e)}")
        all_ok = False
    
    return all_ok

def verify_models():
    """Verify trained models exist."""
    print_header("3. TRAINED MODELS")
    
    model_dir = Path(__file__).parent / "ai_engine" / "saved_models"
    model_files = [
        "scaler.pkl",
        "risk_clf.pkl",
        "return_reg.pkl",
        "risk_logistic.pkl",
        "kmeans.pkl",
    ]
    
    all_ok = True
    for model_file in model_files:
        model_path = model_dir / model_file
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print_check(True, f"{model_file:<20} ({size_mb:.2f} MB)")
        else:
            print_check(False, f"{model_file:<20} [NOT FOUND]")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Models not found. Run: python train_models_setup.py")
    
    return all_ok

def verify_recommendation():
    """Test recommendation generation."""
    print_header("4. RECOMMENDATION ENGINE TEST")
    
    try:
        from ai_engine.recommender import generate_recommendation
        
        print("Generating recommendation for test user...")
        rec = generate_recommendation(
            monthly_income=100000,
            monthly_expenses=70000,
            risk_tolerance="medium",
            financial_goal="Wealth creation and retirement",
            age=35,
            investment_horizon_years=15,
        )
        
        print_check(True, "Recommendation generation successful")
        print(f"  ├─ User Segment: {rec['user_segment']}")
        print(f"  ├─ Risk Profile: {rec['risk_profile']}")
        print(f"  ├─ Monthly Savings: ₹{rec['monthly_savings']:,.0f}")
        print(f"  ├─ Investable Amount: ₹{rec['investable_amount']:,.0f}")
        print(f"  ├─ Expected Return: {rec['expected_return_percent']}%")
        print(f"  ├─ Monthly SIP: ₹{rec['sip_recommendation']['monthly_sip_amount']:,.0f}")
        print(f"  ├─ 5-Year Corpus: ₹{rec['sip_recommendation']['expected_corpus_5yr']:,.0f}")
        print(f"  ├─ 10-Year Corpus: ₹{rec['sip_recommendation']['expected_corpus_10yr']:,.0f}")
        print(f"  └─ Stock Recommendations: {len(rec['stock_recommendations'])} stocks")
        
        return True
    except Exception as e:
        print_check(False, f"Recommendation generation failed: {str(e)}")
        return False

def verify_market_data():
    """Test market data fetching."""
    print_header("5. MARKET DATA TEST")
    
    try:
        from ai_engine.market_data import fetch_real_stock_recommendations, get_market_overall_metrics
        
        print("Testing stock recommendations (Medium Risk)...")
        stocks = fetch_real_stock_recommendations("medium")
        
        if stocks:
            print_check(True, f"Fetched {len(stocks)} real stock recommendations")
            for stock in stocks[:2]:
                print(f"  ├─ {stock['ticker']}: {stock['cagr']:.1f}% CAGR, Sharpe {stock['sharpe_ratio']:.2f}")
        else:
            print_check(False, "No stock data retrieved")
            return False
        
        print("\nTesting market indices...")
        market_metrics = get_market_overall_metrics()
        
        if market_metrics:
            print_check(True, f"Fetched {len(market_metrics)} market indices")
            for market_name, metrics in list(market_metrics.items())[:2]:
                print(f"  ├─ {market_name}: {metrics['current_level']:.2f} ({metrics['yoy_return']:.1f}% YoY)")
        else:
            print_check(False, "No market data retrieved")
        
        return True
    except Exception as e:
        print_check(False, f"Market data test failed: {str(e)}")
        return False

def verify_pydantic_models():
    """Verify Pydantic request/response models."""
    print_header("6. PYDANTIC MODELS")
    
    try:
        from schemas.investment import (
            InvestmentRequest,
            InvestmentRecommendationResponse,
            PortfolioAllocation,
        )
        
        # Test request validation
        req = InvestmentRequest(
            monthly_income=100000,
            monthly_expenses=70000,
            risk_tolerance="medium",
            financial_goal="Wealth creation",
        )
        print_check(True, "InvestmentRequest model validation")
        
        # Test response model
        resp_data = {
            "user_segment": "Balanced Builder",
            "risk_profile": "medium",
            "ml_predicted_risk": "medium",
            "monthly_savings": 30000,
            "savings_rate_percent": 30,
            "investable_amount": 24000,
            "portfolio_allocation": {
                "stocks_percent": 30,
                "mutual_funds_percent": 35,
                "sip_percent": 25,
                "emergency_fund_percent": 10,
            },
            "stock_recommendations": [],
            "mutual_fund_recommendations": [],
            "sip_recommendation": {
                "monthly_sip_amount": 6000,
                "recommended_fund": "Balanced Fund",
                "expected_corpus_5yr": 427500,
                "expected_corpus_10yr": 1087500,
            },
            "expected_return_percent": 11.5,
            "investment_timeframe": "long-term",
            "financial_advice": ["Test advice"],
            "generated_at": "2026-03-03T14:30:00",
        }
        resp = InvestmentRecommendationResponse(**resp_data)
        print_check(True, "InvestmentRecommendationResponse model validation")
        
        return True
    except Exception as e:
        print_check(False, f"Pydantic models test failed: {str(e)}")
        return False

def verify_file_structure():
    """Verify expected file structure."""
    print_header("7. FILE STRUCTURE")
    
    backend_dir = Path(__file__).parent
    required_files = {
        "ai_engine/market_data.py": "Market data module",
        "ai_engine/train_models.py": "Model training module",
        "ai_engine/recommender.py": "Recommendation engine",
        "routers/investments.py": "Investment API routes",
        "schemas/investment.py": "Investment schemas",
        "train_models_setup.py": "Training setup script",
        "AI_ENGINE_README.md": "Complete documentation",
        "QUICKSTART.md": "Quick start guide",
        "DEPLOYMENT_CONFIG.md": "Deployment configuration",
    }
    
    all_ok = True
    for file_path, description in required_files.items():
        full_path = backend_dir / file_path
        if full_path.exists():
            print_check(True, f"{file_path:<35} - {description}")
        else:
            print_check(False, f"{file_path:<35} - {description} [MISSING]")
            all_ok = False
    
    return all_ok

def verify_requirements():
    """Check if all requirements are installed."""
    print_header("8. REQUIREMENTS.TXT")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"Total packages: {len(packages)}")
        print("\nKey packages (first 10):")
        for pkg in packages[:10]:
            print(f"  ├─ {pkg}")
        
        print_check(True, "requirements.txt found and readable")
        return True
    else:
        print_check(False, "requirements.txt not found")
        return False

def run_all_checks():
    """Run all verification checks."""
    print("\n" + "🚀 " * 20)
    print("PROFIT-PATH AI INVESTMENT ENGINE - SYSTEM VERIFICATION")
    print("🚀 " * 20)
    
    results = {
        "Dependencies": verify_imports(),
        "AI Modules": verify_ai_modules(),
        "Models": verify_models(),
        "Market Data": verify_market_data(),
        "Pydantic Models": verify_pydantic_models(),
        "File Structure": verify_file_structure(),
        "Requirements.txt": verify_requirements(),
        "Recommendation Engine": verify_recommendation(),
    }
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for check_name, status in results.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {check_name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED - SYSTEM READY FOR DEPLOYMENT!")
        print("\n📝 Next Steps:")
        print("  1. Run: python main.py")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Test the /api/v1/investments/recommend endpoint")
        print("\n📚 Documentation:")
        print("  - AI_ENGINE_README.md - Full system documentation")
        print("  - QUICKSTART.md - 5-minute setup guide")
        print("  - DEPLOYMENT_CONFIG.md - Production deployment")
        return 0
    else:
        print(f"\n⚠️  {total - passed} issues found. Please fix them before deployment.")
        print("\n🔧 Common fixes:")
        print("  - Missing models? Run: python train_models_setup.py")
        print("  - Missing packages? Run: pip install -r requirements.txt")
        print("  - Import errors? Check Python path and module locations")
        return 1

if __name__ == "__main__":
    exit_code = run_all_checks()
    sys.exit(exit_code)
