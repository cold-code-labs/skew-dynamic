"use client"

import { useEffect, useState } from "react"
import { Moon, Sun } from "lucide-react"

import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

// Light/dark toggle. Persists to localStorage and flips the `.dark` class on
// <html>. The no-flash script in app/layout.tsx applies the saved choice before
// paint, so this only mirrors + updates it.
export function ThemeToggle() {
  const [isDark, setIsDark] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    setIsDark(document.documentElement.classList.contains("dark"))
  }, [])

  function toggle() {
    const next = !isDark
    setIsDark(next)
    document.documentElement.classList.toggle("dark", next)
    try {
      localStorage.setItem("theme", next ? "dark" : "light")
    } catch {}
  }

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton onClick={toggle} tooltip="Alternar tema">
          {mounted && isDark ? <Moon /> : <Sun />}
          <span>{mounted && isDark ? "Tema escuro" : "Tema claro"}</span>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
