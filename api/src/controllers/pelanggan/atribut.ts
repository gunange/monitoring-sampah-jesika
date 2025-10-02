import * as utils from "@/utils";

export class AtributCtrl {
   static async meja(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.meja.findMany(),
      });
   }
   static async kategori(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.kategori.findMany(),
      });
   }
   

}
