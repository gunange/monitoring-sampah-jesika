import * as utils from "@/utils";
import { Storages } from "@/utils/storage";

export class StorageCtrl {
   static async index(c: utils.Context): Promise<any> {
      return c.json({
         data: [],
      });
   }
   static async store(c: utils.Context): Promise<any> {
      return c.json({
         data: await Storages.create(c, "C", "slip-ragistrasi/username"),
         message: "Data berhasil ditambahkan",
      });
   }
   static async update(c: utils.Context): Promise<any> {
      return c.json({
         data: await Storages.update(c, c.req.param("uid")),
         message: "Data berhasil diperbahrui",
      });
   }
   static async destroy(c: utils.Context): Promise<any> {
      return c.json({
         data: await Storages.destroy(c.req.param("uid")),
         message: "Data berhasil dihapus",
      });
   }
}
