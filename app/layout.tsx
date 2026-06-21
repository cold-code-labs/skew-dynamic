import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"

import { ConfirmProvider } from "@/components/ui/confirm"
import { ToastProvider } from "@/components/ui/toast"
import { TooltipProvider } from "@/components/ui/tooltip"
import { APP_DESCRIPTION, APP_NAME } from "@/config/app"
import { BRAND, brandColorVars } from "@/config/brand"

import "./globals.css"

// Applies the saved light/dark choice before first paint (no flash of wrong
// theme). The color preset comes from BRAND.theme via the data-theme attribute.
const noFlashTheme = `(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||(!t&&matchMedia('(prefers-color-scheme: dark)').matches)){document.documentElement.classList.add('dark')}}catch(e){}})()`

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] })
const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
})

export const metadata: Metadata = {
  title: APP_NAME,
  description: APP_DESCRIPTION,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="pt-BR"
      // The noFlashTheme inline script toggles the `dark` class on <html> before
      // hydration, so the server/client classNames intentionally differ here.
      // Scope the suppression to this one element (canonical no-flash-theme fix).
      suppressHydrationWarning
      data-theme={BRAND.theme}
      // An exact NEXT_PUBLIC_BRAND_COLOR (set per Vessel) overrides the preset.
      style={brandColorVars()}
      className={`${geistSans.variable} ${geistMono.variable} bg-background`}
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: noFlashTheme }} />
      </head>
      <body className="font-sans antialiased">
        <TooltipProvider delay={0}>
          <ConfirmProvider>
            <ToastProvider>{children}</ToastProvider>
          </ConfirmProvider>
        </TooltipProvider>
      </body>
    </html>
  )
}
