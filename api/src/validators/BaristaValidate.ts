import * as util from "@/utils";

export class BaristaValidate {
   static async upsert(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         nama: util.zod.string(),
         noHp: util.zod.string(),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
 
}
