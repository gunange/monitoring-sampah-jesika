import { UserResponse } from "@/response/UserResponse";
import * as utils from "@/utils";

export async function login({
   username,
   password,
   c,
}: {
   username: string;
   password: string;
   c: utils.Context;
}) {
   const existingUser = await utils.dbClient.user.findFirst({
      where: { username: username },
      include: {
         Role: true,
      },
   });

   if (
      !existingUser ||
      !(await Bun.password.verify(password, existingUser.password, "bcrypt"))
   ) {
      throw new utils.HTTPException(401, {
         message: "Username or Password Wrong!!",
      });
   }

   return await UserResponse.login(
      existingUser,
      await utils.Token.generate(existingUser, c)
   );
}
