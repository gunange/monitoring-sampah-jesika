import { bearerAuth } from "hono/bearer-auth";
import * as utils from "@/utils";

export async function AuthBearer(
   context: utils.Context,
   next: utils.Next,
   role_id?: number,
) {
   const auth = await bearerAuth({
      verifyToken: async (token, c) => {
         return await utils.Token.verify(token, c, role_id);
      },
      invalidTokenMessage: () => {
         throw new utils.HTTPException(401, { message: "Unauthorized" });
      },
      noAuthenticationHeaderMessage: () => {
         throw new utils.HTTPException(401, {
            message: "You Must Provide Authorization",
         });
      },
      invalidAuthenticationHeaderMessage: () => {
         throw new utils.HTTPException(401, {
            message: "Invalid Authorization",
         });
      },
   });
   return await auth(context, next);
}
