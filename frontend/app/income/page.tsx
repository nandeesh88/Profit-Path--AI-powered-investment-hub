'use client'

import { useState, useEffect, useCallback } from 'react'
import { Sidebar } from '@/components/dashboard/sidebar'
import { ProtectedRoute } from '@/components/protected-route'
import { useAuth } from '@/lib/auth-context'
import { incomeApi } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Wallet, Plus, Trash2, IndianRupee, Calendar } from 'lucide-react'

interface IncomeRecord {
  id: string
  user_id: string
  amount: number
  source: string
  description: string
  month: string
  created_at: string
}

const INCOME_SOURCES = [
  'Salary',
  'Freelance',
  'Business',
  'Investment Returns',
  'Rental Income',
  'Side Hustle',
  'Other',
]

function getMonthOptions() {
  const options: { value: string; label: string }[] = []
  const now = new Date()
  // Show past 6 months + current month + next month
  for (let i = -6; i <= 1; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() + i, 1)
    const value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    const label = d.toLocaleString('en-IN', { month: 'long', year: 'numeric' })
    options.push({ value, label })
  }
  return options
}

export default function IncomePage() {
  const { user } = useAuth()
  const [incomes, setIncomes] = useState<IncomeRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)

  // Form state
  const [amount, setAmount] = useState('')
  const [source, setSource] = useState('Salary')
  const [description, setDescription] = useState('')
  const [month, setMonth] = useState(() => {
    const now = new Date()
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  })
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const monthOptions = getMonthOptions()

  const fetchIncomes = useCallback(async () => {
    try {
      const res = await incomeApi.list()
      const records = res.data as IncomeRecord[]

      // If no income records exist but user registered with monthly_income,
      // auto-create the first income record from their profile
      if (records.length === 0 && user?.monthly_income && user.monthly_income > 0) {
        try {
          const now = new Date()
          const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
          await incomeApi.create({
            amount: user.monthly_income,
            source: 'Salary',
            description: 'Monthly income (from profile)',
            month: currentMonth,
          })
          // Re-fetch after creating
          const updated = await incomeApi.list()
          setIncomes(updated.data)
          return
        } catch (seedErr) {
          console.error('Failed to seed income from profile:', seedErr)
        }
      }

      setIncomes(records)
    } catch (err) {
      console.error('Failed to load income records:', err)
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    fetchIncomes()
  }, [fetchIncomes])

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')
    if (!amount || parseFloat(amount) <= 0) {
      setFormError('Please enter a valid amount')
      return
    }
    setSubmitting(true)
    try {
      await incomeApi.create({
        amount: parseFloat(amount),
        source,
        description,
        month,
      })
      setAmount('')
      setDescription('')
      setShowForm(false)
      fetchIncomes()
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to add income'
      setFormError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await incomeApi.delete(id)
      setIncomes((prev) => prev.filter((i) => i.id !== id))
    } catch (err) {
      console.error('Failed to delete income:', err)
    }
  }

  // Group incomes by month
  const groupedByMonth: Record<string, IncomeRecord[]> = {}
  for (const inc of incomes) {
    if (!groupedByMonth[inc.month]) groupedByMonth[inc.month] = []
    groupedByMonth[inc.month].push(inc)
  }
  const sortedMonths = Object.keys(groupedByMonth).sort().reverse()

  const totalIncome = incomes.reduce((sum, i) => sum + i.amount, 0)

  // Current month income (matches dashboard "Monthly Income")
  const now = new Date()
  const currentMonthKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  const currentMonthIncome = (groupedByMonth[currentMonthKey] || []).reduce(
    (sum, i) => sum + i.amount,
    0
  )

  const fmt = (n: number) =>
    '₹' + n.toLocaleString('en-IN', { maximumFractionDigits: 0 })

  const monthLabel = (m: string) => {
    const [y, mon] = m.split('-')
    const d = new Date(parseInt(y), parseInt(mon) - 1, 1)
    return d.toLocaleString('en-IN', { month: 'long', year: 'numeric' })
  }

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 md:ml-0 p-4 md:p-8">
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-4xl font-bold text-foreground mb-2">Income</h1>
                <p className="text-muted-foreground">
                  Track your monthly salary and other income sources
                </p>
              </div>
              <Button onClick={() => setShowForm(!showForm)} className="gap-2">
                <Plus className="w-4 h-4" />
                Add Income
              </Button>
            </div>

            {/* Summary Card */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <Card className="p-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900/30">
                    <Wallet className="w-5 h-5 text-green-600" />
                  </div>
                  <p className="text-sm text-muted-foreground">This Month&apos;s Income</p>
                </div>
                <p className="text-2xl font-bold">{loading ? '...' : fmt(currentMonthIncome)}</p>
              </Card>
              <Card className="p-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30">
                    <IndianRupee className="w-5 h-5 text-blue-600" />
                  </div>
                  <p className="text-sm text-muted-foreground">Total Income (All Months)</p>
                </div>
                <p className="text-2xl font-bold">{loading ? '...' : fmt(totalIncome)}</p>
              </Card>
              <Card className="p-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/30">
                    <Calendar className="w-5 h-5 text-purple-600" />
                  </div>
                  <p className="text-sm text-muted-foreground">Months Recorded</p>
                </div>
                <p className="text-2xl font-bold">{sortedMonths.length}</p>
              </Card>
            </div>

            {/* Add Income Form */}
            {showForm && (
              <Card className="p-6 mb-8">
                <h2 className="text-lg font-semibold mb-4">Add Income Record</h2>
                {formError && (
                  <div className="mb-4 p-3 bg-destructive/10 text-destructive text-sm rounded-lg">
                    {formError}
                  </div>
                )}
                <form onSubmit={handleAdd} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Month</Label>
                    <Select value={month} onValueChange={setMonth}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {monthOptions.map((opt) => (
                          <SelectItem key={opt.value} value={opt.value}>
                            {opt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Amount (₹)</Label>
                    <Input
                      type="number"
                      min="1"
                      placeholder="e.g. 50000"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Source</Label>
                    <Select value={source} onValueChange={setSource}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {INCOME_SOURCES.map((s) => (
                          <SelectItem key={s} value={s}>
                            {s}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Description (optional)</Label>
                    <Input
                      type="text"
                      placeholder="e.g. January salary"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                    />
                  </div>
                  <div className="md:col-span-2 flex gap-3">
                    <Button type="submit" disabled={submitting}>
                      {submitting ? 'Adding...' : 'Add Income'}
                    </Button>
                    <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                      Cancel
                    </Button>
                  </div>
                </form>
              </Card>
            )}

            {/* Income Records by Month */}
            {loading ? (
              <div className="text-center py-12 text-muted-foreground">Loading...</div>
            ) : sortedMonths.length === 0 ? (
              <Card className="p-12 text-center">
                <Wallet className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
                <h3 className="text-lg font-semibold mb-2">No income records yet</h3>
                <p className="text-muted-foreground mb-4">
                  Start by adding your monthly salary to track your income over time
                </p>
                <Button onClick={() => setShowForm(true)} className="gap-2">
                  <Plus className="w-4 h-4" />
                  Add Your First Income
                </Button>
              </Card>
            ) : (
              <div className="space-y-6">
                {sortedMonths.map((m) => {
                  const records = groupedByMonth[m]
                  const monthTotal = records.reduce((s, r) => s + r.amount, 0)
                  return (
                    <Card key={m} className="overflow-hidden">
                      <div className="p-4 bg-muted/30 border-b flex justify-between items-center">
                        <h3 className="font-semibold text-lg">{monthLabel(m)}</h3>
                        <span className="font-bold text-green-600">{fmt(monthTotal)}</span>
                      </div>
                      <div className="divide-y">
                        {records.map((inc) => (
                          <div
                            key={inc.id}
                            className="p-4 flex items-center justify-between hover:bg-muted/10 transition-colors"
                          >
                            <div className="flex-1">
                              <div className="flex items-center gap-3">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                                  {inc.source}
                                </span>
                                {inc.description && (
                                  <span className="text-sm text-muted-foreground">
                                    {inc.description}
                                  </span>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-4">
                              <span className="font-semibold text-green-600">
                                {fmt(inc.amount)}
                              </span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDelete(inc.id)}
                                className="text-destructive hover:text-destructive hover:bg-destructive/10"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </Card>
                  )
                })}
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
