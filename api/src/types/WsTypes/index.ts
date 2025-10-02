import type { User } from "@prisma/client";

export interface WsContext {
   socketId?: number;
   connectedAt: Date;
   token: string | null;
   user?: User;
}
