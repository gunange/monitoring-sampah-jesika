import type { WsContext } from "@/types/WsTypes";
import type { ServerWebSocket } from "bun";
export const clients = new Map<number, ServerWebSocket<WsContext>>();

export function getClientsByRole(roleIds: number[]) {
  return [...clients.entries()]
    .filter(([, client]) => roleIds.includes(client.data.user?.role_id ?? 0))
    .map(([_, client]) => client);
}
