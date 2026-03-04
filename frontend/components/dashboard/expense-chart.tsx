'use client'

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { Card } from '@/components/ui/card'

export interface CategoryData {
  name: string
  value: number
}

interface ExpenseChartProps {
  data: CategoryData[]
}

const COLORS = [
  'hsl(var(--color-accent))',
  'hsl(var(--color-destructive))',
  'hsl(var(--color-chart-3))',
  'hsl(var(--color-chart-4))',
  'hsl(var(--color-chart-5))',
  'hsl(var(--color-muted))',
  '#8884d8',
  '#82ca9d',
  '#ffc658',
  '#ff7300',
]

export function ExpenseChart({ data }: ExpenseChartProps) {
  const hasData = data.length > 0

  return (
    <Card className="backdrop-blur-md bg-white/60 border border-white/30 shadow-md">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">Expense Breakdown</h3>
        {!hasData ? (
          <div className="flex items-center justify-center h-[300px] text-muted-foreground text-sm text-center">
            No expenses recorded yet.<br />Add expenses to see the breakdown.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
              >
                {data.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                  border: '1px solid rgba(0, 0, 0, 0.1)',
                  borderRadius: '8px',
                }}
                formatter={(value: number) => `₹${value.toLocaleString('en-IN')}`}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </Card>
  )
}
