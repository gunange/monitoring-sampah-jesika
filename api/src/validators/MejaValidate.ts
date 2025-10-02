import * as util from "@/utils";

export class MejaValidate {
   static async upsert(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         nomor: util.zod
            .number()
            .int()
            .refine((value) => value > 0, { message: "Nomor harus positif" }),
         status: util.zod
            .enum(["TERSEDIA", "TERISI", "DIPESAN"])
            .default("TERSEDIA"),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
}
