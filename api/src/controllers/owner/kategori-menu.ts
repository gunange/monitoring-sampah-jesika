import * as utils from "@/utils";
import { KategoriValidate } from "@/validators/KategoriValidate";

export class KategoriMenuCtrl {
   static async index(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.kategori.findMany(),
      });
   }
   static async store(c: utils.Context): Promise<any> {
      const data = await KategoriValidate.upsert(c);

      return c.json({
         data: await utils.dbClient.kategori.create({
            data: data,
         }),
         message: "Data berhasil ditambahkan",
      });
   }
   static async update(c: utils.Context): Promise<any> {
      const data = await KategoriValidate.upsert(c);
      return c.json({
         data: await utils.dbClient.kategori.update({
            where: {
               id: Number(c.req.param("id")),
            },
            data,
         }),
         message: "Data berhasil diperbahrui",
      });
   }
   static async destroy(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.kategori.delete({
            where: {
               id: Number(c.req.param("id")),
            },
         }),
         message: "Data berhasil dihapus",
      });
   }
}
