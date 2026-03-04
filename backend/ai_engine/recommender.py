"""
AI Investment Recommendation Engine (Production-Ready)
Uses trained ML models with real financial market data.
- Risk classification via RandomForest + Logistic Regression
- Return prediction via Gradient Boosting
- Portfolio optimization with real market data
- User segmentation via KMeans clustering
"""
import numpy as np
import pandas as pd
import joblib
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict

try:
    from .train_models import load_models
    from .market_data import (
        fetch_real_stock_recommendations,
        get_market_overall_metrics,
        MarketDataFetcher,
    )
except ImportError:
    from train_models import load_models
    from market_data import (
        fetch_real_stock_recommendations,
        get_market_overall_metrics,
        MarketDataFetcher,
    )

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)

# User segments (from KMeans clustering)
SEGMENT_NAMES = {
    0: "Conservative Saver",
    1: "Balanced Builder",
    2: "Aggressive Grower",
    3: "Income Maximizer",
    4: "Wealth Accumulator",
}

RISK_LABELS = {0: "low", 1: "medium", 2: "high"}

# Portfolio allocation recommendations based on risk profile
PORTFOLIO_BY_RISK = {
    "low": {
        "stocks": 15,
        "mutual_funds": 40,
        "sip": 25,
        "emergency_fund": 20
    },
    "medium": {
        "stocks": 30,
        "mutual_funds": 35,
        "sip": 25,
        "emergency_fund": 10
    },
    "high": {
        "stocks": 50,
        "mutual_funds": 25,
        "sip": 20,
        "emergency_fund": 5
    },
}

# Real stock recommendations by risk (fallback when live data unavailable)
STOCK_RECS_TEMPLATE = {
    "low": [
        {
            "category": "Large Cap – India",
            "ticker": "TCS.NS",
            "current_price": None,
            "description": "TCS: India's largest IT company. Consistent dividend payer, strong cash flows.",
            "risk_level": "low",
            "expected_return_range": "10–14%"
        },
        {
            "category": "Large Cap – India",
            "ticker": "INFY.NS",
            "current_price": None,
            "description": "Infosys: Blue-chip IT bellwether. Stable earnings growth and buyback history.",
            "risk_level": "low",
            "expected_return_range": "10–14%"
        },
        {
            "category": "Large Cap – US",
            "ticker": "MSFT",
            "current_price": None,
            "description": "Microsoft: Cloud (Azure) + AI leader. Strong moat, recurring revenue.",
            "risk_level": "low",
            "expected_return_range": "10–15%"
        },
    ],
    "medium": [
        {
            "category": "Large Cap – India",
            "ticker": "RELIANCE.NS",
            "current_price": None,
            "description": "Reliance Industries: Diversified conglomerate – energy, retail, Jio telecom.",
            "risk_level": "medium",
            "expected_return_range": "12–18%"
        },
        {
            "category": "Large Cap – India",
            "ticker": "HDFC.NS",
            "current_price": None,
            "description": "HDFC Bank: India's largest private bank. Best-in-class asset quality.",
            "risk_level": "medium",
            "expected_return_range": "12–16%"
        },
        {
            "category": "Large Cap – US",
            "ticker": "AAPL",
            "current_price": None,
            "description": "Apple: Services revenue growing 20%+ YoY. World's most valuable brand.",
            "risk_level": "medium",
            "expected_return_range": "12–18%"
        },
        {
            "category": "Large Cap – US",
            "ticker": "GOOGL",
            "current_price": None,
            "description": "Alphabet (Google): Search + YouTube + Cloud. AI integration across products.",
            "risk_level": "medium",
            "expected_return_range": "14–20%"
        },
    ],
    "high": [
        {
            "category": "Mid Cap – India",
            "ticker": "BAJAJFINSV.NS",
            "current_price": None,
            "description": "Bajaj Finserv: High-growth financial services conglomerate. Lending + insurance.",
            "risk_level": "high",
            "expected_return_range": "16–25%"
        },
        {
            "category": "Large Cap – US",
            "ticker": "NVDA",
            "current_price": None,
            "description": "NVIDIA: AI chip leader. Data-center revenue tripled. Dominant GPU maker.",
            "risk_level": "high",
            "expected_return_range": "20–35%"
        },
        {
            "category": "Large Cap – US",
            "ticker": "TSLA",
            "current_price": None,
            "description": "Tesla: EV market leader. Energy + FSD potential. High volatility, high reward.",
            "risk_level": "high",
            "expected_return_range": "15–30%"
        },
        {
            "category": "Large Cap – US",
            "ticker": "AMZN",
            "current_price": None,
            "description": "Amazon: AWS cloud dominance + e-commerce. AI/ML infrastructure leader.",
            "risk_level": "high",
            "expected_return_range": "15–24%"
        },
    ],
}

# Real mutual fund recommendations by risk (actual fund names available in India)
MF_RECS = {
    "low": [
        {
            "fund_type": "Debt Fund",
            "fund_name": "HDFC Corporate Bond Fund – Direct Growth",
            "description": "AAA-rated corporate bonds, 3yr CAGR ~7.5%. Ideal for stable, low-risk returns.",
            "risk_level": "low",
            "expected_return_range": "6–8%"
        },
        {
            "fund_type": "Liquid Fund",
            "fund_name": "Axis Liquid Fund – Direct Growth",
            "description": "Ultra-short term money-market instruments. Ideal parking fund, 1yr return ~7%.",
            "risk_level": "low",
            "expected_return_range": "5–7%"
        },
        {
            "fund_type": "Conservative Hybrid",
            "fund_name": "SBI Conservative Hybrid Fund – Direct Growth",
            "description": "75% debt + 25% equity blend. 3yr CAGR ~9%. Good for first-time investors.",
            "risk_level": "low",
            "expected_return_range": "7–10%"
        },
    ],
    "medium": [
        {
            "fund_type": "Balanced Hybrid Fund",
            "fund_name": "ICICI Prudential Balanced Advantage Fund – Direct Growth",
            "description": "Dynamic equity-debt allocation based on market valuations. 5yr CAGR ~12%.",
            "risk_level": "medium",
            "expected_return_range": "9–13%"
        },
        {
            "fund_type": "Large Cap Fund",
            "fund_name": "Mirae Asset Large Cap Fund – Direct Growth",
            "description": "Top-50 Nifty companies. Consistent 5yr CAGR ~14%. Best-in-class large cap.",
            "risk_level": "medium",
            "expected_return_range": "11–15%"
        },
        {
            "fund_type": "ELSS (Tax Saving)",
            "fund_name": "Quant ELSS Tax Saver Fund – Direct Growth",
            "description": "3yr lock-in with 80C tax benefit. 5yr CAGR ~25%. Top-performing ELSS.",
            "risk_level": "medium",
            "expected_return_range": "12–18%"
        },
        {
            "fund_type": "Flexi Cap Fund",
            "fund_name": "Parag Parikh Flexi Cap Fund – Direct Growth",
            "description": "Multi-cap + international diversification. 5yr CAGR ~18%. Highly rated.",
            "risk_level": "medium",
            "expected_return_range": "12–16%"
        },
    ],
    "high": [
        {
            "fund_type": "Small Cap Fund",
            "fund_name": "Quant Small Cap Fund – Direct Growth",
            "description": "Aggressive small-cap bets. 5yr CAGR ~35%. Highest returns in category.",
            "risk_level": "high",
            "expected_return_range": "18–30%"
        },
        {
            "fund_type": "Mid Cap Fund",
            "fund_name": "Motilal Oswal Midcap Fund – Direct Growth",
            "description": "Focused mid-cap portfolio. 3yr CAGR ~25%. Strong stock-picking track record.",
            "risk_level": "high",
            "expected_return_range": "15–22%"
        },
        {
            "fund_type": "Sectoral – Technology",
            "fund_name": "ICICI Prudential Technology Fund – Direct Growth",
            "description": "IT sector exposure (TCS, Infosys, HCL). 5yr CAGR ~18%. Tech growth play.",
            "risk_level": "high",
            "expected_return_range": "14–22%"
        },
        {
            "fund_type": "International Fund",
            "fund_name": "Motilal Oswal Nasdaq 100 FOF – Direct Growth",
            "description": "US tech giants exposure (Apple, Google, Nvidia). 5yr CAGR ~20%.",
            "risk_level": "high",
            "expected_return_range": "14–20%"
        },
    ],
}

# Financial advice based on risk profile
ADVICE_TEMPLATES = {
    "low": [
        "✅ Build a 6-month emergency fund before investing.",
        "✅ Start with debt funds and gradually shift to balanced funds.",
        "✅ Consider regular fixed deposits or recurring deposits for discipline.",
        "✅ Increase equity exposure gradually as your income grows.",
        "✅ Focus on capital preservation and steady growth.",
    ],
    "medium": [
        "✅ Maintain a 3-4 month emergency fund (liquid investments).",
        "✅ Diversify across large-cap, mid-cap, and debt instruments.",
        "✅ Start a monthly SIP into balanced or hybrid funds.",
        "✅ Review your portfolio every quarter and rebalance if needed.",
        "✅ Take advantage of tax-saving instruments (ELSS under 80C).",
        "✅ Consider both mutual funds and direct stock investment.",
    ],
    "high": [
        "✅ Keep 1-month emergency fund; invest rest aggressively.",
        "✅ Maximum equity exposure (50-60% of investable amount).",
        "✅ Mix large-cap, mid-cap, and small-cap investments.",
        "✅ Consider international funds to hedge domestic market risk.",
        "✅ Monitor portfolio monthly; be ready to cut losses quickly.",
        "✅ Explore direct stock investing alongside mutual funds.",
        "✅ Use leverage cautiously for potential alpha generation.",
    ],
}


def _goal_to_code(financial_goal: str) -> int:
    """Convert financial goal string to numeric code."""
    goal = (financial_goal or "").strip().lower()
    if any(k in goal for k in ["retire", "pension", "retirement"]):
        return 0
    if any(k in goal for k in ["home", "house", "property", "real estate"]):
        return 1
    if any(k in goal for k in ["education", "college", "study", "kids", "child"]):
        return 2
    if any(k in goal for k in ["wealth", "growth", "invest", "corpus", "millionaire"]):
        return 3
    if any(k in goal for k in ["emergency", "safety", "buffer", "contingency"]):
        return 4
    return 3  # Default: wealth creation


def _sip_corpus(monthly: float, rate_annual: float, years: int) -> float:
    """Calculate future value of monthly SIP investment."""
    monthly = max(monthly, 0)
    rate_annual = max(rate_annual, 0)
    years = max(years, 1)
    
    r = rate_annual / 100 / 12
    n = years * 12
    
    if r == 0:
        return monthly * n
    
    return monthly * (((1 + r) ** n - 1) / r) * (1 + r)


def _get_real_stock_recommendations(risk_level: str) -> List[Dict]:
    """Fetch real stock recommendations from market data."""
    try:
        recs = fetch_real_stock_recommendations(risk_level)
        
        # Convert to recommendation format
        formatted_recs = []
        for rec in recs[:5]:  # Top 5 stocks
            formatted_recs.append({
                "category": f"{rec['risk_classification']}-Cap Equity",
                "ticker": rec['ticker'],
                "current_price": round(rec['current_price'], 2),
                "description": f"{rec['ticker']}: {rec['cagr']:.1f}% CAGR, Sharpe Ratio {rec['sharpe_ratio']:.2f}, Beta {rec['beta']:.2f}, 6M Momentum {rec['momentum_6m']:.1f}%",
                "risk_level": rec['risk_classification'].lower() if rec['risk_classification'].lower() in ('low','medium','high') else risk_level,
                "expected_return_range": rec['expected_return_range'],
            })
        
        # If we don't have enough real data, fill with templates
        template_recs = STOCK_RECS_TEMPLATE.get(risk_level, [])
        while len(formatted_recs) < len(template_recs):
            formatted_recs.append(template_recs[len(formatted_recs)])
        
        return formatted_recs
    except Exception as e:
        logger.warning(f"Could not fetch real stock data: {str(e)}. Using templates.")
        return STOCK_RECS_TEMPLATE.get(risk_level, [])


def load_recommendation_models():
    """Load trained ML models."""
    try:
        return load_models()
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise


def generate_recommendation(
    monthly_income: float,
    monthly_expenses: float,
    risk_tolerance: str,  # "low", "medium", "high"
    financial_goal: str,
    savings: Optional[float] = None,
    age: int = 30,
    investment_horizon_years: int = 5,
) -> dict:
    """
    Generate personalized investment recommendations using real ML models and market data.
    
    Args:
        monthly_income: User's monthly gross income
        monthly_expenses: User's monthly total expenses
        risk_tolerance: User's risk preference ("low", "medium", "high")
        financial_goal: User's investment goal
        savings: Optional precomputed savings (else = income - expenses)
        age: User's age in years
        investment_horizon_years: Investment time horizon
    
    Returns:
        Dictionary with comprehensive investment recommendations
    """
    try:
        logger.info(f"Generating recommendations for user: income={monthly_income}, "
                   f"expenses={monthly_expenses}, risk={risk_tolerance}")
        
        # Load trained models
        scaler, risk_clf, return_reg, risk_logistic, kmeans = load_recommendation_models()
        
        # Calculate savings
        computed_savings = max(monthly_income - monthly_expenses, 0)
        savings = computed_savings if savings is None else max(savings, 0)
        savings_rate = savings / monthly_income if monthly_income > 0 else 0
        goal_code = _goal_to_code(financial_goal)
        user_risk_num = {"low": 0, "medium": 1, "high": 2}.get(risk_tolerance, 1)
        
        logger.info(f"Computed savings: {savings:.2f}, Savings rate: {savings_rate:.2%}")
        
        # Prepare features for ML prediction
        # Features: [monthly_income, monthly_expenses, savings, savings_rate, age, goal_code, beta, volatility]
        # For prediction, we'll use reasonable defaults for derived features
        beta = 0.6 + user_risk_num * 0.4  # 0.6 (low), 1.0 (medium), 1.4 (high)
        volatility = 12 + user_risk_num * 12  # 12% (low), 24% (medium), 36% (high)
        
        X = np.array([[
            monthly_income,
            monthly_expenses,
            savings,
            savings_rate,
            age,
            goal_code,
            beta,
            volatility,
        ]])
        
        X_scaled = scaler.transform(X)
        
        # ML predictions
        ml_risk_label = int(risk_clf.predict(X_scaled)[0])
        ml_risk_str = RISK_LABELS.get(ml_risk_label, "medium")
        
        # Risk probability predictions
        try:
            risk_probs = risk_clf.predict_proba(X_scaled)[0]
            logger.info(f"Risk probabilities: low={risk_probs[0]:.2%}, "
                       f"medium={risk_probs[1] if len(risk_probs) > 1 else 0:.2%}, "
                       f"high={risk_probs[2] if len(risk_probs) > 2 else 0:.2%}")
        except:
            pass
        
        # Blend user-provided risk with ML-predicted risk
        blended_risk_num = round((ml_risk_label + user_risk_num) / 2)
        blended_risk = RISK_LABELS.get(blended_risk_num, "medium")
        
        logger.info(f"ML predicted risk: {ml_risk_str}, User input: {risk_tolerance}, "
                   f"Blended: {blended_risk}")
        
        # Predict expected return
        predicted_return = float(return_reg.predict(X_scaled)[0])
        predicted_return = np.clip(predicted_return, 5, 25)  # Realistic bounds
        
        logger.info(f"Predicted expected return: {predicted_return:.2f}%")
        
        # User segmentation
        segment_id = int(kmeans.predict(X_scaled)[0])
        segment_name = SEGMENT_NAMES.get(segment_id, "Balanced Builder")
        
        logger.info(f"User segment: {segment_name} (cluster {segment_id})")
        
        # Portfolio allocation
        alloc = PORTFOLIO_BY_RISK.get(blended_risk, PORTFOLIO_BY_RISK["medium"])
        
        # Calculate investable amount (80% of savings, keep 20% as buffer)
        investable = savings * 0.80
        sip_amount = investable * (alloc["sip"] / 100)
        
        # Investment timeframe
        if investment_horizon_years <= 2:
            timeframe = "short-term"
        elif investment_horizon_years <= 7:
            timeframe = "medium-term"
        else:
            timeframe = "long-term"
        
        # SIP projections using realistic rates based on risk profile
        sip_rates = {"low": 7.5, "medium": 11.0, "high": 15.0}
        sip_rate = sip_rates.get(blended_risk, 11.0)
        corpus_5yr = _sip_corpus(sip_amount, sip_rate, 5)
        corpus_10yr = _sip_corpus(sip_amount, sip_rate, 10)
        
        # SIP fund recommendation
        sip_fund_map = {
            "low": "Multi-Asset / Balanced Fund SIP",
            "medium": "Balanced Hybrid / ELSS Fund SIP",
            "high": "Aggressive Hybrid / Mid-Cap SIP",
        }
        
        # Get real stock recommendations (with fallback to templates)
        stock_recs = _get_real_stock_recommendations(blended_risk)
        
        # Fetch market context
        try:
            market_metrics = get_market_overall_metrics()
            logger.info(f"Market metrics: {market_metrics}")
        except:
            market_metrics = {}
        
        logger.info("✅ Recommendation generation complete")
        
        return {
            "user_segment": segment_name,
            "risk_profile": blended_risk,
            "ml_predicted_risk": ml_risk_str,
            "monthly_savings": round(savings, 2),
            "savings_rate_percent": round(savings_rate * 100, 2),
            "investable_amount": round(investable, 2),
            "portfolio_allocation": {
                "stocks_percent": alloc["stocks"],
                "mutual_funds_percent": alloc["mutual_funds"],
                "sip_percent": alloc["sip"],
                "emergency_fund_percent": alloc["emergency_fund"],
            },
            "stock_recommendations": stock_recs,
            "mutual_fund_recommendations": MF_RECS.get(blended_risk, []),
            "sip_recommendation": {
                "monthly_sip_amount": round(max(sip_amount, 500), 2),  # Minimum SIP amount
                "recommended_fund": sip_fund_map.get(blended_risk, "Balanced Fund"),
                "expected_corpus_5yr": round(corpus_5yr, 2),
                "expected_corpus_10yr": round(corpus_10yr, 2),
            },
            "expected_return_percent": round(predicted_return, 2),
            "investment_timeframe": timeframe,
            "financial_advice": ADVICE_TEMPLATES.get(blended_risk, []),
            "market_context": market_metrics,
            "generated_at": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"Error in recommendation generation: {str(e)}", exc_info=True)
        raise
