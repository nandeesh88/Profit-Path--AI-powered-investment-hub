'use client'

import { useState, useEffect, useCallback } from 'react'
import { Sidebar } from '@/components/dashboard/sidebar'
import { AddExpenseForm, ExpenseData } from '@/components/expenses/add-expense-form'
import { ExpenseList } from '@/components/expenses/expense-list'
import { ReceiptUploadModal } from '@/components/expenses/receipt-upload-modal'
import { ProtectedRoute } from '@/components/protected-route'
import { expensesApi } from '@/lib/api'
import { Upload } from 'lucide-react'

interface Expense {
  id: string
  description: string
  amount: number
  category: string
  date: string
}

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [loading, setLoading] = useState(true)
  const [monthlyTotal, setMonthlyTotal] = useState(0)
  const [uploadOpen, setUploadOpen] = useState(false)

  const fetchExpenses = useCallback(async () => {
    try {
      const res = await expensesApi.list()
      const data = (res.data as any[]).map((e: any) => ({
        id: e.id,
        description: e.description,
        amount: e.amount,
        category: e.category,
        date: e.date,
      }))
      setExpenses(data)

      // Fetch summary for monthly total
      const summaryRes = await expensesApi.summary()
      setMonthlyTotal(summaryRes.data.monthly_expenses || 0)
    } catch (err) {
      console.error('Failed to load expenses:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchExpenses()
  }, [fetchExpenses])

  const handleAddExpense = async (expense: ExpenseData) => {
    try {
      if (expense.upload_id) {
        await expensesApi.createFromExtraction({
          upload_id: expense.upload_id,
          description: expense.description,
          amount: expense.amount,
          category: expense.category,
          date: expense.date,
          transaction_type: 'debit',
          bank_reference_id: expense.bank_reference_id,
        })
      } else {
        await expensesApi.create({
          description: expense.description,
          amount: expense.amount,
          category: expense.category,
          date: expense.date,
          transaction_type: 'debit',
          bank_reference_id: expense.bank_reference_id,
          source_document_id: expense.source_document_id,
        })
      }
      await fetchExpenses()
    } catch (err: any) {
      console.error('Failed to add expense:', err)
      alert(err?.response?.data?.detail || 'Failed to add expense')
    }
  }

  const handleDeleteExpense = async (id: string) => {
    try {
      await expensesApi.delete(id)
      await fetchExpenses()
    } catch (err) {
      console.error('Failed to delete expense:', err)
    }
  }

  const handleEditExpense = (expense: Expense) => {
    console.log('Edit expense:', expense)
  }

  const totalExpenses = expenses.reduce((sum, e) => sum + e.amount, 0)
  const avgExpense = expenses.length > 0 ? (totalExpenses / expenses.length) : 0

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-background">
        <Sidebar />

        <main className="flex-1 md:ml-0 p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h1 className="text-4xl font-bold text-foreground mb-2">Expense Management</h1>
                <p className="text-muted-foreground">Track and manage your spending patterns</p>
              </div>
              <button
                id="upload-receipt-btn"
                onClick={() => setUploadOpen(true)}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-accent to-accent/80 hover:from-accent/90 hover:to-accent/70 shadow-md hover:shadow-lg transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] whitespace-nowrap self-start sm:self-auto"
              >
                <Upload className="w-4 h-4" />
                Upload Receipt / Statement
              </button>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="backdrop-blur-md bg-white/60 border border-white/30 rounded-lg p-6 shadow-md">
                <p className="text-muted-foreground text-sm mb-2">Total Expenses</p>
                <h3 className="text-3xl font-bold text-foreground">
                  {loading ? '...' : `₹${totalExpenses.toFixed(2)}`}
                </h3>
                <p className="text-xs text-muted-foreground mt-2">{expenses.length} transactions</p>
              </div>
              <div className="backdrop-blur-md bg-white/60 border border-white/30 rounded-lg p-6 shadow-md">
                <p className="text-muted-foreground text-sm mb-2">Average Expense</p>
                <h3 className="text-3xl font-bold text-foreground">
                  {loading ? '...' : `₹${avgExpense.toFixed(2)}`}
                </h3>
                <p className="text-xs text-muted-foreground mt-2">Per transaction</p>
              </div>
              <div className="backdrop-blur-md bg-white/60 border border-white/30 rounded-lg p-6 shadow-md">
                <p className="text-muted-foreground text-sm mb-2">This Month</p>
                <h3 className="text-3xl font-bold text-accent">
                  {loading ? '...' : `₹${monthlyTotal.toLocaleString('en-IN')}`}
                </h3>
                <p className="text-xs text-muted-foreground mt-2">Tracked expenses</p>
              </div>
            </div>

            {/* Add Expense Form */}
            <div className="mb-8">
              <AddExpenseForm onSubmit={handleAddExpense} />
            </div>

          {/* Expense List */}
          <ExpenseList
            expenses={expenses}
            onEdit={handleEditExpense}
            onDelete={handleDeleteExpense}
          />
        </div>

        {/* Upload Modal */}
        <ReceiptUploadModal
          open={uploadOpen}
          onOpenChange={setUploadOpen}
          onExpensesAdded={fetchExpenses}
        />
      </main>
      </div>
    </ProtectedRoute>
  )
}
