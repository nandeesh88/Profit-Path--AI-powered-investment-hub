'use client'

import { useState, useEffect } from 'react'
import { Sidebar } from '@/components/dashboard/sidebar'
import { ProtectedRoute } from '@/components/protected-route'
import { useAuth } from '@/lib/auth-context'
import { investmentsApi, expensesApi, incomeApi } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  TrendingUp,
  PieChart,
  Lightbulb,
  RefreshCw,
  IndianRupee,
  BarChart3,
  ArrowUpRight,
  Shield,
  Wallet,
  Clock,
  AlertCircle,
} from 'lucide-react'

interface PortfolioAllocation {
  stocks_percent: number
  mutual_funds_percent: number
  sip_percent: number
  emergency_fund_percent: number
}

interface StockRec {
  category: string
  ticker?: string
  current_price?: number
  description: string
  risk_level: 'low' | 'medium' | 'high'
  expected_return_range: string
}

interface MFRec {
  fund_type: string
  fund_name?: string
  description: string
  risk_level: 'low' | 'medium' | 'high'
  expected_return_range: string
}

interface SIPRec {
  monthly_sip_amount: number
  recommended_fund: string
  expected_corpus_5yr: number
  expected_corpus_10yr: number
}

interface Recommendation {
  user_segment: string
  risk_profile: string
  ml_predicted_risk: string
  monthly_savings: number
  savings_rate_percent: number
  investable_amount: number
  portfolio_allocation: PortfolioAllocation
  stock_recommendations: StockRec[]
  mutual_fund_recommendations: MFRec[]
  sip_recommendation: SIPRec
  expected_return_percent: number
  investment_timeframe: string
  financial_advice: string[]
  market_context: Record<string, { current_level: number; yoy_return: number }>
  generated_at: string
}

const riskColors: Record<string, string> = {
  low: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  high: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
}

const riskBorder: Record<string, string> = {
  low: 'border-green-200 dark:border-green-800',
  medium: 'border-yellow-200 dark:border-yellow-800',
  high: 'border-red-200 dark:border-red-800',
}

export default function InvestmentsPage() {
  const { user } = useAuth()
  const [rec, setRec] = useState<Recommendation | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [monthlyIncome, setMonthlyIncome] = useState(0)
  const [monthlyExpense, setMonthlyExpense] = useState(0)

  const fetchRecommendation = async () => {
    setLoading(true)
    setError('')
    try {
      // Fetch current month income and expense summary in parallel
      const [incomeRes, expSummaryRes] = await Promise.all([
        incomeApi.list(),
        expensesApi.summary(),
      ])

      const now = new Date()
      const currentMonthKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`

      // Sum income for current month from income records, fall back to profile
      const allIncomes = incomeRes.data as any[]
      const currentMonthTotal = allIncomes
        .filter((i: any) => i.month === currentMonthKey)
        .reduce((s: number, i: any) => s + i.amount, 0)
      const income = currentMonthTotal || user?.monthly_income || 0
      const expense = expSummaryRes.data.monthly_expenses || 0

      setMonthlyIncome(income)
      setMonthlyExpense(expense)

      const savings = Math.max(income - expense, 0)

      // Call the ML recommendation API
      const res = await investmentsApi.recommend({
        monthly_income: income,
        monthly_expenses: expense,
        savings,
        risk_tolerance: user?.risk_tolerance || 'medium',
        financial_goal: user?.financial_goal || 'General savings',
        age: 30,
        investment_horizon_years: 5,
      })

      setRec(res.data)
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to generate recommendations'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) fetchRecommendation()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  const fmt = (n: number) =>
    '₹' + Math.abs(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })

  const fmtLakh = (n: number) => {
    if (n >= 10000000) return `₹${(n / 10000000).toFixed(2)} Cr`
    if (n >= 100000) return `₹${(n / 100000).toFixed(2)} L`
    return fmt(n)
  }

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 md:ml-0 p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-4xl font-bold text-foreground mb-2">Investment Hub</h1>
                <p className="text-muted-foreground">
                  AI-powered recommendations using your real financial data &amp; live market analysis
                </p>
              </div>
              <Button
                onClick={fetchRecommendation}
                disabled={loading}
                variant="outline"
                className="gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                {loading ? 'Analyzing...' : 'Refresh'}
              </Button>
            </div>

            {error && (
              <Card className="p-6 mb-8 border-destructive/50 bg-destructive/5">
                <div className="flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-destructive" />
                  <p className="text-destructive">{error}</p>
                </div>
              </Card>
            )}

            {loading && !rec ? (
              <div className="text-center py-24">
                <RefreshCw className="w-10 h-10 mx-auto mb-4 animate-spin text-muted-foreground" />
                <p className="text-lg text-muted-foreground">
                  Analyzing your finances &amp; fetching live market data...
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  This may take a moment while we pull real-time stock data
                </p>
              </div>
            ) : rec ? (
              <>
                {/* Overview KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                  <Card className="p-5">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900/30">
                        <Wallet className="w-5 h-5 text-green-600" />
                      </div>
                      <p className="text-sm text-muted-foreground">Monthly Savings</p>
                    </div>
                    <p className="text-2xl font-bold">{fmt(rec.monthly_savings)}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {rec.savings_rate_percent.toFixed(1)}% of income
                    </p>
                  </Card>
                  <Card className="p-5">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30">
                        <IndianRupee className="w-5 h-5 text-blue-600" />
                      </div>
                      <p className="text-sm text-muted-foreground">Investable Amount</p>
                    </div>
                    <p className="text-2xl font-bold">{fmt(rec.investable_amount)}</p>
                    <p className="text-xs text-muted-foreground mt-1">80% of your savings</p>
                  </Card>
                  <Card className="p-5">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/30">
                        <Shield className="w-5 h-5 text-purple-600" />
                      </div>
                      <p className="text-sm text-muted-foreground">Risk Profile</p>
                    </div>
                    <p className="text-2xl font-bold capitalize">{rec.risk_profile}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      ML predicted: {rec.ml_predicted_risk} · Segment: {rec.user_segment}
                    </p>
                  </Card>
                  <Card className="p-5">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 rounded-lg bg-amber-100 dark:bg-amber-900/30">
                        <TrendingUp className="w-5 h-5 text-amber-600" />
                      </div>
                      <p className="text-sm text-muted-foreground">Expected Return</p>
                    </div>
                    <p className="text-2xl font-bold">{rec.expected_return_percent}% p.a.</p>
                    <p className="text-xs text-muted-foreground mt-1 capitalize">
                      {rec.investment_timeframe} horizon
                    </p>
                  </Card>
                </div>

                {/* Portfolio Allocation */}
                <Card className="p-6 mb-8">
                  <div className="flex items-center gap-3 mb-6">
                    <PieChart className="w-5 h-5 text-primary" />
                    <h2 className="text-xl font-bold">Recommended Portfolio Allocation</h2>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      {
                        label: 'Stocks',
                        pct: rec.portfolio_allocation.stocks_percent,
                        amount: rec.investable_amount * rec.portfolio_allocation.stocks_percent / 100,
                        color: 'bg-blue-500',
                        bg: 'bg-blue-50 dark:bg-blue-950/30',
                      },
                      {
                        label: 'Mutual Funds',
                        pct: rec.portfolio_allocation.mutual_funds_percent,
                        amount: rec.investable_amount * rec.portfolio_allocation.mutual_funds_percent / 100,
                        color: 'bg-green-500',
                        bg: 'bg-green-50 dark:bg-green-950/30',
                      },
                      {
                        label: 'SIP',
                        pct: rec.portfolio_allocation.sip_percent,
                        amount: rec.investable_amount * rec.portfolio_allocation.sip_percent / 100,
                        color: 'bg-purple-500',
                        bg: 'bg-purple-50 dark:bg-purple-950/30',
                      },
                      {
                        label: 'Emergency Fund',
                        pct: rec.portfolio_allocation.emergency_fund_percent,
                        amount: rec.investable_amount * rec.portfolio_allocation.emergency_fund_percent / 100,
                        color: 'bg-amber-500',
                        bg: 'bg-amber-50 dark:bg-amber-950/30',
                      },
                    ].map((item) => (
                      <div key={item.label} className={`rounded-xl p-4 ${item.bg}`}>
                        <div className="flex items-center gap-2 mb-2">
                          <div className={`w-3 h-3 rounded-full ${item.color}`} />
                          <span className="text-sm font-medium">{item.label}</span>
                        </div>
                        <p className="text-2xl font-bold">{item.pct}%</p>
                        <p className="text-xs text-muted-foreground">{fmt(item.amount)}/month</p>
                      </div>
                    ))}
                  </div>
                  {/* Bar visual */}
                  <div className="mt-4 flex rounded-full h-3 overflow-hidden">
                    <div className="bg-blue-500" style={{ width: `${rec.portfolio_allocation.stocks_percent}%` }} />
                    <div className="bg-green-500" style={{ width: `${rec.portfolio_allocation.mutual_funds_percent}%` }} />
                    <div className="bg-purple-500" style={{ width: `${rec.portfolio_allocation.sip_percent}%` }} />
                    <div className="bg-amber-500" style={{ width: `${rec.portfolio_allocation.emergency_fund_percent}%` }} />
                  </div>
                </Card>

                {/* Stock Recommendations */}
                <div className="mb-8">
                  <div className="flex items-center gap-3 mb-4">
                    <BarChart3 className="w-5 h-5 text-blue-600" />
                    <h2 className="text-xl font-bold">Stock Recommendations</h2>
                    <Badge variant="outline" className="text-xs">Live Data</Badge>
                  </div>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {rec.stock_recommendations.map((stock, i) => (
                      <Card
                        key={i}
                        className={`p-5 border-2 ${riskBorder[stock.risk_level] || ''} hover:shadow-lg transition-shadow`}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            {stock.ticker && (
                              <p className="text-lg font-bold text-foreground">{stock.ticker}</p>
                            )}
                            <p className="text-sm text-muted-foreground">{stock.category}</p>
                          </div>
                          <Badge className={riskColors[stock.risk_level] || ''}>
                            {stock.risk_level} risk
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">{stock.description}</p>
                        <div className="flex items-center justify-between pt-3 border-t">
                          {stock.current_price ? (
                            <div>
                              <p className="text-xs text-muted-foreground">Current Price</p>
                              <p className="font-semibold">
                                {stock.ticker?.includes('.NS') ? '₹' : '$'}
                                {stock.current_price.toLocaleString('en-IN')}
                              </p>
                            </div>
                          ) : (
                            <div />
                          )}
                          <div className="text-right">
                            <p className="text-xs text-muted-foreground">Expected Return</p>
                            <p className="font-semibold text-green-600 flex items-center gap-1">
                              <ArrowUpRight className="w-3 h-3" />
                              {stock.expected_return_range}
                            </p>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>

                {/* Mutual Fund Recommendations */}
                <div className="mb-8">
                  <div className="flex items-center gap-3 mb-4">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                    <h2 className="text-xl font-bold">Mutual Fund Recommendations</h2>
                  </div>
                  <div className="grid md:grid-cols-2 gap-4">
                    {rec.mutual_fund_recommendations.map((mf, i) => (
                      <Card
                        key={i}
                        className={`p-5 border-2 ${riskBorder[mf.risk_level] || ''} hover:shadow-lg transition-shadow`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            {mf.fund_name && (
                              <p className="text-base font-bold text-foreground mb-1">
                                {mf.fund_name}
                              </p>
                            )}
                            <p className="text-sm font-medium text-muted-foreground">
                              {mf.fund_type}
                            </p>
                          </div>
                          <Badge className={riskColors[mf.risk_level] || ''}>
                            {mf.risk_level} risk
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">{mf.description}</p>
                        <div className="flex items-center justify-end pt-3 border-t">
                          <p className="font-semibold text-green-600 flex items-center gap-1">
                            <ArrowUpRight className="w-3 h-3" />
                            {mf.expected_return_range} p.a.
                          </p>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>

                {/* SIP Plan */}
                <Card className="p-6 mb-8 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/20 dark:to-blue-950/20 border-purple-200 dark:border-purple-800">
                  <div className="flex items-center gap-3 mb-4">
                    <Clock className="w-5 h-5 text-purple-600" />
                    <h2 className="text-xl font-bold">SIP Plan (Systematic Investment Plan)</h2>
                  </div>
                  <div className="grid md:grid-cols-4 gap-6">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Monthly SIP Amount</p>
                      <p className="text-2xl font-bold text-purple-700 dark:text-purple-400">
                        {fmt(rec.sip_recommendation.monthly_sip_amount)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Recommended Fund</p>
                      <p className="text-base font-semibold">
                        {rec.sip_recommendation.recommended_fund}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">5-Year Corpus</p>
                      <p className="text-2xl font-bold text-green-600">
                        {fmtLakh(rec.sip_recommendation.expected_corpus_5yr)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">10-Year Corpus</p>
                      <p className="text-2xl font-bold text-green-700 dark:text-green-500">
                        {fmtLakh(rec.sip_recommendation.expected_corpus_10yr)}
                      </p>
                    </div>
                  </div>
                </Card>

                {/* Market Context */}
                {rec.market_context && Object.keys(rec.market_context).length > 0 && (
                  <Card className="p-6 mb-8">
                    <div className="flex items-center gap-3 mb-4">
                      <BarChart3 className="w-5 h-5 text-primary" />
                      <h2 className="text-xl font-bold">Market Overview</h2>
                      <Badge variant="outline" className="text-xs">Live</Badge>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(rec.market_context).map(([name, data]) => (
                        <div key={name} className="text-center p-3 rounded-lg bg-muted/30">
                          <p className="text-xs text-muted-foreground mb-1">
                            {name.replace(/_/g, ' ')}
                          </p>
                          <p className="text-lg font-bold">
                            {data.current_level.toLocaleString('en-IN', {
                              maximumFractionDigits: 0,
                            })}
                          </p>
                          <p
                            className={`text-sm font-medium ${
                              data.yoy_return >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}
                          >
                            {data.yoy_return >= 0 ? '+' : ''}
                            {data.yoy_return.toFixed(1)}% YoY
                          </p>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {/* Financial Advice */}
                <Card className="p-6 mb-8">
                  <div className="flex items-center gap-3 mb-4">
                    <Lightbulb className="w-5 h-5 text-amber-500" />
                    <h2 className="text-xl font-bold">Personalized Financial Advice</h2>
                  </div>
                  <div className="grid md:grid-cols-2 gap-3">
                    {rec.financial_advice.map((advice, i) => (
                      <div
                        key={i}
                        className="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/30 text-sm"
                      >
                        {advice}
                      </div>
                    ))}
                  </div>
                </Card>

                {/* Income vs Expense Used */}
                <div className="text-center text-sm text-muted-foreground pb-8">
                  Based on your current month income of {fmt(monthlyIncome)} and expenses of{' '}
                  {fmt(monthlyExpense)} · Leftover: {fmt(monthlyIncome - monthlyExpense)}
                </div>
              </>
            ) : null}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
