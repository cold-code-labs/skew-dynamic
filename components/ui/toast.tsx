"use client"

import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
  type ReactNode,
} from "react"
import { CheckCircle2, Info, X, XCircle } from "lucide-react"

import { cn } from "@/lib/utils"

// Tiny dependency-free toast system. <ToastProvider> mounts once (root layout);
// anywhere below, `useToast().toast({...})` shows a transient message.
export type ToastVariant = "default" | "success" | "destructive"

type Toast = {
  id: number
  title: string
  description?: string
  variant: ToastVariant
}

type ToastInput = {
  title: string
  description?: string
  variant?: ToastVariant
}

const ToastContext = createContext<{ toast: (t: ToastInput) => void } | null>(null)

const ICONS = {
  default: Info,
  success: CheckCircle2,
  destructive: XCircle,
} as const

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const nextId = useRef(1)

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const toast = useCallback(
    ({ title, description, variant = "default" }: ToastInput) => {
      const id = nextId.current++
      setToasts((prev) => [...prev, { id, title, description, variant }])
      setTimeout(() => dismiss(id), 4500)
    },
    [dismiss],
  )

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-full max-w-sm flex-col gap-2">
        {toasts.map((t) => {
          const Icon = ICONS[t.variant]
          return (
            <div
              key={t.id}
              className={cn(
                "pointer-events-auto flex items-start gap-2.5 rounded-lg border bg-popover p-3 text-sm shadow-lg",
                t.variant === "destructive" && "border-destructive/30",
                t.variant === "success" && "border-primary/30",
              )}
            >
              <Icon
                className={cn(
                  "mt-0.5 size-4 shrink-0",
                  t.variant === "success" && "text-primary",
                  t.variant === "destructive" && "text-destructive",
                  t.variant === "default" && "text-muted-foreground",
                )}
              />
              <div className="flex flex-1 flex-col gap-0.5">
                <span className="font-medium">{t.title}</span>
                {t.description ? (
                  <span className="text-muted-foreground">{t.description}</span>
                ) : null}
              </div>
              <button
                onClick={() => dismiss(t.id)}
                className="text-muted-foreground transition-colors hover:text-foreground"
                aria-label="Fechar"
              >
                <X className="size-4" />
              </button>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error("useToast must be used within a ToastProvider")
  return ctx
}
