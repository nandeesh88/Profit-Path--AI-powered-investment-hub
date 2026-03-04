import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'

export interface BudgetCategory {
  name: string
  spent: number
}

interface BudgetTrackerProps {
  data: BudgetCategory[]
  monthlyIncome: number
}

export function BudgetTracker({ data, monthlyIncome }: BudgetTrackerProps) {
  // Allocate budget proportionally: each category gets a share of income based on typical ratios
  // If no income set, show spent only without budget comparison
  const totalSpent = data.reduce((s, c) => s + c.spent, 0)
  const hasData = data.length > 0

  return (
    <Card className="backdrop-blur-md bg-white/60 border border-white/30 shadow-md">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-6">Budget Tracker</h3>
        {!hasData ? (
          <p className="text-muted-foreground text-sm py-4">
            No expenses this month. Add expenses to track your budget.
          </p>
        ) : (
          <div className="space-y-5">
            {data.map((category) => {
              // Budget per category is proportional share of monthly income
              // If no income, treat total as the baseline
              const budget = monthlyIncome > 0
                ? Math.round((monthlyIncome / data.length))
                : category.spent
              const percentage = budget > 0
                ? Math.min((category.spent / budget) * 100, 100)
                : 0
              const isOverBudget = monthlyIncome > 0 && category.spent > budget

              return (
                <div key={category.name} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-foreground">{category.name}</p>
                    <span className={`text-sm font-semibold ${isOverBudget ? 'text-destructive' : 'text-accent'}`}>
                      ₹{category.spent.toLocaleString('en-IN')}
                      {monthlyIncome > 0 && ` / ₹${budget.toLocaleString('en-IN')}`}
                    </span>
                  </div>
                  <Progress
                    value={percentage}
                    className="h-2 bg-white/50"
                    style={{
                      background: 'hsl(var(--color-muted))',
                    } as any}
                  />
                </div>
              )
            })}

            {/* Total row */}
            <div className="pt-3 border-t border-border/50">
              <div className="flex items-center justify-between">
                <p className="font-semibold text-foreground">Total Spent</p>
                <span className={`text-sm font-bold ${
                  monthlyIncome > 0 && totalSpent > monthlyIncome ? 'text-destructive' : 'text-accent'
                }`}>
                  ₹{totalSpent.toLocaleString('en-IN')}
                  {monthlyIncome > 0 && ` / ₹${monthlyIncome.toLocaleString('en-IN')}`}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  )
}
