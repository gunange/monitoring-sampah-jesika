import * as util from "@/utils";

export class SaveLogsValidate {
   static async store(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         label: util.zod.string().min(1).max(150),
         h_mean: util.zod.number(),
         h_std: util.zod.number(),
         s_mean: util.zod.number(),
         s_std: util.zod.number(),
         v_mean: util.zod.number(),
         v_std: util.zod.number(),
         laplacian_var: util.zod.number(),
         edge_ratio: util.zod.number(),
         shape_area_ratio: util.zod.number(),
         frame: util.zod.object({
            width: util.zod.number(),
            height: util.zod.number(),
         }),
         roi: util.zod.object({
            x: util.zod.number(),
            y: util.zod.number(),
            w: util.zod.number(),
            h: util.zod.number(),
         }),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
}
