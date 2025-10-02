import * as utils from "@/utils";
import { MejaValidate } from "@/validators/MejaValidate";

export class MejaCtrl {
   static async index(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.meja.findMany({
            orderBy: {
               nomor: "asc",
            },
         }),
      });
   }
   static async upsert(c: utils.Context): Promise<any> {
      const data = await MejaValidate.upsert(c);
      return c.json({
         data: await utils.dbClient.meja.upsert({
            where: {
               nomor: data.nomor,
            },
            update: {
               status: data.status,
            },
            create: data,
         }),
         message: "Data berhasil dikirim",
      });
   }

   static async destroy(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.meja.delete({
            where : {
               id : Number(c.req.param("id"))
            }
         }).catch((err)=> {
            err.meta["message"] = "Data sudah berelasi dengan orderan";
            throw err;
         }),
         message: "Data berhasil dihapus",
      });
   }
}
