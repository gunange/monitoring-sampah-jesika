import * as util from "@/utils";

export class MenuValidate {
   static async upsert(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         kategoryId: util.zod.number(),
         nama: util.zod.string(),
         deskripsi: util.zod.string().optional(),
         harga: util.zod.number(),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
 
}
