"""
PRODUCTION-READY VERIFICATION SCRIPT
Tests all FastAPI backend components with MongoDB and AI Engine
"""
import asyncio
import sys

async def test_all_components():
    print("=" * 70)
    print("PRODUCTION-READY FASTAPI BACKEND VERIFICATION")
    print("=" * 70)
    
    tests = {
        "Database Connection": test_database,
        "Authentication": test_auth,
        "AI Engine": test_ai_engine,
        "FastAPI Setup": test_fastapi_setup,
        "Required Packages": test_packages,
    }
    
    results = {}
    for test_name, test_func in tests.items():
        try:
            print(f"\n[TESTING] {test_name}...", end=" ")
            result = await test_func() if asyncio.iscoroutinefunction(test_func) else test_func()
            results[test_name] = "PASS" if result else "FAIL"
            print(f"[{'PASS' if result else 'FAIL'}]")
        except Exception as e:
            results[test_name] = f"ERROR: {str(e)[:50]}"
            print(f"[ERROR] {str(e)[:50]}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for test_name, status in results.items():
        symbol = "✓" if status == "PASS" else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    all_pass = all(v == "PASS" for v in results.values())
    print("\n" + ("=" * 70))
    if all_pass:
        print("ALL SYSTEMS READY FOR PRODUCTION!")
    else:
        print("SOME ISSUES NEED FIXING!")
    print("=" * 70 + "\n")
    
    return all_pass


async def test_database():
    """Test MongoDB connection"""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
        # Test ping is the only real test we need
        info = await client.admin.command('ping')
        if info:
            await client.close()
            return True
        return False
    except Exception as e:
        return False


async def test_auth():
    """Test authentication system"""
    try:
        from core.security import hash_password, verify_password, create_access_token, decode_access_token
        
        # Test password hashing
        pwd = "testpassword123"
        hashed = hash_password(pwd)
        assert verify_password(pwd, hashed), "Password verification failed"
        
        # Test JWT tokens
        token = create_access_token({"sub": "test_user_id"})
        payload = decode_access_token(token)
        assert payload.get("sub") == "test_user_id", "Token decode failed"
        
        return True
    except Exception as e:
        print(f"\nAuth Error: {e}")
        return False


async def test_ai_engine():
    """Test AI recommendation engine"""
    try:
        from ai_engine.recommender import load_models, generate_recommendation
        
        # Load models (trains if missing)
        models = load_models()
        assert models is not None, "Models failed to load"
        
        # Generate a sample recommendation
        rec = generate_recommendation(
            monthly_income=100000,
            monthly_expenses=50000,
            risk_tolerance="medium",
            financial_goal="Retirement Planning",
            age=35,
            investment_horizon_years=20
        )
        
        assert rec.get("user_segment"), "No user segment"
        assert rec.get("portfolio_allocation"), "No portfolio allocation"
        assert rec.get("stock_recommendations"), "No stock recommendations"
        assert rec.get("expected_return_percent"), "No expected return"
        
        return True
    except Exception as e:
        print(f"\nAI Engine Error: {e}")
        return False


def test_fastapi_setup():
    """Test FastAPI application"""
    try:
        from main import app
        assert app is not None, "FastAPI app not initialized"
        
        # Check routers are registered
        routes = [route.path for route in app.routes]
        required_prefixes = ["/api/v1/auth", "/api/v1/expenses", "/api/v1/goals", "/api/v1/investments", "/api/v1/users"]
        
        for prefix in required_prefixes:
            found = any(prefix in route for route in routes)
            assert found, f"Router {prefix} not registered"
        
        return True
    except Exception as e:
        print(f"\nFastAPI Error: {e}")
        return False


def test_packages():
    """Test required packages are installed"""
    try:
        packages = [
            'fastapi', 'uvicorn', 'motor', 'pydantic', 'pydantic_settings',
            'jose', 'passlib', 'bcrypt', 'sklearn', 'xgboost', 'numpy', 'pandas'
        ]
        
        for pkg in packages:
            if pkg == 'sklearn':
                __import__('sklearn')
            elif pkg == 'pydantic_settings':
                __import__('pydantic_settings')
            elif pkg == 'jose':
                __import__('jose')
            elif pkg == 'xgboost':
                __import__('xgboost')
            else:
                __import__(pkg)
        
        return True
    except ImportError as e:
        print(f"\nPackage Error: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_all_components())
    sys.exit(0 if result else 1)
