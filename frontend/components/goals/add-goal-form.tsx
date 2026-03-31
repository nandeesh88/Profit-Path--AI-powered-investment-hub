'use client'

import React from "react"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Plus } from 'lucide-react'

interface AddGoalFormProps {
  onSubmit?: (goal: GoalData) => void | Promise<void>
}

export interface GoalData {
  name: string
  targetAmount: number
  currentAmount: number
  deadline: string
  priority: 'low' | 'medium' | 'high'
  description?: string
}

export function AddGoalForm({ onSubmit }: AddGoalFormProps) {
  const [name, setName] = useState('')
  const [targetAmount, setTargetAmount] = useState('')
  const [currentAmount, setCurrentAmount] = useState('')
  const [deadline, setDeadline] = useState('')
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium')
  const [isLoading, setIsLoading] = useState(false)

  // Dynamic Sub-fields Tracking
  const [houseType, setHouseType] = useState('1BHK')
  const [carBrand, setCarBrand] = useState('')
  const [carModel, setCarModel] = useState('')
  const [courseName, setCourseName] = useState('')

  const isHouseGoal = /(house|home|flat|plot|villa|apartment|bhk)/i.test(name)
  const isVehicleGoal = /(car|bike|vehicle|motorcycle|scooter)/i.test(name)
  const isEduGoal = /(college|degree|education|study|university)/i.test(name)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    let description = ''
    if (isHouseGoal) description = `Property Type: ${houseType}`
    else if (isVehicleGoal && (carBrand || carModel)) description = `Vehicle: ${carBrand} ${carModel}`.trim()
    else if (isEduGoal && courseName) description = `Course: ${courseName}`

    const goal: GoalData = {
      name,
      targetAmount: parseFloat(targetAmount),
      currentAmount: currentAmount ? parseFloat(currentAmount) : 0,
      deadline,
      priority,
      description,
    }

    try {
      await onSubmit?.(goal)
      setName('')
      setTargetAmount('')
      setCurrentAmount('')
      setDeadline('')
      setPriority('medium')
      setHouseType('1BHK')
      setCarBrand('')
      setCarModel('')
      setCourseName('')
    } catch (err) {
      console.error('Failed to create goal:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="backdrop-blur-md bg-white/60 border border-white/30 shadow-md">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-6">Create New Goal</h3>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="goalName" className="text-foreground font-medium">
              Goal Name
            </Label>
            <Input
              id="goalName"
              placeholder="e.g., Buy a House"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="bg-white/50 border-white/30 backdrop-blur-sm"
            />
          </div>

          {isHouseGoal && (
            <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
              <Label htmlFor="houseType" className="text-foreground font-medium text-sm">
                Property Type
              </Label>
              <Select value={houseType} onValueChange={setHouseType}>
                <SelectTrigger className="bg-white/50 border-white/30 backdrop-blur-sm h-11">
                  <SelectValue placeholder="Select property type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1RK">1RK</SelectItem>
                  <SelectItem value="1BHK">1BHK</SelectItem>
                  <SelectItem value="2BHK">2BHK</SelectItem>
                  <SelectItem value="3BHK">3BHK</SelectItem>
                  <SelectItem value="4BHK+">4BHK+</SelectItem>
                  <SelectItem value="Villa">Villa / Independent House</SelectItem>
                  <SelectItem value="Plot">Plot / Land</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {isVehicleGoal && (
            <div className="grid md:grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-2 duration-300">
              <div className="space-y-2">
                <Label htmlFor="carBrand" className="text-foreground font-medium text-sm">
                  Vehicle Brand / Company
                </Label>
                <Input
                  id="carBrand"
                  placeholder="e.g., Tata, Honda"
                  value={carBrand}
                  onChange={(e) => setCarBrand(e.target.value)}
                  className="bg-white/50 border-white/30 backdrop-blur-sm"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="carModel" className="text-foreground font-medium text-sm">
                  Vehicle Model
                </Label>
                <Input
                  id="carModel"
                  placeholder="e.g., Nexon, City"
                  value={carModel}
                  onChange={(e) => setCarModel(e.target.value)}
                  className="bg-white/50 border-white/30 backdrop-blur-sm"
                />
              </div>
            </div>
          )}

          {isEduGoal && (
            <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
              <Label htmlFor="courseName" className="text-foreground font-medium text-sm">
                Course / Program Name
              </Label>
              <Input
                id="courseName"
                placeholder="e.g., MBA, B.Tech, Certification"
                value={courseName}
                onChange={(e) => setCourseName(e.target.value)}
                className="bg-white/50 border-white/30 backdrop-blur-sm"
              />
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="target" className="text-foreground font-medium">
                Target Amount (₹)
              </Label>
              <Input
                id="target"
                type="number"
                placeholder="50000"
                step="100"
                min="0"
                value={targetAmount}
                onChange={(e) => setTargetAmount(e.target.value)}
                required
                className="bg-white/50 border-white/30 backdrop-blur-sm"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="current" className="text-foreground font-medium">
                Current Savings (₹)
              </Label>
              <Input
                id="current"
                type="number"
                placeholder="0"
                step="100"
                min="0"
                value={currentAmount}
                onChange={(e) => setCurrentAmount(e.target.value)}
                className="bg-white/50 border-white/30 backdrop-blur-sm"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="deadline" className="text-foreground font-medium">
              Target Date
            </Label>
            <Input
              id="deadline"
              type="date"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              required
              className="bg-white/50 border-white/30 backdrop-blur-sm"
            />
          </div>

          <div className="space-y-3">
            <Label className="text-foreground font-medium">Priority Level</Label>
            <RadioGroup value={priority} onValueChange={(v) => setPriority(v as any)}>
              <div className="flex items-center space-x-2 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 cursor-pointer transition-colors">
                <RadioGroupItem value="low" id="low" />
                <Label htmlFor="low" className="cursor-pointer flex-1">
                  <div className="font-medium">Low</div>
                  <div className="text-sm text-muted-foreground">Nice to have, flexible timeline</div>
                </Label>
              </div>

              <div className="flex items-center space-x-2 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 cursor-pointer transition-colors">
                <RadioGroupItem value="medium" id="medium" />
                <Label htmlFor="medium" className="cursor-pointer flex-1">
                  <div className="font-medium">Medium</div>
                  <div className="text-sm text-muted-foreground">Important, planning needed</div>
                </Label>
              </div>

              <div className="flex items-center space-x-2 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 cursor-pointer transition-colors">
                <RadioGroupItem value="high" id="high" />
                <Label htmlFor="high" className="cursor-pointer flex-1">
                  <div className="font-medium">High</div>
                  <div className="text-sm text-muted-foreground">Critical, immediate attention</div>
                </Label>
              </div>
            </RadioGroup>
          </div>

          <Button
            type="submit"
            disabled={isLoading || !name || !targetAmount || !deadline}
            className="w-full bg-accent hover:bg-accent/90 text-accent-foreground font-semibold h-11 gap-2"
          >
            <Plus className="w-4 h-4" />
            {isLoading ? 'Creating...' : 'Create Goal'}
          </Button>
        </form>
      </div>
    </Card>
  )
}
