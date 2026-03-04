'use client'

import { ProfileSetup } from '@/components/auth/profile-setup'
import { useRouter } from 'next/navigation'
import { ProtectedRoute } from '@/components/protected-route'

export default function OnboardingPage() {
  const router = useRouter()

  const handleProfileComplete = () => {
    router.push('/dashboard')
  }

  return (
    <ProtectedRoute>
      <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 flex items-center justify-center p-4">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-accent/5 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-10 w-72 h-72 bg-secondary/5 rounded-full blur-3xl"></div>
        </div>

        <div className="relative z-10">
          <ProfileSetup onComplete={handleProfileComplete} />
        </div>
      </main>
    </ProtectedRoute>
  )
}
