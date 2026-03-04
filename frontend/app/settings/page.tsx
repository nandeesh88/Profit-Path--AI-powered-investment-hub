'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/dashboard/sidebar'
import { ProtectedRoute } from '@/components/protected-route'
import { useAuth } from '@/lib/auth-context'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { User, IndianRupee, Shield, Target, Check } from 'lucide-react'

export default function SettingsPage() {
  const { user, updateUser } = useAuth()

  const [name, setName] = useState(user?.name || '')
  const [monthlyIncome, setMonthlyIncome] = useState(String(user?.monthly_income || 0))
  const [riskTolerance, setRiskTolerance] = useState<'low' | 'medium' | 'high'>(
    user?.risk_tolerance || 'medium'
  )
  const [financialGoal, setFinancialGoal] = useState(user?.financial_goal || '')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSaved(false)

    try {
      await updateUser({
        name,
        monthly_income: parseFloat(monthlyIncome) || 0,
        risk_tolerance: riskTolerance,
        financial_goal: financialGoal || 'General savings',
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to update profile'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 md:ml-0 p-4 md:p-8">
          <div className="max-w-2xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-foreground mb-2">Settings</h1>
              <p className="text-muted-foreground">Manage your profile and financial preferences</p>
            </div>

            {error && (
              <div className="mb-6 p-3 bg-destructive/10 text-destructive text-sm rounded-lg">
                {error}
              </div>
            )}

            {saved && (
              <div className="mb-6 p-3 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-sm rounded-lg flex items-center gap-2">
                <Check className="w-4 h-4" />
                Profile updated successfully!
              </div>
            )}

            <form onSubmit={handleSave} className="space-y-6">
              {/* Personal Info */}
              <Card className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30">
                    <User className="w-5 h-5 text-blue-600" />
                  </div>
                  <h2 className="text-lg font-semibold">Personal Information</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input
                      id="name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Your name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input value={user?.email || ''} disabled className="opacity-60" />
                    <p className="text-xs text-muted-foreground">Email cannot be changed</p>
                  </div>
                </div>
              </Card>

              {/* Income Settings */}
              <Card className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900/30">
                    <IndianRupee className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold">Monthly Income</h2>
                    <p className="text-sm text-muted-foreground">
                      Your default monthly income used for budgeting and forecasts
                    </p>
                  </div>
                </div>
                <div className="max-w-sm">
                  <div className="space-y-2">
                    <Label htmlFor="income">Monthly Income (₹)</Label>
                    <Input
                      id="income"
                      type="number"
                      min="0"
                      value={monthlyIncome}
                      onChange={(e) => setMonthlyIncome(e.target.value)}
                      placeholder="e.g. 50000"
                    />
                    <p className="text-xs text-muted-foreground">
                      Tip: Use the Income page to log salary for individual months
                    </p>
                  </div>
                </div>
              </Card>

              {/* Risk Tolerance */}
              <Card className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-lg bg-amber-100 dark:bg-amber-900/30">
                    <Shield className="w-5 h-5 text-amber-600" />
                  </div>
                  <h2 className="text-lg font-semibold">Risk Tolerance</h2>
                </div>
                <RadioGroup
                  value={riskTolerance}
                  onValueChange={(v) => setRiskTolerance(v as 'low' | 'medium' | 'high')}
                  className="space-y-3"
                >
                  <div className="flex items-center space-x-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 cursor-pointer transition-colors">
                    <RadioGroupItem value="low" id="low" />
                    <Label htmlFor="low" className="flex-1 cursor-pointer">
                      <span className="font-medium">Conservative</span>
                      <p className="text-sm text-muted-foreground">
                        Prefer low-risk, stable returns
                      </p>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 cursor-pointer transition-colors">
                    <RadioGroupItem value="medium" id="medium" />
                    <Label htmlFor="medium" className="flex-1 cursor-pointer">
                      <span className="font-medium">Balanced</span>
                      <p className="text-sm text-muted-foreground">
                        Mix of growth and stability
                      </p>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 cursor-pointer transition-colors">
                    <RadioGroupItem value="high" id="high" />
                    <Label htmlFor="high" className="flex-1 cursor-pointer">
                      <span className="font-medium">Aggressive</span>
                      <p className="text-sm text-muted-foreground">
                        Higher risk for potentially higher returns
                      </p>
                    </Label>
                  </div>
                </RadioGroup>
              </Card>

              {/* Financial Goal */}
              <Card className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/30">
                    <Target className="w-5 h-5 text-purple-600" />
                  </div>
                  <h2 className="text-lg font-semibold">Financial Goal</h2>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="goal">Primary Financial Goal</Label>
                  <Input
                    id="goal"
                    value={financialGoal}
                    onChange={(e) => setFinancialGoal(e.target.value)}
                    placeholder="e.g. Buy a House, Retirement Planning"
                  />
                </div>
              </Card>

              {/* Save Button */}
              <div className="flex justify-end">
                <Button type="submit" disabled={saving} className="min-w-[140px]">
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
