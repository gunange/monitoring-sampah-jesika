import { WSController } from "@/controller/controllers/WSController";
import { alertCtrl } from "@/components/dashboard/petugas/controllers/alert";
import { infoCtrl } from "@/components/dashboard/petugas/controllers/info";

const wsController = new WSController();

class WSHandler {
  get ws() {
    return wsController.ws;
  }

  async init(token: string): Promise<void> {
    await wsController.ensureConnected(token);
    const ws = this.ws;
    if (!ws) throw new Error("WebSocket tidak tersedia setelah connect");

    ws.onmessage = (ev: MessageEvent) => {
      let payload: any = ev.data;
      if (typeof payload === "string") {
        try {
          payload = JSON.parse(payload);
        } catch {}
      }

      const path = (payload?.path ?? "").toLowerCase();
      switch (path) {
        case "info":
          infoCtrl.handleWsData(payload);
          break;
          case "alert":
          alertCtrl.handleWsData(payload);
          break;
        default:
          break;
      }
    };
  }

  close(code: number = 1000, reason: string = "Client disconnect"): void {
    const ws = this.ws;
    if (ws) {
      try {
        ws.onmessage = null;
        ws.onopen = null;
        ws.onerror = null;
        ws.onclose = null;
      } catch {}
    }
    wsController.disconnect(code, reason);
  }
}
export const wsHeandler = new WSHandler();
