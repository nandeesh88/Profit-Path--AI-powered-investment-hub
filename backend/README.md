# Backend - Profit Path

This is the FastAPI backend for the Profit Path FinTech SaaS platform, providing production-ready REST APIs for expense tracking, financial goals, and AI-powered investment recommendations.

## Project Structure

```
backend/
├── main.py                      # FastAPI app entry point
├── requirements.txt             # Python dependencies
├── __init__.py                  # Package init
├── .env                         # Environment variables (local)
├── .env.example                 # Example env file
│
├── core/                        # Core Modules
│   ├── __init__.py
│   ├── config.py               # Settings & configuration
│   ├── database.py             # MongoDB connection & setup
│   ├── security.py             # JWT, password hashing, security
│   └── deps.py                 # Dependency injection
│
├── routers/                     # API Endpoints (v1)
│   ├── __init__.py
│   ├── auth.py                 # Authentication endpoints
│   ├── users.py                # User management endpoints
│   ├── expenses.py             # Expense tracking endpoints
│   ├── goals.py                # Financial goals endpoints
│   └── investments.py          # Investment endpoints
│
├── models/                      # Data Models
│   ├── __init__.py
│   ├── helpers.py              # Model helper functions
│   └── ... (specific model classes)
│
├── schemas/                     # Pydantic Request/Response Schemas
│   ├── __init__.py
│   ├── user.py                 # User schemas
│   ├── expense.py              # Expense schemas
│   ├── goal.py                 # Goal schemas
│   └── investment.py           # Investment schemas
│
├── ai_engine/                   # AI/ML Module
│   ├── __init__.py
│   ├── recommender.py          # ML recommendation engine
│   └── saved_models/           # Trained model files
│       ├── model.joblib
│       ├── scaler.joblib
│       └── label_encoder.joblib
│
└── __pycache__/                # Python cache (auto-generated)
```

## Technology Stack

- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **python-jose** - JWT authentication
- **passlib** - Password hashing
- **Scikit-learn** - Machine learning
- **XGBoost** - Gradient boosting ML
- **Pandas & NumPy** - Data processing

## Setup & Installation

### Prerequisites

- Python 3.9+
- MongoDB
- Virtual environment tool (venv or conda)

### Installation Steps

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update `.env` with your configuration:
```env
DATABASE_URL=mongodb://localhost:27017
DATABASE_NAME=profit_path
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_ORIGIN=http://localhost:3000
APP_NAME=Profit Path
```

### Run Development Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication Endpoints (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `GET /auth/me` - Get current user info

### User Endpoints (`/users`)
- `GET /users/{user_id}` - Get user profile
- `PUT /users/{user_id}` - Update user profile
- `DELETE /users/{user_id}` - Delete user account

### Expense Endpoints (`/expenses`)
- `GET /expenses` - List all expenses
- `POST /expenses` - Create new expense
- `GET /expenses/{expense_id}` - Get expense details
- `PUT /expenses/{expense_id}` - Update expense
- `DELETE /expenses/{expense_id}` - Delete expense
- `GET /expenses/stats` - Get expense statistics

### Goal Endpoints (`/goals`)
- `GET /goals` - List all goals
- `POST /goals` - Create new goal
- `GET /goals/{goal_id}` - Get goal details
- `PUT /goals/{goal_id}` - Update goal
- `DELETE /goals/{goal_id}` - Delete goal
- `PUT /goals/{goal_id}/progress` - Update goal progress

### Investment Endpoints (`/investments`)
- `GET /investments` - List investments
- `GET /investments/recommendations` - Get AI recommendations
- `GET /investments/{investment_id}` - Get investment details
- `POST /investments/analyze` - Analyze investment

## Database Schema

### Users
```python
{
    "_id": ObjectId,
    "email": str,
    "full_name": str,
    "password_hash": str,
    "is_active": bool,
    "created_at": datetime,
    "updated_at": datetime
}
```

### Expenses
```python
{
    "_id": ObjectId,
    "user_id": ObjectId,
    "amount": float,
    "category": str,
    "description": str,
    "date": datetime,
    "created_at": datetime,
    "updated_at": datetime
}
```

### Goals
```python
{
    "_id": ObjectId,
    "user_id": ObjectId,
    "title": str,
    "target_amount": float,
    "current_amount": float,
    "deadline": datetime,
    "priority": str,
    "created_at": datetime,
    "updated_at": datetime
}
```

### Investments
```python
{
    "_id": ObjectId,
    "name": str,
    "type": str,
    "risk_level": str,
    "expected_return": float,
    "description": str,
    "created_at": datetime
}
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. User logs in and receives a JWT token
2. Token is stored in frontend localStorage
3. Token is sent in Authorization header: `Bearer <token>`
4. Token expires after configured minutes
5. Refresh token mechanism available

## AI/ML Features

### Investment Recommendations

The recommend system uses:
- **XGBoost** classifier for investment suggestions
- **Scikit-learn** preprocessing and feature scaling
- User profile & historical data analysis
- Risk assessment based on user behavior

Models are loaded on application startup for performance.

```python
from .ai_engine.recommender import get_recommendations

recommendations = get_recommendations(user_id, profile_data)
```

## Security

- **Password Hashing**: Bcrypt with salt
- **JWT Tokens**: HS256 algorithm
- **CORS**: Configured for frontend origin
- **Request Validation**: Pydantic schemas
- **SQL Injection Prevention**: Parameterized queries
- **Rate Limiting**: Can be added per endpoint

## Error Handling

All endpoints return standardized error responses:

```json
{
    "detail": "Error message",
    "status_code": 400
}
```

Common status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Server Error

## Logging

Logs are printed to console. For production, configure:
- File-based logging
- Log rotation
- Structured logging (JSON)
- Different log levels (DEBUG, INFO, WARNING, ERROR)

## Testing

Create test files in the root:

```bash
pytest tests/
```

Example test structure:
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
```

## Deployment

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t profit-path-backend .
docker run -p 8000:8000 profit-path-backend
```

### Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | MongoDB connection string | mongodb://localhost:27017 |
| DATABASE_NAME | MongoDB database name | profit_path |
| SECRET_KEY | JWT signing key | change-me |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration time | 30 |
| FRONTEND_ORIGIN | CORS allowed frontend URL | http://localhost:3000 |
| APP_NAME | Application name | Profit Path |

## Troubleshooting

### MongoDB Connection Failed
```bash
# Ensure MongoDB is running
# Windows: MongoDB should be running as service
# macOS: brew services start mongodb-community
# Linux: sudo service mongod start
```

### Port 8000 Already in Use
```bash
uvicorn main:app --reload --port 8001
```

### Module Not Found Errors
```bash
# Ensure you're in the correct directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Timeout
Check:
- MongoDB is running
- `DATABASE_URL` in `.env` is correct
- Network connectivity to MongoDB

## Contributing

When adding new endpoints:
1. Create router file in `routers/`
2. Create schemas in `schemas/`
3. Create models/helpers in `models/`
4. Include proper error handling
5. Add request/response validation
6. Update API documentation (auto-generated)

## Performance Monitoring

FastAPI provides automatic API documentation and request logging:
- Check Swagger UI at `/docs`
- Monitor response times in console
- Use FastAPI dependency injection for shared resources
- Use async functions for I/O operations

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Motor Documentation](https://motor.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JWT.io](https://jwt.io/)
