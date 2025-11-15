import * as utils from "@/utils";
import { SaveLogsValidate } from "@/validators/SaveLogsValidate";

export class SaveLogsCtrl {
   static async index(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.saveLogs.findMany({
            orderBy: {
               id: "desc",
            },
         }),
      });
   }
   static async store(c: utils.Context): Promise<any> {
      const data = await SaveLogsValidate.store(c);
      return c.json({
         data: await utils.dbClient.saveLogs.create({ data }),
         message: "Data berhasil ditambahkan",
      });
   }
   static async destroy(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.saveLogs.delete({
            where: {
               id: Number(c.req.param("id")),
            },
         }),
         message: "Data berhasil dihapus",
      });
   }
}
