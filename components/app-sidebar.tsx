"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"
import { useCan } from "@/components/auth/use-can"
import { NavUser } from "@/components/nav-user"
import { ThemeToggle } from "@/components/theme-toggle"
import { BRAND, brandInitials } from "@/config/brand"
import { GROUP_LABELS, MODULE_GROUPS, modulesByGroup } from "@/config/modules"

function BrandMark() {
  return (
    <div className="flex items-center gap-2 px-2 py-1.5">
      <div
        className={
          "flex size-8 items-center justify-center overflow-hidden rounded-lg " +
          // A real logo (colored in the brand color) sits on a neutral chip so
          // it stays visible; the lettermark keeps the primary fill.
          (BRAND.logo.image
            ? "border border-border bg-card p-1"
            : "bg-primary text-primary-foreground")
        }
      >
        {BRAND.logo.image ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={BRAND.logo.image} alt={BRAND.name} className="size-full object-contain" />
        ) : (
          <span className="text-xs font-semibold">{brandInitials()}</span>
        )}
      </div>
      <div className="flex flex-col leading-none">
        <span className="text-sm font-semibold">{BRAND.name}</span>
        <span className="text-xs text-muted-foreground">{BRAND.tagline}</span>
      </div>
    </div>
  )
}

export function AppSidebar({ enabledKeys }: { enabledKeys: string[] }) {
  const pathname = usePathname()
  const can = useCan()
  const enabled = new Set(enabledKeys)

  return (
    <Sidebar>
      <SidebarHeader>
        <BrandMark />
      </SidebarHeader>

      <SidebarContent>
        {MODULE_GROUPS.map((group) => {
          const items = modulesByGroup(group).filter(
            (m) => enabled.has(m.key) && (!m.capability || can(m.capability)),
          )
          if (items.length === 0) return null
          return (
            <SidebarGroup key={group}>
              <SidebarGroupLabel>{GROUP_LABELS[group]}</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {items.map((item) => (
                    <SidebarMenuItem key={item.key}>
                      <SidebarMenuButton
                        isActive={pathname === item.href || pathname.startsWith(`${item.href}/`)}
                        tooltip={item.label}
                        render={
                          <Link href={item.href}>
                            <item.icon />
                            <span>{item.label}</span>
                          </Link>
                        }
                      />
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          )
        })}
      </SidebarContent>

      <SidebarFooter>
        <ThemeToggle />
        <NavUser />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
