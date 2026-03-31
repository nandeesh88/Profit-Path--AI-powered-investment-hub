'use client';

import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Target, Calendar, IndianRupee, Trash2 } from 'lucide-react'

interface GoalCardProps {
  id: string
  name: string
  targetAmount: number
  currentAmount: number
  deadline: string
  priority: 'low' | 'medium' | 'high'
  description?: string
  onDelete?: (id: string) => void
}

const priorityColors = {
  low: 'bg-blue-100 text-blue-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-destructive/20 text-destructive',
}

export function GoalCard({
  id,
  name,
  targetAmount,
  currentAmount,
  deadline,
  priority,
  description,
  onDelete,
}: GoalCardProps) {
  const percentage = Math.min((currentAmount / targetAmount) * 100, 100)
  const remainingAmount = Math.max(targetAmount - currentAmount, 0)

  const deadlineDate = new Date(deadline)
  const today = new Date()
  const daysRemaining = Math.ceil(
    (deadlineDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
  )
  const isOverdue = daysRemaining < 0

  return (
    <Card className="backdrop-blur-md bg-white/60 border border-white/30 shadow-md hover:shadow-lg transition-all overflow-hidden group">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="bg-accent/20 p-3 rounded-lg">
              <Target className="w-5 h-5 text-accent" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground">{name}</h3>
              <div className="flex items-center gap-4 mt-2">
                <span
                  className={`text-xs font-semibold px-3 py-1 rounded-full ${
                    priorityColors[priority]
                  }`}
                >
                  {priority.charAt(0).toUpperCase() + priority.slice(1)} Priority
                </span>
                {description && (
                  <span className="text-xs bg-white/20 text-foreground font-medium px-3 py-1 rounded-full border border-white/40">
                    {description}
                  </span>
                )}
              </div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete?.(id)}
            className="hover:bg-destructive/20 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <Trash2 className="w-4 h-4 text-destructive" />
          </Button>
        </div>

        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-foreground">₹{currentAmount}</span>
            <span className="text-sm text-muted-foreground">₹{targetAmount}</span>
          </div>
          <Progress value={percentage} className="h-2" />
          <p className="text-xs text-muted-foreground mt-2">{percentage.toFixed(0)}% Complete</p>
        </div>

        <div className="grid grid-cols-2 gap-3 pt-4 border-t border-white/20">
          <div className="flex items-center gap-2 text-sm">
            <IndianRupee className="w-4 h-4 text-accent" />
            <div>
              <p className="text-xs text-muted-foreground">Remaining</p>
              <p className="font-semibold text-foreground">₹{remainingAmount.toFixed(2)}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Calendar className="w-4 h-4 text-accent" />
            <div>
              <p className="text-xs text-muted-foreground">Days Left</p>
              <p className={`font-semibold ${isOverdue ? 'text-destructive' : 'text-accent'}`}>
                {Math.abs(daysRemaining)}d
              </p>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}
