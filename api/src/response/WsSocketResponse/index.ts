export enum WsResponseType {
   CONNECTED = "connected",
   ADD = "add",
   MODIFIED = "modified",
   DELETE = "delete",
   ERROR = "error",
}

function buildWsResponse({
   type,
   path,
   message = null,
   data = null,
}: {
   type: WsResponseType;
   path?: string | null;
   message?: string | null;
   data?: any;
}) {
   return JSON.stringify({ type, path, message, data });
}

export const wsResponse = {
   connected: ({
      message = null,
      data = null,
   }: {
      message?: string | null;
      data?: any;
   }) => buildWsResponse({ type: WsResponseType.CONNECTED, message, data }),
   add: ({
      message = null,
      data = null,
      path
   }: {
      path: string;
      message?: string | null;
      data?: any;
   }) => buildWsResponse({ type: WsResponseType.ADD, path, message, data }),
   modified: ({
      message = null,
      data = null,
      path
   }: {
      path: string;
      message?: string | null;
      data?: any;
   }) => buildWsResponse({ type: WsResponseType.MODIFIED, path, message, data }),
   delete: ({
      message = null,
      data = null,
      path
   }: {
      path: string;
      message?: string | null;
      data?: any;
   }) => buildWsResponse({ type: WsResponseType.DELETE, path, message, data }),
   error: ({
      message = null,
      data = null,
   }: {
      message?: string | null;
      data?: any;
   }) => buildWsResponse({ type: WsResponseType.ERROR, message, data }),
};
