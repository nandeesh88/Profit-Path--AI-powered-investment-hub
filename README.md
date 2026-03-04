# 💰 Profit-Path — AI-Powered Personal Finance Management Platform

> A full-stack intelligent personal finance platform that combines **real-time market data**, **machine learning models**, and **interactive dashboards** to help users track expenses, manage income, set financial goals, and receive personalized investment recommendations with real stock and mutual fund names.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Machine Learning Pipeline](#-machine-learning-pipeline)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Frontend Pages & Components](#-frontend-pages--components)
- [Infrastructure & Deployment](#-infrastructure--deployment)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [Screenshots](#-screenshots)

---

## 🚀 Project Overview

**Profit-Path** is a production-ready personal finance management system that enables users to:

1. **Register & Authenticate** — Secure JWT-based authentication with bcrypt password hashing
2. **Track Income** — Record monthly income from multiple sources (salary, freelance, business, etc.)
3. **Manage Expenses** — Categorize and analyze spending across 10 categories
4. **Set Financial Goals** — Create goals with target amounts, deadlines, and priority levels
5. **Get AI Investment Recommendations** — ML-powered, personalized recommendations with **real stock tickers** (NSE/US), **real mutual fund names**, portfolio allocation, SIP plans, and live market data
6. **Monitor Dashboard** — Real-time KPI cards, trend charts, expense breakdowns, and budget tracking

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **JWT Authentication** | Secure registration/login with bcrypt hashing and HS256 JWT tokens (24h expiry) |
| **Expense Tracking** | CRUD operations across 10 categories with monthly summaries and category breakdowns |
| **Multi-Source Income** | Track income per month per source (salary, freelance, business, etc.) with auto-seeding from profile |
| **Financial Goals** | Priority-based goals (low/medium/high) with progress tracking against net savings |
| **AI Investment Engine** | 5 trained ML models analyzing user financial profiles to generate personalized recommendations |
| **Real Stock Data** | Live stock prices via Yahoo Finance for Indian (NSE) and US stocks |
| **Real Mutual Funds** | Named Indian mutual funds (HDFC, SBI, ICICI, Mirae, Quant, Parag Parikh, Motilal Oswal) |
| **Portfolio Allocation** | Risk-adjusted allocation across stocks, mutual funds, SIP, and emergency fund |
| **SIP Projections** | 5-year and 10-year corpus projections using future-value annuity formula |
| **Market Overview** | Live indices — NIFTY 50, SENSEX, S&P 500, NASDAQ with YoY returns |
| **Interactive Dashboard** | Recharts-powered trend charts, pie charts, budget trackers with real data |
| **Rate Limiting** | Per-IP sliding-window rate limits (60/min, 1000/hr) with headers |
| **Security Headers** | HSTS, X-Frame-Options, X-Content-Type-Options, CSP, Referrer-Policy |
| **Request Logging** | UUID-tagged request/response logging with response time tracking |
| **Caching** | In-memory TTL cache for market data (1hr) and recommendations (24hr) |
| **Docker & Kubernetes** | Production-ready Docker Compose (3 services) and K8s manifests (3 replicas) |

---

## 🛠 Tech Stack

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.13 | Runtime |
| **FastAPI** | ≥0.110.0 | Async REST API framework |
| **MongoDB** | 5.0+ | NoSQL document database |
| **Motor** | ≥3.3.0 | Async MongoDB driver |
| **Pydantic** | ≥2.6.0 | Data validation & serialization |
| **python-jose** | ≥3.3.0 | JWT token creation/verification |
| **bcrypt** | — | Password hashing |
| **scikit-learn** | ≥1.4.0 | ML models (RF, GB, KMeans, LR, StandardScaler) |
| **yfinance** | ≥0.2.33 | Yahoo Finance real-time market data |
| **pandas** | ≥2.2.0 | Data manipulation for ML pipeline |
| **numpy** | ≥1.26.0 | Numerical computing |
| **xgboost** | ≥2.0.0 | Advanced gradient boosting (available) |
| **scipy** | ≥1.12.0 | Scientific computing |
| **ta** | ≥0.10.2 | Technical analysis indicators |
| **gunicorn** | ≥22.0.0 | Production ASGI server |
| **uvicorn** | ≥0.29.0 | ASGI server (development) |

### Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Next.js** | 16.0.10 | React meta-framework (App Router + Turbopack) |
| **React** | 19.2.0 | UI library |
| **TypeScript** | 5 | Type-safe JavaScript |
| **Tailwind CSS** | 4.1.9 | Utility-first CSS framework |
| **shadcn/ui** | — | 30+ Radix UI-based components |
| **Recharts** | 2.15.4 | Data visualization (charts) |
| **Axios** | 1.13.6 | HTTP client with interceptors |
| **react-hook-form** | 7.60 | Form management |
| **Zod** | 3.25 | Schema validation |
| **Lucide React** | 0.454.0 | Icon library |
| **date-fns** | — | Date utilities |

### Infrastructure

| Technology | Purpose |
|-----------|---------|
| **Docker** | Containerization (Python 3.9-slim base) |
| **Docker Compose** | Multi-service orchestration (API + MongoDB + Frontend) |
| **Kubernetes** | Production deployment (3 replicas, LoadBalancer, PVC) |
| **Gunicorn** | Production WSGI/ASGI server (4 workers) |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                           │
│                    (Next.js 16 + React 19)                      │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐      │
│  │Dashboard │ Income   │ Expenses │Investments│  Goals   │      │
│  │  Page    │   Page   │   Page   │   Page   │   Page   │      │
│  └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘      │
│       └──────────┴──────────┴──────────┴──────────┘             │
│                          │ Axios (JWT)                          │
└──────────────────────────┼──────────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────┼──────────────────────────────────────┐
│                    FASTAPI BACKEND                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              MIDDLEWARE STACK (outermost → innermost)    │    │
│  │  CORS → Security Headers → Request Logging → Rate Limit │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌───────────┬──────────┬──────────┬───────────┬──────────┐    │
│  │ Auth      │ Users    │ Expenses │ Income    │ Goals    │    │
│  │ Router    │ Router   │ Router   │ Router    │ Router   │    │
│  └───────────┴──────────┴──────────┴───────────┴──────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              INVESTMENTS ROUTER                          │    │
│  │    ┌──────────────────────────────────────────────┐     │    │
│  │    │           AI ENGINE                           │     │    │
│  │    │  ┌────────────┐  ┌─────────────────────┐    │     │    │
│  │    │  │ ML Models  │  │  Market Data Fetcher │    │     │    │
│  │    │  │ (5 models) │  │  (yfinance live)     │    │     │    │
│  │    │  └────────────┘  └─────────────────────┘    │     │    │
│  │    │  ┌────────────────────────────────────┐     │     │    │
│  │    │  │  Recommendation Engine              │     │     │    │
│  │    │  │  (risk, return, segment, portfolio) │     │     │    │
│  │    │  └────────────────────────────────────┘     │     │    │
│  │    └──────────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌────────────┐  ┌───────┴────────┐                             │
│  │ TTL Cache  │  │  Motor (Async) │                             │
│  │ (in-memory)│  │  MongoDB Driver │                             │
│  └────────────┘  └───────┬────────┘                             │
└──────────────────────────┼──────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────────┐
│                    MONGODB 5.0                                   │
│  ┌──────┬─────────┬────────┬───────┬─────────────┐             │
│  │users │expenses │incomes │goals  │investments  │             │
│  └──────┴─────────┴────────┴───────┴─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Machine Learning Pipeline

### Model Training

The ML pipeline (`backend/ai_engine/train_models.py`) uses **real market data** from Yahoo Finance to train models:

1. **Data Collection** — Fetches 5 years of historical data for 15 stock tickers across 3 risk categories
2. **Synthetic Profile Generation** — Creates 500 user financial profiles calibrated to real market conditions
3. **Feature Engineering** — `monthly_income`, `monthly_expenses`, `savings`, `savings_rate`, `age`, `goal_code`, `beta`, `volatility`
4. **Model Training** — Trains 5 models and saves to `backend/ai_engine/saved_models/`

### Trained Models

| # | Model File | Algorithm | Purpose | Configuration |
|---|-----------|-----------|---------|---------------|
| 1 | `scaler.pkl` | **StandardScaler** | Feature normalization | — |
| 2 | `risk_clf.pkl` | **RandomForestClassifier** | Risk classification (low/medium/high) | 200 trees, max_depth=10 |
| 3 | `return_reg.pkl` | **GradientBoostingRegressor** | Expected return prediction (%) | 150 trees, learning_rate=0.1 |
| 4 | `risk_logistic.pkl` | **LogisticRegression** | Interpretable risk classification | max_iter=1000 |
| 5 | `kmeans.pkl` | **KMeans** | User segmentation (5 clusters) | 5 clusters, 20 initializations |

### User Segments (KMeans Clusters)

| Cluster | Segment Name |
|---------|-------------|
| 0 | Conservative Saver |
| 1 | Balanced Builder |
| 2 | Aggressive Grower |
| 3 | Income Maximizer |
| 4 | Wealth Accumulator |

### Recommendation Flow

```
User Input (income, expenses, risk_tolerance, goal)
        │
        ▼
┌─────────────────────┐
│  Feature Engineering │ → savings, savings_rate, goal_code, risk features
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐ ┌──────────┐
│ Scaler │ │  KMeans  │ → User Segment
└───┬────┘ └──────────┘
    │
    ├──────────────────────┐
    ▼                      ▼
┌──────────────┐  ┌────────────────┐
│ RandomForest │  │GradientBoosting│ → Expected Return % (clipped 5-25%)
│ Risk Clf     │  │ Return Reg     │
└──────┬───────┘  └────────────────┘
       │
       ▼
┌─────────────────┐
│ Risk Blending   │ → blend ML prediction with user-provided risk
└────────┬────────┘
         │
    ┌────┴────────────────────────────┐
    ▼                                 ▼
┌──────────────────┐    ┌───────────────────────┐
│ Portfolio Alloc  │    │ yfinance Stock Fetch   │
│ (by risk level)  │    │ (real prices + metrics) │
└──────────────────┘    └───────────────────────┘
         │                         │
         └───────────┬─────────────┘
                     ▼
        ┌───────────────────────┐
        │  Final Recommendation │
        │  • Stock Recs (5)     │
        │  • MF Recs (3)        │
        │  • SIP Plan           │
        │  • Portfolio %        │
        │  • Financial Advice   │
        │  • Market Context     │
        └───────────────────────┘
```

### Portfolio Allocation (by Risk Profile)

| Risk Level | Stocks | Mutual Funds | SIP | Emergency Fund |
|-----------|--------|-------------|-----|----------------|
| **Low** | 15% | 40% | 25% | 20% |
| **Medium** | 30% | 35% | 25% | 10% |
| **High** | 50% | 25% | 20% | 5% |

### Real Stocks Tracked

**Indian Stocks (NSE):**
| Ticker | Company |
|--------|---------|
| TCS.NS | Tata Consultancy Services |
| INFY.NS | Infosys Limited |
| RELIANCE.NS | Reliance Industries |
| HDFC.NS | HDFC Ltd |
| BAJAJFINSV.NS | Bajaj Finserv |
| WIPRO.NS | Wipro Limited |

**US Stocks:**
| Ticker | Company |
|--------|---------|
| MSFT | Microsoft Corporation |
| AAPL | Apple Inc. |
| GOOGL | Alphabet Inc. |
| AMZN | Amazon.com Inc. |
| NVDA | NVIDIA Corporation |
| TSLA | Tesla Inc. |
| JNJ | Johnson & Johnson |
| PG | Procter & Gamble |

### Real Mutual Funds Recommended

| Risk Level | Fund Name | Type |
|-----------|-----------|------|
| Low | HDFC Corporate Bond Fund | Debt / Corporate Bond |
| Low | Axis Liquid Fund | Liquid |
| Low | SBI Conservative Hybrid Fund | Hybrid / Conservative |
| Medium | ICICI Prudential Balanced Advantage Fund | Hybrid / Dynamic Allocation |
| Medium | Mirae Asset Large Cap Fund | Equity / Large Cap |
| Medium | Quant ELSS Tax Saver Fund | Equity / ELSS (Tax Saving) |
| Medium | Parag Parikh Flexi Cap Fund | Equity / Flexi Cap |
| High | Quant Small Cap Fund | Equity / Small Cap |
| High | Motilal Oswal Midcap Fund | Equity / Midcap |
| High | ICICI Prudential Technology Fund | Equity / Sector (Technology) |
| High | Motilal Oswal Nasdaq 100 FOF | Equity / International (US Tech) |

### Market Data Metrics (per Stock)

- **CAGR** — Compound Annual Growth Rate
- **Sharpe Ratio** — Risk-adjusted return (6% risk-free rate)
- **Beta** — Volatility relative to market index (^NSEI for Indian, SPY for US)
- **Annualized Volatility** — Standard deviation of returns
- **6-Month Momentum** — Short-term trend strength
- **52-Week High/Low** — Price range context

---

## 📡 API Documentation

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/auth/register` | ✗ | Create new account → returns JWT + user profile |
| `POST` | `/api/v1/auth/login` | ✗ | Login → returns JWT + user profile |

### User Profile

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/v1/users/me` | ✓ | Get current user profile |
| `PUT` | `/api/v1/users/me` | ✓ | Update profile (name, income, risk, goal) |

### Income

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/income` | ✓ | Add income record (unique per month + source) |
| `GET` | `/api/v1/income` | ✓ | List all income records |
| `GET` | `/api/v1/income/summary` | ✓ | Income summary (total, by month, by source) |
| `PUT` | `/api/v1/income/{id}` | ✓ | Update income record |
| `DELETE` | `/api/v1/income/{id}` | ✓ | Delete income record |

### Expenses

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/expenses` | ✓ | Add expense |
| `GET` | `/api/v1/expenses` | ✓ | List all expenses (sorted by date desc) |
| `GET` | `/api/v1/expenses/summary` | ✓ | Expense summary (total, monthly avg, by category) |
| `PUT` | `/api/v1/expenses/{id}` | ✓ | Update expense |
| `DELETE` | `/api/v1/expenses/{id}` | ✓ | Delete expense |

### Financial Goals

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/goals` | ✓ | Create financial goal |
| `GET` | `/api/v1/goals` | ✓ | List all goals |
| `PUT` | `/api/v1/goals/{id}` | ✓ | Update goal |
| `DELETE` | `/api/v1/goals/{id}` | ✓ | Delete goal |

### Investment Recommendations (AI)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/investments/recommend` | ✓ | Generate AI-powered investment recommendation |
| `GET` | `/api/v1/investments/history` | ✓ | Get last 10 recommendation history |
| `GET` | `/api/v1/investments/market-status` | ✓ | Live market indices (NIFTY, SENSEX, S&P 500, NASDAQ) |

### Health

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/` | ✗ | Root health check |
| `GET` | `/health` | ✗ | Health status |

**Interactive API docs available at:** `http://localhost:8000/docs` (Swagger UI)

---

## 🗄 Database Schema

**Database:** MongoDB 5.0+ (async via Motor driver)  
**Database Name:** `profitpath`

### Collections & Indexes

| Collection | Fields | Indexes |
|------------|--------|---------|
| **users** | `_id`, `name`, `email`, `hashed_password`, `monthly_income`, `risk_tolerance`, `financial_goal`, `created_at` | `email` (unique) |
| **expenses** | `_id`, `user_id`, `description`, `amount`, `category`, `date`, `created_at` | `(user_id, date)` compound desc |
| **incomes** | `_id`, `user_id`, `amount`, `source`, `description`, `month`, `created_at` | `(user_id, month)` desc; `(user_id, month, source)` unique |
| **goals** | `_id`, `user_id`, `title`, `description`, `target_amount`, `current_amount`, `target_date`, `category`, `priority`, `created_at` | `(user_id)` |
| **investments** | `_id`, `user_id`, `input`, `recommendation`, `created_at` | `(user_id, created_at)` compound; `created_at` desc |

### Expense Categories
`Food & Dining` · `Transportation` · `Housing` · `Healthcare` · `Entertainment` · `Shopping` · `Education` · `Utilities` · `Travel` · `Other`

### Goal Categories
`Emergency Fund` · `Retirement` · `Education` · `Home` · `Travel` · `Investment` · `Other`

### Income Sources
`Salary` · `Freelance` · `Business` · `Investment Returns` · `Rental Income` · `Side Hustle` · `Other`

---

## 🖥 Frontend Pages & Components

### Pages

| Page | Route | Auth | Description |
|------|-------|------|-------------|
| **Landing** | `/` | ✗ | Hero section with features grid, social proof stats, and CTA |
| **Sign Up** | `/signup` | ✗ | Registration form (name, email, password, monthly income, risk tolerance, financial goal) |
| **Login** | `/login` | ✗ | Email/password login |
| **Onboarding** | `/onboarding` | ✓ | Profile setup wizard after registration |
| **Dashboard** | `/dashboard` | ✓ | KPI cards (Total Balance, Monthly Income, Monthly Expense, Net Savings), Trend Chart (6-month income vs expense), Expense Pie Chart, Budget Tracker |
| **Income** | `/income` | ✓ | Add/list/delete monthly income records grouped by month, auto-seeds from registration income |
| **Expenses** | `/expenses` | ✓ | Add/list/edit/delete expenses with 10 categories |
| **Investments** | `/investments` | ✓ | AI recommendation engine — portfolio allocation, real stock recommendations with live prices, real mutual fund names, SIP projections (5yr/10yr), market indices, personalized advice |
| **Goals** | `/goals` | ✓ | Create/track financial goals with priority levels, progress bars driven by net savings |
| **Settings** | `/settings` | ✓ | Edit profile (name, income, risk tolerance, financial goal) |

### Key Components

| Component | Description |
|-----------|-------------|
| `sidebar.tsx` | Responsive navigation sidebar with mobile hamburger (Dashboard, Income, Expenses, Investments, Goals, Settings, Logout) |
| `kpi-card.tsx` | KPI metric display cards with icons and trend indicators |
| `trend-chart.tsx` | Recharts line/bar chart showing 6-month income vs expense trends |
| `expense-chart.tsx` | Recharts pie/donut chart for expense category breakdown |
| `budget-tracker.tsx` | Monthly budget progress bars by category |
| `protected-route.tsx` | Auth guard HOC — redirects to `/login` if not authenticated |
| `auth-context.tsx` | React Context for auth state (login, register, logout, session persistence) |

---

## 🐳 Infrastructure & Deployment

### Docker Compose (3 services)

```yaml
Services:
  api:        FastAPI backend (port 8000), Gunicorn + 4 Uvicorn workers
  mongodb:    MongoDB 5.0 (port 27017), persistent volume, health check
  frontend:   Next.js app (port 3000)

Networks:   profit-path-net (bridge)
Volumes:    mongodb_data, model_data
```

### Kubernetes (5 resources)

| Resource | Name | Details |
|----------|------|---------|
| **Deployment** | `profit-path-api` | 3 replicas, CPU 250m–500m, Memory 256Mi–512Mi, liveness/readiness probes on `/health` |
| **Service** | `profit-path-api-service` | LoadBalancer, port 80 → 8000 |
| **ConfigMap** | `profit-path-config` | MongoDB URL, database name, CORS origins |
| **Secret** | `profit-path-secrets` | JWT secret key (base64 encoded) |
| **PVC** | `profit-path-models-pvc` | 2Gi ReadWriteOnce for ML model persistence |

### Middleware Stack

```
Request → CORS → Security Headers → Request Logging → Rate Limiting → Router
                                                                         │
Response ← CORS ← Security Headers ← Request Logging ← Rate Limiting ←──┘
```

| Middleware | Features |
|-----------|----------|
| **CORS** | Configurable origins, credentials, all methods/headers |
| **Security Headers** | HSTS, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, X-XSS-Protection, Referrer-Policy, Permissions-Policy |
| **Request Logging** | UUID per request, timing, `X-Request-ID` and `X-Response-Time` headers |
| **Rate Limiting** | 60 req/min + 1000 req/hr per IP, sliding window, `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers |

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.10+ (tested with 3.13)
- **Node.js** 18+ and **pnpm** (or npm)
- **MongoDB** 5.0+ (local or Atlas)
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/nandeesh88/Profit-Path.git
cd Profit-Path
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

The backend will:
- Connect to MongoDB at `localhost:27017`
- Auto-create database `profitpath` and indexes
- Auto-train ML models on first investment recommendation request (saved to `ai_engine/saved_models/`)
- Serve API docs at `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install
# or: npm install

# Start development server
pnpm dev
# or: npm run dev
```

Frontend runs at `http://localhost:3000`

### 4. Docker Compose (Alternative)

```bash
# From project root
docker-compose up --build
```

This starts all 3 services (API + MongoDB + Frontend) automatically.

---

## 📁 Project Structure

```
Profit-Path/
├── README.md                         # This file
├── Dockerfile                        # Backend Docker image
├── docker-compose.yml                # Multi-service orchestration
├── k8s/
│   └── deployment.yaml               # Kubernetes manifests (5 resources)
│
├── backend/
│   ├── main.py                       # FastAPI app entry point
│   ├── requirements.txt              # Python dependencies
│   │
│   ├── ai_engine/                    # ML/AI Module
│   │   ├── recommender.py            # Recommendation engine (core logic)
│   │   ├── market_data.py            # Yahoo Finance data fetcher
│   │   ├── train_models.py           # Model training pipeline
│   │   └── saved_models/             # Trained model pickle files
│   │       ├── scaler.pkl
│   │       ├── risk_clf.pkl
│   │       ├── return_reg.pkl
│   │       ├── risk_logistic.pkl
│   │       └── kmeans.pkl
│   │
│   ├── core/                         # Core infrastructure
│   │   ├── config.py                 # Settings (pydantic-settings)
│   │   ├── database.py               # MongoDB connection + indexes
│   │   ├── security.py               # JWT + bcrypt password hashing
│   │   ├── deps.py                   # FastAPI dependencies (auth)
│   │   ├── middleware.py             # Security headers + request logging
│   │   ├── rate_limit.py            # Sliding-window rate limiter
│   │   ├── cache.py                  # In-memory TTL cache
│   │   └── logging_config.py         # JSON/human-readable logging
│   │
│   ├── routers/                      # API route handlers
│   │   ├── auth.py                   # Register + Login
│   │   ├── users.py                  # User profile CRUD
│   │   ├── expenses.py               # Expense CRUD + summary
│   │   ├── income.py                 # Income CRUD + summary
│   │   ├── goals.py                  # Goal CRUD
│   │   └── investments.py            # AI recommendations + history
│   │
│   ├── schemas/                      # Pydantic request/response models
│   │   ├── user.py
│   │   ├── expense.py
│   │   ├── income.py
│   │   ├── goal.py
│   │   └── investment.py
│   │
│   └── models/
│       └── helpers.py                # MongoDB document serializers
│
└── frontend/
    ├── package.json                  # Node.js dependencies
    ├── next.config.mjs               # Next.js configuration
    ├── tsconfig.json                 # TypeScript configuration
    ├── postcss.config.mjs            # PostCSS (Tailwind)
    │
    ├── app/                          # Next.js App Router pages
    │   ├── layout.tsx                # Root layout (fonts, theme, auth provider)
    │   ├── page.tsx                  # Landing page
    │   ├── globals.css               # Global styles
    │   ├── login/page.tsx
    │   ├── signup/page.tsx
    │   ├── onboarding/page.tsx
    │   ├── dashboard/page.tsx
    │   ├── income/page.tsx
    │   ├── expenses/page.tsx
    │   ├── investments/page.tsx
    │   ├── goals/page.tsx
    │   └── settings/page.tsx
    │
    ├── components/                   # React components
    │   ├── auth/                     # Login, Signup, Profile setup
    │   ├── dashboard/                # Sidebar, KPI, Charts, Budget
    │   ├── expenses/                 # Expense form + list
    │   ├── goals/                    # Goal form + card
    │   ├── investments/              # Investment card + recommendation
    │   └── ui/                       # shadcn/ui (30+ components)
    │
    ├── lib/                          # Utilities
    │   ├── api.ts                    # Axios client + API modules
    │   ├── auth-context.tsx          # Auth React context
    │   ├── auth.ts                   # Auth helper functions
    │   └── utils.ts                  # Utility functions
    │
    └── hooks/                        # Custom React hooks
        ├── use-mobile.ts
        └── use-toast.ts
```

---

## ⚙ Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment mode |
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection string |
| `DATABASE_NAME` | `profitpath` | Database name |
| `SECRET_KEY` | *(set a strong key)* | JWT signing secret |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | CORS allowed origins |
| `RATE_LIMIT_PER_MINUTE` | `60` | API rate limit per minute |
| `ENABLE_REAL_MARKET_DATA` | `true` | Enable live Yahoo Finance data |
| `ENABLE_ML_PREDICTIONS` | `true` | Enable ML model predictions |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## 📊 Screenshots

> *Run the application locally to see the full UI including:*
> - **Dashboard** — KPI cards, trend charts, expense breakdown, budget tracker
> - **Income Management** — Monthly income tracking with auto-seeding
> - **Expense Tracker** — Categorized expense management with summaries
> - **AI Investment Hub** — ML-powered recommendations with real stock tickers, live prices, mutual fund names, portfolio allocation, SIP projections, and market indices
> - **Financial Goals** — Priority-based goal tracking with progress bars

---

## 👥 Team

| Role | Technology |
|------|-----------|
| Backend Development | FastAPI, MongoDB, Python |
| ML/AI Engineering | scikit-learn, yfinance, pandas, numpy |
| Frontend Development | Next.js, React, TypeScript, Tailwind CSS |
| Infrastructure | Docker, Kubernetes, Gunicorn |

---

## 📄 License

This project is for educational and demonstration purposes.

---

<p align="center">
  Built with ❤️ using FastAPI + Next.js + scikit-learn
</p>
