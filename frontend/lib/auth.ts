// Simple client-side auth for demo purposes
export const setAuthToken = (token: string) => {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('authToken', token)
  }
}

export const getAuthToken = () => {
  if (typeof window !== 'undefined') {
    return sessionStorage.getItem('authToken')
  }
  return null
}

export const clearAuthToken = () => {
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem('authToken')
  }
}

export const isAuthenticated = () => {
  return !!getAuthToken()
}
