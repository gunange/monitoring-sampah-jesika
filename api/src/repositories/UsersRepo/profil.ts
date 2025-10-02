import * as utils from "@/utils";
import type { Role, User } from "@prisma/client";

export async function profil(c: utils.Context): Promise<User & { Role: Role }> {
   const user = c.get("user");

   if (!user) {
      throw new utils.HTTPException(401, {
         message: "Unauthorized",
      });
   }

   return {
      ...user,
      Role: user.Role, // Pastikan `Role` adalah bagian dari `user`
   };
}
