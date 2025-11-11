import * as utils from "@/utils";
import { Env } from "@/app/env";
import { Storages } from "@/utils/storage";
import { DatasetValidate } from "@/validators/DatasetValidate";
import { UsersRepo } from "@/repositories";

export class MachineCtrl {
   static async index(c: utils.Context): Promise<any> {
      const data = await utils.requestApi.get(
         `http://${Env.ml_hostname}:${Env.ml_port}/machine-learning`,
         { name: "Machine Learning" }
      );
      return c.json(data);
   }
   static async start(c: utils.Context): Promise<any> {
      const data = await utils.requestApi.get(
         `http://${Env.ml_hostname}:${Env.ml_port}/machine-learning/start`,
         { name: "Machine Learning" }
      );
      return c.json(data);
   }
   static async stop(c: utils.Context): Promise<any> {
      const data = await utils.requestApi.get(
         `http://${Env.ml_hostname}:${Env.ml_port}/machine-learning/stop`,
         { name: "Machine Learning" }
      );
      return c.json(data);
   }
   static async storeToMl(c: utils.Context): Promise<any> {
      const storage = await Storages.create(
         c,
         Date.now().toString(),
         "dataset"
      );
      const data = await DatasetValidate.storeFormMl(c);
      data.storage_uid = storage.uid;

      return c.json({
         data: await utils.dbClient.dataset.create({ data }),
         message: "Data berhasil ditambahkan",
      });
   }

   static async dataset(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.dataset.findMany({
            orderBy: {
               id: "desc",
            },
         }),
      });
   }
}
