import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { ArrowRight, TrendingUp, Target, CreditCard, BarChart3 } from 'lucide-react'

export default function HomePage() {
  const features = [
    {
      icon: CreditCard,
      title: 'Expense Tracking',
      description: 'Categorize and monitor all your spending in real-time with AI-powered insights',
      href: '/login',
    },
    {
      icon: BarChart3,
      title: 'Smart Dashboards',
      description: 'Visualize your financial health with beautiful, interactive charts and analytics',
      href: '/login',
    },
    {
      icon: TrendingUp,
      title: 'Investment Hub',
      description: 'Discover personalized investment opportunities tailored to your risk profile',
      href: '/login',
    },
    {
      icon: Target,
      title: 'Goal Planning',
      description: 'Set financial goals and track progress with intelligent milestone recommendations',
      href: '/login',
    },
  ]

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Navigation */}
      <nav className="flex items-center justify-between p-6 max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-foreground">Profit Path</h1>
        <div className="flex gap-4">
          <Link href="/login">
            <Button variant="outline">Sign In</Button>
          </Link>
          <Link href="/signup">
            <Button className="bg-primary hover:bg-primary/90">Get Started</Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 md:py-32">
        <div className="absolute top-20 left-10 w-72 h-72 bg-accent/5 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-20 right-10 w-72 h-72 bg-secondary/5 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-5xl md:text-6xl font-bold text-foreground mb-6 text-balance">
              Take Control of Your Finances
            </h2>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto text-balance">
              Intelligent expense tracking, AI-powered investment recommendations, and automated savings planning in one beautiful platform
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/signup">
                <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2 group">
                  Start Free Trial <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mt-20">
            {features.map((feature) => {
              const Icon = feature.icon
              return (
                <Link key={feature.title} href={feature.href}>
                  <Card className="backdrop-blur-md bg-white/60 border border-white/30 shadow-md hover:shadow-lg hover:scale-105 transition-all p-6 h-full cursor-pointer">
                    <div className="bg-accent/20 p-3 rounded-lg w-fit mb-4">
                      <Icon className="w-6 h-6 text-accent" />
                    </div>
                    <h3 className="text-lg font-semibold text-foreground mb-2">{feature.title}</h3>
                    <p className="text-muted-foreground text-sm">
                      {feature.description}
                    </p>
                  </Card>
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-primary/5 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-4xl font-bold text-foreground mb-12 text-center">Why Choose Profit Path?</h2>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="space-y-4">
              <div className="text-4xl font-bold text-accent">92%</div>
              <h3 className="text-xl font-semibold text-foreground">Savings Increase</h3>
              <p className="text-muted-foreground">
                Users who actively track expenses save 92% more compared to manual tracking
              </p>
            </div>

            <div className="space-y-4">
              <div className="text-4xl font-bold text-accent">15%</div>
              <h3 className="text-xl font-semibold text-foreground">Average Returns</h3>
              <p className="text-muted-foreground">
                AI-recommended portfolios outperform average market returns by 15%
              </p>
            </div>

            <div className="space-y-4">
              <div className="text-4xl font-bold text-accent">10K+</div>
              <h3 className="text-xl font-semibold text-foreground">Happy Users</h3>
              <p className="text-muted-foreground">
                Join thousands of users taking control of their financial futures
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="backdrop-blur-md bg-gradient-to-r from-accent/10 to-secondary/10 border border-white/30 rounded-2xl p-12 text-center">
          <h2 className="text-4xl font-bold text-foreground mb-4">Ready to Transform Your Finances?</h2>
          <p className="text-xl text-muted-foreground mb-8">
            Join thousands of users who have taken control of their financial future
          </p>
          <Link href="/signup">
            <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2 group">
              Start Your Journey <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/20 py-8">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-muted-foreground">© 2024 Profit Path. All rights reserved.</p>
            <div className="flex gap-6">
              <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                Privacy
              </Link>
              <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                Terms
              </Link>
              <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                Contact
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </main>
  )
}
