'use client'

import { useState, useEffect, useCallback } from 'react'
import { Sidebar } from '@/components/dashboard/sidebar'
import { AddGoalForm, GoalData } from '@/components/goals/add-goal-form'
import { GoalCard } from '@/components/goals/goal-card'
import { ProtectedRoute } from '@/components/protected-route'
import { goalsApi, incomeApi, expensesApi } from '@/lib/api'
import { useAuth } from '@/lib/auth-context'

interface Goal {
  id: string
  name: string
  targetAmount: number
  currentAmount: number
  deadline: string
  priority: 'low' | 'medium' | 'high'
  description?: string
}

export default function GoalsPage() {
  const { user } = useAuth()
  const [goals, setGoals] = useState<Goal[]>([])
  const [netSavings, setNetSavings] = useState(0)
  const [loading, setLoading] = useState(true)

  const fetchGoals = useCallback(async () => {
    try {
      const [goalsRes, incomeRes, expSummaryRes] = await Promise.all([
        goalsApi.list(),
        incomeApi.list(),
        expensesApi.summary(),
      ])

      const data = (goalsRes.data as any[]).map((g: any) => ({
        id: g.id,
        name: g.title,
        targetAmount: g.target_amount,
        currentAmount: g.current_amount,
        deadline: g.target_date,
        priority: g.priority || 'medium',
        description: g.description,
      }))
      setGoals(data)

      // Calculate Net Savings = total income - total expenses
      const allIncomes = incomeRes.data as any[]
      const totalIncomeFromRecords = allIncomes.reduce((s: number, i: any) => s + i.amount, 0)
      const defaultIncome = user?.monthly_income || 0
      const now = new Date()
      const currentMonthKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
      const hasCurrentMonthRecord = allIncomes.some((i: any) => i.month === currentMonthKey)
      const totalIncome = hasCurrentMonthRecord ? totalIncomeFromRecords : totalIncomeFromRecords + defaultIncome
      const totalExpenses = expSummaryRes.data.total_expenses || 0
      setNetSavings(Math.max(totalIncome - totalExpenses, 0))
    } catch (err) {
      console.error('Failed to load goals:', err)
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    fetchGoals()
  }, [fetchGoals])

  const handleAddGoal = async (goal: GoalData) => {
    try {
      await goalsApi.create({
        title: goal.name,
        target_amount: goal.targetAmount,
        current_amount: goal.currentAmount,
        target_date: goal.deadline,
        category: 'Other',
        priority: goal.priority,
        description: goal.description,
      })
      await fetchGoals()
    } catch (err: any) {
      console.error('Failed to add goal:', err)
      alert(err?.response?.data?.detail || 'Failed to add goal')
    }
  }

  const handleDeleteGoal = async (id: string) => {
    try {
      await goalsApi.delete(id)
      await fetchGoals()
    } catch (err) {
      console.error('Failed to delete goal:', err)
    }
  }

  const highPriorityGoals = goals.filter((g) => g.priority === 'high')
  const mediumPriorityGoals = goals.filter((g) => g.priority === 'medium')
  const lowPriorityGoals = goals.filter((g) => g.priority === 'low')

  const totalGoalAmount = goals.reduce((sum, g) => sum + g.targetAmount, 0)
  const totalSaved = netSavings
  const totalRemaining = Math.max(totalGoalAmount - totalSaved, 0)

  // Distribute net savings proportionally across goals based on target amount
  const getGoalSavings = (goal: Goal) => {
    if (totalGoalAmount <= 0) return 0
    const proportion = goal.targetAmount / totalGoalAmount
    return Math.min(Math.round(netSavings * proportion), goal.targetAmount)
  }

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-background">
        <Sidebar />

        <main className="flex-1 md:ml-0 p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-foreground mb-2">Financial Goals</h1>
              <p className="text-muted-foreground">Set, track, and achieve your financial objectives</p>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="backdrop-blur-md bg-white/60 border border-white/30 rounded-lg p-6 shadow-md">
                <p className="text-muted-foreground text-sm mb-2">Total Goal Amount</p>
                <h3 className="text-3xl font-bold text-foreground">
                  {loading ? '...' : `₹${totalGoalAmount.toLocaleString()}`}
                </h3>
                <p className="text-xs text-muted-foreground mt-2">{goals.length} active goals</p>
              </div>
              <div className="backdrop-blur-md bg-white/60 border border-white/30 rounded-lg p-6 shadow-md">
                <p className="text-muted-foreground text-sm mb-2">Net Savings</p>
                <h3 className="text-3xl font-bold text-accent">
                  {loading ? '...' : `₹${totalSaved.toLocaleString()}`}
                </h3>
                <p className="text-xs text-muted-foreground mt-2">
                  {totalGoalAmount > 0
                    ? `${((totalSaved / totalGoalAmount) * 100).toFixed(1)}% towards goals`
                    : 'No goals yet'}
                </p>
              </div>
              <div className="backdrop-blur-md bg-white/60 border border-white/30 rounded-lg p-6 shadow-md">
                <p className="text-muted-foreground text-sm mb-2">Still Needed</p>
                <h3 className="text-3xl font-bold text-foreground">
                  {loading ? '...' : `₹${totalRemaining.toLocaleString()}`}
                </h3>
                <p className="text-xs text-muted-foreground mt-2">
                  {goals.length > 0 ? `Average: ₹${(totalRemaining / goals.length).toFixed(0)}` : 'Add a goal to start'}
                </p>
              </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-8">
              {/* Add Goal Form */}
              <div>
                <AddGoalForm onSubmit={handleAddGoal} />
              </div>

              {/* Goals List */}
              <div className="lg:col-span-2 space-y-8">
                {/* High Priority Goals */}
                {highPriorityGoals.length > 0 && (
                  <div>
                    <h2 className="text-xl font-bold text-foreground mb-4">High Priority</h2>
                    <div className="space-y-4">
                      {highPriorityGoals.map((goal) => (
                        <GoalCard
                          key={goal.id}
                          {...goal}
                          currentAmount={getGoalSavings(goal)}
                          onDelete={handleDeleteGoal}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Medium Priority Goals */}
                {mediumPriorityGoals.length > 0 && (
                  <div>
                    <h2 className="text-xl font-bold text-foreground mb-4">Medium Priority</h2>
                    <div className="space-y-4">
                      {mediumPriorityGoals.map((goal) => (
                        <GoalCard
                          key={goal.id}
                          {...goal}
                          currentAmount={getGoalSavings(goal)}
                          onDelete={handleDeleteGoal}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Low Priority Goals */}
                {lowPriorityGoals.length > 0 && (
                  <div>
                    <h2 className="text-xl font-bold text-foreground mb-4">Low Priority</h2>
                    <div className="space-y-4">
                      {lowPriorityGoals.map((goal) => (
                        <GoalCard
                          key={goal.id}
                          {...goal}
                          currentAmount={getGoalSavings(goal)}
                          onDelete={handleDeleteGoal}
                        />
                      ))}
                    </div>
                  </div>
                )}
            </div>
          </div>
        </div>
      </main>
      </div>
    </ProtectedRoute>
  )
}
