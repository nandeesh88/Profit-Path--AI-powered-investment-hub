from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Profit-Path"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "profitpath"
    MONGODB_POOL_SIZE: int = 10
    MONGODB_TIMEOUT: int = 5000

    # API Configuration
    API_TITLE: str = "Profit-Path Investment API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Production-ready investment recommendation engine"

    # JWT Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000"

    # AI Engine
    MODEL_CACHE_HOURS: int = 24
    MARKET_DATA_CACHE_MINUTES: int = 60
    BATCH_INFERENCE_SIZE: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Feature Flags
    ENABLE_REAL_MARKET_DATA: bool = True
    ENABLE_ML_PREDICTIONS: bool = True
    ENABLE_DATABASE_PERSISTENCE: bool = True
    ENABLE_RECOMMENDATION_CACHING: bool = True

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Market Data Configuration
    STOCK_DATA_LOOKBACK_YEARS: int = 5
    VOLATILITY_WINDOW_DAYS: int = 252
    BETA_CALCULATION_PERIODS: int = 252

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated ALLOWED_ORIGINS into list."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
