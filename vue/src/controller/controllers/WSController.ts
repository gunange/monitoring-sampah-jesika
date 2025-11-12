import { api } from "@/config/apiConfig";
import { defineStore } from "pinia";

export const wsStorage = defineStore("ws-store", {
   state: (): {
      websocket: WebSocket | null;
   } => ({
      websocket: null,
   }),
});

export class WSController {
   get ws() {
      const store = wsStorage();
      return store.websocket;
   }
   get connected() {
      return this.ws?.readyState === WebSocket.OPEN;
   }
   get instance() {
      return this.ws;
   }

   async connect(tokenRaw: string): Promise<WebSocket> {
      if (!tokenRaw) {
         throw new Error("Token kosong. Pastikan sudah login & ambil token.");
      }

      const token = tokenRaw.replace(/^Bearer\s+/i, "");
      const url = `${api.url_ws}?token=${token}`;

      const store = wsStorage();

      // Jika sudah ada koneksi aktif atau sedang menghubungkan, kembalikan yang ada
      if (store.websocket && (store.websocket.readyState === WebSocket.OPEN || store.websocket.readyState === WebSocket.CONNECTING)) {
         return store.websocket;
      }

      if (store.websocket && store.websocket.readyState !== WebSocket.CLOSED) {
         try {
            store.websocket.close(1000, "Reconnecting");
         } catch {}
         store.websocket = null;
      }

      return new Promise<WebSocket>((resolve, reject) => {
         const ws = new WebSocket(url);
         ws.onopen = () => {
            // Simpan ke Pinia agar bisa digunakan di mana saja
            store.websocket = ws;
            resolve(ws);
         };
         ws.onerror = (ev) => {
            reject(new Error(`WebSocket error: ${String((ev as any)?.message ?? "unknown")}`));
         };
         ws.onclose = () => {
            // Hanya clear jika ini memang instance yang tersimpan
            if (store.websocket === ws) {
               store.websocket = null;
            }
         };
      });
   }

   disconnect(code: number = 1000, reason: string = "Client disconnect") {
      const store = wsStorage();
      if (store.websocket) {
         try {
            store.websocket.close(code, reason);
         } finally {
            store.websocket = null;
         }
      }
   }

   send(data: any) {
      const ws = this.ws;
      if (!ws || ws.readyState !== WebSocket.OPEN) {
         throw new Error("WebSocket belum terhubung");
      }
      const payload = typeof data === "string" ? data : JSON.stringify(data);
      ws.send(payload);
   }

   async ensureConnected(tokenRaw: string): Promise<WebSocket> {
      if (this.connected && this.ws) return this.ws;
      return this.connect(tokenRaw);
   }
}
