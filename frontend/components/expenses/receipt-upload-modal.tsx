'use client'

import React, { useState, useRef, useCallback } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Upload,
  FileText,
  ImageIcon,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  ArrowRight,
  ArrowLeft,
  X,
  FileUp,
  Sparkles,
} from 'lucide-react'
import { expensesApi } from '@/lib/api'

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface ExtractedTransaction {
  amount: number
  transaction_date: string
  merchant_name: string
  transaction_type: 'debit'
  bank_reference_id?: string | null
  is_duplicate: boolean
}

interface ExtractionResponse {
  upload_id: string
  filename: string
  transactions: ExtractedTransaction[]
}

interface EditableTransaction extends ExtractedTransaction {
  selected: boolean
  description: string
  category: string
}

const categories = [
  { value: 'Food & Dining', label: 'Food & Dining' },
  { value: 'Housing', label: 'Housing / Rent' },
  { value: 'Entertainment', label: 'Entertainment' },
  { value: 'Transportation', label: 'Transportation' },
  { value: 'Utilities', label: 'Utilities' },
  { value: 'Shopping', label: 'Shopping' },
  { value: 'Healthcare', label: 'Healthcare' },
  { value: 'Education', label: 'Education' },
  { value: 'Travel', label: 'Travel' },
  { value: 'Other', label: 'Other' },
]

const ACCEPTED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
const ACCEPTED_EXTENSIONS = '.jpg,.jpeg,.png,.pdf'
const MAX_SIZE = 10 * 1024 * 1024 // 10 MB

type Step = 'upload' | 'review' | 'confirm'

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

interface ReceiptUploadModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onExpensesAdded: () => void
}

export function ReceiptUploadModal({
  open,
  onOpenChange,
  onExpensesAdded,
}: ReceiptUploadModalProps) {
  /* ── state ──────────────────────────────────────────────────────── */
  const [step, setStep] = useState<Step>('upload')
  const [file, setFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const [extraction, setExtraction] = useState<ExtractionResponse | null>(null)
  const [editableTransactions, setEditableTransactions] = useState<EditableTransaction[]>([])

  const [saving, setSaving] = useState(false)
  const [savedCount, setSavedCount] = useState(0)
  const [saveErrors, setSaveErrors] = useState<string[]>([])

  const fileInputRef = useRef<HTMLInputElement>(null)

  /* ── helpers ────────────────────────────────────────────────────── */

  const reset = useCallback(() => {
    setStep('upload')
    setFile(null)
    setDragActive(false)
    setUploading(false)
    setUploadProgress(0)
    setError(null)
    setExtraction(null)
    setEditableTransactions([])
    setSaving(false)
    setSavedCount(0)
    setSaveErrors([])
  }, [])

  const handleClose = useCallback(() => {
    reset()
    onOpenChange(false)
  }, [reset, onOpenChange])

  const validateFile = (f: File) => {
    if (!ACCEPTED_TYPES.includes(f.type) && !f.name.match(/\.(jpg|jpeg|png|pdf)$/i)) {
      return 'Unsupported file type. Please upload a JPG, PNG, or PDF file.'
    }
    if (f.size > MAX_SIZE) {
      return 'File size exceeds 10 MB limit.'
    }
    return null
  }

  const isImageFile = (f: File) => f.type.startsWith('image/')

  /* ── drag & drop ────────────────────────────────────────────────── */

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true)
    else if (e.type === 'dragleave') setDragActive(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    const droppedFile = e.dataTransfer.files?.[0]
    if (droppedFile) {
      const err = validateFile(droppedFile)
      if (err) { setError(err); return }
      setError(null)
      setFile(droppedFile)
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0]
    if (selected) {
      const err = validateFile(selected)
      if (err) { setError(err); return }
      setError(null)
      setFile(selected)
    }
  }

  /* ── upload & extract ───────────────────────────────────────────── */

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError(null)
    setUploadProgress(15)

    // Simulate gradual progress while waiting for extraction
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => Math.min(prev + 8, 85))
    }, 400)

    try {
      const res = await expensesApi.uploadAndExtract(file)
      clearInterval(progressInterval)
      setUploadProgress(100)

      const data = res.data as ExtractionResponse
      setExtraction(data)

      // Build editable list
      const editable: EditableTransaction[] = data.transactions.map((tx) => ({
        ...tx,
        selected: !tx.is_duplicate,
        description: tx.merchant_name,
        category: 'Other',
      }))
      setEditableTransactions(editable)

      // Brief pause to show 100% progress
      await new Promise((r) => setTimeout(r, 400))
      setStep('review')
    } catch (err: any) {
      clearInterval(progressInterval)
      const detail = err?.response?.data?.detail || 'Upload failed. Please try again.'
      setError(detail)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  /* ── selection helpers ──────────────────────────────────────────── */

  const toggleSelect = (idx: number) => {
    setEditableTransactions((prev) =>
      prev.map((tx, i) => (i === idx ? { ...tx, selected: !tx.selected } : tx))
    )
  }

  const selectAll = () =>
    setEditableTransactions((prev) => prev.map((tx) => ({ ...tx, selected: true })))

  const deselectAll = () =>
    setEditableTransactions((prev) => prev.map((tx) => ({ ...tx, selected: false })))

  const selectedCount = editableTransactions.filter((t) => t.selected).length

  /* ── edit helpers ───────────────────────────────────────────────── */

  const updateField = (idx: number, field: keyof EditableTransaction, value: string | number) => {
    setEditableTransactions((prev) =>
      prev.map((tx, i) => (i === idx ? { ...tx, [field]: value } : tx))
    )
  }

  /* ── save ────────────────────────────────────────────────────────── */

  const handleSaveAll = async () => {
    if (!extraction) return
    const toSave = editableTransactions.filter((tx) => tx.selected)
    if (toSave.length === 0) return

    setSaving(true)
    setSavedCount(0)
    setSaveErrors([])

    let successCount = 0
    const errors: string[] = []

    for (const tx of toSave) {
      try {
        await expensesApi.createFromExtraction({
          upload_id: extraction.upload_id,
          description: tx.description,
          amount: tx.amount,
          category: tx.category,
          date: tx.transaction_date,
          transaction_type: 'debit',
          bank_reference_id: tx.bank_reference_id || undefined,
        })
        successCount++
        setSavedCount(successCount)
      } catch (err: any) {
        const detail = err?.response?.data?.detail || 'Failed to save expense'
        errors.push(`${tx.description}: ${detail}`)
      }
    }

    setSaveErrors(errors)

    if (successCount > 0) {
      onExpensesAdded()
    }

    // Show confirm step
    setStep('confirm')
    setSaving(false)
  }

  /* ── render ─────────────────────────────────────────────────────── */

  return (
    <Dialog open={open} onOpenChange={(v) => (v ? onOpenChange(true) : handleClose())}>
      <DialogContent
        className="sm:max-w-2xl max-h-[90vh] overflow-y-auto backdrop-blur-xl bg-white/80 dark:bg-zinc-900/80 border-white/30"
        showCloseButton={!saving}
      >
        {/* ── Step indicator ──────────────────────────────────────── */}
        <div className="flex items-center justify-center gap-2 mb-2">
          {(['upload', 'review', 'confirm'] as Step[]).map((s, i) => (
            <React.Fragment key={s}>
              <div
                className={`flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold transition-all duration-300 ${
                  s === step
                    ? 'bg-accent text-accent-foreground scale-110 shadow-md'
                    : i < ['upload', 'review', 'confirm'].indexOf(step)
                    ? 'bg-accent/30 text-accent'
                    : 'bg-muted text-muted-foreground'
                }`}
              >
                {i + 1}
              </div>
              {i < 2 && (
                <div
                  className={`h-0.5 w-8 rounded transition-colors duration-300 ${
                    i < ['upload', 'review', 'confirm'].indexOf(step)
                      ? 'bg-accent/50'
                      : 'bg-muted'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* ── STEP 1: Upload ──────────────────────────────────────── */}
        {step === 'upload' && (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-xl">
                <FileUp className="w-5 h-5 text-accent" />
                Upload Bank Statement or Receipt
              </DialogTitle>
              <DialogDescription>
                Upload an image or PDF of your bank debit details, transaction receipt, or bank statement.
                We&apos;ll automatically extract the transaction details using OCR.
              </DialogDescription>
            </DialogHeader>

            {/* Drop zone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`relative cursor-pointer rounded-xl border-2 border-dashed transition-all duration-300 p-8 text-center ${
                dragActive
                  ? 'border-accent bg-accent/10 scale-[1.01] shadow-lg'
                  : file
                  ? 'border-accent/50 bg-accent/5'
                  : 'border-muted-foreground/30 hover:border-accent/50 hover:bg-accent/5'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept={ACCEPTED_EXTENSIONS}
                onChange={handleFileSelect}
                className="hidden"
                id="receipt-file-input"
              />

              {file ? (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-14 h-14 rounded-xl bg-accent/15 flex items-center justify-center">
                    {isImageFile(file) ? (
                      <ImageIcon className="w-7 h-7 text-accent" />
                    ) : (
                      <FileText className="w-7 h-7 text-accent" />
                    )}
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">{file.name}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {(file.size / 1024).toFixed(0)} KB •{' '}
                      {file.type.includes('pdf') ? 'PDF Document' : 'Image File'}
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      setFile(null)
                      setError(null)
                    }}
                    className="text-muted-foreground hover:text-destructive"
                  >
                    <X className="w-4 h-4 mr-1" /> Remove
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent/20 to-accent/5 flex items-center justify-center">
                    <Upload className="w-8 h-8 text-accent" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">
                      Drag & drop your file here
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                      or click to browse
                    </p>
                  </div>
                  <div className="flex gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">JPG</Badge>
                    <Badge variant="outline" className="text-xs">PNG</Badge>
                    <Badge variant="outline" className="text-xs">PDF</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">Max file size: 10 MB</p>
                </div>
              )}
            </div>

            {/* Progress bar */}
            {uploading && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="w-4 h-4 animate-spin text-accent" />
                  <span>Extracting transaction details…</span>
                </div>
                <Progress value={uploadProgress} className="h-2" />
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-sm text-destructive">
                <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <DialogFooter>
              <Button variant="ghost" onClick={handleClose} disabled={uploading}>
                Cancel
              </Button>
              <Button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="bg-accent hover:bg-accent/90 text-accent-foreground gap-2"
              >
                {uploading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )}
                {uploading ? 'Extracting…' : 'Extract Transactions'}
              </Button>
            </DialogFooter>
          </>
        )}

        {/* ── STEP 2: Review ──────────────────────────────────────── */}
        {step === 'review' && (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-xl">
                <CheckCircle2 className="w-5 h-5 text-accent" />
                Review Extracted Transactions
              </DialogTitle>
              <DialogDescription>
                We found {editableTransactions.length} transaction{editableTransactions.length !== 1 ? 's' : ''} in{' '}
                <span className="font-medium text-foreground">{extraction?.filename}</span>.
                Select which ones to add.
              </DialogDescription>
            </DialogHeader>

            {/* Bulk select controls */}
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                <span className="font-semibold text-foreground">{selectedCount}</span> of{' '}
                {editableTransactions.length} selected
              </p>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={selectAll} className="text-xs">
                  Select All
                </Button>
                <Button variant="ghost" size="sm" onClick={deselectAll} className="text-xs">
                  Deselect All
                </Button>
              </div>
            </div>

            {/* Transaction cards */}
            <div className="space-y-3 max-h-[45vh] overflow-y-auto pr-1">
              {editableTransactions.map((tx, idx) => (
                <div
                  key={idx}
                  className={`rounded-xl border p-4 transition-all duration-200 ${
                    tx.selected
                      ? 'border-accent/40 bg-accent/5 shadow-sm'
                      : 'border-muted/50 bg-muted/10 opacity-60'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <Checkbox
                      id={`tx-select-${idx}`}
                      checked={tx.selected}
                      onCheckedChange={() => toggleSelect(idx)}
                      className="mt-1"
                    />
                    <div className="flex-1 min-w-0">
                      {/* Header row */}
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2 min-w-0">
                          <label
                            htmlFor={`tx-select-${idx}`}
                            className="font-semibold text-foreground truncate cursor-pointer"
                          >
                            {tx.merchant_name}
                          </label>
                          {tx.is_duplicate && (
                            <Badge
                              variant="destructive"
                              className="text-[10px] shrink-0 gap-1"
                            >
                              <AlertTriangle className="w-3 h-3" />
                              Possible duplicate
                            </Badge>
                          )}
                        </div>
                        <span className="font-bold text-lg text-foreground whitespace-nowrap">
                          ₹{tx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </span>
                      </div>

                      {/* Details row */}
                      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                        <span>📅 {new Date(tx.transaction_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                        <span>💳 Debit</span>
                        {tx.bank_reference_id && (
                          <span>🔗 Ref: {tx.bank_reference_id}</span>
                        )}
                      </div>

                      {/* Editable fields (when selected) */}
                      {tx.selected && (
                        <div className="grid grid-cols-2 gap-3 mt-3 pt-3 border-t border-muted/30">
                          <div className="col-span-2 sm:col-span-1 space-y-1">
                            <Label className="text-xs text-muted-foreground">Description</Label>
                            <Input
                              value={tx.description}
                              onChange={(e) => updateField(idx, 'description', e.target.value)}
                              className="h-8 text-sm bg-white/50 dark:bg-zinc-800/50"
                              placeholder="Transaction description"
                            />
                          </div>
                          <div className="col-span-2 sm:col-span-1 space-y-1">
                            <Label className="text-xs text-muted-foreground">Category</Label>
                            <Select
                              value={tx.category}
                              onValueChange={(val) => updateField(idx, 'category', val)}
                            >
                              <SelectTrigger className="h-8 text-sm bg-white/50 dark:bg-zinc-800/50">
                                <SelectValue placeholder="Category" />
                              </SelectTrigger>
                              <SelectContent>
                                {categories.map((c) => (
                                  <SelectItem key={c.value} value={c.value}>
                                    {c.label}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-1">
                            <Label className="text-xs text-muted-foreground">Amount (₹)</Label>
                            <Input
                              type="number"
                              step="0.01"
                              min="0"
                              value={tx.amount}
                              onChange={(e) =>
                                updateField(idx, 'amount', parseFloat(e.target.value) || 0)
                              }
                              className="h-8 text-sm bg-white/50 dark:bg-zinc-800/50"
                            />
                          </div>
                          <div className="space-y-1">
                            <Label className="text-xs text-muted-foreground">Date</Label>
                            <Input
                              type="date"
                              value={tx.transaction_date}
                              onChange={(e) =>
                                updateField(idx, 'transaction_date', e.target.value)
                              }
                              className="h-8 text-sm bg-white/50 dark:bg-zinc-800/50"
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <DialogFooter className="gap-2">
              <Button
                variant="ghost"
                onClick={() => { reset(); setStep('upload') }}
                className="gap-1"
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </Button>
              <Button
                onClick={handleSaveAll}
                disabled={selectedCount === 0 || saving}
                className="bg-accent hover:bg-accent/90 text-accent-foreground gap-2"
              >
                {saving ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <ArrowRight className="w-4 h-4" />
                )}
                {saving
                  ? `Saving (${savedCount}/${selectedCount})…`
                  : `Add ${selectedCount} Expense${selectedCount !== 1 ? 's' : ''}`}
              </Button>
            </DialogFooter>
          </>
        )}

        {/* ── STEP 3: Confirmation ────────────────────────────────── */}
        {step === 'confirm' && (
          <>
            <div className="flex flex-col items-center text-center py-4">
              <div className="w-16 h-16 rounded-full bg-accent/15 flex items-center justify-center mb-4">
                <CheckCircle2 className="w-9 h-9 text-accent" />
              </div>
              <DialogTitle className="text-xl mb-2">
                {savedCount > 0 ? 'Expenses Added!' : 'No Expenses Added'}
              </DialogTitle>
              <DialogDescription className="max-w-sm">
                {savedCount > 0 && (
                  <span>
                    Successfully added <strong>{savedCount}</strong> expense
                    {savedCount !== 1 ? 's' : ''} from your uploaded document.
                  </span>
                )}
              </DialogDescription>

              {/* Errors */}
              {saveErrors.length > 0 && (
                <div className="mt-4 w-full text-left space-y-2">
                  <p className="text-sm font-medium text-destructive">
                    {saveErrors.length} transaction{saveErrors.length !== 1 ? 's' : ''} could not be saved:
                  </p>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {saveErrors.map((err, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-2 text-xs text-destructive bg-destructive/5 rounded-md p-2"
                      >
                        <AlertTriangle className="w-3 h-3 mt-0.5 shrink-0" />
                        {err}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <DialogFooter>
              <Button
                onClick={handleClose}
                className="w-full bg-accent hover:bg-accent/90 text-accent-foreground"
              >
                Done
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
