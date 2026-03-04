import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = sessionStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// On 401 redirect to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      sessionStorage.removeItem('authToken')
      sessionStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: {
    name: string
    email: string
    password: string
    monthly_income: number
    risk_tolerance: 'low' | 'medium' | 'high'
    financial_goal: string
  }) => api.post('/auth/register', data),

  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
}

// ── Users ─────────────────────────────────────────────────────────────────────
export const usersApi = {
  me: () => api.get('/users/me'),
  update: (data: {
    name?: string
    monthly_income?: number
    risk_tolerance?: 'low' | 'medium' | 'high'
    financial_goal?: string
  }) => api.put('/users/me', data),
}

// ── Expenses ──────────────────────────────────────────────────────────────────
export const expensesApi = {
  list: () => api.get('/expenses'),
  summary: () => api.get('/expenses/summary'),
  create: (data: { description: string; amount: number; category: string; date: string }) =>
    api.post('/expenses', data),
  update: (id: string, data: Partial<{ description: string; amount: number; category: string; date: string }>) =>
    api.put(`/expenses/${id}`, data),
  delete: (id: string) => api.delete(`/expenses/${id}`),
}

// ── Goals ─────────────────────────────────────────────────────────────────────
export const goalsApi = {
  list: () => api.get('/goals'),
  create: (data: {
    title: string
    description?: string
    target_amount: number
    current_amount?: number
    target_date: string
    category?: string
    priority?: 'low' | 'medium' | 'high'
  }) => api.post('/goals', data),
  update: (id: string, data: Partial<{ title: string; description: string; target_amount: number; current_amount: number; target_date: string; category: string; priority: string }>) =>
    api.put(`/goals/${id}`, data),
  delete: (id: string) => api.delete(`/goals/${id}`),
}

// ── Investments ───────────────────────────────────────────────────────────────
export const investmentsApi = {
  recommend: (data: {
    monthly_income: number
    monthly_expenses: number
    savings?: number
    risk_tolerance: 'low' | 'medium' | 'high' | string
    financial_goal: string
    age?: number
    investment_horizon_years?: number
  }) => api.post('/investments/recommend', data),
  history: () => api.get('/investments/history'),
}
// ── Income ────────────────────────────────────────────────────────────────
export const incomeApi = {
  list: () => api.get('/income'),
  summary: () => api.get('/income/summary'),
  create: (data: { amount: number; source: string; description?: string; month: string }) =>
    api.post('/income', data),
  update: (id: string, data: Partial<{ amount: number; source: string; description: string; month: string }>) =>
    api.put(`/income/${id}`, data),
  delete: (id: string) => api.delete(`/income/${id}`),
}