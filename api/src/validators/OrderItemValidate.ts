import * as util from "@/utils";

export class OrderItemValidate {
   static async store(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         orderId: util.zod.number().int(),
         menuItemId: util.zod.number().int(),
         quantity: util.zod.number().int().default(1),
         harga: util.zod.number().default(0),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
   static async update(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         quantity: util.zod.number().int().default(1),
         harga: util.zod.number().default(0),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
}
