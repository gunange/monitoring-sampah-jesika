import { convertTypes } from "./convert-type";
import { handleAppError } from "./heandle-app-error";
import type { Context } from "hono";

export class HeandleRequest {
   static async parse(c: Context, convertFields: string[] = []): Promise<any> {
      let body = null;
      try {
         const contentType = c.req.header("content-type") || "";

         if (contentType.includes("application/json")) {
            body = await c.req.json();
         } else if (contentType.includes("application/x-www-form-urlencoded")) {
            body = await c.req.parseBody();
         } else if (contentType.includes("multipart/form-data")) {
            body = await c.req.parseBody();
         } else {
            throw new Error("Unsupported Content-Type");
         }
         // 👇 Cek jika ada field "form" dan parse isinya
         if (typeof body.form === "string") {
            try {
               const parsed = JSON.parse(body.form);
               if (typeof parsed === "object" && parsed !== null) {
                  body = { ...parsed, ...body };
               }
            } catch (e) {
               throw new Error("Field 'form' harus berisi JSON yang valid.");
            }
         }
      } catch (err) {
         return handleAppError.jsonCatch(err);
      }

      if (
         !body ||
         (typeof body === "object" && Object.keys(body).length === 0)
      ) {
         return handleAppError.jsonCatch(new Error("Body request kosong"));
      }

      return convertFields.length > 0
         ? convertTypes(body, convertFields)
         : body;
   }
}
