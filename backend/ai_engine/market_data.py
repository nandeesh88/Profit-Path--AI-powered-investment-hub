"""
Real-Time Financial Market Data Fetcher
Fetches actual stock and mutual fund data from live APIs.
Uses yfinance for stocks and historical OHLC data.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Major Indian and US stocks with real data available
RECOMMENDED_STOCKS = {
    "Low Risk": [
        "TCS.NS",      # Tata Consultancy Services (India)
        "INFY.NS",     # Infosys (India)
        "MSFT",        # Microsoft
        "JNJ",         # Johnson & Johnson
        "PG",          # Procter & Gamble
    ],
    "Medium Risk": [
        "HDFC.NS",     # HDFC Bank (India)
        "RELIANCE.NS",  # Reliance Industries (India)
        "AAPL",        # Apple
        "GOOGL",       # Google
        "AMZN",        # Amazon
    ],
    "High Risk": [
        "WIPRO.NS",    # Wipro (India)
        "BAJAJFINSV.NS",  # Bajaj Finance (India)
        "NVDA",        # NVIDIA
        "TSLA",        # Tesla
        "MSTR",        # MicroStrategy
    ],
}

# Mutual Fund data - using NSE AMC fund codes
MUTUAL_FUND_CODES = {
    "Low Risk Debt": [
        "LIQUID_FUNDS",
        "SHORT_DURATION_DEBT",
        "CONSERVATIVE_HYBRIDS",
    ],
    "Medium Risk Hybrid": [
        "BALANCED_HYBRID",
        "DYNAMIC_ASSET_ALLOCATION",
        "FLEXIBLE_ALLOCATION",
    ],
    "High Risk Equity": [
        "LARGE_CAP_EQUITY",
        "MULTI_CAP_EQUITY",
        "DIVERSIFIED_EQUITY",
        "SMALL_CAP",
        "MID_CAP",
    ],
}


# Global cache to prevent API spam across user requests (saves ~5-10 seconds per API hit)
_market_data_cache = {}

class MarketDataFetcher:
    """Fetches real stock prices, historical data, and derived metrics."""
    
    def __init__(self, lookback_years: int = 5):
        self.lookback_years = lookback_years
        self.lookback_date = datetime.now() - timedelta(days=lookback_years * 365)
    
    def fetch_stock_data(
        self,
        ticker: str,
        period: str = "5y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """Fetch historical OHLCV data for a stock."""
        cache_key = f"{ticker}_{period}_{interval}"
        if cache_key in _market_data_cache:
            return _market_data_cache[cache_key]

        try:
            logger.info(f"Fetching data for {ticker}...")
            stock = yf.Ticker(ticker)
            
            # Get historical data
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                logger.warning(f"No data found for {ticker}")
                return None
            
            _market_data_cache[cache_key] = hist
            return hist
        except Exception as e:
            logger.error(f"Error fetching {ticker}: {str(e)}")
            return None
    
    def get_stock_metrics(self, ticker: str) -> Optional[Dict]:
        """Calculate technical metrics for a stock."""
        try:
            hist = self.fetch_stock_data(ticker, period="5y")
            
            if hist is None or len(hist) < 30:
                return None
            
            # Calculate metrics
            returns = hist['Close'].pct_change()
            
            # Volatility (annualized)
            volatility = returns.std() * np.sqrt(252)
            
            # CAGR (Compound Annual Growth Rate)
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            days_held = len(hist)
            years = days_held / 365.25
            cagr = (end_price / start_price) ** (1 / years) - 1 if years > 0 else 0
            
            # Current price
            current_price = hist['Close'].iloc[-1]
            
            # 52-week high/low
            last_year = hist.tail(252)
            high_52w = last_year['Close'].max()
            low_52w = last_year['Close'].min()
            
            # Sharpe ratio (assuming 6% risk-free rate)
            daily_rf = 0.06 / 252
            sharpe = (returns.mean() - daily_rf) / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            
            # Beta (vs market proxy - using SPY for global, ^NSEI for India)
            market_ticker = "^NSEI" if ".NS" in ticker else "SPY"
            try:
                market_hist = yf.Ticker(market_ticker).history(period="5y")
                if not market_hist.empty:
                    market_returns = market_hist['Close'].pct_change()
                    common_idx = returns.index.intersection(market_returns.index)
                    if len(common_idx) > 0:
                        covariance = np.cov(returns[common_idx], market_returns[common_idx])[0][1]
                        market_var = np.var(market_returns[common_idx])
                        beta = covariance / market_var if market_var > 0 else 1.0
                    else:
                        beta = 1.0
                else:
                    beta = 1.0
            except:
                beta = 1.0
            
            # Price momentum (6-month vs current)
            six_months_ago = hist.tail(126)
            if len(six_months_ago) > 0:
                momentum = (current_price / six_months_ago['Close'].iloc[0] - 1) * 100
            else:
                momentum = 0
            
            return {
                "ticker": ticker,
                "current_price": float(current_price),
                "volatility": float(volatility),
                "cagr": float(cagr),
                "sharpe_ratio": float(sharpe),
                "beta": float(beta),
                "momentum_6m": float(momentum),
                "high_52w": float(high_52w),
                "low_52w": float(low_52w),
                "last_updated": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error calculating metrics for {ticker}: {str(e)}")
            return None
    
    def get_portfolio_metrics(self, tickers: List[str]) -> Dict[str, Dict]:
        """Fetch metrics for multiple stocks."""
        metrics = {}
        for ticker in tickers:
            data = self.get_stock_metrics(ticker)
            if data:
                metrics[ticker] = data
        return metrics
    
    def classify_stock_by_risk(self, metrics: Dict) -> str:
        """Classify stock risk based on volatility."""
        volatility = metrics.get("volatility", 0)
        beta = metrics.get("beta", 1.0)
        
        combined_risk = volatility * 0.6 + (beta - 1) * 0.4
        
        if combined_risk < 0.25:
            return "Low"
        elif combined_risk < 0.45:
            return "Medium"
        else:
            return "High"
    
    def rank_stocks_by_risk_adjusted_return(
        self,
        metrics_dict: Dict[str, Dict],
        risk_level: str = "medium"
    ) -> List[Tuple[str, float]]:
        """Rank stocks by Sharpe ratio (risk-adjusted return)."""
        ranked = []
        for ticker, metrics in metrics_dict.items():
            ranked.append((ticker, metrics.get("sharpe_ratio", 0)))
        
        # Sort by Sharpe ratio (descending)
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked


def fetch_real_stock_recommendations(
    risk_level: str = "medium"
) -> List[Dict]:
    """Fetch real stock data and return recommendations."""
    fetcher = MarketDataFetcher()
    
    # Get stocks for the risk level e.g. "Low Risk"
    tickers = RECOMMENDED_STOCKS.get(f"{risk_level.capitalize()} Risk", [])
    
    # Fetch metrics for all stocks
    metrics_dict = fetcher.get_portfolio_metrics(tickers)
    
    # Rank by Sharpe ratio
    ranked = fetcher.rank_stocks_by_risk_adjusted_return(metrics_dict, risk_level)
    
    recommendations = []
    for ticker, sharpe in ranked:
        if ticker not in metrics_dict:
            continue
        
        metrics = metrics_dict[ticker]
        classified_risk = fetcher.classify_stock_by_risk(metrics)
        
        recommendations.append({
            "ticker": ticker,
            "current_price": metrics["current_price"],
            "volatility": round(metrics["volatility"] * 100, 2),
            "cagr": round(metrics["cagr"] * 100, 2),
            "sharpe_ratio": round(metrics["sharpe_ratio"], 2),
            "beta": round(metrics["beta"], 2),
            "momentum_6m": round(metrics["momentum_6m"], 2),
            "risk_classification": classified_risk,
            "description": f"{ticker}: {classified_risk}-risk equity with {round(metrics['cagr']*100, 1)}% CAGR",
            "expected_return_range": f"{max(3, round(metrics['cagr']*100-5, 0)):.0f}–{round(metrics['cagr']*100+5, 0):.0f}%",
        })
    
    return recommendations


def get_market_overall_metrics() -> Dict:
    """Get overall market metrics (indices)."""
    try:
        # Fetch major indices
        indices = {
            "NIFTY_50": "^NSEI",
            "SENSEX": "^BSESN",
            "SP500": "^GSPC",
            "NASDAQ": "^IXIC",
        }
        
        metrics = {}
        for name, ticker in indices.items():
            cache_key = f"idx_metrics_{ticker}"
            if cache_key in _market_data_cache:
                metrics[name] = _market_data_cache[cache_key]
                continue

            try:
                idx = yf.Ticker(ticker)
                hist = idx.history(period="1y")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    year_ago = hist['Close'].iloc[0]
                    yoy_return = (current / year_ago - 1) * 100
                    res = {
                        "current_level": float(current),
                        "yoy_return": float(yoy_return),
                    }
                    _market_data_cache[cache_key] = res
                    metrics[name] = res
            except:
                pass
        
        return metrics
    except Exception as e:
        logger.error(f"Error fetching market metrics: {str(e)}")
        return {}


if __name__ == "__main__":
    # Test the fetcher
    logging.basicConfig(level=logging.INFO)
    
    print("🔍 Fetching real market data...")
    
    # Test stock metrics
    recs = fetch_real_stock_recommendations("medium")
    print(f"\n📊 Top stock recommendations (Medium Risk):")
    for rec in recs[:3]:
        print(f"  {rec['ticker']}: {rec['description']}")
        print(f"    CAGR: {rec['cagr']}%, Sharpe: {rec['sharpe_ratio']}, Beta: {rec['beta']}")
    
    # Test market metrics
    market_metrics = get_market_overall_metrics()
    print(f"\n📈 Market Metrics:")
    for market, metrics in market_metrics.items():
        print(f"  {market}: {metrics['current_level']:.2f} ({metrics['yoy_return']:.2f}% YoY)")
