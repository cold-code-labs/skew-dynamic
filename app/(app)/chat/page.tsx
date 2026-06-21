import { redirect } from "next/navigation"

import { DATA_MODE } from "@/config/env"
import { requireFeature } from "@/config/features"
import { ChatView } from "@/components/chat/chat-view"
import { can } from "@/config/roles"
import { getSession } from "@/lib/auth/session"
import { listChannelsForUser, listChatUsers, listMessages } from "@/lib/chat/data"
import { realtimeProps } from "@/lib/realtime/server"

export const dynamic = "force-dynamic"

export default async function ChatPage() {
  requireFeature("chat")
  // The app layout already gates auth, but this server component can render
  // concurrently with the layout's redirect — guard the session ourselves so an
  // unauthenticated render never dereferences a null user.
  const user = await getSession()
  if (!user) redirect("/login")

  const channels = await listChannelsForUser(user)
  const activeId = channels[0]?.id ?? ""
  const [initialMessages, users, realtime] = await Promise.all([
    activeId ? listMessages(activeId) : Promise.resolve([]),
    listChatUsers(user.id),
    realtimeProps(),
  ])

  return (
    <ChatView
      currentUser={{ id: user.id, name: user.name, avatar: user.avatar }}
      channels={channels}
      activeId={activeId}
      initialMessages={initialMessages}
      users={users}
      canManage={can(user.role, "members.manage")}
      persisted={DATA_MODE !== "stub"}
      sseRelay={DATA_MODE === "pocketbase"}
      realtime={realtime}
    />
  )
}
