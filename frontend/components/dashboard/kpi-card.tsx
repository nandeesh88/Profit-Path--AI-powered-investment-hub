import { Card } from '@/components/ui/card'
import { ArrowUp, ArrowDown, Wallet, TrendingUp, IndianRupee, Target } from 'lucide-react'

interface KPICardProps {
  title: string
  value: string | number
  description?: string
  trend?: number
  icon?: 'wallet' | 'income' | 'expense' | 'savings' | 'investment'
  className?: string
}

export function KPICard({
  title,
  value,
  description,
  trend,
  icon = 'wallet',
  className = '',
}: KPICardProps) {
  const iconMap = {
    wallet: Wallet,
    income: IndianRupee,
    expense: TrendingUp,
    savings: ArrowUp,
    investment: Target,
  }

  const IconComponent = iconMap[icon]
  const isPositive = trend === undefined || trend >= 0

  return (
    <Card className={`backdrop-blur-md bg-white/60 border border-white/30 shadow-md hover:shadow-lg transition-shadow ${className}`}>
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <p className="text-muted-foreground text-sm font-medium mb-1">{title}</p>
            <div className="flex items-baseline gap-2">
              <h3 className="text-3xl font-bold text-foreground">{value}</h3>
              {trend !== undefined && (
                <div className={`flex items-center gap-1 text-sm font-semibold ${isPositive ? 'text-accent' : 'text-destructive'}`}>
                  {isPositive ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
                  {Math.abs(trend)}%
                </div>
              )}
            </div>
          </div>

          <div className="bg-accent/10 p-3 rounded-lg">
            <IconComponent className="w-6 h-6 text-accent" />
          </div>
        </div>

        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
    </Card>
  )
}
