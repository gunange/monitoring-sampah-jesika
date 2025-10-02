import * as utils from "@/utils";
import { Storages } from "@/utils/storage";

export class StorageController {
   static async index(c: utils.Context): Promise<any> {
      return await Storages.readonly(c.req.param("uid"));
   }
   static async info(c: utils.Context): Promise<any> {
      return c.json({
         data : await utils.dbClient.storage.findFirstOrThrow({
            where : {
               uid : c.req.param("uid")
             },
             select : {
               mime_type : true,
               name : true,
               size : true,
             }
         })
      });
   }
}
