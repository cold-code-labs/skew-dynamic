"use client"

import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
  type ReactNode,
} from "react"
import { Dialog } from "@base-ui/react/dialog"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

// Promise-based confirm dialog. `const ok = await confirm({...})` replaces the
// native window.confirm with a branded modal. <ConfirmProvider> mounts once.
type ConfirmOptions = {
  title: string
  description?: string
  confirmText?: string
  cancelText?: string
  destructive?: boolean
}

const ConfirmContext = createContext<{
  confirm: (o: ConfirmOptions) => Promise<boolean>
} | null>(null)

export function ConfirmProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const [options, setOptions] = useState<ConfirmOptions | null>(null)
  const resolver = useRef<((v: boolean) => void) | null>(null)

  const confirm = useCallback((o: ConfirmOptions) => {
    setOptions(o)
    setOpen(true)
    return new Promise<boolean>((resolve) => {
      resolver.current = resolve
    })
  }, [])

  function settle(value: boolean) {
    setOpen(false)
    resolver.current?.(value)
    resolver.current = null
  }

  return (
    <ConfirmContext.Provider value={{ confirm }}>
      {children}
      <Dialog.Root open={open} onOpenChange={(o) => (o ? null : settle(false))}>
        <Dialog.Portal>
          <Dialog.Backdrop className="fixed inset-0 z-50 bg-black/20 transition-opacity duration-150 data-ending-style:opacity-0 data-starting-style:opacity-0" />
          <Dialog.Popup
            className={cn(
              "fixed left-1/2 top-1/2 z-50 flex w-full max-w-sm -translate-x-1/2 -translate-y-1/2 flex-col gap-3 rounded-xl border bg-popover p-5 text-sm shadow-lg transition duration-150 data-ending-style:scale-95 data-ending-style:opacity-0 data-starting-style:scale-95 data-starting-style:opacity-0",
            )}
          >
            <Dialog.Title className="text-base font-medium">
              {options?.title}
            </Dialog.Title>
            {options?.description ? (
              <Dialog.Description className="text-muted-foreground">
                {options.description}
              </Dialog.Description>
            ) : null}
            <div className="mt-2 flex justify-end gap-2">
              <Button variant="outline" size="sm" onClick={() => settle(false)}>
                {options?.cancelText ?? "Cancelar"}
              </Button>
              <Button
                variant={options?.destructive ? "destructive" : "default"}
                size="sm"
                onClick={() => settle(true)}
              >
                {options?.confirmText ?? "Confirmar"}
              </Button>
            </div>
          </Dialog.Popup>
        </Dialog.Portal>
      </Dialog.Root>
    </ConfirmContext.Provider>
  )
}

export function useConfirm() {
  const ctx = useContext(ConfirmContext)
  if (!ctx) throw new Error("useConfirm must be used within a ConfirmProvider")
  return ctx.confirm
}
