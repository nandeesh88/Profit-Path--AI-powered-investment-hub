'use client'

import { useState, useEffect } from 'react'
import { Sidebar } from '@/components/dashboard/sidebar'
import { KPICard } from '@/components/dashboard/kpi-card'
import { ExpenseChart, CategoryData } from '@/components/dashboard/expense-chart'
import { TrendChart, TrendDataPoint } from '@/components/dashboard/trend-chart'
import { BudgetTracker, BudgetCategory } from '@/components/dashboard/budget-tracker'
import { ProtectedRoute } from '@/components/protected-route'
import { useAuth } from '@/lib/auth-context'
import { expensesApi, goalsApi, incomeApi } from '@/lib/api'

const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

export default function DashboardPage() {
  const { user } = useAuth()
  const [totalBalance, setTotalBalance] = useState(0)
  const [monthlyIncome, setMonthlyIncome] = useState(0)
  const [monthlyExpense, setMonthlyExpense] = useState(0)
  const [netSavings, setNetSavings] = useState(0)
  const [loading, setLoading] = useState(true)

  // Chart data states
  const [trendData, setTrendData] = useState<TrendDataPoint[]>([])
  const [categoryData, setCategoryData] = useState<CategoryData[]>([])
  const [budgetData, setBudgetData] = useState<BudgetCategory[]>([])

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const defaultIncome = user?.monthly_income || 0

        // Fetch all expenses, summary, goals, and income records in parallel
        const [expListRes, expSummaryRes, goalsRes, incomeRes] = await Promise.all([
          expensesApi.list(),
          expensesApi.summary(),
          goalsApi.list(),
          incomeApi.list(),
        ])

        const allExpenses = expListRes.data as any[]
        const summary = expSummaryRes.data
        const allIncomes = incomeRes.data as any[]
        const monthlyExp = summary.monthly_expenses || 0
        setMonthlyExpense(monthlyExp)

        // Build a map of income by month from income records
        const incomeByMonth: Record<string, number> = {}
        for (const inc of allIncomes) {
          incomeByMonth[inc.month] = (incomeByMonth[inc.month] || 0) + inc.amount
        }

        // Calculate current month income
        const now = new Date()
        const currentMonthKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
        const currentIncome = incomeByMonth[currentMonthKey] ?? defaultIncome
        setMonthlyIncome(currentIncome)

        // Total income across all recorded months
        const totalIncomeFromRecords = allIncomes.reduce((s: number, i: any) => s + i.amount, 0)
        // If no income record exists for current month, include profile income so
        // new users who entered income at registration still see it on dashboard
        const hasCurrentMonthRecord = currentMonthKey in incomeByMonth
        const totalIncomeAllMonths = hasCurrentMonthRecord
          ? totalIncomeFromRecords
          : totalIncomeFromRecords + defaultIncome

        // Total expenses across all time
        const totalExpensesAllTime = summary.total_expenses || 0

        // Goals total saved
        const totalSaved = (goalsRes.data as any[]).reduce(
          (sum: number, g: any) => sum + (g.current_amount || 0),
          0
        )

        const savings = currentIncome - monthlyExp
        setNetSavings(savings)
        // Total Balance = cumulative income - cumulative expenses + goal savings
        setTotalBalance(totalIncomeAllMonths - totalExpensesAllTime + totalSaved)

        // ── Build Trend Data (last 6 months income vs expenses) ──
        const monthlyExpMap: Record<string, number> = {}
        for (let i = 5; i >= 0; i--) {
          const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
          const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
          monthlyExpMap[key] = 0
        }
        for (const exp of allExpenses) {
          const dateStr = exp.date as string // "YYYY-MM-DD"
          const key = dateStr.substring(0, 7) // "YYYY-MM"
          if (key in monthlyExpMap) {
            monthlyExpMap[key] += exp.amount
          }
        }
        const trend: TrendDataPoint[] = Object.entries(monthlyExpMap).map(([key, total]) => {
          const [y, m] = key.split('-')
          // Use per-month income from records, or fall back to user's default monthly_income
          const monthIncome = incomeByMonth[key] ?? defaultIncome
          return {
            month: MONTH_NAMES[parseInt(m) - 1],
            income: Math.round(monthIncome),
            expense: Math.round(total),
          }
        })
        setTrendData(trend)

        // ── Build Category Breakdown (all-time by_category from summary) ──
        const byCat: Record<string, number> = summary.by_category || {}
        const catData: CategoryData[] = Object.entries(byCat)
          .filter(([, v]) => v > 0)
          .sort((a, b) => b[1] - a[1])
          .map(([name, value]) => ({ name, value: Math.round(value) }))
        setCategoryData(catData)

        // ── Build Budget Tracker (current month by category) ──
        const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
        const currentMonthCats: Record<string, number> = {}
        for (const exp of allExpenses) {
          const dateStr = exp.date as string
          if (dateStr.startsWith(currentMonth)) {
            currentMonthCats[exp.category] = (currentMonthCats[exp.category] || 0) + exp.amount
          }
        }
        const budget: BudgetCategory[] = Object.entries(currentMonthCats)
          .sort((a, b) => b[1] - a[1])
          .map(([name, spent]) => ({ name, spent: Math.round(spent) }))
        setBudgetData(budget)
      } catch (err) {
        console.error('Failed to load dashboard data:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchDashboardData()
  }, [user])

  const fmt = (n: number) =>
    '₹' + Math.abs(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-background">
        <Sidebar />

        <main className="flex-1 md:ml-0 p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-foreground mb-2">Command Center</h1>
              <p className="text-muted-foreground">
                Welcome back{user?.name ? `, ${user.name}` : ''}! Here's your financial overview.
              </p>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <KPICard
                title="Total Balance"
                value={loading ? '...' : fmt(totalBalance)}
                description="All income − all expenses"
                trend={0}
                icon="wallet"
              />
              <KPICard
                title="Monthly Income"
                value={loading ? '...' : fmt(monthlyIncome)}
                description="From your profile"
                trend={0}
                icon="income"
              />
              <KPICard
                title="Monthly Expense"
                value={loading ? '...' : fmt(monthlyExpense)}
                description="Tracked this month"
                trend={0}
                icon="expense"
              />
              <KPICard
                title="Net Savings"
                value={loading ? '...' : fmt(netSavings)}
                description="Available to invest"
                trend={0}
                icon="savings"
              />
            </div>

            {/* Charts and Tracker */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              <div className="lg:col-span-2">
                <TrendChart data={trendData} />
              </div>
              <div>
                <ExpenseChart data={categoryData} />
              </div>
            </div>

          {/* Budget Tracker */}
          <BudgetTracker data={budgetData} monthlyIncome={monthlyIncome} />
        </div>
      </main>
    </div>
    </ProtectedRoute>
  )
}
