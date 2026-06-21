"use client"

import { LogOut } from "lucide-react"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/lib/auth/context"
import { SidebarMenu, SidebarMenuItem } from "@/components/ui/sidebar"

function initials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase()
}

// Bottom-of-sidebar profile. Intentionally NOT a dropdown/switcher: it shows the
// signed-in user and a single logout button. Account details live in the
// "Minha conta" page (Configurações); multi-tenant switching is opt-in and not
// surfaced here by default.
export function NavUser() {
  const { user, logout } = useAuth()

  return (
    <SidebarMenu>
      <SidebarMenuItem className="flex items-center gap-2 px-1 py-1.5">
        <Avatar className="size-8 rounded-lg">
          {/* Only render the image when there's a real avatar — otherwise the
              initials fallback takes over (no fake /placeholder.svg → no 404). */}
          {user.avatar ? <AvatarImage src={user.avatar} alt={user.name} /> : null}
          <AvatarFallback className="rounded-lg">{initials(user.name)}</AvatarFallback>
        </Avatar>
        <div className="grid flex-1 text-left text-sm leading-tight">
          <span className="truncate font-medium">{user.name}</span>
          <span className="truncate text-xs text-muted-foreground">{user.email}</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="size-8 shrink-0"
          onClick={logout}
          aria-label="Sair"
          title="Sair"
        >
          <LogOut className="size-4" />
        </Button>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
