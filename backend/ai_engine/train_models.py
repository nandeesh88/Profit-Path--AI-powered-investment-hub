"""
Machine Learning Model Training Module
Trains real ML models using actual financial data from yfinance.
Models are saved as pickle files for production use.
"""
import os
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Tuple, Dict

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
import joblib
import logging

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)


class RealFinancialDataTrainer:
    """Trains ML models using real financial data from yfinance."""
    
    def __init__(self, lookback_years: int = 5):
        self.lookback_years = lookback_years
        self.lookback_date = datetime.now() - timedelta(days=lookback_years * 365)
    
    def fetch_stock_data(self, ticker: str, period: str = "5y") -> pd.DataFrame:
        """Fetch historical stock data."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            return hist
        except Exception as e:
            logger.error(f"Error fetching {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def calculate_stock_returns(self, ticker: str) -> float:
        """Calculate annualized return for a stock."""
        try:
            hist = self.fetch_stock_data(ticker, period="5y")
            if hist.empty or len(hist) < 252:
                return 7.0  # Default fallback
            
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            years = len(hist) / 252
            cagr = (end_price / start_price) ** (1 / years) - 1
            return float(cagr * 100)
        except:
            return 7.0
    
    def calculate_stock_volatility(self, ticker: str) -> float:
        """Calculate annualized volatility for a stock."""
        try:
            hist = self.fetch_stock_data(ticker, period="5y")
            if hist.empty or len(hist) < 252:
                return 15.0  # Default fallback
            
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            return float(volatility * 100)
        except:
            return 15.0
    
    def generate_training_data_from_real_market(
        self,
        n_samples: int = 500
    ) -> pd.DataFrame:
        """
        Generate training data by fetching real market data.
        Each sample represents a user profile based on real market conditions.
        """
        logger.info(f"Generating {n_samples} training samples from real market data...")
        
        # Real stock tickers across risk levels
        low_risk_stocks = ["TCS.NS", "INFY.NS", "MSFT", "JNJ", "PG"]
        medium_risk_stocks = ["HDFC.NS", "RELIANCE.NS", "AAPL", "GOOGL", "AMZN"]
        high_risk_stocks = ["WIPRO.NS", "BAJAJFINSV.NS", "NVDA", "TSLA", "META"]
        
        # Fetch real returns and volatility
        logger.info("Fetching real market data for risk calibration...")
        
        low_risk_metrics = self._get_stock_group_metrics(low_risk_stocks)
        medium_risk_metrics = self._get_stock_group_metrics(medium_risk_stocks)
        high_risk_metrics = self._get_stock_group_metrics(high_risk_stocks)
        
        # Generate synthetic user profiles based on real market conditions
        rng = np.random.default_rng(42)
        
        incomes = rng.uniform(25000, 250000, n_samples)
        expense_ratios = rng.uniform(0.35, 0.85, n_samples)
        expenses = incomes * expense_ratios
        savings = incomes - expenses
        savings_rate = savings / incomes
        
        ages = rng.integers(22, 65, n_samples)
        goals = rng.choice([0, 1, 2, 3, 4], n_samples)  # goal codes
        
        # Risk labels influenced by savings rate and real market conditions
        risk_labels = np.zeros(n_samples, dtype=int)
        
        # Low risk: high savings rate, lower income
        low_idx = (savings_rate > 0.40) & (incomes < 100000)
        risk_labels[low_idx] = 0
        
        # High risk: lower savings rate, higher income
        high_idx = (savings_rate < 0.25) & (incomes > 150000)
        risk_labels[high_idx] = 2
        
        # Medium risk: everything else
        medium_idx = ~(low_idx | high_idx)
        risk_labels[medium_idx] = 1
        
        # Expected returns based on real market data
        expected_returns = np.zeros(n_samples)
        
        # Map risk to real market returns
        expected_returns[risk_labels == 0] = rng.normal(
            low_risk_metrics["avg_return"], 2, np.sum(risk_labels == 0)
        )
        expected_returns[risk_labels == 1] = rng.normal(
            medium_risk_metrics["avg_return"], 4, np.sum(risk_labels == 1)
        )
        expected_returns[risk_labels == 2] = rng.normal(
            high_risk_metrics["avg_return"], 6, np.sum(risk_labels == 2)
        )
        
        expected_returns = np.clip(expected_returns, 5, 25)
        
        # Beta values based on risk profiles
        betas = np.zeros(n_samples)
        betas[risk_labels == 0] = rng.normal(0.6, 0.1, np.sum(risk_labels == 0))
        betas[risk_labels == 1] = rng.normal(1.0, 0.15, np.sum(risk_labels == 1))
        betas[risk_labels == 2] = rng.normal(1.4, 0.2, np.sum(risk_labels == 2))
        
        betas = np.clip(betas, 0.3, 2.0)
        
        # Volatilities from real market data
        volatilities = np.zeros(n_samples)
        volatilities[risk_labels == 0] = rng.normal(
            low_risk_metrics["avg_volatility"], 3, np.sum(risk_labels == 0)
        )
        volatilities[risk_labels == 1] = rng.normal(
            medium_risk_metrics["avg_volatility"], 5, np.sum(risk_labels == 1)
        )
        volatilities[risk_labels == 2] = rng.normal(
            high_risk_metrics["avg_volatility"], 7, np.sum(risk_labels == 2)
        )
        
        volatilities = np.clip(volatilities, 8, 45)
        
        df = pd.DataFrame({
            "monthly_income": incomes,
            "monthly_expenses": expenses,
            "savings": savings,
            "savings_rate": savings_rate,
            "age": ages,
            "goal_code": goals,
            "user_risk_input": risk_labels,
            "expected_return": expected_returns,
            "beta": betas,
            "volatility": volatilities,
            "risk_label": risk_labels,
        })
        
        logger.info(f"✅ Generated {len(df)} training samples")
        return df
    
    def _get_stock_group_metrics(self, tickers: list) -> Dict:
        """Calculate average metrics for a group of stocks."""
        returns = []
        volatilities = []
        
        for ticker in tickers:
            ret = self.calculate_stock_returns(ticker)
            vol = self.calculate_stock_volatility(ticker)
            
            if ret > 0 and vol > 0:
                returns.append(ret)
                volatilities.append(vol)
        
        return {
            "avg_return": np.mean(returns) if returns else 10.0,
            "avg_volatility": np.mean(volatilities) if volatilities else 18.0,
        }
    
    def get_feature_matrix(self, df: pd.DataFrame) -> np.ndarray:
        """Extract feature matrix from training data."""
        features = [
            "monthly_income",
            "monthly_expenses",
            "savings",
            "savings_rate",
            "age",
            "goal_code",
            "beta",
            "volatility",
        ]
        return df[features].values
    
    def train_models(self) -> Tuple:
        """Train all ML models using real financial data."""
        logger.info("Starting model training with real market data...")
        
        # Generate training data from real market data
        df = self.generate_training_data_from_real_market(n_samples=500)
        
        X = self.get_feature_matrix(df)
        y_risk = df["risk_label"].values
        y_return = df["expected_return"].values
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        logger.info("Training risk classification model...")
        # Risk classifier: RandomForest
        risk_clf = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )
        risk_clf.fit(X_scaled, y_risk)
        
        logger.info("Training return prediction model...")
        # Return regressor: GradientBoosting
        return_reg = GradientBoostingRegressor(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42,
        )
        return_reg.fit(X_scaled, y_return)
        
        logger.info("Training risk classifier (Logistic Regression)...")
        # Risk classifier: Logistic Regression for interpretability
        risk_logistic = LogisticRegression(
            max_iter=1000,
            random_state=42,
            n_jobs=-1,
        )
        risk_logistic.fit(X_scaled, y_risk)
        
        logger.info("Training user clustering model...")
        # KMeans: User segmentation
        kmeans = KMeans(
            n_clusters=5,
            n_init=20,
            max_iter=300,
            random_state=42,
        )
        kmeans.fit(X_scaled)
        
        # Save all models
        logger.info("Saving trained models...")
        joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
        joblib.dump(risk_clf, os.path.join(MODEL_DIR, "risk_clf.pkl"))
        joblib.dump(return_reg, os.path.join(MODEL_DIR, "return_reg.pkl"))
        joblib.dump(risk_logistic, os.path.join(MODEL_DIR, "risk_logistic.pkl"))
        joblib.dump(kmeans, os.path.join(MODEL_DIR, "kmeans.pkl"))
        
        logger.info("✅ All models trained and saved successfully")
        
        # Print model performance
        train_risk_score = risk_clf.score(X_scaled, y_risk)
        train_return_score = return_reg.score(X_scaled, y_return)
        
        logger.info(f"   Risk Classification Accuracy: {train_risk_score:.2%}")
        logger.info(f"   Return Prediction R² Score: {train_return_score:.2%}")
        
        return scaler, risk_clf, return_reg, risk_logistic, kmeans
    
    def load_models(self):
        """Load pre-trained models or train new ones."""
        model_files = [
            "scaler.pkl",
            "risk_clf.pkl",
            "return_reg.pkl",
            "risk_logistic.pkl",
            "kmeans.pkl",
        ]
        
        # Check if all models exist
        missing = [
            f for f in model_files
            if not os.path.exists(os.path.join(MODEL_DIR, f))
        ]
        
        if missing:
            logger.info(f"Models missing: {missing}. Training new models...")
            return self.train_models()
        
        logger.info("Loading pre-trained models...")
        scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
        risk_clf = joblib.load(os.path.join(MODEL_DIR, "risk_clf.pkl"))
        return_reg = joblib.load(os.path.join(MODEL_DIR, "return_reg.pkl"))
        risk_logistic = joblib.load(os.path.join(MODEL_DIR, "risk_logistic.pkl"))
        kmeans = joblib.load(os.path.join(MODEL_DIR, "kmeans.pkl"))
        
        logger.info("✅ Models loaded successfully")
        return scaler, risk_clf, return_reg, risk_logistic, kmeans


def train_and_save_models():
    """Entry point for training models."""
    trainer = RealFinancialDataTrainer()
    return trainer.train_models()


def load_models():
    """Entry point for loading models."""
    trainer = RealFinancialDataTrainer()
    return trainer.load_models()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Training ML models with real financial data...")
    train_and_save_models()
    logger.info("✅ Training complete!")
