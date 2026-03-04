'use client'

import React from "react"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'

export function SignupForm() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [monthlyIncome, setMonthlyIncome] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const { register } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (!fullName || !email || !password) {
      setError('Please fill in all fields')
      return
    }

    setIsLoading(true)

    try {
      await register({
        name: fullName,
        email,
        password,
        monthly_income: monthlyIncome ? parseFloat(monthlyIncome) : 0,
        risk_tolerance: 'medium',
        financial_goal: 'General savings',
      })
      router.push('/onboarding')
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to create account'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-md backdrop-blur-md bg-white/80 border border-white/20 shadow-lg">
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Get Started</h1>
          <p className="text-muted-foreground">Create your Profit Path account</p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-destructive/10 text-destructive text-sm rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="fullName" className="text-foreground font-medium">
              Full Name
            </Label>
            <Input
              id="fullName"
              type="text"
              placeholder="John Doe"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              className="bg-white/50 border-white/30 backdrop-blur-sm"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-foreground font-medium">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="bg-white/50 border-white/30 backdrop-blur-sm"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-foreground font-medium">
              Password
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="bg-white/50 border-white/30 backdrop-blur-sm"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword" className="text-foreground font-medium">
              Confirm Password
            </Label>
            <Input
              id="confirmPassword"
              type="password"
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="bg-white/50 border-white/30 backdrop-blur-sm"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="monthlyIncome" className="text-foreground font-medium">
              Monthly Income (₹)
            </Label>
            <Input
              id="monthlyIncome"
              type="number"
              placeholder="e.g. 50000"
              min="0"
              value={monthlyIncome}
              onChange={(e) => setMonthlyIncome(e.target.value)}
              className="bg-white/50 border-white/30 backdrop-blur-sm"
            />
            <p className="text-xs text-muted-foreground">Optional — you can update this later</p>
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold h-11"
          >
            {isLoading ? 'Creating account...' : 'Create Account'}
          </Button>
        </form>

        <p className="mt-6 text-center text-muted-foreground">
          Already have an account?{' '}
          <Link href="/login" className="text-accent font-semibold hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </Card>
  )
}
