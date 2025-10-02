import * as utils from "@/utils";
import { UserValidate } from "@/validators/UserValidate";
import { UsersRepo } from "@/repositories";
import { UserResponse } from "@/response/UserResponse";
export class UserController {
   static async login(c: utils.Context): Promise<any> {
      const data = await UserValidate.login(c);
      return c.json(
         {
            data: await UsersRepo.login({
               username: data.username,
               password: data.password,
               c: c,
            }),
         },
         201
      );
   }
   static async logout(c: utils.Context): Promise<any> {
      return c.json(
         {
            data: await UsersRepo.logout({
               c,
            }),
         },
         200
      );
   }
   static async profil(c: utils.Context): Promise<any> {
      return c.json(
         {
            data: UserResponse.auth(await UsersRepo.profil(c)),
         },
         200
      );
   }
   static async resetPassword(c: utils.Context): Promise<any> {
      return c.json(await UsersRepo.resetPassword(c), 200);
   }
}
