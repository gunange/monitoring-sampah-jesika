import * as utils from "@/utils";
import { UserValidate } from "@/validators/UserValidate";

export async function resetPassword(
   c: utils.Context,
   id?: number
): Promise<{
   message: string;
   data: any;
}> {
   const user = c.get("user");
   const data = await UserValidate.resetPassword(c);

   const newPassword = await Bun.password.hash(`${data.password}`, {
      algorithm: "bcrypt",
      cost: 10,
   });

   const db = await utils.dbClient.user.update({
      where: {
         id: id ?? Number(user.id),
      },
      data: {
         password: newPassword,
      },
   });

   return {
      data: {
         username: db.username,
      },
      message: `Akun ${db.username} Berhasil Ganti Password dengan ${data.password}`,
   };
}
