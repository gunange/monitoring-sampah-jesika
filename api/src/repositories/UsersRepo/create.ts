import * as util from "@/utils";
import { Prisma, type User } from "@prisma/client";
export async function create({
   username,
   password,
   role_id,
   error_message,
}: {
   username: string;
   password: string;
   role_id: number;
   error_message?: string;
}): Promise<User> {
   const newPassword = await Bun.password.hash(`${password}`, {
      algorithm: "bcrypt",
      cost: 10,
   });
   const data = await util.dbClient.user
      .create({
         data: {
            username: username,
            password: newPassword,
            role_id: role_id,
         },
      })
      .catch((err) => {
         if (
            err instanceof Prisma.PrismaClientKnownRequestError &&
            err.code === "P2002"
         ) {
            err.meta = {
               ...(err.meta ?? {}),
               message:
                  error_message ??
                  "Username yang anda berikan tidak dapat digunakan",
            };
         }
         throw err;
      });
   data.password = password;
   return data;
}
