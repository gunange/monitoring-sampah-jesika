import * as utils from "@/utils";

export async function logout({ c }: { c: utils.Context }) {
   const user = c.get("user");
   const token = c.get("token");
   const auth = await utils.dbClient.personalAksesToken.findFirstOrThrow({
      where: {
         token: token,
      },
   });

   await utils.dbClient.personalAksesToken.delete({
      where: {
         id: auth.id,
      },
   });
   return {
      message: "Berhasil Logout",
      data: user,
   };
}
