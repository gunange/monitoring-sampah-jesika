import * as util from "@/utils";

export class OrderValidate {
   static async upStatus(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         status: util.zod
            .enum(["PENDING", "PREPARING", "SERVED", "PAID"])
            .default("PENDING"),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
  
}
