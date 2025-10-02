import * as util from "@/utils";

export class KategoriValidate {
   static async upsert(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         label: util.zod.string(),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
 
}
