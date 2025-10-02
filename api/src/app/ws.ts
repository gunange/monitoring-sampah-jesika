import type { ServerWebSocket } from "bun";
import { Env } from "./env";
import { DateTime } from "luxon";
import * as utils from "@/utils";
import { WsService } from "@/services/WsService";
import type { WsContext } from "@/types/WsTypes";
import { wsResponse } from "@/response/WsSocketResponse";

export const wsHandler = {
   open: async function (ws: ServerWebSocket<WsContext>) {
      const token = ws.data.token;
      const now = DateTime.now().setZone("Asia/Jayapura").setLocale("id");

      let user = null;
      if (token) {
         user = await utils.Token.getUserByToken(token);
         if (user) {
            ws.data.user = user;
            const socketId: number = Date.now();
            ws.data.socketId = socketId;
            WsService.clients.set(socketId, ws);
         }
      }
      if (user) {
         ws.send(
            wsResponse.connected({
               message: `👋 Hello from WebSocket user : ${user.username}`,
            })
         );
      } else {
         ws.send(
            wsResponse.connected({
               message: `👋 Hello from WebSocket user Unknown `,
            })
         );
      }
      const log = user
         ? `🔌 WebSocket client connected at ${now.toFormat(
              "cccc, dd LLLL yyyy (HH:mm:ss)"
           )} - akses by ${user.username}-[${ws.data.socketId}]`
         : `🔌 WebSocket client connected at ${now.toFormat(
              "cccc, dd LLLL yyyy (HH:mm:ss)"
           )}`;

      if (Env.access_log) {
         const path = "logs/access.log";
         const exists = await Bun.file(path).exists();

         if (exists) {
            const prev = await Bun.file(path).text();
            await Bun.write(path, prev + log + "\n");
         } else {
            await Bun.write(path, log + "\n");
         }
      }
      console.log(log);
   },
   message(ws: ServerWebSocket<WsContext>, message: string) {
      console.log("📨 Received:", message);
      ws.send(`📥 Echo: ${message}`);
   },
   close(ws: ServerWebSocket<WsContext>) {
      const socketId = ws.data.socketId;
      if (socketId) {
         const username = ws.data.user?.username ?? "Unknown";
         console.log("❌ Disconnected:", username);
         WsService.clients.delete(socketId);
      }
   },
};
