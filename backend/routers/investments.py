"""
Investment Recommendations Router (Production-Ready)
Handles API endpoints for AI-powered investment recommendations with real market data.
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import hashlib
import logging

from core.deps import get_current_user
from core.database import get_collection
from core.config import settings
from core.cache import get_or_compute_recommendation
from core.logging_config import RequestTimer
from schemas.investment import InvestmentRequest, InvestmentRecommendationResponse
from ai_engine.recommender import generate_recommendation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/investments", tags=["Investments"])


@router.post("/recommend", response_model=InvestmentRecommendationResponse)
async def get_recommendation(
    data: InvestmentRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate personalized investment recommendations based on user's financial profile.
    
    Uses real market data and trained ML models to provide:
    - Risk profile classification
    - Portfolio allocation
    - Stock and mutual fund recommendations
    - SIP planning
    - Expected returns
    
    Args:
        data: User's financial information
        current_user: Authenticated user
    
    Returns:
        Comprehensive investment recommendation with market analysis
    """
    try:
        logger.info(f"Generating recommendation for user {current_user.get('_id')}")

        # Build a cache key from the request inputs
        cache_key = hashlib.md5(
            f"{data.monthly_income}:{data.monthly_expenses}:{data.savings}:"
            f"{data.risk_tolerance}:{data.financial_goal}:{data.age}:"
            f"{data.investment_horizon_years}".encode()
        ).hexdigest()

        with RequestTimer("recommendation") as timer:
            result = get_or_compute_recommendation(
                key=cache_key,
                generator_fn=generate_recommendation,
                monthly_income=data.monthly_income,
                monthly_expenses=data.monthly_expenses,
                savings=data.savings,
                risk_tolerance=data.risk_tolerance,
                financial_goal=data.financial_goal,
                age=data.age or 30,
                investment_horizon_years=data.investment_horizon_years or 5,
            )

        logger.info(f"✅ Recommendation generated in {timer.elapsed_ms:.1f}ms")
        
    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"AI engine error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI engine error: {str(e)}")

    try:
        if not settings.ENABLE_DATABASE_PERSISTENCE:
            logger.debug("Database persistence disabled via feature flag")
        else:
            # Persist recommendation to database
            investments = get_collection("investments")
            await investments.insert_one({
                "user_id": current_user["_id"],
                "input": data.model_dump(),
                "recommendation": {
                    **result,
                    "generated_at": result["generated_at"].isoformat(),
                },
                "created_at": datetime.utcnow(),
            })
            logger.info("✅ Recommendation saved to database")
    except Exception as e:
        logger.warning(f"Could not save recommendation to database: {str(e)}")
        # Don't fail the API call if database persistence fails

    return InvestmentRecommendationResponse(**result)


@router.get("/history")
async def get_recommendation_history(current_user: dict = Depends(get_current_user)):
    """
    Retrieve the user's recommendation history.
    
    Returns:
        List of previous recommendations (up to 10, sorted by most recent)
    """
    try:
        investments = get_collection("investments")
        cursor = investments.find(
            {"user_id": current_user["_id"]},
            {"_id": 0, "user_id": 0},
        ).sort("created_at", -1).limit(10)

        results = []
        async for doc in cursor:
            doc["created_at"] = doc["created_at"].isoformat()
            results.append(doc)
        
        logger.info(f"Retrieved {len(results)} recommendations from history")
        return results
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


@router.get("/market-status")
async def get_market_status(current_user: dict = Depends(get_current_user)):
    """
    Get current market status and indices.
    
    Returns:
        Real-time market metrics for reference
    """
    try:
        from ai_engine.market_data import get_market_overall_metrics
        
        metrics = get_market_overall_metrics()
        logger.info(f"Market metrics retrieved: {list(metrics.keys())}")
        
        return {
            "market_metrics": metrics,
            "last_updated": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error fetching market metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching market metrics: {str(e)}")

