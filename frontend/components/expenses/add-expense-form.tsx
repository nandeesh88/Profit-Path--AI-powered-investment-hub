'use client'

import React from "react"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Plus } from 'lucide-react'

const categories = [
  { value: 'Food & Dining', label: 'Food & Dining' },
  { value: 'Housing', label: 'Housing / Rent' },
  { value: 'Entertainment', label: 'Entertainment' },
  { value: 'Transportation', label: 'Transportation' },
  { value: 'Utilities', label: 'Utilities' },
  { value: 'Shopping', label: 'Shopping' },
  { value: 'Healthcare', label: 'Healthcare' },
  { value: 'Education', label: 'Education' },
  { value: 'Travel', label: 'Travel' },
  { value: 'Other', label: 'Other' },
]

interface AddExpenseFormProps {
  onSubmit?: (expense: ExpenseData) => void
}

export interface ExpenseData {
  description: string
  amount: number
  category: string
  date: string
}

export function AddExpenseForm({ onSubmit }: AddExpenseFormProps) {
  const [description, setDescription] = useState('')
  const [amount, setAmount] = useState('')
  const [category, setCategory] = useState('')
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    const expense: ExpenseData = {
      description,
      amount: parseFloat(amount),
      category,
      date,
    }

    try {
      console.log('Adding expense:', expense)
      setTimeout(() => {
        setIsLoading(false)
        onSubmit?.(expense)
        setDescription('')
        setAmount('')
        setCategory('')
        setDate(new Date().toISOString().split('T')[0])
      }, 500)
    } catch (err) {
      setIsLoading(false)
    }
  }

  return (
    <Card className="backdrop-blur-md bg-white/60 border border-white/30 shadow-md">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-6">Add New Expense</h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="description" className="text-foreground font-medium">
                Description
              </Label>
              <Input
                id="description"
                placeholder="e.g., Coffee at Starbucks"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
                className="bg-white/50 border-white/30 backdrop-blur-sm"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="amount" className="text-foreground font-medium">
                Amount (₹)
              </Label>
              <Input
                id="amount"
                type="number"
                placeholder="0.00"
                step="0.01"
                min="0"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
                className="bg-white/50 border-white/30 backdrop-blur-sm"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category" className="text-foreground font-medium">
                Category
              </Label>
              <Select value={category} onValueChange={setCategory} required>
                <SelectTrigger className="bg-white/50 border-white/30 backdrop-blur-sm">
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat.value} value={cat.value}>
                      {cat.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="date" className="text-foreground font-medium">
                Date
              </Label>
              <Input
                id="date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
                className="bg-white/50 border-white/30 backdrop-blur-sm"
              />
            </div>
          </div>

          <Button
            type="submit"
            disabled={isLoading || !description || !amount || !category}
            className="w-full bg-accent hover:bg-accent/90 text-accent-foreground font-semibold h-11 gap-2"
          >
            <Plus className="w-4 h-4" />
            {isLoading ? 'Adding...' : 'Add Expense'}
          </Button>
        </form>
      </div>
    </Card>
  )
}
