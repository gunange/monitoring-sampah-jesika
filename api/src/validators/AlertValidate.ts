import * as util from "@/utils";

export class AlertValidate {
   static async send(c: util.Context) {
      const validate: util.ZodType = util.zod.object({
         pred: util.zod.string(),
         result: util.zod.object({
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
            features: util.zod.object({
               h_mean: util.zod.number(),
               h_std: util.zod.number(),
               s_mean: util.zod.number(),
               s_std: util.zod.number(),
               v_mean: util.zod.number(),
               v_std: util.zod.number(),
               laplacian_var: util.zod.number(),
               edge_ratio: util.zod.number(),
               shape_area_ratio: util.zod.number(),
            }),
         }),
      });

      let data = await validate.parse(await util.HeandleRequest.parse(c));

      return data;
   }
   
}
