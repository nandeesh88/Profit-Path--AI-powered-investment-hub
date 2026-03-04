'use client'

import { useEffect, ReactNode, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const router = useRouter()
  const { user, loading } = useAuth()
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  useEffect(() => {
    if (isMounted && !loading && !user) {
      router.push('/login')
    }
  }, [isMounted, loading, user, router])

  if (!isMounted || loading) {
    return <div className="flex min-h-screen items-center justify-center bg-background" />
  }

  if (!user) {
    return <div className="flex min-h-screen items-center justify-center bg-background" />
  }

  return children
}
