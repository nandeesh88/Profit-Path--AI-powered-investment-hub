'use client';

import { Card } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Trash2, Edit2 } from 'lucide-react'

const categoryIcons: Record<string, string> = {
  food: '🍕',
  rent: '🏠',
  entertainment: '🎬',
  transportation: '🚗',
  utilities: '💡',
  shopping: '🛍️',
  health: '💪',
  education: '📚',
  other: '📌',
}

interface Expense {
  id: string
  description: string
  amount: number
  category: string
  date: string
}

interface ExpenseListProps {
  expenses: Expense[]
  onEdit?: (expense: Expense) => void
  onDelete?: (id: string) => void
}

export function ExpenseList({ expenses, onEdit, onDelete }: ExpenseListProps) {
  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      food: 'Food & Dining',
      rent: 'Rent',
      entertainment: 'Entertainment',
      transportation: 'Transportation',
      utilities: 'Utilities',
      shopping: 'Shopping',
      health: 'Health & Fitness',
      education: 'Education',
      other: 'Other',
    }
    return labels[category] || category
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  return (
    <Card className="backdrop-blur-md bg-white/60 border border-white/30 shadow-md">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">Recent Expenses</h3>

        {expenses.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">No expenses yet. Add your first expense above!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-white/20">
                  <TableHead className="text-foreground font-semibold">Description</TableHead>
                  <TableHead className="text-foreground font-semibold">Category</TableHead>
                  <TableHead className="text-foreground font-semibold">Date</TableHead>
                  <TableHead className="text-foreground font-semibold text-right">Amount</TableHead>
                  <TableHead className="text-foreground font-semibold text-center">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {expenses.map((expense) => (
                  <TableRow key={expense.id} className="border-white/10">
                    <TableCell className="text-foreground">
                      <div className="flex items-center gap-2">
                        <span>{categoryIcons[expense.category] || '📌'}</span>
                        {expense.description}
                      </div>
                    </TableCell>
                    <TableCell className="text-foreground">
                      {getCategoryLabel(expense.category)}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatDate(expense.date)}
                    </TableCell>
                    <TableCell className="text-foreground font-semibold text-right">
                      ₹{expense.amount.toFixed(2)}
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex items-center justify-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onEdit?.(expense)}
                          className="hover:bg-accent/20"
                        >
                          <Edit2 className="w-4 h-4 text-accent" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onDelete?.(expense.id)}
                          className="hover:bg-destructive/20"
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </Card>
  )
}
