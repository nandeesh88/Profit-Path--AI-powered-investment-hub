'use client'

import React from "react"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { useAuth } from '@/lib/auth-context'

interface ProfileSetupProps {
  onComplete?: () => void
}

export function ProfileSetup({ onComplete }: ProfileSetupProps) {
  const [age, setAge] = useState('')
  const [monthlyIncome, setMonthlyIncome] = useState('')
  const [riskTolerance, setRiskTolerance] = useState<'low' | 'medium' | 'high'>('medium')
  const [goals, setGoals] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const { updateUser } = useAuth()

  const financialGoalOptions = [
    { id: 'house', label: 'Buy a House' },
    { id: 'retirement', label: 'Retirement Planning' },
    { id: 'education', label: 'Education Fund' },
    { id: 'emergency', label: 'Emergency Fund' },
    { id: 'investment', label: 'Investment Growth' },
    { id: 'travel', label: 'Travel Fund' },
  ]

  const toggleGoal = (goalId: string) => {
    setGoals((prev) =>
      prev.includes(goalId) ? prev.filter((g) => g !== goalId) : [...prev, goalId]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const goalLabels = goals
        .map((id) => financialGoalOptions.find((o) => o.id === id)?.label)
        .filter(Boolean)
        .join(', ')

      await updateUser({
        monthly_income: parseFloat(monthlyIncome),
        risk_tolerance: riskTolerance,
        financial_goal: goalLabels || 'General savings',
      })
      onComplete?.()
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to save profile'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-2xl">
      <Card className="backdrop-blur-md bg-white/80 border border-white/20 shadow-lg">
        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">Setup Your Profile</h1>
            <p className="text-muted-foreground">
              Help us understand your financial profile to provide personalized recommendations
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-3 bg-destructive/10 text-destructive text-sm rounded-lg">
                {error}
              </div>
            )}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="age" className="text-foreground font-medium">
                  Age
                </Label>
                <Input
                  id="age"
                  type="number"
                  min="18"
                  max="100"
                  placeholder="25"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  required
                  className="bg-white/50 border-white/30 backdrop-blur-sm"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="income" className="text-foreground font-medium">
                  Monthly Income (₹)
                </Label>
                <Input
                  id="income"
                  type="number"
                  placeholder="5000"
                  value={monthlyIncome}
                  onChange={(e) => setMonthlyIncome(e.target.value)}
                  required
                  className="bg-white/50 border-white/30 backdrop-blur-sm"
                />
              </div>
            </div>

            <div className="space-y-4">
              <Label className="text-foreground font-medium">Risk Tolerance</Label>
              <RadioGroup value={riskTolerance} onValueChange={(v) => setRiskTolerance(v as any)}>
                <div className="flex items-center space-x-2 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 cursor-pointer transition-colors">
                  <RadioGroupItem value="low" id="low" />
                  <Label htmlFor="low" className="cursor-pointer flex-1">
                    <div className="font-medium">Low Risk</div>
                    <div className="text-sm text-muted-foreground">Conservative, stable investments</div>
                  </Label>
                </div>

                <div className="flex items-center space-x-2 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 cursor-pointer transition-colors">
                  <RadioGroupItem value="medium" id="medium" />
                  <Label htmlFor="medium" className="cursor-pointer flex-1">
                    <div className="font-medium">Medium Risk</div>
                    <div className="text-sm text-muted-foreground">Balanced growth and stability</div>
                  </Label>
                </div>

                <div className="flex items-center space-x-2 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 cursor-pointer transition-colors">
                  <RadioGroupItem value="high" id="high" />
                  <Label htmlFor="high" className="cursor-pointer flex-1">
                    <div className="font-medium">High Risk</div>
                    <div className="text-sm text-muted-foreground">Aggressive growth potential</div>
                  </Label>
                </div>
              </RadioGroup>
            </div>

            <div className="space-y-4">
              <Label className="text-foreground font-medium">Financial Goals (Select all that apply)</Label>
              <div className="grid sm:grid-cols-2 gap-3">
                {financialGoalOptions.map((option) => (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => toggleGoal(option.id)}
                    className={`p-3 rounded-lg border-2 transition-all text-left ${
                      goals.includes(option.id)
                        ? 'border-accent bg-accent/10'
                        : 'border-border bg-white/50 hover:bg-white/70'
                    }`}
                  >
                    <div className="font-medium text-foreground">{option.label}</div>
                  </button>
                ))}
              </div>
            </div>

            <Button
              type="submit"
              disabled={isLoading || !age || !monthlyIncome || goals.length === 0}
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold h-11"
            >
              {isLoading ? 'Setting up...' : 'Complete Setup'}
            </Button>
          </form>
        </div>
      </Card>
    </div>
  )
}
