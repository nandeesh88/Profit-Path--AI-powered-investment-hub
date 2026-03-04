import { Card } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Lightbulb, ArrowRight } from 'lucide-react'

interface RecommendationProps {
  title: string
  description: string
  reason: string
  savingsNeeded: number
  potentialGain: number
  timeframe: string
}

export function InvestmentRecommendation({
  title,
  description,
  reason,
  savingsNeeded,
  potentialGain,
  timeframe,
}: RecommendationProps) {
  return (
    <Card className="backdrop-blur-md bg-gradient-to-br from-accent/10 to-accent/5 border border-accent/30 shadow-md">
      <div className="p-6">
        <div className="flex items-start gap-4 mb-4">
          <div className="bg-accent/20 p-3 rounded-lg">
            <Lightbulb className="w-6 h-6 text-accent" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-foreground mb-1">{title}</h3>
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
        </div>

        <Alert className="mb-6 bg-white/50 border border-accent/30">
          <AlertDescription className="text-foreground text-sm">
            <strong>Why this recommendation:</strong> {reason}
          </AlertDescription>
        </Alert>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 rounded-lg bg-white/40">
            <p className="text-xs text-muted-foreground mb-1">Required Savings</p>
            <p className="text-2xl font-bold text-foreground">₹{savingsNeeded}</p>
          </div>
          <div className="text-center p-4 rounded-lg bg-accent/10">
            <p className="text-xs text-muted-foreground mb-1">Potential Gain</p>
            <p className="text-2xl font-bold text-accent">₹{potentialGain}</p>
          </div>
          <div className="text-center p-4 rounded-lg bg-white/40">
            <p className="text-xs text-muted-foreground mb-1">Timeframe</p>
            <p className="text-lg font-bold text-foreground">{timeframe}</p>
          </div>
        </div>

        <Button className="w-full bg-accent hover:bg-accent/90 text-accent-foreground font-semibold gap-2 group">
          Start Investing
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </Button>
      </div>
    </Card>
  )
}
