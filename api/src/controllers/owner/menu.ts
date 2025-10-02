import * as utils from "@/utils";
import { Storages } from "@/utils/storage";
import { MenuValidate } from "@/validators/MenuValidate";

const include = {
   Kategori : true,
}

export class MenuCtrl {
   static async index(c: utils.Context): Promise<any> {
      return c.json({
         data: await utils.dbClient.menuItem.findMany({
            include :{
               Kategori : true,
            }
         }),
      });
   }
   static async store(c: utils.Context): Promise<any> {
      const data = await MenuValidate.upsert(c);

      return c.json({
         data: await utils.dbClient.menuItem.create({
            data: data,
            include
         }),
         message: "Data berhasil ditambahkan",
      });
   }
   static async update(c: utils.Context): Promise<any> {
      const data = await MenuValidate.upsert(c);
      return c.json({
         data: await utils.dbClient.menuItem.update({
            where: {
               id: Number(c.req.param("id")),
            },
            data,
            include
         }),
         message: "Data berhasil diperbahrui",
      });
   }
   static async gambarMenu(c: utils.Context): Promise<any> {
      const db = await utils.dbClient.menuItem.findFirstOrThrow({
         where: {
            id: Number(c.req.param("id")),
         },
      });

      let storageUid;

      if (db.storageUid) {
         storageUid = await Storages.update(c, db.storageUid);
      } else {
         storageUid = await Storages.create(c, db.nama, "menu");
      }

      return c.json({
         data: await utils.dbClient.menuItem.update({
            where: {
               id: db.id,
            },
            data: {
               storageUid: storageUid.uid,
            },
            include
         }),
         message: "Gambar Menu diperbahrui",
      });
   }
   static async destroy(c: utils.Context): Promise<any> {
      const db = await utils.dbClient.menuItem.delete({
         where: {
            id: Number(c.req.param("id")),
         },
      });

      if (db && db.storageUid) {
         await Storages.destroy(db.storageUid);
      }

      return c.json({
         data: db,
         message: "Data berhasil dihapus",
      });
   }
}
