import * as util from "@/utils";

export class UserValidate {
   static async login(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         username: util.zod.string().max(200),
         password: util.zod.union([
            util.zod.string().max(100),
            util.zod.number().min(3),
         ]),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
   static async resetPassword(c: util.Context): Promise<{
      password: string;
   }> {
      const validate: util.ZodType = util.zod.object({
         password: util.zod.union([
            util.zod.string().max(100),
            util.zod.number().min(3),
         ]),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
   static async registrasi(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         username: util.zod.string().max(200),
         password: util.zod.union([
            util.zod.string().max(100),
            util.zod.number().min(3),
         ]),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
   static async registrasiUsernameOnly(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         username: util.zod.string().max(200),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
}
