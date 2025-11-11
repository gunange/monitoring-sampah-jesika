import { Env } from "@/app/env";
import * as utils from "@/utils";
import { Storages } from "@/utils/storage";
import { DatasetValidate } from "@/validators/DatasetValidate";

export class DatasetCtrl {
   static async index(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.dataset.findMany({
            orderBy: {
               id: "desc",
            },
         }),
      });
   }
   static async store(c: utils.Context): Promise<any> {
      const data = await DatasetValidate.store(c);
      const apiReq = await utils.requestApi.post(
         `http://${Env.ml_hostname}:${Env.ml_port}/dataset`,
         data
      );
      return c.json({
         data: apiReq,
         message: "Data berhasil ditambahkan",
      });
   }

   static async destroy(c: utils.Context): Promise<any> {
      const data = await utils.dbClient.dataset.delete({
         where: {
            id :  Number(c.req.param("id")),
         }
      }).then(async (res) => {
         await Storages.destroy(res.storage_uid);
         return res;
      });
      return c.json({
         data: data,
         message: "Data berhasil dihapus",
      });
   }
}
