import * as util from "@/utils";
import { timeNow } from "@/utils/convert/time-zone-parse";


export class PembayaranValidate {
   static async upsert(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         method: util.zod.enum(["CASH", "CARD", "QRIS"]),
         jumlah : util.zod.number(),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));
      data.paidAt = timeNow().toJSDate();

      return data;
   }
}
