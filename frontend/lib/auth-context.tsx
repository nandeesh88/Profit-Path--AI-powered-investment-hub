'use client'

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { authApi, usersApi } from '@/lib/api'

export interface User {
  id: string
  name: string
  email: string
  monthly_income: number
  risk_tolerance: 'low' | 'medium' | 'high'
  financial_goal: string
  created_at: string
}

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: {
    name: string
    email: string
    password: string
    monthly_income: number
    risk_tolerance: 'low' | 'medium' | 'high'
    financial_goal: string
  }) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
  updateUser: (data: Partial<User>) => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Restore session on mount
  useEffect(() => {
    const token = sessionStorage.getItem('authToken')
    const cached = sessionStorage.getItem('user')
    if (token && cached) {
      try {
        setUser(JSON.parse(cached))
      } catch {}
    }
    setLoading(false)
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const res = await authApi.login({ email, password })
    const { access_token, user: userData } = res.data
    sessionStorage.setItem('authToken', access_token)
    sessionStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }, [])

  const register = useCallback(async (data: Parameters<AuthContextValue['register']>[0]) => {
    const res = await authApi.register(data)
    const { access_token, user: userData } = res.data
    sessionStorage.setItem('authToken', access_token)
    sessionStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }, [])

  const logout = useCallback(() => {
    sessionStorage.removeItem('authToken')
    sessionStorage.removeItem('user')
    setUser(null)
  }, [])

  const refreshUser = useCallback(async () => {
    const res = await usersApi.me()
    sessionStorage.setItem('user', JSON.stringify(res.data))
    setUser(res.data)
  }, [])

  const updateUser = useCallback(async (data: Partial<User>) => {
    const res = await usersApi.update(data)
    sessionStorage.setItem('user', JSON.stringify(res.data))
    setUser(res.data)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser, updateUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
