import app from "@/app";
import { wsHandler } from "@/app/ws";
import { Env } from "@/app/env";


Bun.serve({
   fetch(req, server) {
      const url = new URL(req.url);

      // Tangani WebSocket secara manual
      if (
         url.pathname === "/api/ws" &&
         req.headers.get("upgrade") === "websocket"
      ) {
         const token = url.searchParams.get("token") ?? null;

         const success = server.upgrade(req, {
            data: {
               connectedAt: new Date(),
               token,
            },
         });

         // Harus kembalikan Response meskipun upgrade berhasil
         if (success) {
            return; // biarkan Bun lanjutkan proses WebSocket handshake
         }
         return new Response("WebSocket upgrade failed", { status: 400 });
      }

      // Semua request HTTP biasa
      return app.fetch(req);
   },
   websocket: wsHandler,
   port: Env.port,
});

console.log(`🚀 Server is running at http://${Env.hostname}:${Env.port}`);
