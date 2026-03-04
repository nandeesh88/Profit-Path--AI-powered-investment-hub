import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { TrendingUp } from 'lucide-react'

interface InvestmentCardProps {
  name: string
  type: 'sip' | 'mutual-fund' | 'stock'
  description: string
  riskLevel: 'low' | 'medium' | 'high'
  expectedReturn: number
  minInvestment: number
  recommendedFor?: string[]
}

const typeIcons = {
  sip: '💰',
  'mutual-fund': '📈',
  stock: '📊',
}

const riskColors = {
  low: 'bg-accent/20 text-accent',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-destructive/20 text-destructive',
}

export function InvestmentCard({
  name,
  type,
  description,
  riskLevel,
  expectedReturn,
  minInvestment,
  recommendedFor = [],
}: InvestmentCardProps) {
  return (
    <Card className="backdrop-blur-md bg-white/60 border border-white/30 shadow-md hover:shadow-lg transition-all hover:border-white/50 overflow-hidden group">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{typeIcons[type]}</span>
              <h3 className="text-xl font-semibold text-foreground">{name}</h3>
            </div>
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
          <Badge variant="outline" className={riskColors[riskLevel]}>
            {riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)} Risk
          </Badge>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6 py-4 border-y border-white/20">
          <div>
            <p className="text-xs text-muted-foreground mb-1">Expected Return</p>
            <div className="flex items-center gap-1">
              <TrendingUp className="w-4 h-4 text-accent" />
              <span className="font-bold text-accent">{expectedReturn}% p.a.</span>
            </div>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Min. Investment</p>
            <p className="font-bold text-foreground">₹{minInvestment}</p>
          </div>
        </div>

        {recommendedFor.length > 0 && (
          <div className="mb-6">
            <p className="text-xs text-muted-foreground mb-2">Recommended For:</p>
            <div className="flex flex-wrap gap-2">
              {recommendedFor.map((rec) => (
                <Badge key={rec} variant="secondary" className="bg-secondary/20 text-foreground">
                  {rec}
                </Badge>
              ))}
            </div>
          </div>
        )}

        <Button className="w-full bg-accent hover:bg-accent/90 text-accent-foreground font-semibold">
          Learn More & Invest
        </Button>
      </div>
    </Card>
  )
}
